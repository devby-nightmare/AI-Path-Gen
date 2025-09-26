"""
Achievement and Milestone System for AI Learning Career Dashboard
Tracks user progress and awards badges based on various criteria
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import streamlit as st


class AchievementSystem:
    def __init__(self):
        self.achievement_definitions = self._initialize_achievements()
        self.milestone_definitions = self._initialize_milestones()
    
    def _initialize_achievements(self) -> Dict[str, Dict]:
        """Initialize all available achievements"""
        return {
            # Learning Achievements
            'first_login': {
                'name': '🌟 Welcome Aboard',
                'description': 'Completed your first login to the dashboard',
                'category': 'Getting Started',
                'points': 10,
                'hidden': False
            },
            'profile_complete': {
                'name': '👤 Profile Master',
                'description': 'Completed your user profile with all information',
                'category': 'Getting Started',
                'points': 25,
                'hidden': False
            },
            'first_course_start': {
                'name': '🚀 Learning Journey Begins',
                'description': 'Started your first course',
                'category': 'Learning',
                'points': 20,
                'hidden': False
            },
            'first_course_complete': {
                'name': '🎓 First Graduate',
                'description': 'Completed your first course',
                'category': 'Learning',
                'points': 50,
                'hidden': False
            },
            'course_streak_3': {
                'name': '🔥 On Fire',
                'description': 'Completed courses for 3 days straight',
                'category': 'Consistency',
                'points': 75,
                'hidden': False
            },
            'course_streak_7': {
                'name': '⚡ Week Warrior',
                'description': 'Maintained a 7-day learning streak',
                'category': 'Consistency',
                'points': 150,
                'hidden': False
            },
            'course_streak_30': {
                'name': '💪 Month Champion',
                'description': 'Incredible 30-day learning streak!',
                'category': 'Consistency',
                'points': 500,
                'hidden': False
            },
            
            # Skill-based Achievements
            'ml_specialist': {
                'name': '🤖 ML Specialist',
                'description': 'Completed 5 Machine Learning courses',
                'category': 'Expertise',
                'points': 200,
                'hidden': False
            },
            'dl_expert': {
                'name': '🧠 Deep Learning Expert',
                'description': 'Mastered Deep Learning fundamentals',
                'category': 'Expertise',
                'points': 300,
                'hidden': False
            },
            'data_scientist': {
                'name': '📊 Data Scientist',
                'description': 'Completed comprehensive Data Science track',
                'category': 'Expertise',
                'points': 400,
                'hidden': False
            },
            'ai_researcher': {
                'name': '🔬 AI Researcher',
                'description': 'Achieved advanced level in AI research methodologies',
                'category': 'Expertise',
                'points': 600,
                'hidden': False
            },
            
            # Progress Achievements
            'courses_5': {
                'name': '🎯 Getting Started',
                'description': 'Completed 5 courses',
                'category': 'Progress',
                'points': 100,
                'hidden': False
            },
            'courses_10': {
                'name': '📚 Dedicated Learner',
                'description': 'Completed 10 courses',
                'category': 'Progress',
                'points': 200,
                'hidden': False
            },
            'courses_25': {
                'name': '🏆 Learning Master',
                'description': 'Completed 25 courses',
                'category': 'Progress',
                'points': 500,
                'hidden': False
            },
            'courses_50': {
                'name': '👑 Knowledge King',
                'description': 'Completed 50 courses - Incredible dedication!',
                'category': 'Progress',
                'points': 1000,
                'hidden': False
            },
            
            # Performance Achievements
            'high_scorer': {
                'name': '⭐ Excellence Award',
                'description': 'Achieved 90%+ score on 5 courses',
                'category': 'Performance',
                'points': 250,
                'hidden': False
            },
            'perfect_score': {
                'name': '💯 Perfectionist',
                'description': 'Achieved a perfect score on any course',
                'category': 'Performance',
                'points': 300,
                'hidden': False
            },
            'quick_learner': {
                'name': '🚄 Speed Demon',
                'description': 'Completed 3 courses in one week',
                'category': 'Performance',
                'points': 150,
                'hidden': False
            },
            
            # Special Achievements
            'early_bird': {
                'name': '🌅 Early Bird',
                'description': 'Completed lessons before 8 AM',
                'category': 'Special',
                'points': 50,
                'hidden': False
            },
            'night_owl': {
                'name': '🦉 Night Owl',
                'description': 'Completed lessons after 10 PM',
                'category': 'Special',
                'points': 50,
                'hidden': False
            },
            'weekend_warrior': {
                'name': '💼 Weekend Warrior',
                'description': 'Completed courses on weekends',
                'category': 'Special',
                'points': 75,
                'hidden': False
            },
            'curiosity_driven': {
                'name': '🔍 Curiosity Driven',
                'description': 'Explored courses in 5 different areas',
                'category': 'Special',
                'points': 200,
                'hidden': False
            },
            
            # Hidden/Secret Achievements
            'secret_agent': {
                'name': '🕵️ Secret Agent',
                'description': 'Found a hidden easter egg',
                'category': 'Secret',
                'points': 100,
                'hidden': True
            },
            'time_traveler': {
                'name': '⏰ Time Traveler',
                'description': 'Learned something from the future',
                'category': 'Secret',
                'points': 150,
                'hidden': True
            }
        }
    
    def _initialize_milestones(self) -> Dict[str, Dict]:
        """Initialize milestone definitions"""
        return {
            # Learning Milestones
            'beginner_complete': {
                'name': '🎓 Beginner Graduate',
                'description': 'Completed all beginner-level courses',
                'requirements': {
                    'courses_completed': 10,
                    'min_level': 'Beginner'
                },
                'rewards': {
                    'points': 300,
                    'badge': '🎓 Beginner Graduate',
                    'unlocks': ['intermediate_track']
                }
            },
            'intermediate_complete': {
                'name': '🚀 Intermediate Master',
                'description': 'Mastered intermediate-level concepts',
                'requirements': {
                    'courses_completed': 20,
                    'min_level': 'Intermediate',
                    'min_avg_score': 80
                },
                'rewards': {
                    'points': 600,
                    'badge': '🚀 Intermediate Master',
                    'unlocks': ['advanced_track', 'mentorship_program']
                }
            },
            'advanced_complete': {
                'name': '👑 Advanced Expert',
                'description': 'Achieved mastery in advanced topics',
                'requirements': {
                    'courses_completed': 30,
                    'min_level': 'Advanced',
                    'min_avg_score': 85,
                    'streak_days': 30
                },
                'rewards': {
                    'points': 1000,
                    'badge': '👑 Advanced Expert',
                    'unlocks': ['research_projects', 'industry_connections']
                }
            },
            
            # Career Milestones
            'nsqf_level_5': {
                'name': '📜 NSQF Level 5 Ready',
                'description': 'Ready for NSQF Level 5 roles',
                'requirements': {
                    'nsqf_level': 5,
                    'courses_completed': 15,
                    'certifications': 3
                },
                'rewards': {
                    'points': 400,
                    'badge': '📜 NSQF Level 5',
                    'unlocks': ['job_board_access', 'career_counseling']
                }
            },
            'nsqf_level_6': {
                'name': '🎖️ NSQF Level 6 Ready',
                'description': 'Qualified for senior roles',
                'requirements': {
                    'nsqf_level': 6,
                    'courses_completed': 25,
                    'certifications': 5,
                    'high_scores': 10
                },
                'rewards': {
                    'points': 700,
                    'badge': '🎖️ NSQF Level 6',
                    'unlocks': ['leadership_track', 'mentorship_program']
                }
            },
            'nsqf_level_7': {
                'name': '🏅 NSQF Level 7 Ready',
                'description': 'Expert-level professional',
                'requirements': {
                    'nsqf_level': 7,
                    'courses_completed': 35,
                    'certifications': 8,
                    'perfect_scores': 5
                },
                'rewards': {
                    'points': 1200,
                    'badge': '🏅 NSQF Level 7',
                    'unlocks': ['research_opportunities', 'conference_speaker']
                }
            },
            
            # Specialty Milestones
            'ai_pioneer': {
                'name': '🌟 AI Pioneer',
                'description': 'Pioneer in artificial intelligence',
                'requirements': {
                    'ai_courses': 20,
                    'research_papers': 3,
                    'innovations': 1
                },
                'rewards': {
                    'points': 2000,
                    'badge': '🌟 AI Pioneer',
                    'unlocks': ['research_lab_access', 'innovation_fund']
                }
            }
        }
    
    def check_achievements(self, user_data: Dict[str, Any]) -> List[str]:
        """Check which new achievements the user has earned"""
        current_achievements = user_data.get('achievements', [])
        new_achievements = []
        
        # Get user stats
        profile = user_data.get('profile', {})
        progress = user_data.get('progress', {})
        certifications = user_data.get('certifications', [])
        activities = user_data.get('activities', [])
        
        # Check each achievement
        for achievement_id, achievement in self.achievement_definitions.items():
            if achievement_id not in current_achievements:
                if self._check_achievement_criteria(achievement_id, user_data):
                    new_achievements.append(achievement_id)
        
        return new_achievements
    
    def _check_achievement_criteria(self, achievement_id: str, user_data: Dict) -> bool:
        """Check if user meets criteria for specific achievement"""
        profile = user_data.get('profile', {})
        progress = user_data.get('progress', {})
        certifications = user_data.get('certifications', [])
        activities = user_data.get('activities', [])
        
        completed_courses = progress.get('completed', 0)
        streak = progress.get('streak', 0)
        
        # Count completed certifications
        completed_certs = len([c for c in certifications if c.get('status') == 'Completed'])
        high_score_certs = len([c for c in certifications if c.get('score', 0) >= 90])
        perfect_score_certs = len([c for c in certifications if c.get('score', 0) == 100])
        
        # Check criteria based on achievement ID
        criteria_map = {
            'first_login': lambda: True,  # Always true once they're using the system
            'profile_complete': lambda: all([
                profile.get('name'),
                profile.get('education'),
                profile.get('experience'),
                profile.get('interests')
            ]),
            'first_course_start': lambda: len(certifications) > 0,
            'first_course_complete': lambda: completed_certs >= 1,
            'course_streak_3': lambda: streak >= 3,
            'course_streak_7': lambda: streak >= 7,
            'course_streak_30': lambda: streak >= 30,
            'courses_5': lambda: completed_courses >= 5,
            'courses_10': lambda: completed_courses >= 10,
            'courses_25': lambda: completed_courses >= 25,
            'courses_50': lambda: completed_courses >= 50,
            'high_scorer': lambda: high_score_certs >= 5,
            'perfect_score': lambda: perfect_score_certs >= 1,
            'quick_learner': lambda: self._check_quick_learner(activities),
            'ml_specialist': lambda: self._count_ml_courses(certifications) >= 5,
            'dl_expert': lambda: self._count_dl_courses(certifications) >= 3,
            'data_scientist': lambda: self._count_ds_courses(certifications) >= 8,
            'curiosity_driven': lambda: self._count_diverse_interests(certifications) >= 5,
            'weekend_warrior': lambda: self._check_weekend_activity(activities),
            'early_bird': lambda: self._check_early_activity(activities),
            'night_owl': lambda: self._check_late_activity(activities),
        }
        
        check_function = criteria_map.get(achievement_id, lambda: False)
        return check_function()
    
    def _check_quick_learner(self, activities: List[Dict]) -> bool:
        """Check if user completed 3 courses in one week"""
        if len(activities) < 3:
            return False
        
        # Sort activities by date
        completed_activities = [a for a in activities if a.get('action') == 'Completed']
        
        if len(completed_activities) < 3:
            return False
        
        # Check for 3 completions within 7 days
        for i in range(len(completed_activities) - 2):
            try:
                date1 = datetime.fromisoformat(completed_activities[i].get('date', ''))
                date3 = datetime.fromisoformat(completed_activities[i + 2].get('date', ''))
                if (date1 - date3).days <= 7:
                    return True
            except:
                continue
        
        return False
    
    def _count_ml_courses(self, certifications: List[Dict]) -> int:
        """Count machine learning related courses"""
        ml_keywords = ['machine learning', 'ml', 'supervised', 'unsupervised', 'algorithm']
        count = 0
        
        for cert in certifications:
            if cert.get('status') == 'Completed':
                course_name = cert.get('course', '').lower()
                if any(keyword in course_name for keyword in ml_keywords):
                    count += 1
        
        return count
    
    def _count_dl_courses(self, certifications: List[Dict]) -> int:
        """Count deep learning related courses"""
        dl_keywords = ['deep learning', 'neural network', 'cnn', 'rnn', 'transformer', 'tensorflow', 'pytorch']
        count = 0
        
        for cert in certifications:
            if cert.get('status') == 'Completed':
                course_name = cert.get('course', '').lower()
                if any(keyword in course_name for keyword in dl_keywords):
                    count += 1
        
        return count
    
    def _count_ds_courses(self, certifications: List[Dict]) -> int:
        """Count data science related courses"""
        ds_keywords = ['data science', 'analytics', 'statistics', 'pandas', 'numpy', 'visualization']
        count = 0
        
        for cert in certifications:
            if cert.get('status') == 'Completed':
                course_name = cert.get('course', '').lower()
                if any(keyword in course_name for keyword in ds_keywords):
                    count += 1
        
        return count
    
    def _count_diverse_interests(self, certifications: List[Dict]) -> int:
        """Count number of different subject areas"""
        areas = set()
        
        for cert in certifications:
            if cert.get('status') == 'Completed':
                course_name = cert.get('course', '').lower()
                
                if any(kw in course_name for kw in ['machine learning', 'ml']):
                    areas.add('ml')
                elif any(kw in course_name for kw in ['deep learning', 'neural']):
                    areas.add('dl')
                elif any(kw in course_name for kw in ['data science', 'analytics']):
                    areas.add('ds')
                elif any(kw in course_name for kw in ['computer vision', 'cv']):
                    areas.add('cv')
                elif any(kw in course_name for kw in ['nlp', 'natural language']):
                    areas.add('nlp')
                elif any(kw in course_name for kw in ['robotics']):
                    areas.add('robotics')
                elif any(kw in course_name for kw in ['ethics']):
                    areas.add('ethics')
        
        return len(areas)
    
    def _check_weekend_activity(self, activities: List[Dict]) -> bool:
        """Check if user has weekend activity"""
        for activity in activities:
            try:
                date_str = activity.get('date', '')
                date_obj = datetime.fromisoformat(date_str)
                if date_obj.weekday() >= 5:  # Saturday or Sunday
                    return True
            except:
                continue
        return False
    
    def _check_early_activity(self, activities: List[Dict]) -> bool:
        """Check if user has early morning activity"""
        # This would require timestamp data, simulating for now
        return len(activities) > 5  # Placeholder
    
    def _check_late_activity(self, activities: List[Dict]) -> bool:
        """Check if user has late night activity"""
        # This would require timestamp data, simulating for now
        return len(activities) > 3  # Placeholder
    
    def check_milestones(self, user_data: Dict[str, Any]) -> List[str]:
        """Check which milestones the user has achieved"""
        current_milestones = user_data.get('milestones', [])
        new_milestones = []
        
        for milestone_id, milestone in self.milestone_definitions.items():
            if milestone_id not in current_milestones:
                if self._check_milestone_criteria(milestone_id, user_data):
                    new_milestones.append(milestone_id)
        
        return new_milestones
    
    def _check_milestone_criteria(self, milestone_id: str, user_data: Dict) -> bool:
        """Check if user meets criteria for specific milestone"""
        milestone = self.milestone_definitions[milestone_id]
        requirements = milestone['requirements']
        
        progress = user_data.get('progress', {})
        certifications = user_data.get('certifications', [])
        
        completed_courses = progress.get('completed', 0)
        completed_certs = len([c for c in certifications if c.get('status') == 'Completed'])
        
        # Check each requirement
        if 'courses_completed' in requirements:
            if completed_courses < requirements['courses_completed']:
                return False
        
        if 'certifications' in requirements:
            if completed_certs < requirements['certifications']:
                return False
        
        if 'min_avg_score' in requirements:
            scores = [c.get('score', 0) for c in certifications if c.get('score')]
            if not scores or sum(scores) / len(scores) < requirements['min_avg_score']:
                return False
        
        if 'streak_days' in requirements:
            if progress.get('streak', 0) < requirements['streak_days']:
                return False
        
        return True
    
    def get_achievement_display_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for displaying achievements in the UI"""
        current_achievements = user_data.get('achievements', [])
        current_milestones = user_data.get('milestones', [])
        
        # Calculate total points
        total_points = sum(
            self.achievement_definitions[ach]['points']
            for ach in current_achievements
            if ach in self.achievement_definitions
        )
        
        # Add milestone points
        total_points += sum(
            self.milestone_definitions[mil]['rewards']['points']
            for mil in current_milestones
            if mil in self.milestone_definitions
        )
        
        # Categorize achievements
        categorized_achievements = {}
        for ach_id in current_achievements:
            if ach_id in self.achievement_definitions:
                ach = self.achievement_definitions[ach_id]
                category = ach['category']
                if category not in categorized_achievements:
                    categorized_achievements[category] = []
                categorized_achievements[category].append({
                    'id': ach_id,
                    'name': ach['name'],
                    'description': ach['description'],
                    'points': ach['points']
                })
        
        # Get progress towards next achievements
        next_achievements = self._get_next_achievements(user_data)
        
        return {
            'total_achievements': len(current_achievements),
            'total_milestones': len(current_milestones),
            'total_points': total_points,
            'categorized_achievements': categorized_achievements,
            'recent_milestones': [
                {
                    'id': mil_id,
                    'name': self.milestone_definitions[mil_id]['name'],
                    'description': self.milestone_definitions[mil_id]['description'],
                    'points': self.milestone_definitions[mil_id]['rewards']['points']
                }
                for mil_id in current_milestones[-3:]  # Last 3 milestones
                if mil_id in self.milestone_definitions
            ],
            'next_achievements': next_achievements,
            'level': self._calculate_user_level(total_points),
            'level_progress': self._calculate_level_progress(total_points)
        }
    
    def _get_next_achievements(self, user_data: Dict) -> List[Dict]:
        """Get achievements user is close to earning"""
        current_achievements = user_data.get('achievements', [])
        next_achievements = []
        
        for ach_id, ach in self.achievement_definitions.items():
            if ach_id not in current_achievements and not ach.get('hidden', False):
                progress = self._calculate_achievement_progress(ach_id, user_data)
                if progress > 0:
                    next_achievements.append({
                        'id': ach_id,
                        'name': ach['name'],
                        'description': ach['description'],
                        'progress': progress,
                        'points': ach['points']
                    })
        
        # Sort by progress (closest first)
        next_achievements.sort(key=lambda x: x['progress'], reverse=True)
        return next_achievements[:5]
    
    def _calculate_achievement_progress(self, achievement_id: str, user_data: Dict) -> float:
        """Calculate progress towards a specific achievement (0-100%)"""
        progress = user_data.get('progress', {})
        certifications = user_data.get('certifications', [])
        
        completed_courses = progress.get('completed', 0)
        completed_certs = len([c for c in certifications if c.get('status') == 'Completed'])
        
        # Simple progress calculation for common achievements
        progress_map = {
            'courses_5': min(completed_courses / 5 * 100, 100),
            'courses_10': min(completed_courses / 10 * 100, 100),
            'courses_25': min(completed_courses / 25 * 100, 100),
            'first_course_complete': min(completed_certs / 1 * 100, 100),
            'course_streak_3': min(progress.get('streak', 0) / 3 * 100, 100),
            'course_streak_7': min(progress.get('streak', 0) / 7 * 100, 100),
        }
        
        return progress_map.get(achievement_id, 0)
    
    def _calculate_user_level(self, total_points: int) -> int:
        """Calculate user level based on total points"""
        if total_points < 100:
            return 1
        elif total_points < 300:
            return 2
        elif total_points < 600:
            return 3
        elif total_points < 1000:
            return 4
        elif total_points < 1500:
            return 5
        elif total_points < 2500:
            return 6
        elif total_points < 4000:
            return 7
        elif total_points < 6000:
            return 8
        elif total_points < 9000:
            return 9
        else:
            return 10
    
    def _calculate_level_progress(self, total_points: int) -> float:
        """Calculate progress towards next level (0-100%)"""
        level = self._calculate_user_level(total_points)
        
        level_thresholds = [0, 100, 300, 600, 1000, 1500, 2500, 4000, 6000, 9000, 12000]
        
        if level >= 10:
            return 100.0
        
        current_threshold = level_thresholds[level - 1]
        next_threshold = level_thresholds[level]
        
        progress = (total_points - current_threshold) / (next_threshold - current_threshold) * 100
        return max(0, min(100, progress))


def update_user_achievements(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update user achievements and return any new ones"""
    achievement_system = AchievementSystem()
    
    # Check for new achievements
    new_achievements = achievement_system.check_achievements(user_data)
    new_milestones = achievement_system.check_milestones(user_data)
    
    # Update user data
    if 'achievements' not in user_data:
        user_data['achievements'] = []
    if 'milestones' not in user_data:
        user_data['milestones'] = []
    
    user_data['achievements'].extend(new_achievements)
    user_data['milestones'].extend(new_milestones)
    
    return {
        'new_achievements': new_achievements,
        'new_milestones': new_milestones,
        'display_data': achievement_system.get_achievement_display_data(user_data)
    }