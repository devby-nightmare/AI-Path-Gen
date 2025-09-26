import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from database import get_user_progress, get_quiz_history
from learning_data import get_topic_by_id, get_learning_topics, get_topic_categories
import numpy as np

st.set_page_config(page_title="Progress Tracking", page_icon="📊", layout="wide")

def calculate_study_streak(progress_data):
    """Calculate current study streak based on progress updates."""
    # This is a simplified calculation - in a real app, you'd track daily activity
    if not progress_data:
        return 0
    
    # Sort by last accessed date
    sorted_data = sorted(progress_data, key=lambda x: x['last_accessed'], reverse=True)
    
    # For demo purposes, assume a streak based on recent activity
    recent_activity = len([p for p in progress_data if p['progress'] > 0])
    return min(recent_activity, 30)  # Cap at 30 days

def get_learning_insights(progress_data, quiz_history):
    """Generate learning insights and recommendations."""
    insights = []
    
    if not progress_data:
        insights.append({
            "type": "info",
            "title": "Get Started",
            "message": "Begin your learning journey by selecting topics from the Learning Paths page."
        })
        return insights
    
    # Progress insights
    total_topics = len(progress_data)
    completed_topics = len([p for p in progress_data if p['progress'] >= 100])
    in_progress_topics = len([p for p in progress_data if 0 < p['progress'] < 100])
    
    if completed_topics > 0:
        insights.append({
            "type": "success",
            "title": "Great Progress!",
            "message": f"You've completed {completed_topics} topics. Keep up the excellent work!"
        })
    
    if in_progress_topics > 5:
        insights.append({
            "type": "warning",
            "title": "Focus Recommendation",
            "message": f"You have {in_progress_topics} topics in progress. Consider focusing on fewer topics for better retention."
        })
    
    # Quiz performance insights
    if quiz_history:
        avg_score = sum(q['score'] for q in quiz_history) / sum(q['total_questions'] for q in quiz_history) * 100
        
        if avg_score >= 80:
            insights.append({
                "type": "success",
                "title": "Quiz Master",
                "message": f"Excellent quiz performance with {avg_score:.1f}% average score!"
            })
        elif avg_score < 60:
            insights.append({
                "type": "info",
                "title": "Practice Opportunity",
                "message": f"Your quiz average is {avg_score:.1f}%. Consider reviewing study materials before taking quizzes."
            })
    
    # Difficulty distribution insights
    difficulty_counts = {}
    for p in progress_data:
        difficulty = p.get('difficulty', 'Unknown')
        difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
    
    if difficulty_counts.get('Advanced', 0) > difficulty_counts.get('Beginner', 0):
        insights.append({
            "type": "warning",
            "title": "Foundation Check",
            "message": "You're tackling many advanced topics. Ensure you have solid fundamentals first."
        })
    
    return insights

