"""
Utility functions for the AI Learning Career Dashboard
"""

import streamlit as st
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any

def initialize_session_state():
    """Initialize session state variables with default values"""
    
    # User profile defaults
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    
    if 'user_education' not in st.session_state:
        st.session_state.user_education = "Bachelor's"
    
    if 'user_experience' not in st.session_state:
        st.session_state.user_experience = "Beginner (0-1 years)"
    
    if 'user_interests' not in st.session_state:
        st.session_state.user_interests = ["Machine Learning", "Data Science"]
    
    # Learning progress defaults
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = {
            'total_topics': 25,
            'completed': 8,
            'in_progress': 5,
            'not_started': 12,
            'streak': 7
        }
    
    # Recent activities
    if 'recent_activities' not in st.session_state:
        st.session_state.recent_activities = generate_default_activities()
    
    # Goals and preferences
    if 'career_goals' not in st.session_state:
        st.session_state.career_goals = []
    
    if 'preferred_learning_style' not in st.session_state:
        st.session_state.preferred_learning_style = "Visual"

def generate_default_activities() -> List[Dict[str, Any]]:
    """Generate default recent activities for demonstration"""
    
    activities = [
        {
            'action': 'Completed',
            'topic': 'Introduction to Machine Learning',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'duration': '2 hours'
        },
        {
            'action': 'Started',
            'topic': 'Deep Learning Fundamentals',
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'duration': '1.5 hours'
        },
        {
            'action': 'Completed Quiz',
            'topic': 'Python for Data Science',
            'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'duration': '45 minutes'
        },
        {
            'action': 'Watched Video',
            'topic': 'Neural Network Basics',
            'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'duration': '30 minutes'
        },
        {
            'action': 'Completed',
            'topic': 'Data Preprocessing Techniques',
            'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'duration': '3 hours'
        }
    ]
    
    return activities

def get_user_stats() -> Dict[str, Any]:
    """Get user learning statistics"""
    
    progress = st.session_state.learning_progress
    completion_rate = (progress['completed'] / progress['total_topics']) * 100
    
    return {
        'total_topics': progress['total_topics'],
        'completed': progress['completed'],
        'in_progress': progress['in_progress'],
        'not_started': progress['not_started'],
        'completion_rate': completion_rate,
        'streak': progress['streak']
    }

def get_recent_activities() -> List[Dict[str, Any]]:
    """Get recent learning activities"""
    return st.session_state.recent_activities

def update_learning_progress(topic: str, action: str):
    """Update learning progress when user completes an activity"""
    
    # Add to recent activities
    new_activity = {
        'action': action,
        'topic': topic,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'duration': f"{random.randint(30, 180)} minutes"
    }
    
    # Add to beginning of list and keep only last 10
    st.session_state.recent_activities.insert(0, new_activity)
    st.session_state.recent_activities = st.session_state.recent_activities[:10]
    
    # Update progress statistics
    if action == 'Completed':
        st.session_state.learning_progress['completed'] += 1
        st.session_state.learning_progress['in_progress'] = max(0, 
            st.session_state.learning_progress['in_progress'] - 1)
    elif action == 'Started':
        st.session_state.learning_progress['in_progress'] += 1
        st.session_state.learning_progress['not_started'] = max(0,
            st.session_state.learning_progress['not_started'] - 1)

def get_personalized_greeting() -> str:
    """Get personalized greeting based on time and user data"""
    
    current_hour = datetime.now().hour
    name = st.session_state.get('user_name', 'Learner')
    
    if current_hour < 12:
        greeting = f"Good morning, {name}! 🌅"
    elif current_hour < 17:
        greeting = f"Good afternoon, {name}! ☀️"
    else:
        greeting = f"Good evening, {name}! 🌙"
    
    return greeting

def calculate_skill_proficiency(skill: str, completed_topics: List[str]) -> int:
    """Calculate skill proficiency based on completed topics"""
    
    skill_topic_mapping = {
        'Machine Learning': ['Introduction to ML', 'Supervised Learning', 'Unsupervised Learning', 
                           'Feature Engineering', 'Model Evaluation'],
        'Deep Learning': ['Neural Networks', 'CNN', 'RNN', 'Transfer Learning', 'GANs'],
        'Data Science': ['Data Analysis', 'Statistics', 'Data Visualization', 'Pandas', 'NumPy'],
        'Python': ['Python Basics', 'Object-Oriented Programming', 'Data Structures', 
                  'Libraries', 'Advanced Python']
    }
    
    if skill not in skill_topic_mapping:
        return 0
    
    required_topics = skill_topic_mapping[skill]
    completed_count = sum(1 for topic in completed_topics 
                         if any(req in topic for req in required_topics))
    
    proficiency = min(100, (completed_count / len(required_topics)) * 100)
    return int(proficiency)

