from typing import List, Dict, Optional

# Comprehensive AI/ML learning topics organized by difficulty and category
LEARNING_TOPICS = [
    # Beginner Level
    {
        "id": "ai_intro",
        "title": "Introduction to Artificial Intelligence",
        "difficulty": "Beginner",
        "category": "Foundations",
        "description": "Basic concepts of AI, its history, and applications",
        "estimated_hours": 6,
        "prerequisites": [],
        "learning_objectives": [
            "Understand what AI is and isn't",
            "Learn about different types of AI",
            "Explore real-world AI applications"
        ]
    },
    {
        "id": "python_basics",
        "title": "Python Programming for AI",
        "difficulty": "Beginner",
        "category": "Programming",
        "description": "Essential Python skills for AI and machine learning",
        "estimated_hours": 15,
        "prerequisites": [],
        "learning_objectives": [
            "Master Python fundamentals",
            "Learn data structures and control flow",
            "Understand object-oriented programming"
        ]
    },
    {
        "id": "ml_basics",
        "title": "Machine Learning Fundamentals",
        "difficulty": "Beginner",
        "category": "Machine Learning",
        "description": "Core concepts of machine learning and its types",
        "estimated_hours": 10,
        "prerequisites": ["python_basics"],
        "learning_objectives": [
            "Understand supervised vs unsupervised learning",
            "Learn about different ML algorithms",
            "Practice with simple ML problems"
        ]
    },
    {
        "id": "data_science_intro",
        "title": "Data Science Essentials",
        "difficulty": "Beginner",
        "category": "Data Science",
        "description": "Introduction to data analysis and visualization",
        "estimated_hours": 12,
        "prerequisites": ["python_basics"],
        "learning_objectives": [
            "Learn data manipulation with pandas",
            "Create visualizations with matplotlib",
            "Understand statistical basics"
        ]
    },
    
    # Intermediate Level
    {
        "id": "supervised_learning",
        "title": "Supervised Learning Algorithms",
        "difficulty": "Intermediate",
        "category": "Machine Learning",
        "description": "Deep dive into classification and regression algorithms",
        "estimated_hours": 20,
        "prerequisites": ["ml_basics", "data_science_intro"],
        "learning_objectives": [
            "Implement linear and logistic regression",
            "Understand decision trees and random forests",
            "Apply support vector machines"
        ]
    },
    {
        "id": "unsupervised_learning",
        "title": "Unsupervised Learning & Clustering",
        "difficulty": "Intermediate",
        "category": "Machine Learning",
        "description": "Clustering, dimensionality reduction, and pattern discovery",
        "estimated_hours": 18,
        "prerequisites": ["ml_basics", "data_science_intro"],
        "learning_objectives": [
            "Master k-means and hierarchical clustering",
            "Apply PCA and t-SNE",
            "Understand association rules"
        ]
    },
    {
        "id": "neural_networks",
        "title": "Neural Networks Introduction",
        "difficulty": "Intermediate",
        "category": "Deep Learning",
        "description": "Fundamentals of artificial neural networks",
        "estimated_hours": 16,
        "prerequisites": ["supervised_learning"],
        "learning_objectives": [
            "Understand perceptrons and multilayer networks",
            "Learn backpropagation algorithm",
            "Implement neural networks from scratch"
        ]
    },
    {
        "id": "feature_engineering",
        "title": "Feature Engineering & Selection",
        "difficulty": "Intermediate",
        "category": "Data Science",
        "description": "Techniques for creating and selecting optimal features",
        "estimated_hours": 14,
        "prerequisites": ["supervised_learning", "unsupervised_learning"],
        "learning_objectives": [
            "Master feature scaling and normalization",
            "Learn feature selection techniques",
            "Create meaningful features from raw data"
        ]
    },
    {
        "id": "nlp_basics",
        "title": "Natural Language Processing Basics",
        "difficulty": "Intermediate",
        "category": "Natural Language Processing",
        "description": "Introduction to processing and analyzing text data",
        "estimated_hours": 18,
        "prerequisites": ["supervised_learning"],
        "learning_objectives": [
            "Understand text preprocessing techniques",
            "Learn bag-of-words and TF-IDF",
            "Apply sentiment analysis"
        ]
    },
    
    # Advanced Level
    {
        "id": "deep_learning",
        "title": "Deep Learning with TensorFlow",
        "difficulty": "Advanced",
        "category": "Deep Learning",
        "description": "Advanced neural networks and deep learning architectures",
        "estimated_hours": 25,
        "prerequisites": ["neural_networks"],
        "learning_objectives": [
            "Build convolutional neural networks",
            "Implement recurrent neural networks",
            "Master transfer learning techniques"
        ]
    },
    {
        "id": "computer_vision",
        "title": "Computer Vision & Image Processing",
        "difficulty": "Advanced",
        "category": "Computer Vision",
        "description": "Image analysis and computer vision applications",
        "estimated_hours": 22,
        "prerequisites": ["deep_learning"],
        "learning_objectives": [
            "Implement image classification models",
            "Learn object detection techniques",
            "Apply image segmentation"
        ]
    },
    {
        "id": "advanced_nlp",
        "title": "Advanced NLP & Transformers",
        "difficulty": "Advanced",
        "category": "Natural Language Processing",
        "description": "Modern NLP with transformers and large language models",
        "estimated_hours": 20,
        "prerequisites": ["nlp_basics", "deep_learning"],
        "learning_objectives": [
            "Understand transformer architecture",
            "Implement BERT and GPT models",
            "Apply advanced text generation"
        ]
    },
    {
        "id": "reinforcement_learning",
        "title": "Reinforcement Learning",
        "difficulty": "Advanced",
        "category": "Reinforcement Learning",
        "description": "Agent-based learning and decision making",
        "estimated_hours": 24,
        "prerequisites": ["deep_learning"],
        "learning_objectives": [
            "Understand Q-learning and policy gradients",
            "Implement deep Q-networks",
            "Apply RL to game environments"
        ]
    },
    {
        "id": "mlops",
        "title": "MLOps & Production Deployment",
        "difficulty": "Advanced",
        "category": "MLOps",
        "description": "Deploying and maintaining ML models in production",
        "estimated_hours": 18,
        "prerequisites": ["supervised_learning", "feature_engineering"],
        "learning_objectives": [
            "Learn model versioning and tracking",
            "Implement CI/CD for ML",
            "Monitor model performance in production"
        ]
    },
    {
        "id": "ai_ethics",
        "title": "AI Ethics & Responsible AI",
        "difficulty": "Intermediate",
        "category": "Ethics",
        "description": "Ethical considerations and bias in AI systems",
        "estimated_hours": 8,
        "prerequisites": ["ml_basics"],
        "learning_objectives": [
            "Understand bias and fairness in AI",
            "Learn privacy and security considerations",
            "Apply ethical AI frameworks"
        ]
    }
]

