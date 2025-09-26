import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from learning_data import (
    get_learning_topics, get_topics_by_difficulty, get_topics_by_category,
    get_topic_by_id, get_prerequisite_topics, get_next_topics,
    get_learning_path_suggestions, get_topic_categories, search_topics
)
from database import get_user_progress, update_user_progress
import pandas as pd

st.set_page_config(page_title="Learning Paths", page_icon="🛤️", layout="wide")

def main():
    st.title("🛤️ AI/ML Learning Paths")
    st.markdown("Explore structured learning paths tailored to your experience level and interests.")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters & Search")
        
        # Search functionality
        search_query = st.text_input("🔍 Search Topics", placeholder="Enter keywords...")
        
        # Difficulty filter
        difficulty_filter = st.selectbox(
            "Difficulty Level",
            ["All", "Beginner", "Intermediate", "Advanced"]
        )
        
        # Category filter
        categories = ["All"] + get_topic_categories()
        category_filter = st.selectbox("Category", categories)
        
        # Show only available topics (prerequisites met)
        if 'user_id' in st.session_state:
            progress_data = get_user_progress(st.session_state.user_id)
            completed_topics = [p['topic_id'] for p in progress_data if p['progress'] >= 100]
            show_available_only = st.checkbox("Show only available topics", value=False)
        else:
            show_available_only = False
            completed_topics = []
    
    # Get and filter topics
    if search_query:
        topics = search_topics(search_query)
    else:
        topics = get_learning_topics()
    
    # Apply filters
    if difficulty_filter != "All":
        topics = [t for t in topics if t["difficulty"] == difficulty_filter]
    
    if category_filter != "All":
        topics = [t for t in topics if t["category"] == category_filter]
    
    if show_available_only:
        available_topics = []
        for topic in topics:
            prerequisites = topic.get("prerequisites", [])
            if all(prereq in completed_topics for prereq in prerequisites):
                available_topics.append(topic)
        topics = available_topics
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Learning path visualization
        st.subheader("📊 Learning Path Overview")
        
        if topics:
            # Create a DataFrame for visualization
            df = pd.DataFrame(topics)
            
            # Difficulty distribution
            difficulty_counts = df['difficulty'].value_counts()
            fig_difficulty = px.pie(
                values=difficulty_counts.values,
                names=difficulty_counts.index,
                title="Topics by Difficulty Level"
            )
            fig_difficulty.update_layout(height=300)
            st.plotly_chart(fig_difficulty, use_container_width=True)
            
            # Category distribution
            category_counts = df['category'].value_counts()
            fig_category = px.bar(
                x=category_counts.values,
                y=category_counts.index,
                orientation='h',
                title="Topics by Category",
                labels={'x': 'Number of Topics', 'y': 'Category'}
            )
            fig_category.update_layout(height=400)
            st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Personalized Suggestions")
        
        if hasattr(st.session_state, 'experience_level') and hasattr(st.session_state, 'interests'):
            suggested_topics = get_learning_path_suggestions(
                st.session_state.experience_level,
                st.session_state.interests
            )[:5]
            
            for i, topic in enumerate(suggested_topics, 1):
                with st.container():
                    st.markdown(f"**{i}. {topic['title']}**")
                    st.markdown(f"*{topic['difficulty']} • {topic['estimated_hours']}h*")
                    st.markdown(topic['description'][:100] + "...")
                    if st.button(f"View Details", key=f"suggest_{topic['id']}"):
                        st.session_state.selected_topic = topic['id']
                        st.rerun()
                    st.markdown("---")
        else:
            st.info("Complete your profile in the main dashboard to see personalized suggestions.")
    
    # Topics grid
    st.subheader(f"📚 Available Topics ({len(topics)})")
    
    if not topics:
        st.warning("No topics found matching your criteria. Try adjusting the filters.")
        return
    
    # Create expandable sections for each topic
    for topic in topics:
        with st.expander(f"{topic['title']} - {topic['difficulty']} ({topic['estimated_hours']}h)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Category:** {topic['category']}")
                st.markdown(f"**Description:** {topic['description']}")
                
                # Learning objectives
                st.markdown("**Learning Objectives:**")
                for objective in topic['learning_objectives']:
                    st.markdown(f"• {objective}")
                
                # Prerequisites
                if topic.get('prerequisites'):
                    st.markdown("**Prerequisites:**")
                    prereq_topics = get_prerequisite_topics(topic['id'])
                    for prereq in prereq_topics:
                        status = "✅" if prereq['id'] in completed_topics else "❌"
                        st.markdown(f"{status} {prereq['title']}")
                else:
                    st.markdown("**Prerequisites:** None")
            
            with col2:
                # Progress tracking
                if 'user_id' in st.session_state:
                    progress_data = get_user_progress(st.session_state.user_id)
                    topic_progress = next(
                        (p for p in progress_data if p['topic_id'] == topic['id']), 
                        {'progress': 0}
                    )
                    
                    current_progress = topic_progress['progress']
                    st.metric("Progress", f"{current_progress:.0f}%")
                    
                    # Progress bar
                    progress_bar = st.progress(current_progress / 100)
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("Start Learning", key=f"start_{topic['id']}"):
                            st.session_state.current_topic = topic['id']
                            st.switch_page("pages/5_Study_Materials.py")
                    
                    with col_b:
                        if current_progress > 0:
                            if st.button("Take Quiz", key=f"quiz_{topic['id']}"):
                                st.session_state.current_topic = topic['id']
                                st.switch_page("pages/2_Quiz_System.py")
                    
                    # Manual progress update
                    new_progress = st.slider(
                        "Update Progress",
                        0, 100, int(current_progress),
                        key=f"progress_{topic['id']}"
                    )
                    
                    if new_progress != current_progress:
                        if st.button("Save Progress", key=f"save_{topic['id']}"):
                            update_user_progress(
                                st.session_state.user_id,
                                topic['id'],
                                new_progress,
                                difficulty=topic['difficulty']
                            )
                            st.success("Progress updated!")
                            st.rerun()
    
    # Learning path recommendations
    if 'user_id' in st.session_state and completed_topics:
        st.subheader("🔮 What's Next?")
        next_topics = get_next_topics(completed_topics)[:3]
        
        if next_topics:
            cols = st.columns(len(next_topics))
            for i, topic in enumerate(next_topics):
                with cols[i]:
                    st.markdown(f"**{topic['title']}**")
                    st.markdown(f"*{topic['difficulty']} level*")
                    st.markdown(topic['description'][:80] + "...")
                    if st.button("Start Now", key=f"next_{topic['id']}"):
                        st.session_state.current_topic = topic['id']
                        st.switch_page("pages/5_Study_Materials.py")
        else:
            st.info("Great job! You've completed all available prerequisites. Keep exploring advanced topics!")

if __name__ == "__main__":
    main()