def main():
    st.title("📊 Progress Tracking & Analytics")
    st.markdown("Visualize your learning journey and track your achievements.")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Please set up your profile in the main dashboard to track progress.")
        return
    
    # Get user data
    progress_data = get_user_progress(st.session_state.user_id)
    quiz_history = get_quiz_history(st.session_state.user_id)
    
    # Overview metrics
    st.subheader("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_topics = len(progress_data)
        st.metric("Topics Started", total_topics)
    
    with col2:
        completed_topics = len([p for p in progress_data if p['progress'] >= 100])
        st.metric("Completed", completed_topics)
    
    with col3:
        avg_progress = np.mean([p['progress'] for p in progress_data]) if progress_data else 0
        st.metric("Average Progress", f"{avg_progress:.1f}%")
    
    with col4:
        study_streak = calculate_study_streak(progress_data)
        st.metric("Study Streak", f"{study_streak} days")
    
    if not progress_data:
        st.info("Start learning topics to see your progress analytics here!")
        
        # Show available topics as motivation
        st.subheader("🚀 Ready to Start?")
        topics = get_learning_topics()
        beginner_topics = [t for t in topics if t['difficulty'] == 'Beginner'][:3]
        
        cols = st.columns(len(beginner_topics))
        for i, topic in enumerate(beginner_topics):
            with cols[i]:
                st.markdown(f"**{topic['title']}**")
                st.markdown(topic['description'][:100] + "...")
                if st.button(f"Start Learning", key=f"start_{topic['id']}"):
                    st.session_state.current_topic = topic['id']
                    st.switch_page("pages/1_Learning_Paths.py")
        
        return
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Progress Overview", "🧠 Quiz Analytics", "📅 Timeline", "💡 Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Progress by difficulty
            df = pd.DataFrame(progress_data)
            difficulty_progress = df.groupby('difficulty')['progress'].agg(['mean', 'count']).reset_index()
            
            fig_difficulty = px.bar(
                difficulty_progress,
                x='difficulty',
                y='mean',
                title="Average Progress by Difficulty Level",
                labels={'mean': 'Average Progress (%)', 'difficulty': 'Difficulty Level'},
                color='mean',
                color_continuous_scale='viridis'
            )
            fig_difficulty.update_layout(height=400)
            st.plotly_chart(fig_difficulty, use_container_width=True)
        
        with col2:
            # Progress distribution
            progress_ranges = {
                'Not Started (0%)': len([p for p in progress_data if p['progress'] == 0]),
                'Beginner (1-25%)': len([p for p in progress_data if 1 <= p['progress'] <= 25]),
                'Learning (26-50%)': len([p for p in progress_data if 26 <= p['progress'] <= 50]),
                'Progressing (51-75%)': len([p for p in progress_data if 51 <= p['progress'] <= 75]),
                'Advanced (76-99%)': len([p for p in progress_data if 76 <= p['progress'] <= 99]),
                'Completed (100%)': len([p for p in progress_data if p['progress'] == 100])
            }
            
            # Remove empty categories
            progress_ranges = {k: v for k, v in progress_ranges.items() if v > 0}
            
            fig_distribution = px.pie(
                values=list(progress_ranges.values()),
                names=list(progress_ranges.keys()),
                title="Learning Progress Distribution"
            )
            fig_distribution.update_layout(height=400)
            st.plotly_chart(fig_distribution, use_container_width=True)
        
        # Detailed progress table
        st.subheader("📝 Detailed Progress")
        
        # Create detailed DataFrame
        detailed_data = []
        for p in progress_data:
            topic = get_topic_by_id(p['topic_id'])
            if topic:
                detailed_data.append({
                    'Topic': topic['title'],
                    'Category': topic['category'],
                    'Difficulty': p['difficulty'],
                    'Progress': f"{p['progress']:.1f}%",
                    'Quiz Scores': len(p['quiz_scores']),
                    'Last Accessed': p['last_accessed'][:10] if p['last_accessed'] else 'Never'
                })
        
        if detailed_data:
            df_detailed = pd.DataFrame(detailed_data)
            st.dataframe(df_detailed, use_container_width=True)
    
    with tab2:
        if not quiz_history:
            st.info("Take some quizzes to see analytics here!")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Quiz performance over time
                quiz_df = pd.DataFrame(quiz_history)
                quiz_df['score_percentage'] = (quiz_df['score'] / quiz_df['total_questions']) * 100
                quiz_df['date'] = pd.to_datetime(quiz_df['timestamp']).dt.date
                
                fig_performance = px.line(
                    quiz_df.sort_values('timestamp'),
                    x='date',
                    y='score_percentage',
                    title="Quiz Performance Over Time",
                    labels={'score_percentage': 'Score (%)', 'date': 'Date'},
                    markers=True
                )
                fig_performance.update_layout(height=400)
                st.plotly_chart(fig_performance, use_container_width=True)
            
            with col2:
                # Quiz performance by topic
                topic_scores = {}
                for quiz in quiz_history:
                    topic = get_topic_by_id(quiz['topic_id'])
                    if topic:
                        topic_name = topic['title']
                        score_pct = (quiz['score'] / quiz['total_questions']) * 100
                        if topic_name not in topic_scores:
                            topic_scores[topic_name] = []
                        topic_scores[topic_name].append(score_pct)
                
                # Calculate average scores
                avg_topic_scores = {topic: np.mean(scores) for topic, scores in topic_scores.items()}
                
                if avg_topic_scores:
                    fig_topics = px.bar(
                        x=list(avg_topic_scores.values()),
                        y=list(avg_topic_scores.keys()),
                        orientation='h',
                        title="Average Quiz Scores by Topic",
                        labels={'x': 'Average Score (%)', 'y': 'Topic'},
                        color=list(avg_topic_scores.values()),
                        color_continuous_scale='RdYlGn'
                    )
                    fig_topics.update_layout(height=400)
                    st.plotly_chart(fig_topics, use_container_width=True)
            
            # Quiz statistics
            st.subheader("🎯 Quiz Statistics")
            
            total_quizzes = len(quiz_history)
            total_questions = sum(q['total_questions'] for q in quiz_history)
            total_correct = sum(q['score'] for q in quiz_history)
            overall_accuracy = (total_correct / total_questions) * 100 if total_questions > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Quizzes", total_quizzes)
            with col2:
                st.metric("Questions Answered", total_questions)
            with col3:
                st.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
            with col4:
                best_score = max((q['score'] / q['total_questions']) * 100 for q in quiz_history)
                st.metric("Best Score", f"{best_score:.1f}%")
    
    with tab3:
        # Learning timeline
        st.subheader("📅 Learning Timeline")
        
        # Create timeline data
        timeline_data = []
        
        # Add progress updates
        for p in progress_data:
            if p['last_accessed']:
                topic = get_topic_by_id(p['topic_id'])
                if topic:
                    timeline_data.append({
                        'date': p['last_accessed'][:10],
                        'event': f"Studied: {topic['title']}",
                        'type': 'Study',
                        'progress': p['progress']
                    })
        
        # Add quiz attempts
        for quiz in quiz_history:
            topic = get_topic_by_id(quiz['topic_id'])
            if topic:
                score_pct = (quiz['score'] / quiz['total_questions']) * 100
                timeline_data.append({
                    'date': quiz['timestamp'][:10],
                    'event': f"Quiz: {topic['title']} ({score_pct:.1f}%)",
                    'type': 'Quiz',
                    'progress': score_pct
                })
        
        if timeline_data:
            # Sort by date
            timeline_data.sort(key=lambda x: x['date'], reverse=True)
            
            # Display timeline
            for i, event in enumerate(timeline_data[:20]):  # Show last 20 events
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.markdown(f"**{event['date']}**")
                
                with col2:
                    icon = "🧠" if event['type'] == 'Quiz' else "📚"
                    st.markdown(f"{icon} {event['event']}")
                
                with col3:
                    if event['type'] == 'Quiz':
                        if event['progress'] >= 80:
                            st.success(f"{event['progress']:.1f}%")
                        elif event['progress'] >= 60:
                            st.warning(f"{event['progress']:.1f}%")
                        else:
                            st.error(f"{event['progress']:.1f}%")
                    else:
                        st.info(f"{event['progress']:.1f}%")
                
                if i < len(timeline_data[:20]) - 1:
                    st.markdown("---")
        else:
            st.info("Your learning timeline will appear here as you study and take quizzes.")
    
    with tab4:
        # Learning insights and recommendations
        st.subheader("💡 Learning Insights")
        
        insights = get_learning_insights(progress_data, quiz_history)
        
        for insight in insights:
            if insight['type'] == 'success':
                st.success(f"**{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'warning':
                st.warning(f"**{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'info':
                st.info(f"**{insight['title']}**: {insight['message']}")
            else:
                st.markdown(f"**{insight['title']}**: {insight['message']}")
        
        # Learning recommendations
        st.subheader("🎯 Personalized Recommendations")
        
        completed_topics = [p['topic_id'] for p in progress_data if p['progress'] >= 100]
        all_topics = get_learning_topics()
        
        # Find topics with completed prerequisites
        recommended_topics = []
        for topic in all_topics:
            if topic['id'] not in [p['topic_id'] for p in progress_data]:  # Not started
                prerequisites = topic.get('prerequisites', [])
                if all(prereq in completed_topics for prereq in prerequisites):
                    recommended_topics.append(topic)
        
        if recommended_topics:
            st.markdown("Based on your completed topics, here are some recommendations:")
            
            for i, topic in enumerate(recommended_topics[:3], 1):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{i}. {topic['title']}**")
                    st.markdown(f"*{topic['difficulty']} • {topic['category']} • {topic['estimated_hours']}h*")
                    st.markdown(topic['description'])
                
                with col2:
                    if st.button(f"Start Learning", key=f"rec_insight_{topic['id']}"):
                        st.session_state.current_topic = topic['id']
                        st.switch_page("pages/5_Study_Materials.py")
        else:
            st.info("Complete more topics to get personalized recommendations!")

if __name__ == "__main__":
    main()
