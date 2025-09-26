"""
NSQF (National Skills Qualifications Framework) data structure and utility functions
"""

import random
from typing import Dict, List, Any

# NSQF Data Structure
NSQF_DATA = {
    4: {
        "level": 4,
        "title": "Certificate Level",
        "topics": [
            "Basic Programming Concepts",
            "Introduction to Data Analysis",
            "Computer Fundamentals",
            "Basic Statistics",
            "Excel for Data Analysis"
        ],
        "job_roles": [
            "Junior Data Entry Operator",
            "Computer Operator",
            "Basic Data Analyst",
            "IT Support Technician"
        ],
        "competencies": [
            "Basic computer literacy",
            "Data entry and validation",
            "Simple data visualization",
            "Basic problem-solving"
        ],
        "salary_range": "₹2-4 LPA",
        "skills": [
            "MS Office Suite",
            "Basic SQL",
            "Data Cleaning",
            "Report Generation"
        ]
    },
    5: {
        "level": 5,
        "title": "Diploma Level",
        "topics": [
            "Programming Fundamentals (Python/Java)",
            "Database Management",
            "Statistics and Probability",
            "Basic Machine Learning",
            "Data Visualization Tools"
        ],
        "job_roles": [
            "Data Analyst",
            "Junior Software Developer",
            "Database Administrator",
            "Business Intelligence Analyst"
        ],
        "competencies": [
            "Programming in at least one language",
            "Database design and querying",
            "Statistical analysis",
            "Data visualization and reporting"
        ],
        "salary_range": "₹3-6 LPA",
        "skills": [
            "Python/Java Programming",
            "SQL and NoSQL Databases",
            "Tableau/Power BI",
            "Statistical Analysis"
        ]
    },
    6: {
        "level": 6,
        "title": "Advanced Diploma/Bachelor's Level",
        "topics": [
            "Advanced Programming",
            "Machine Learning Algorithms",
            "Data Science Methodologies",
            "Web Development",
            "Cloud Computing Basics"
        ],
        "job_roles": [
            "Data Scientist",
            "Machine Learning Engineer",
            "Software Developer",
            "Systems Analyst",
            "Product Analyst"
        ],
        "competencies": [
            "Advanced programming skills",
            "Machine learning model development",
            "Statistical modeling",
            "Project management basics",
            "Technical communication"
        ],
        "salary_range": "₹5-10 LPA",
        "skills": [
            "Python/R/Java",
            "Scikit-learn, Pandas",
            "AWS/Azure Basics",
            "Git Version Control",
            "Agile Methodologies"
        ]
    },
    7: {
        "level": 7,
        "title": "Bachelor's Honors/Master's Level",
        "topics": [
            "Deep Learning",
            "Natural Language Processing",
            "Computer Vision",
            "Advanced Analytics",
            "MLOps and Deployment",
            "Big Data Technologies"
        ],
        "job_roles": [
            "Senior Data Scientist",
            "ML Research Engineer",
            "AI Solutions Architect",
            "Lead Data Engineer",
            "Technical Product Manager"
        ],
        "competencies": [
            "Advanced ML/DL model development",
            "Research and innovation",
            "Team leadership",
            "Architecture design",
            "Strategic thinking"
        ],
        "salary_range": "₹8-18 LPA",
        "skills": [
            "TensorFlow/PyTorch",
            "Kubernetes/Docker",
            "Apache Spark/Hadoop",
            "Advanced Statistics",
            "Leadership Skills"
        ]
    },
    8: {
        "level": 8,
        "title": "Master's/Research Level",
        "topics": [
            "AI Research Methodologies",
            "Advanced Deep Learning",
            "Reinforcement Learning",
            "AI Ethics and Governance",
            "Cutting-edge AI Applications",
            "Innovation Management"
        ],
        "job_roles": [
            "Principal Data Scientist",
            "AI Research Director",
            "Chief Technology Officer",
            "AI Consultant",
            "University Professor/Researcher"
        ],
        "competencies": [
            "Research leadership",
            "Strategic AI planning",
            "Innovation management",
            "Cross-functional collaboration",
            "Thought leadership"
        ],
        "salary_range": "₹15-30+ LPA",
        "skills": [
            "Advanced Research Skills",
            "Publication and Patents",
            "Strategic Planning",
            "Team Management",
            "Industry Expertise"
        ]
    }
}