def get_learning_topics() -> List[Dict]:
    """Get all available learning topics."""
    return LEARNING_TOPICS

def get_topics_by_difficulty(difficulty: str) -> List[Dict]:
    """Get topics filtered by difficulty level."""
    return [topic for topic in LEARNING_TOPICS if topic["difficulty"] == difficulty]

def get_topics_by_category(category: str) -> List[Dict]:
    """Get topics filtered by category."""
    return [topic for topic in LEARNING_TOPICS if topic["category"] == category]

def get_topic_by_id(topic_id: str) -> Optional[Dict]:
    """Get a specific topic by its ID."""
    for topic in LEARNING_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None

def get_prerequisite_topics(topic_id: str) -> List[Dict]:
    """Get prerequisite topics for a given topic."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        return []
    
    prerequisites = []
    for prereq_id in topic.get("prerequisites", []):
        prereq_topic = get_topic_by_id(prereq_id)
        if prereq_topic:
            prerequisites.append(prereq_topic)
    
    return prerequisites

def get_next_topics(completed_topics: List[str]) -> List[Dict]:
    """Get suggested next topics based on completed ones."""
    available_topics = []
    
    for topic in LEARNING_TOPICS:
        prerequisites = topic.get("prerequisites", [])
        
        # Check if all prerequisites are completed
        if all(prereq in completed_topics for prereq in prerequisites):
            # Only suggest if not already completed
            if topic["id"] not in completed_topics:
                available_topics.append(topic)
    
    return available_topics

def get_learning_path_suggestions(experience_level: str, interests: List[str]) -> List[Dict]:
    """Get suggested learning path based on experience and interests."""
    suggested_topics = []
    
    # Filter by experience level
    if experience_level == "Beginner":
        relevant_difficulties = ["Beginner"]
    elif experience_level == "Intermediate":
        relevant_difficulties = ["Beginner", "Intermediate"]
    else:  # Advanced
        relevant_difficulties = ["Beginner", "Intermediate", "Advanced"]
    
    # Filter by interests and difficulty
    for topic in LEARNING_TOPICS:
        if topic["difficulty"] in relevant_difficulties:
            # Check if topic category matches interests
            category_keywords = {
                "Machine Learning": ["machine learning", "ml"],
                "Deep Learning": ["deep learning", "neural networks"],
                "Natural Language Processing": ["nlp", "natural language processing"],
                "Computer Vision": ["computer vision", "cv"],
                "Data Science": ["data science", "data analysis"],
                "Reinforcement Learning": ["reinforcement learning", "rl"],
                "MLOps": ["mlops", "deployment", "production"]
            }
            
            topic_matches = False
            for interest in interests:
                for category, keywords in category_keywords.items():
                    if (interest.lower() in [kw.lower() for kw in keywords] and 
                        topic["category"] == category):
                        topic_matches = True
                        break
                if topic_matches:
                    break
            
            if topic_matches or not interests:  # Include if matches interest or no specific interests
                suggested_topics.append(topic)
    
    # Sort by difficulty (beginner first) and estimated hours
    suggested_topics.sort(key=lambda x: (
        {"Beginner": 0, "Intermediate": 1, "Advanced": 2}[x["difficulty"]],
        x["estimated_hours"]
    ))
    
    return suggested_topics

def get_topic_categories() -> List[str]:
    """Get all unique categories."""
    categories = list(set(topic["category"] for topic in LEARNING_TOPICS))
    return sorted(categories)

def search_topics(query: str) -> List[Dict]:
    """Search topics by title, description, or learning objectives."""
    query = query.lower()
    matching_topics = []
    
    for topic in LEARNING_TOPICS:
        # Search in title
        if query in topic["title"].lower():
            matching_topics.append(topic)
            continue
            
        # Search in description
        if query in topic["description"].lower():
            matching_topics.append(topic)
            continue
            
        # Search in learning objectives
        objectives_text = " ".join(topic["learning_objectives"]).lower()
        if query in objectives_text:
            matching_topics.append(topic)
            continue
    
    return matching_topics
