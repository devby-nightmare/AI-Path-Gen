import json
import os
from openai import OpenAI
from typing import List, Dict, Any

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "default_key")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_personalized_recommendations(experience_level: str, interests: List[str], 
                                   progress_data: List[Dict]) -> List[Dict]:
    """Generate personalized learning recommendations using AI."""
    try:
        # Prepare context for AI
        context = {
            "experience_level": experience_level,
            "interests": interests,
            "completed_topics": [p['topic_id'] for p in progress_data if p['progress'] >= 100],
            "in_progress_topics": [p['topic_id'] for p in progress_data if 0 < p['progress'] < 100]
        }
        
        prompt = f"""
        Based on the user's learning profile, provide 3 personalized AI/ML topic recommendations.
        
        User Profile:
        - Experience Level: {experience_level}
        - Interests: {', '.join(interests)}
        - Completed Topics: {', '.join(context['completed_topics']) if context['completed_topics'] else 'None'}
        - In Progress Topics: {', '.join(context['in_progress_topics']) if context['in_progress_topics'] else 'None'}
        
        Provide recommendations in JSON format with the following structure:
        {{
            "recommendations": [
                {{
                    "topic_id": "unique_id",
                    "title": "Topic Title",
                    "description": "Brief description explaining why this is recommended",
                    "difficulty": "Beginner|Intermediate|Advanced",
                    "estimated_hours": number,
                    "prerequisites": ["prerequisite1", "prerequisite2"]
                }}
            ]
        }}
        
        Focus on topics that:
        1. Match the user's experience level or slightly challenge them
        2. Align with their stated interests
        3. Build upon completed topics
        4. Provide logical progression in their learning path
        """
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an AI learning path advisor specializing in AI/ML education."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("recommendations", [])
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        # Return fallback recommendations
        return [
            {
                "topic_id": "ml_basics",
                "title": "Machine Learning Fundamentals",
                "description": "Perfect starting point for understanding core ML concepts",
                "difficulty": "Beginner",
                "estimated_hours": 8,
                "prerequisites": []
            },
            {
                "topic_id": "python_for_ml",
                "title": "Python for Machine Learning",
                "description": "Essential programming skills for ML practitioners",
                "difficulty": "Beginner",
                "estimated_hours": 12,
                "prerequisites": []
            }
        ]

def generate_quiz_questions(topic_id: str, difficulty: str, num_questions: int = 5) -> List[Dict]:
    """Generate quiz questions for a specific topic."""
    try:
        prompt = f"""
        Generate {num_questions} multiple-choice quiz questions for the AI/ML topic: {topic_id}.
        Difficulty level: {difficulty}
        
        Provide questions in JSON format:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Detailed explanation of the correct answer",
                    "difficulty": "{difficulty}"
                }}
            ]
        }}
        
        Ensure questions are:
        1. Technically accurate and up-to-date
        2. Appropriate for the specified difficulty level
        3. Covering different aspects of the topic
        4. Include clear explanations for learning
        """
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert AI/ML educator creating assessment questions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
        
    except Exception as e:
        print(f"Error generating quiz questions: {e}")
        # Return fallback questions
        return [
            {
                "question": "What is the primary goal of machine learning?",
                "options": [
                    "To replace human intelligence",
                    "To learn patterns from data and make predictions",
                    "To create artificial consciousness",
                    "To automate all human tasks"
                ],
                "correct_answer": 1,
                "explanation": "Machine learning focuses on enabling computers to learn patterns from data and make predictions or decisions without being explicitly programmed for each specific task.",
                "difficulty": difficulty
            }
        ]

def generate_study_material(topic: str, user_level: str, specific_concept: str = None) -> Dict:
    """Generate comprehensive study material for a topic."""
    try:
        concept_focus = f" with specific focus on: {specific_concept}" if specific_concept else ""
        
        prompt = f"""
        Create comprehensive study material for the AI/ML topic: {topic}
        Target audience: {user_level} level learners{concept_focus}
        
        Provide the content in JSON format:
        {{
            "title": "Study Material Title",
            "overview": "Brief overview of the topic",
            "key_concepts": [
                {{
                    "concept": "Concept Name",
                    "definition": "Clear definition",
                    "importance": "Why this concept matters",
                    "examples": ["Real-world example 1", "Real-world example 2"]
                }}
            ],
            "step_by_step_guide": [
                {{
                    "step": 1,
                    "title": "Step Title",
                    "description": "Detailed explanation",
                    "code_example": "# Python code example if applicable"
                }}
            ],
            "common_pitfalls": [
                {{
                    "pitfall": "Common mistake description",
                    "solution": "How to avoid or fix this issue"
                }}
            ],
            "practical_exercises": [
                {{
                    "exercise": "Exercise description",
                    "difficulty": "Easy|Medium|Hard",
                    "expected_outcome": "What the learner should achieve"
                }}
            ],
            "further_reading": [
                {{
                    "title": "Resource title",
                    "type": "Paper|Tutorial|Documentation|Book",
                    "description": "Brief description of the resource"
                }}
            ]
        }}
        
        Ensure the content is:
        1. Accurate and current with AI/ML best practices
        2. Appropriate for the specified difficulty level
        3. Includes practical examples and code where relevant
        4. Provides clear learning progression
        """
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert AI/ML educator creating detailed study materials."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error generating study material: {e}")
        # Return fallback content
        return {
            "title": f"Introduction to {topic}",
            "overview": f"This study material provides an introduction to {topic} for {user_level} level learners.",
            "key_concepts": [
                {
                    "concept": "Fundamental Concept",
                    "definition": "Basic definition of the main concept",
                    "importance": "Understanding this concept is crucial for further learning",
                    "examples": ["Example application in real world"]
                }
            ],
            "step_by_step_guide": [
                {
                    "step": 1,
                    "title": "Getting Started",
                    "description": "Begin by understanding the basic principles",
                    "code_example": "# Basic code example\nprint('Hello, AI!')"
                }
            ],
            "common_pitfalls": [
                {
                    "pitfall": "Common beginner mistake",
                    "solution": "How to avoid this mistake"
                }
            ],
            "practical_exercises": [
                {
                    "exercise": "Apply the concepts in a simple project",
                    "difficulty": "Easy",
                    "expected_outcome": "Better understanding of the fundamentals"
                }
            ],
            "further_reading": [
                {
                    "title": "Additional Resource",
                    "type": "Tutorial",
                    "description": "Further learning material"
                }
            ]
        }

def explain_concept(concept: str, user_level: str, context: str = None) -> str:
    """Generate a detailed explanation of a specific AI/ML concept."""
    try:
        context_info = f" in the context of {context}" if context else ""
        
        prompt = f"""
        Provide a clear, detailed explanation of the AI/ML concept: {concept}
        Target audience: {user_level} level{context_info}
        
        The explanation should:
        1. Start with a simple, intuitive definition
        2. Provide analogies or real-world examples
        3. Explain the technical details appropriate for the level
        4. Include practical applications
        5. Mention related concepts and how they connect
        
        Make the explanation engaging and educational.
        """
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert AI/ML educator known for clear, engaging explanations."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error explaining concept: {e}")
        return f"I apologize, but I'm currently unable to provide a detailed explanation of {concept}. Please check your internet connection and try again."