# Education to NSQF Level Mapping
EDUCATION_TO_NSQF = {
    "High School": 4,
    "Diploma": 5,
    "Bachelor's": 6,
    "Master's": 7,
    "PhD": 8
}

# Topic to NSQF Mapping
TOPIC_TO_NSQF = {
    "Basic Programming": [4, 5],
    "Machine Learning": [5, 6, 7],
    "Deep Learning": [6, 7, 8],
    "Data Science": [5, 6, 7],
    "Natural Language Processing": [6, 7, 8],
    "Computer Vision": [6, 7, 8],
    "AI Ethics": [7, 8],
    "MLOps": [6, 7, 8],
    "Robotics": [7, 8],
    "Research Methods": [7, 8]
}

def get_nsqf_level_by_education(education: str) -> int:
    """
    Map education level to NSQF level
    
    Args:
        education (str): Education level
    
    Returns:
        int: Corresponding NSQF level
    """
    return EDUCATION_TO_NSQF.get(education, 6)

def get_career_pathway(current_level: int, target_role: str) -> Dict[str, Any]:
    """
    Generate career pathway from current level to target role
    
    Args:
        current_level (int): Current NSQF level
        target_role (str): Target job role
    
    Returns:
        dict: Career pathway information
    """
    # Find the NSQF level for the target role
    target_level = current_level
    for level, data in NSQF_DATA.items():
        if target_role in data["job_roles"]:
            target_level = level
            break
    
    pathway = {
        "current_level": current_level,
        "target_level": target_level,
        "target_role": target_role,
        "progression": []
    }
    
    # Generate progression steps
    for level in range(current_level, min(target_level + 1, 9)):
        if level in NSQF_DATA:
            pathway["progression"].append(NSQF_DATA[level])
    
    return pathway

def map_topic_to_nsqf(topic: str) -> List[int]:
    """
    Map a topic to relevant NSQF levels
    
    Args:
        topic (str): Topic name
    
    Returns:
        list: List of relevant NSQF levels
    """
    # Find partial matches
    relevant_levels = []
    for key, levels in TOPIC_TO_NSQF.items():
        if key.lower() in topic.lower() or topic.lower() in key.lower():
            relevant_levels.extend(levels)
    
    return sorted(list(set(relevant_levels))) if relevant_levels else [6]

