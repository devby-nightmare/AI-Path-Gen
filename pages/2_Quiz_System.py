import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ai_service import generate_quiz_questions
from database import save_quiz_result, get_quiz_history, update_user_progress
from learning_data import get_topic_by_id, get_learning_topics
import json
from datetime import datetime

st.set_page_config(page_title="Quiz System", page_icon="🧠", layout="wide")

def initialize_quiz_session():
    """Initialize quiz session state variables."""
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'quiz_topic' not in st.session_state:
        st.session_state.quiz_topic = None

def start_quiz(topic_id: str, difficulty: str, num_questions: int):
    """Start a new quiz for the given topic."""
    try:
        with st.spinner("Generating quiz questions..."):
            questions = generate_quiz_questions(topic_id, difficulty, num_questions)
        
        if questions:
            st.session_state.quiz_questions = questions
            st.session_state.quiz_active = True
            st.session_state.current_question = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.quiz_topic = topic_id
            st.success(f"Quiz started! {len(questions)} questions generated.")
            st.rerun()
        else:
            st.error("Failed to generate quiz questions. Please try again.")
    except Exception as e:
        st.error(f"Error starting quiz: {str(e)}")

def submit_quiz():
    """Submit the completed quiz and calculate results."""
    if not st.session_state.quiz_questions:
        return
    
    correct_answers = 0
    total_questions = len(st.session_state.quiz_questions)
    
    for i, question in enumerate(st.session_state.quiz_questions):
        user_answer = st.session_state.user_answers.get(i)
        if user_answer is not None and user_answer == question['correct_answer']:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100
    
    # Save quiz result to database
    if 'user_id' in st.session_state:
        quiz_data = {
            'questions': st.session_state.quiz_questions,
            'answers': st.session_state.user_answers,
            'score': score,
            'correct_answers': correct_answers
        }
        
        save_quiz_result(
            st.session_state.user_id,
            st.session_state.quiz_topic,
            quiz_data,
            score,
            total_questions
        )
        
        # Update topic progress based on quiz performance
        if score >= 80:  # Good performance
            progress_boost = 20
        elif score >= 60:  # Average performance
            progress_boost = 10
        else:  # Need improvement
            progress_boost = 5
        
        # Get current progress
        from database import get_user_progress
        progress_data = get_user_progress(st.session_state.user_id)
        current_progress = 0
        for p in progress_data:
            if p['topic_id'] == st.session_state.quiz_topic:
                current_progress = p['progress']
                break
        
        new_progress = min(100, current_progress + progress_boost)
        topic = get_topic_by_id(st.session_state.quiz_topic)
        
        update_user_progress(
            st.session_state.user_id,
            st.session_state.quiz_topic,
            new_progress,
            quiz_score=score,
            difficulty=topic['difficulty'] if topic else 'Unknown'
        )
    
    st.session_state.quiz_completed = True
    st.session_state.quiz_score = score
    st.session_state.correct_answers = correct_answers
    
    return score, correct_answers, total_questions

def reset_quiz():
    """Reset quiz session state."""
    st.session_state.quiz_active = False
    st.session_state.quiz_questions = []
    st.session_state.current_question = 0
    st.session_state.user_answers = {}
    st.session_state.quiz_completed = False
    st.session_state.quiz_topic = None

