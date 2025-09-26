import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

from database import init_database, get_user_progress, update_user_progress
from learning_data import get_learning_topics, get_topic_by_id
from ai_service import get_personalized_recommendations
from nsqf import get_ai_ml_recommendations, get_nsqf_level_by_education
from utils import initialize_session_state, get_user_stats, get_recent_activities
from data_persistence import load_session_from_file, save_session_to_file, auto_save_session, DataManager, get_user_id
from achievement_system import update_user_achievements

init_database()

st.set_page_config(
    page_title="JourneyGen",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_session_state()

if 'user_id' not in st.session_state:
    st.session_state.user_id = "default_user"
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None

if 'data_loaded' not in st.session_state:
        data_manager = DataManager()
    all_users = data_manager.get_all_users()
    if all_users:
                recent_user_id = all_users[-1]         if load_session_from_file(recent_user_id):
            st.session_state.user_id = recent_user_id
            st.session_state.data_loaded = True

def main():
    st.title("🤖 JourneyGen")
    st.markdown("Welcome to your personalized AI/ML learning journey with career progression!")
    st.markdown("---")

        with st.sidebar:
        st.header("👤 User Profile")
        
                user_name = st.text_input("Your Name", value=st.session_state.get('user_name', 'AI Learner'))
        st.session_state.user_name = user_name
        
                education_options = ["High School", "Diploma", "Bachelor's", "Master's", "PhD"]
        education = st.selectbox(
            "Education Level",
            education_options,
            index=2 if not st.session_state.get('user_education') else
            education_options.index(st.session_state.get('user_education', "Bachelor's"))
        )
        
                experience_options = ["Beginner", "Intermediate", "Advanced"]
        experience_level = st.selectbox(
            "Experience Level",
            experience_options,
            key="experience_level"
        )
        
                interests = st.multiselect(
            "Learning Interests",
            ["Machine Learning", "Deep Learning", "Natural Language Processing",
             "Computer Vision", "Reinforcement Learning", "MLOps", "Data Science", 
             "Robotics", "AI Ethics"],
            default=st.session_state.get('user_interests', ["Machine Learning", "Deep Learning"]),
            key="interests"
        )
        
                st.page_link("pages/2_NSQF_Pathway.py", label="NSQF Career Pathway", icon="🎯")
        
                if st.button("Update Profile"):
            st.session_state.user_name = user_name
            st.session_state.user_education = education
            st.session_state.user_experience = experience_level
            st.session_state.user_interests = interests
            
                        if save_session_to_file():
                st.success("Profile updated and saved!")
                                user_data = {
                    'profile': {'name': user_name, 'education': education, 'experience': experience_level, 'interests': interests},
                    'progress': st.session_state.get('learning_progress', {}),
                    'activities': st.session_state.get('recent_activities', []),
                    'certifications': st.session_state.get('certifications', []),
                    'achievements': st.session_state.get('achievements', []),
                    'milestones': st.session_state.get('milestones', [])
                }
                
                achievement_updates = update_user_achievements(user_data)
                if achievement_updates['new_achievements']:
                    st.balloons()
                    st.success("🎉 New achievements unlocked! Check the Achievements page.")
                    st.session_state.achievements = user_data['achievements']
                    save_session_to_file()
            else:
                st.success("Profile updated!")
                st.warning("Could not save to file - changes will be lost when session ends.")
            st.rerun()

        col1, col2 = st.columns([2, 1])
    
    with col1:
                st.header("📊 Dashboard Overview")
        if st.session_state.get('user_name'):
            st.success(f"Welcome back, **{st.session_state.user_name}**!")
            
                        profile_col1, profile_col2 = st.columns(2)
            with profile_col1:
                st.info(f"**Education:** {education}")
                st.info(f"**Experience:** {experience_level}")
            with profile_col2:
                nsqf_level = get_nsqf_level_by_education(education)
                st.info(f"**NSQF Level:** {nsqf_level}")
                st.info(f"**Interests:** {', '.join(interests)}")
        else:
            st.warning("Please update your profile in the sidebar to get personalized recommendations.")
        
                st.subheader("📈 Quick Statistics")
        
                stats_app2 = get_user_stats()
        progress_data = get_user_progress(st.session_state.user_id)
        topics = get_learning_topics()
        
                total_topics = len(topics) if topics else stats_app2['total_topics']
        completed_topics = len([p for p in progress_data if p['progress'] >= 100]) if progress_data else stats_app2['completed']
        completion_rate = (completed_topics / total_topics * 100) if total_topics > 0 else stats_app2['completion_rate']
        study_streak = stats_app2['streak']
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Total Topics", total_topics, delta=5)
        with metric_col2:
            st.metric("Completed", completed_topics, delta=2)
        with metric_col3:
            st.metric("Completion Rate", f"{completion_rate:.1f}%", delta="1.2%")
        with metric_col4:
            st.metric("Learning Streak", f"{study_streak} days", delta=1)

                st.subheader("📊 Learning Progress")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
                        if progress_data:
                df = pd.DataFrame(progress_data)
                difficulty_progress = df.groupby('difficulty')['progress'].mean().reset_index()
                fig_progress = px.bar(
                    difficulty_progress,
                    x='difficulty',
                    y='progress',
                    title="Average Progress by Difficulty Level",
                    color='progress',
                    color_continuous_scale='viridis'
                )
            else:
                                progress_data_fallback = pd.DataFrame({
                    'Topic': ['Machine Learning', 'Deep Learning', 'Data Science', 'NLP', 'Computer Vision'],
                    'Progress': [85, 60, 90, 45, 30],
                    'Total': [100, 100, 100, 100, 100]
                })
                fig_progress = px.bar(
                    progress_data_fallback,
                    x='Topic',
                    y='Progress',
                    title='Learning Progress by Topic',
                    color='Progress',
                    color_continuous_scale='Blues'
                )
            
            fig_progress.update_layout(height=400)
            st.plotly_chart(fig_progress, use_container_width=True)

        with chart_col2:
                        if progress_data:
                df = pd.DataFrame(progress_data)
                completed = len(df[df['progress'] >= 100])
                in_progress = len(df[(df['progress'] > 0) & (df['progress'] < 100)])
                not_started = len(df[df['progress'] == 0])
            else:
                completed = completed_topics
                in_progress = 8
                not_started = 12
            
                        fig_pie = go.Figure(data=[go.Pie(
                labels=['Completed', 'In Progress', 'Not Started'],
                values=[completed, in_progress, not_started],
                hole=0.3
            )])
            fig_pie.update_layout(title="Learning Status Distribution", height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
                st.subheader("🎯 Personalized Recommendations")
        
                try:
            if progress_data:
                recommendations_app1 = get_personalized_recommendations(
                    experience_level,
                    interests,
                    progress_data if progress_data else []
                )
                
                if recommendations_app1:
                    for i, rec in enumerate(recommendations_app1[:3], 1):
                        with st.container():
                            st.markdown(f"**{i}. {rec['title']}**")
                            st.markdown(f"*{rec['difficulty']} level*")
                            st.markdown(rec['description'])
                            if st.button(f"Start Learning", key=f"rec_{i}"):
                                st.session_state.current_topic = rec['topic_id']
                                st.switch_page("pages/1_Learning_Paths.py")
                            st.markdown("---")
                else:
                    raise Exception("No recommendations from ai_service")
        except Exception as e:
                        if st.session_state.get('user_interests') and st.session_state.get('user_experience'):
                recommendations_app2 = get_ai_ml_recommendations(
                    st.session_state.user_interests,
                    experience_level,
                    education
                )
                
                for i, rec in enumerate(recommendations_app2[:5], 1):
                    with st.expander(f"📚 Recommendation {i}: {rec['title']}"):
                        st.write(f"**Level:** {rec['level']}")
                        st.write(f"**Duration:** {rec['duration']}")
                        st.write(f"**Description:** {rec['description']}")
                        st.write(f"**Priority:** {rec['priority']}")
            else:
                st.info("Complete your profile to get personalized recommendations.")

                st.subheader("📝 Recent Activity")
        
                if progress_data:
            recent_df = pd.DataFrame(progress_data).sort_values('last_accessed', ascending=False).head(5)
            for _, row in recent_df.iterrows():
                topic = get_topic_by_id(row['topic_id'])
                if topic:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{topic['title']}**")
                    with col2:
                        st.write(f"{row['progress']:.0f}%")
                    with col3:
                        st.write(topic['difficulty'])
        else:
                        recent_activities = get_recent_activities()
            for activity in recent_activities:
                st.write(f"🔹 {activity['action']} - {activity['topic']}")
                st.caption(f"{activity['date']} • {activity['duration']}")
            st.write("---")

        if not progress_data and not get_recent_activities():
        st.info("No recent activity. Start learning to see your progress here!")

if __name__ == "__main__":
    main()