def get_ai_ml_recommendations(interests: List[str], experience: str, education: str) -> List[Dict[str, Any]]:
    """
    Generate personalized AI/ML recommendations based on user profile
    
    Args:
        interests (list): User's areas of interest
        experience (str): Experience level
        education (str): Education level
    
    Returns:
        list: List of personalized recommendations
    """
    nsqf_level = get_nsqf_level_by_education(education)
    
    # Base recommendations for different experience levels
    base_recommendations = {
        "Beginner (0-1 years)": [
            {
                "title": "Python for Data Science Fundamentals",
                "level": "Beginner",
                "duration": "4-6 weeks",
                "description": "Master Python basics and data manipulation with Pandas",
                "priority": "High"
            },
            {
                "title": "Statistics and Probability for ML",
                "level": "Beginner",
                "duration": "3-4 weeks",
                "description": "Essential statistical concepts for machine learning",
                "priority": "High"
            },
            {
                "title": "Introduction to Machine Learning",
                "level": "Beginner",
                "duration": "6-8 weeks",
                "description": "Learn supervised and unsupervised learning algorithms",
                "priority": "Medium"
            }
        ],
        "Intermediate (2-4 years)": [
            {
                "title": "Advanced Machine Learning Algorithms",
                "level": "Intermediate",
                "duration": "6-8 weeks",
                "description": "Deep dive into ensemble methods, SVM, and neural networks",
                "priority": "High"
            },
            {
                "title": "MLOps and Model Deployment",
                "level": "Intermediate",
                "duration": "5-6 weeks",
                "description": "Learn to deploy and monitor ML models in production",
                "priority": "High"
            },
            {
                "title": "Deep Learning with TensorFlow",
                "level": "Intermediate",
                "duration": "8-10 weeks",
                "description": "Build and train deep neural networks",
                "priority": "Medium"
            }
        ],
        "Advanced (5+ years)": [
            {
                "title": "AI Research Methodologies",
                "level": "Advanced",
                "duration": "10-12 weeks",
                "description": "Learn cutting-edge research techniques in AI",
                "priority": "High"
            },
            {
                "title": "Reinforcement Learning",
                "level": "Advanced",
                "duration": "8-10 weeks",
                "description": "Master RL algorithms for complex decision-making",
                "priority": "Medium"
            },
            {
                "title": "AI Ethics and Governance",
                "level": "Advanced",
                "duration": "4-5 weeks",
                "description": "Understand ethical implications of AI systems",
                "priority": "High"
            }
        ]
    }
    
    # Interest-specific recommendations
    interest_recommendations = {
        "Machine Learning": [
            {
                "title": "Advanced Ensemble Methods",
                "level": "Intermediate",
                "duration": "4-5 weeks",
                "description": "Master Random Forest, XGBoost, and LightGBM",
                "priority": "Medium"
            }
        ],
        "Deep Learning": [
            {
                "title": "Transformer Architecture Deep Dive",
                "level": "Advanced",
                "duration": "6-7 weeks",
                "description": "Understand attention mechanisms and transformer models",
                "priority": "High"
            }
        ],
        "Natural Language Processing": [
            {
                "title": "Modern NLP with Transformers",
                "level": "Intermediate",
                "duration": "7-8 weeks",
                "description": "BERT, GPT, and other transformer-based models",
                "priority": "High"
            }
        ],
        "Computer Vision": [
            {
                "title": "Convolutional Neural Networks",
                "level": "Intermediate",
                "duration": "6-7 weeks",
                "description": "Image classification and object detection",
                "priority": "High"
            }
        ],
        "Data Science": [
            {
                "title": "Advanced Data Analytics",
                "level": "Intermediate",
                "duration": "5-6 weeks",
                "description": "Time series analysis and advanced statistics",
                "priority": "Medium"
            }
        ]
    }
    
    # Combine recommendations
    recommendations = base_recommendations.get(experience, [])
    
    # Add interest-specific recommendations
    for interest in interests:
        if interest in interest_recommendations:
            recommendations.extend(interest_recommendations[interest])
    
    # Shuffle and return top recommendations
    random.shuffle(recommendations)
    return recommendations[:8]

def get_nsqf_data(level: int) -> Dict[str, Any]:
    """
    Get NSQF data for a specific level
    
    Args:
        level (int): NSQF level
    
    Returns:
        dict: NSQF level data
    """
    return NSQF_DATA.get(level, {})

def get_all_job_roles() -> List[str]:
    """
    Get all available job roles across NSQF levels
    
    Returns:
        list: All job roles
    """
    roles = []
    for level_data in NSQF_DATA.values():
        roles.extend(level_data["job_roles"])
    return sorted(list(set(roles)))

def get_next_levels(current_level: int, num_levels: int = 2) -> List[int]:
    """
    Get next NSQF levels for progression
    
    Args:
        current_level (int): Current NSQF level
        num_levels (int): Number of next levels to return
    
    Returns:
        list: Next NSQF levels
    """
    next_levels = []
    for level in range(current_level + 1, min(current_level + num_levels + 1, 9)):
        if level in NSQF_DATA:
            next_levels.append(level)
    return next_levels