def get_learning_recommendations(user_interests: List[str], experience_level: str) -> List[Dict[str, Any]]:
    """Get personalized learning recommendations"""
    
    base_recommendations = {
        'Beginner (0-1 years)': [
            {
                'title': 'Python Programming Fundamentals',
                'description': 'Master the basics of Python programming',
                'estimated_time': '4-6 weeks',
                'difficulty': 'Beginner'
            },
            {
                'title': 'Statistics for Data Science',
                'description': 'Essential statistical concepts for data analysis',
                'estimated_time': '3-4 weeks',
                'difficulty': 'Beginner'
            }
        ],
        'Intermediate (2-4 years)': [
            {
                'title': 'Advanced Machine Learning',
                'description': 'Deep dive into complex ML algorithms',
                'estimated_time': '6-8 weeks',
                'difficulty': 'Intermediate'
            },
            {
                'title': 'MLOps and Deployment',
                'description': 'Learn to deploy ML models in production',
                'estimated_time': '5-6 weeks',
                'difficulty': 'Intermediate'
            }
        ],
        'Advanced (5+ years)': [
            {
                'title': 'AI Research Methodologies',
                'description': 'Cutting-edge research techniques in AI',
                'estimated_time': '8-10 weeks',
                'difficulty': 'Advanced'
            },
            {
                'title': 'Custom AI Architecture Design',
                'description': 'Design scalable AI systems',
                'estimated_time': '10-12 weeks',
                'difficulty': 'Advanced'
            }
        ]
    }
    
    return base_recommendations.get(experience_level, [])

def format_duration(minutes: int) -> str:
    """Format duration from minutes to human-readable format"""
    
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes < 1440:  # Less than a day
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours}h {remaining_minutes}m"
    else:  # Days
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days} day{'s' if days > 1 else ''}"
        else:
            return f"{days}d {remaining_hours}h"

def get_achievement_badges(user_stats: Dict[str, Any]) -> List[str]:
    """Get achievement badges based on user statistics"""
    
    badges = []
    completed = user_stats['completed']
    streak = user_stats['streak']
    completion_rate = user_stats['completion_rate']
    
    # Completion badges
    if completed >= 1:
        badges.append("🌟 First Steps")
    if completed >= 5:
        badges.append("🚀 Learning Momentum")
    if completed >= 10:
        badges.append("🎓 Dedicated Learner")
    if completed >= 20:
        badges.append("🏆 Learning Master")
    
    # Streak badges
    if streak >= 3:
        badges.append("🔥 On Fire")
    if streak >= 7:
        badges.append("⚡ Week Warrior")
    if streak >= 30:
        badges.append("💪 Month Champion")
    
    # Completion rate badges
    if completion_rate >= 50:
        badges.append("🎯 Half Way There")
    if completion_rate >= 75:
        badges.append("⭐ Almost There")
    if completion_rate >= 90:
        badges.append("👑 Completion King")
    
    return badges

def save_user_preferences(preferences: Dict[str, Any]):
    """Save user preferences to session state"""
    
    for key, value in preferences.items():
        st.session_state[f"pref_{key}"] = value

def load_user_preferences() -> Dict[str, Any]:
    """Load user preferences from session state"""
    
    preferences = {}
    for key in st.session_state:
        if key.startswith("pref_"):
            pref_name = key[5:]  # Remove 'pref_' prefix
            preferences[pref_name] = st.session_state[key]
    
    return preferences

def validate_email(email: str) -> bool:
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_learning_path(interests: List[str], experience: str, target_role: str) -> List[Dict[str, Any]]:
    """Generate a structured learning path"""
    
    learning_path = []
    
    # Define learning modules by interest and experience
    modules = {
        'Machine Learning': {
            'Beginner': ['Python Basics', 'Statistics', 'Intro to ML', 'Supervised Learning'],
            'Intermediate': ['Advanced ML', 'Feature Engineering', 'Model Selection', 'Ensemble Methods'],
            'Advanced': ['Deep Learning', 'Neural Architecture Search', 'AutoML', 'ML Research']
        },
        'Data Science': {
            'Beginner': ['Data Analysis', 'Pandas', 'Visualization', 'Statistics'],
            'Intermediate': ['Advanced Analytics', 'Time Series', 'A/B Testing', 'SQL'],
            'Advanced': ['Big Data', 'Data Engineering', 'MLOps', 'Data Strategy']
        }
    }
    
    for interest in interests:
        if interest in modules:
            experience_level = experience.split()[0]  # Extract level from full string
            if experience_level in modules[interest]:
                for i, module in enumerate(modules[interest][experience_level]):
                    learning_path.append({
                        'order': len(learning_path) + 1,
                        'module': module,
                        'category': interest,
                        'estimated_weeks': random.randint(2, 6),
                        'prerequisite_completed': i == 0,  # First module has no prerequisites
                        'difficulty': experience_level
                    })
    
    return learning_path

def export_learning_data() -> Dict[str, Any]:
    """Export user learning data for backup or analysis"""
    
    export_data = {
        'user_profile': {
            'name': st.session_state.get('user_name', ''),
            'education': st.session_state.get('user_education', ''),
            'experience': st.session_state.get('user_experience', ''),
            'interests': st.session_state.get('user_interests', [])
        },
        'progress': st.session_state.get('learning_progress', {}),
        'activities': st.session_state.get('recent_activities', []),
        'export_date': datetime.now().isoformat()
    }
    
    return export_data
