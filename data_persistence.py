"""
Data persistence module for AI Learning Career Dashboard
Handles saving and loading user data, progress, and certifications to JSON files
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st


class DataManager:
    def __init__(self, data_dir: str = "user_data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_user_file_path(self, user_id: str) -> str:
        """Get file path for user data"""
        return os.path.join(self.data_dir, f"user_{user_id}.json")
    
    def save_user_data(self, user_id: str, data: Dict[str, Any]):
        """Save user data to file"""
        file_path = self.get_user_file_path(user_id)
        data['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving user data: {str(e)}")
            return False
    
    def load_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user data from file"""
        file_path = self.get_user_file_path(user_id)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading user data: {str(e)}")
            return None
    
    def get_all_users(self) -> List[str]:
        """Get list of all user IDs"""
        users = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith('user_') and filename.endswith('.json'):
                    user_id = filename[5:-5]  # Remove 'user_' prefix and '.json' suffix
                    users.append(user_id)
        return users
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete user data file"""
        file_path = self.get_user_file_path(user_id)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            st.error(f"Error deleting user data: {str(e)}")
            return False


def get_user_id() -> str:
    """Generate or retrieve user ID for the session"""
    if 'user_id' not in st.session_state:
        # Simple user ID generation - could be enhanced with proper authentication
        if 'user_name' in st.session_state and st.session_state.user_name:
            # Use sanitized name as user ID
            user_id = st.session_state.user_name.lower().replace(' ', '_').replace('@', '_at_')
            # Add timestamp to make it unique if needed
            existing_users = DataManager().get_all_users()
            if user_id in existing_users:
                user_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            # Generate timestamp-based ID
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        st.session_state.user_id = user_id
    
    return st.session_state.user_id


def save_session_to_file():
    """Save current session state to file"""
    user_id = get_user_id()
    data_manager = DataManager()
    
    # Prepare data to save
    user_data = {
        'profile': {
            'name': st.session_state.get('user_name', ''),
            'education': st.session_state.get('user_education', ''),
            'experience': st.session_state.get('user_experience', ''),
            'interests': st.session_state.get('user_interests', [])
        },
        'progress': st.session_state.get('learning_progress', {}),
        'activities': st.session_state.get('recent_activities', []),
        'certifications': st.session_state.get('certifications', []),
        'goals': st.session_state.get('career_goals', []),
        'preferences': st.session_state.get('user_preferences', {})
    }
    
    return data_manager.save_user_data(user_id, user_data)


def load_session_from_file(user_id: str = None) -> bool:
    """Load session state from file"""
    if user_id is None:
        user_id = get_user_id()
    
    data_manager = DataManager()
    user_data = data_manager.load_user_data(user_id)
    
    if user_data is None:
        return False
    
    try:
        # Load profile data
        if 'profile' in user_data:
            profile = user_data['profile']
            st.session_state.user_name = profile.get('name', '')
            st.session_state.user_education = profile.get('education', 'Bachelor\'s')
            st.session_state.user_experience = profile.get('experience', 'Beginner (0-1 years)')
            st.session_state.user_interests = profile.get('interests', ['Machine Learning', 'Data Science'])
        
        # Load progress data
        if 'progress' in user_data:
            st.session_state.learning_progress = user_data['progress']
        
        # Load activities
        if 'activities' in user_data:
            st.session_state.recent_activities = user_data['activities']
        
        # Load certifications
        if 'certifications' in user_data:
            # Convert datetime strings back to datetime objects if needed
            certs = user_data['certifications']
            for cert in certs:
                if cert.get('completion_date') and isinstance(cert['completion_date'], str):
                    try:
                        cert['completion_date'] = datetime.fromisoformat(cert['completion_date'])
                    except:
                        cert['completion_date'] = None
            st.session_state.certifications = certs
        
        # Load goals and preferences
        if 'goals' in user_data:
            st.session_state.career_goals = user_data['goals']
        
        if 'preferences' in user_data:
            st.session_state.user_preferences = user_data['preferences']
        
        return True
    
    except Exception as e:
        st.error(f"Error loading session data: {str(e)}")
        return False


def auto_save_session():
    """Auto-save session data if user has a name"""
    if st.session_state.get('user_name'):
        save_session_to_file()


def export_user_data(user_id: str = None) -> Dict[str, Any]:
    """Export user data for backup or analysis"""
    if user_id is None:
        user_id = get_user_id()
    
    data_manager = DataManager()
    user_data = data_manager.load_user_data(user_id)
    
    if user_data:
        user_data['export_timestamp'] = datetime.now().isoformat()
        user_data['user_id'] = user_id
    
    return user_data or {}


def import_user_data(data: Dict[str, Any], user_id: str = None) -> bool:
    """Import user data from backup"""
    if user_id is None:
        user_id = get_user_id()
    
    data_manager = DataManager()
    
    # Remove export-specific fields
    import_data = data.copy()
    import_data.pop('export_timestamp', None)
    import_data.pop('user_id', None)
    
    return data_manager.save_user_data(user_id, import_data)


def get_user_stats_from_file(user_id: str = None) -> Dict[str, Any]:
    """Get user statistics from saved data"""
    if user_id is None:
        user_id = get_user_id()
    
    data_manager = DataManager()
    user_data = data_manager.load_user_data(user_id)
    
    if not user_data or 'progress' not in user_data:
        # Return default stats
        return {
            'total_topics': 25,
            'completed': 0,
            'in_progress': 0,
            'not_started': 25,
            'completion_rate': 0,
            'streak': 0
        }
    
    progress = user_data['progress']
    total_topics = progress.get('total_topics', 25)
    completed = progress.get('completed', 0)
    
    return {
        'total_topics': total_topics,
        'completed': completed,
        'in_progress': progress.get('in_progress', 0),
        'not_started': progress.get('not_started', total_topics - completed),
        'completion_rate': (completed / total_topics * 100) if total_topics > 0 else 0,
        'streak': progress.get('streak', 0)
    }