def main():
    st.title("🧠 Interactive Quiz System")
    st.markdown("Test your knowledge with AI-generated quizzes tailored to each topic.")
    
    initialize_quiz_session()
    
    # Sidebar for quiz options
    with st.sidebar:
        st.header("Quiz Options")
        
        # Topic selection
        topics = get_learning_topics()
        topic_options = {f"{topic['title']} ({topic['difficulty']})": topic['id'] for topic in topics}
        
        selected_topic_display = st.selectbox("Select Topic", list(topic_options.keys()))
        selected_topic_id = topic_options[selected_topic_display]
        selected_topic = get_topic_by_id(selected_topic_id)
        
        # Quiz settings
        difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(selected_topic['difficulty'])
        )
        
        num_questions = st.slider("Number of Questions", 3, 10, 5)
        
        # Start quiz button
        if not st.session_state.quiz_active:
            if st.button("🚀 Start Quiz", type="primary"):
                start_quiz(selected_topic_id, difficulty_level, num_questions)
        else:
            if st.button("🔄 Reset Quiz"):
                reset_quiz()
                st.rerun()
        
        # Quiz history
        if 'user_id' in st.session_state:
            st.markdown("---")
            st.subheader("📊 Quiz History")
            quiz_history = get_quiz_history(st.session_state.user_id)
            
            if quiz_history:
                for i, quiz in enumerate(quiz_history[:5]):
                    topic = get_topic_by_id(quiz['topic_id'])
                    topic_title = topic['title'] if topic else 'Unknown Topic'
                    score_percentage = (quiz['score'] / quiz['total_questions']) * 100
                    
                    st.markdown(f"**{topic_title}**")
                    st.markdown(f"Score: {score_percentage:.1f}% ({quiz['score']}/{quiz['total_questions']})")
                    st.markdown(f"Date: {quiz['timestamp'][:10]}")
                    st.markdown("---")
            else:
                st.info("No quiz history yet. Take your first quiz!")
    
    # Main quiz area
    if not st.session_state.quiz_active:
        # Welcome screen
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Welcome to the Quiz System!")
            st.markdown("""
            **How it works:**
            1. Select a topic and difficulty level from the sidebar
            2. Choose the number of questions (3-10)
            3. Click 'Start Quiz' to begin
            4. Answer all questions and submit for results
            5. Get detailed feedback and explanations
            
            **Features:**
            - AI-generated questions tailored to each topic
            - Instant feedback with detailed explanations
            - Progress tracking based on quiz performance
            - Comprehensive quiz history
            """)
            
            if selected_topic:
                st.markdown(f"**Selected Topic:** {selected_topic['title']}")
                st.markdown(f"**Description:** {selected_topic['description']}")
                st.markdown(f"**Estimated Study Time:** {selected_topic['estimated_hours']} hours")
        
        with col2:
            # Quiz statistics
            if 'user_id' in st.session_state:
                st.subheader("📈 Your Stats")
                quiz_history = get_quiz_history(st.session_state.user_id)
                
                if quiz_history:
                    total_quizzes = len(quiz_history)
                    avg_score = sum(q['score'] for q in quiz_history) / sum(q['total_questions'] for q in quiz_history) * 100
                    
                    st.metric("Total Quizzes", total_quizzes)
                    st.metric("Average Score", f"{avg_score:.1f}%")
                    
                    # Recent performance chart
                    if len(quiz_history) >= 3:
                        recent_scores = [(q['score'] / q['total_questions']) * 100 for q in quiz_history[:10]]
                        fig = px.line(
                            x=list(range(1, len(recent_scores) + 1)),
                            y=recent_scores,
                            title="Recent Quiz Performance",
                            labels={'x': 'Quiz Number (Most Recent)', 'y': 'Score (%)'}
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Take your first quiz to see statistics!")
    
    elif st.session_state.quiz_completed:
        # Quiz results screen
        st.subheader("🎉 Quiz Completed!")
        
        score = st.session_state.quiz_score
        correct = st.session_state.correct_answers
        total = len(st.session_state.quiz_questions)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{score:.1f}%")
        with col2:
            st.metric("Correct Answers", f"{correct}/{total}")
        with col3:
            if score >= 80:
                performance = "Excellent! 🌟"
            elif score >= 60:
                performance = "Good 👍"
            else:
                performance = "Keep Learning 📚"
            st.metric("Performance", performance)
        
        # Performance visualization
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Quiz Score"},
            delta={'reference': 70},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed results
        st.subheader("📝 Detailed Results")
        
        for i, question in enumerate(st.session_state.quiz_questions):
            user_answer = st.session_state.user_answers.get(i)
            correct_answer = question['correct_answer']
            is_correct = user_answer == correct_answer
            
            with st.expander(f"Question {i+1}: {'✅' if is_correct else '❌'}"):
                st.markdown(f"**{question['question']}**")
                
                for j, option in enumerate(question['options']):
                    if j == correct_answer:
                        st.markdown(f"✅ {option} *(Correct Answer)*")
                    elif j == user_answer:
                        st.markdown(f"❌ {option} *(Your Answer)*")
                    else:
                        st.markdown(f"• {option}")
                
                st.markdown(f"**Explanation:** {question['explanation']}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Take Another Quiz"):
                reset_quiz()
                st.rerun()
        with col2:
            if st.button("📚 Study This Topic"):
                st.session_state.current_topic = st.session_state.quiz_topic
                st.switch_page("pages/5_Study_Materials.py")
    
    else:
        # Active quiz screen
        questions = st.session_state.quiz_questions
        current_q = st.session_state.current_question
        
        if current_q < len(questions):
            question = questions[current_q]
            
            # Progress indicator
            progress = (current_q + 1) / len(questions)
            st.progress(progress)
            st.markdown(f"**Question {current_q + 1} of {len(questions)}**")
            
            # Question display
            st.subheader(question['question'])
            
            # Answer options
            user_answer = st.radio(
                "Select your answer:",
                range(len(question['options'])),
                format_func=lambda x: question['options'][x],
                key=f"question_{current_q}"
            )
            
            # Store answer
            st.session_state.user_answers[current_q] = user_answer
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if current_q > 0:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_question -= 1
                        st.rerun()
            
            with col2:
                # Show current question info
                st.markdown(f"*Difficulty: {question.get('difficulty', 'Unknown')}*")
            
            with col3:
                if current_q < len(questions) - 1:
                    if st.button("Next ➡️"):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("🏁 Submit Quiz", type="primary"):
                        submit_quiz()
                        st.rerun()
        
        # Question overview
        st.markdown("---")
        st.subheader("Question Overview")
        
        overview_cols = st.columns(min(len(questions), 10))
        for i, col in enumerate(overview_cols):
            if i < len(questions):
                answered = "✅" if i in st.session_state.user_answers else "⭕"
                current = "📍" if i == current_q else ""
                
                with col:
                    if st.button(f"{answered} {i+1} {current}", key=f"nav_{i}"):
                        st.session_state.current_question = i
                        st.rerun()

if __name__ == "__main__":
    main()
