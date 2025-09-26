"""
Advanced Salary Prediction module for AI Learning Career Dashboard
Provides predictive analytics for career progression and salary forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from nsqf import NSQF_DATA, get_nsqf_level_by_education


class SalaryPredictor:
    def __init__(self):
        self.base_salary_data = self._initialize_salary_data()
        self.growth_factors = self._initialize_growth_factors()
        self.market_trends = self._initialize_market_trends()
    
    def _initialize_salary_data(self) -> Dict[str, Any]:
        """Initialize base salary data from NSQF framework"""
        salary_data = {}
        
        for level, data in NSQF_DATA.items():
            # Extract numeric salary ranges
            salary_range = data['salary_range']
            if '₹' in salary_range and '-' in salary_range:
                try:
                    parts = salary_range.split('₹')[1].split('-')
                    min_sal = float(parts[0].replace('LPA', '').strip())
                    
                    if len(parts) > 1:
                        max_sal_str = parts[1].replace('LPA', '').replace('+', '').strip()
                        max_sal = float(max_sal_str) if max_sal_str.replace('.', '').isdigit() else min_sal * 1.5
                    else:
                        max_sal = min_sal * 1.5
                    
                    salary_data[level] = {
                        'min_salary': min_sal,
                        'max_salary': max_sal,
                        'avg_salary': (min_sal + max_sal) / 2,
                        'roles': data['job_roles'],
                        'skills': data['skills']
                    }
                except (ValueError, IndexError):
                    # Fallback values
                    salary_data[level] = {
                        'min_salary': 5.0 + (level - 4) * 3,
                        'max_salary': 10.0 + (level - 4) * 5,
                        'avg_salary': 7.5 + (level - 4) * 4,
                        'roles': data['job_roles'],
                        'skills': data['skills']
                    }
        
        return salary_data
    
    def _initialize_growth_factors(self) -> Dict[str, float]:
        """Initialize salary growth factors based on various parameters"""
        return {
            'experience_multiplier': {
                'Beginner (0-1 years)': 0.85,
                'Intermediate (2-4 years)': 1.0,
                'Advanced (5+ years)': 1.35
            },
            'skill_bonuses': {
                'Machine Learning': 0.15,
                'Deep Learning': 0.25,
                'Natural Language Processing': 0.20,
                'Computer Vision': 0.20,
                'Data Science': 0.10,
                'Robotics': 0.30,
                'AI Ethics': 0.05,
                'MLOps': 0.18
            },
            'location_multipliers': {
                'Bangalore': 1.2,
                'Mumbai': 1.15,
                'Delhi': 1.1,
                'Hyderabad': 1.05,
                'Chennai': 1.0,
                'Pune': 0.95,
                'Other Metro': 0.85,
                'Tier 2 Cities': 0.7
            },
            'company_size_multipliers': {
                'Startup (1-50)': 0.8,
                'Small (51-200)': 0.9,
                'Medium (201-1000)': 1.0,
                'Large (1001-5000)': 1.2,
                'Enterprise (5000+)': 1.4
            }
        }
    
    def _initialize_market_trends(self) -> Dict[str, Any]:
        """Initialize market trend data for predictions"""
        return {
            'annual_growth_rate': 0.18,  # 18% annual growth in AI salaries
            'demand_trends': {
                'Machine Learning': 1.25,
                'Deep Learning': 1.35,
                'Natural Language Processing': 1.45,
                'Computer Vision': 1.30,
                'Data Science': 1.15,
                'Robotics': 1.40,
                'AI Ethics': 1.05,
                'MLOps': 1.50
            },
            'market_saturation': {
                'Beginner (0-1 years)': 0.8,  # High supply, lower premiums
                'Intermediate (2-4 years)': 1.1,  # Balanced
                'Advanced (5+ years)': 1.3   # High demand, low supply
            }
        }
    
    def predict_current_salary(self, 
                             education: str,
                             experience: str,
                             interests: List[str],
                             location: str = "Bangalore",
                             company_size: str = "Medium (201-1000)") -> Dict[str, Any]:
        """Predict current salary based on user profile"""
        
        nsqf_level = get_nsqf_level_by_education(education)
        base_data = self.base_salary_data.get(nsqf_level, self.base_salary_data[6])
        
        # Start with base salary
        base_salary = base_data['avg_salary']
        
        # Apply experience multiplier
        exp_multiplier = self.growth_factors['experience_multiplier'].get(experience, 1.0)
        
        # Apply skill bonuses
        skill_bonus = 0
        for interest in interests:
            skill_bonus += self.growth_factors['skill_bonuses'].get(interest, 0)
        skill_bonus = min(skill_bonus, 0.5)  # Cap at 50% bonus
        
        # Apply location multiplier
        location_multiplier = self.growth_factors['location_multipliers'].get(location, 1.0)
        
        # Apply company size multiplier
        company_multiplier = self.growth_factors['company_size_multipliers'].get(company_size, 1.0)
        
        # Apply market saturation
        market_multiplier = self.market_trends['market_saturation'].get(experience, 1.0)
        
        # Calculate final salary
        predicted_salary = base_salary * exp_multiplier * (1 + skill_bonus) * location_multiplier * company_multiplier * market_multiplier
        
        # Calculate range
        salary_range = {
            'min': predicted_salary * 0.8,
            'max': predicted_salary * 1.3,
            'median': predicted_salary
        }
        
        return {
            'predicted_salary': round(predicted_salary, 1),
            'salary_range': {k: round(v, 1) for k, v in salary_range.items()},
            'factors': {
                'base_salary': round(base_salary, 1),
                'experience_factor': exp_multiplier,
                'skill_bonus': round(skill_bonus * 100, 1),
                'location_factor': location_multiplier,
                'company_factor': company_multiplier,
                'market_factor': market_multiplier
            },
            'nsqf_level': nsqf_level,
            'confidence': self._calculate_confidence(nsqf_level, experience, interests)
        }
    
    def predict_career_progression(self,
                                 current_education: str,
                                 current_experience: str,
                                 target_role: str,
                                 years_ahead: int = 5) -> Dict[str, Any]:
        """Predict salary progression over time"""
        
        current_nsqf = get_nsqf_level_by_education(current_education)
        
        # Find target NSQF level
        target_nsqf = current_nsqf
        for level, data in NSQF_DATA.items():
            if target_role in data['job_roles']:
                target_nsqf = level
                break
        
        progression = []
        annual_growth = self.market_trends['annual_growth_rate']
        
        # Current salary
        current_prediction = self.predict_current_salary(current_education, current_experience, [])
        current_salary = current_prediction['predicted_salary']
        
        for year in range(years_ahead + 1):
            # Experience progression
            if year == 0:
                exp_level = current_experience
                nsqf_level = current_nsqf
            elif year <= 2:
                exp_level = "Intermediate (2-4 years)"
                nsqf_level = min(current_nsqf + (year // 2), target_nsqf)
            else:
                exp_level = "Advanced (5+ years)"
                nsqf_level = min(current_nsqf + (year // 2), target_nsqf)
            
            # Calculate salary with growth
            growth_factor = (1 + annual_growth) ** year
            
            # NSQF progression bonus
            if nsqf_level > current_nsqf:
                nsqf_bonus = (nsqf_level - current_nsqf) * 0.2  # 20% per level
            else:
                nsqf_bonus = 0
            
            projected_salary = current_salary * growth_factor * (1 + nsqf_bonus)
            
            progression.append({
                'year': year,
                'salary': round(projected_salary, 1),
                'nsqf_level': nsqf_level,
                'experience_level': exp_level,
                'growth_rate': round(annual_growth * 100, 1) if year > 0 else 0
            })
        
        return {
            'progression': progression,
            'target_achieved_year': self._find_target_achievement_year(progression, target_nsqf),
            'total_growth': round(((progression[-1]['salary'] - progression[0]['salary']) / progression[0]['salary']) * 100, 1),
            'annual_avg_growth': round(annual_growth * 100, 1)
        }
    
    def get_salary_insights(self, education: str, experience: str, interests: List[str]) -> Dict[str, Any]:
        """Get comprehensive salary insights and recommendations"""
        
        current_prediction = self.predict_current_salary(education, experience, interests)
        
        # Market comparison
        nsqf_level = current_prediction['nsqf_level']
        market_avg = self.base_salary_data[nsqf_level]['avg_salary']
        
        # Skill impact analysis
        skill_impact = {}
        for interest in interests:
            if interest in self.growth_factors['skill_bonuses']:
                impact = self.growth_factors['skill_bonuses'][interest]
                potential_increase = current_prediction['predicted_salary'] * impact
                skill_impact[interest] = {
                    'impact_percentage': round(impact * 100, 1),
                    'potential_increase': round(potential_increase, 1)
                }
        
        # Top paying roles at current level
        current_roles = self.base_salary_data[nsqf_level]['roles']
        
        # Next level opportunities
        next_level_data = self.base_salary_data.get(nsqf_level + 1)
        next_level_potential = None
        if next_level_data:
            next_level_potential = {
                'level': nsqf_level + 1,
                'avg_salary': next_level_data['avg_salary'],
                'potential_increase': round(next_level_data['avg_salary'] - current_prediction['predicted_salary'], 1),
                'roles': next_level_data['roles'][:3]
            }
        
        return {
            'current_prediction': current_prediction,
            'market_comparison': {
                'your_prediction': current_prediction['predicted_salary'],
                'market_average': round(market_avg, 1),
                'difference': round(current_prediction['predicted_salary'] - market_avg, 1),
                'percentile': self._calculate_percentile(current_prediction['predicted_salary'], nsqf_level)
            },
            'skill_impact': skill_impact,
            'current_level_roles': current_roles,
            'next_level_opportunity': next_level_potential,
            'recommendations': self._get_salary_recommendations(current_prediction, interests)
        }
    
    def _calculate_confidence(self, nsqf_level: int, experience: str, interests: List[str]) -> float:
        """Calculate prediction confidence score"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence for middle NSQF levels
        if 5 <= nsqf_level <= 7:
            confidence += 0.1
        
        # Higher confidence for common experience levels
        if experience in ['Intermediate (2-4 years)', 'Advanced (5+ years)']:
            confidence += 0.1
        
        # More interests = higher confidence
        confidence += min(len(interests) * 0.02, 0.1)
        
        return min(confidence, 0.95)
    
    def _find_target_achievement_year(self, progression: List[Dict], target_nsqf: int) -> Optional[int]:
        """Find the year when target NSQF level is achieved"""
        for entry in progression:
            if entry['nsqf_level'] >= target_nsqf:
                return entry['year']
        return None
    
    def _calculate_percentile(self, salary: float, nsqf_level: int) -> int:
        """Calculate salary percentile within NSQF level"""
        level_data = self.base_salary_data[nsqf_level]
        min_sal = level_data['min_salary']
        max_sal = level_data['max_salary']
        
        if salary <= min_sal:
            return 25
        elif salary >= max_sal:
            return 90
        else:
            # Linear interpolation
            percentile = 25 + ((salary - min_sal) / (max_sal - min_sal)) * 65
            return round(percentile)
    
    def _get_salary_recommendations(self, prediction: Dict, interests: List[str]) -> List[str]:
        """Get personalized salary improvement recommendations"""
        recommendations = []
        
        confidence = prediction['confidence']
        if confidence < 0.8:
            recommendations.append("📊 Build more specific skills to improve salary prediction accuracy")
        
        # Skill-based recommendations
        high_impact_skills = [skill for skill, bonus in self.growth_factors['skill_bonuses'].items() 
                             if bonus > 0.15 and skill not in interests]
        
        if high_impact_skills:
            recommendations.append(f"🚀 Consider learning {high_impact_skills[0]} for up to {self.growth_factors['skill_bonuses'][high_impact_skills[0]]*100:.0f}% salary boost")
        
        # Experience recommendations
        if prediction['factors']['experience_factor'] < 1.0:
            recommendations.append("⏰ Gain more experience to increase salary potential significantly")
        
        # Location recommendations
        if prediction['factors']['location_factor'] < 1.1:
            recommendations.append("📍 Consider opportunities in Bangalore/Mumbai for higher compensation")
        
        # Company size recommendations
        if prediction['factors']['company_factor'] < 1.2:
            recommendations.append("🏢 Target larger companies for better compensation packages")
        
        return recommendations[:4]  # Return top 4 recommendations


def get_salary_prediction_dashboard_data(education: str, experience: str, interests: List[str]) -> Dict[str, Any]:
    """Get comprehensive salary data for dashboard display"""
    predictor = SalaryPredictor()
    
    # Get current salary insights
    insights = predictor.get_salary_insights(education, experience, interests)
    
    # Get 5-year progression
    progression = predictor.predict_career_progression(education, experience, "", 5)
    
    # Get role-based predictions
    role_predictions = {}
    current_nsqf = get_nsqf_level_by_education(education)
    
    # Get predictions for different roles
    for level in range(current_nsqf, min(current_nsqf + 3, 9)):
        if level in NSQF_DATA:
            for role in NSQF_DATA[level]['job_roles'][:2]:  # Top 2 roles per level
                role_pred = predictor.predict_current_salary(education, experience, interests)
                # Adjust for role specificity
                role_multiplier = 1.0 + (level - current_nsqf) * 0.15
                role_predictions[role] = {
                    'salary': round(role_pred['predicted_salary'] * role_multiplier, 1),
                    'nsqf_level': level,
                    'confidence': role_pred['confidence']
                }
    
    return {
        'insights': insights,
        'progression': progression,
        'role_predictions': role_predictions,
        'market_data': predictor.market_trends,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
    }