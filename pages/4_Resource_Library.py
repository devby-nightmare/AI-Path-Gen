import streamlit as st
import pandas as pd
import plotly.express as px
from learning_data import get_learning_topics, get_topic_categories, get_topic_by_id
import json

st.set_page_config(page_title="Resource Library", page_icon="📚", layout="wide")

# Curated resources for AI/ML learning
RESOURCE_LIBRARY = {
    "Papers": [
        {
            "title": "Attention Is All You Need",
            "authors": "Vaswani et al.",
            "year": 2017,
            "topic": "Deep Learning",
            "difficulty": "Advanced",
            "url": "https://arxiv.org/abs/1706.03762",
            "description": "Introduces the Transformer architecture that revolutionized NLP.",
            "tags": ["transformers", "attention", "nlp", "architecture"]
        },
        {
            "title": "Deep Residual Learning for Image Recognition",
            "authors": "He et al.",
            "year": 2015,
            "topic": "Computer Vision",
            "difficulty": "Advanced",
            "url": "https://arxiv.org/abs/1512.03385",
            "description": "Introduces ResNet architecture with skip connections.",
            "tags": ["cnn", "computer vision", "residual networks", "deep learning"]
        },
        {
            "title": "Playing Atari with Deep Reinforcement Learning",
            "authors": "Mnih et al.",
            "year": 2013,
            "topic": "Reinforcement Learning",
            "difficulty": "Advanced",
            "url": "https://arxiv.org/abs/1312.5602",
            "description": "First deep learning model to learn control policies directly from high-dimensional sensory input.",
            "tags": ["dqn", "reinforcement learning", "atari", "deep learning"]
        },
        {
            "title": "Random Forests",
            "authors": "Breiman",
            "year": 2001,
            "topic": "Machine Learning",
            "difficulty": "Intermediate",
            "url": "https://link.springer.com/article/10.1023/A:1010933404324",
            "description": "Introduces the Random Forest algorithm for classification and regression.",
            "tags": ["random forest", "ensemble", "classification", "regression"]
        },
        {
            "title": "Support Vector Networks",
            "authors": "Cortes & Vapnik",
            "year": 1995,
            "topic": "Machine Learning",
            "difficulty": "Intermediate",
            "url": "https://link.springer.com/article/10.1007/BF00994018",
            "description": "Original paper introducing Support Vector Machines.",
            "tags": ["svm", "support vector", "classification", "kernel"]
        }
    ],
    "Tutorials": [
        {
            "title": "Deep Learning Specialization",
            "provider": "Coursera (Andrew Ng)",
            "topic": "Deep Learning",
            "difficulty": "Beginner to Advanced",
            "url": "https://www.coursera.org/specializations/deep-learning",
            "description": "Comprehensive course series covering deep learning fundamentals to advanced topics.",
            "tags": ["neural networks", "cnn", "rnn", "deep learning", "course"]
        },
        {
            "title": "Machine Learning Course",
            "provider": "Coursera (Andrew Ng)",
            "topic": "Machine Learning",
            "difficulty": "Beginner",
            "url": "https://www.coursera.org/learn/machine-learning",
            "description": "Classic introduction to machine learning concepts and algorithms.",
            "tags": ["ml", "supervised learning", "unsupervised learning", "course"]
        },
        {
            "title": "Fast.ai Practical Deep Learning",
            "provider": "Fast.ai",
            "topic": "Deep Learning",
            "difficulty": "Intermediate",
            "url": "https://course.fast.ai/",
            "description": "Practical approach to deep learning with immediate applications.",
            "tags": ["practical", "deep learning", "pytorch", "applications"]
        },
        {
            "title": "CS231n: Convolutional Neural Networks",
            "provider": "Stanford University",
            "topic": "Computer Vision",
            "difficulty": "Advanced",
            "url": "http://cs231n.stanford.edu/",
            "description": "Stanford's course on CNNs for visual recognition.",
            "tags": ["cnn", "computer vision", "stanford", "course"]
        },
        {
            "title": "Natural Language Processing with Python",
            "provider": "NLTK Team",
            "topic": "Natural Language Processing",
            "difficulty": "Intermediate",
            "url": "https://www.nltk.org/book/",
            "description": "Comprehensive guide to NLP with Python and NLTK.",
            "tags": ["nlp", "python", "nltk", "text processing"]
        }
    ],
    "Datasets": [
        {
            "title": "ImageNet",
            "type": "Image Classification",
            "topic": "Computer Vision",
            "size": "150GB+",
            "url": "https://www.image-net.org/",
            "description": "Large-scale image database for object recognition research.",
            "tags": ["images", "classification", "benchmark", "large-scale"]
        },
        {
            "title": "IMDB Movie Reviews",
            "type": "Text Classification",
            "topic": "Natural Language Processing",
            "size": "80MB",
            "url": "https://ai.stanford.edu/~amaas/data/sentiment/",
            "description": "50,000 movie reviews for binary sentiment classification.",
            "tags": ["sentiment", "text", "classification", "reviews"]
        },
        {
            "title": "Titanic Dataset",
            "type": "Classification",
            "topic": "Machine Learning",
            "size": "60KB",
            "url": "https://www.kaggle.com/c/titanic/data",
            "description": "Classic dataset for learning classification algorithms.",
            "tags": ["classification", "beginner", "kaggle", "survival"]
        },
        {
            "title": "MNIST Handwritten Digits",
            "type": "Image Classification",
            "topic": "Computer Vision",
            "size": "60MB",
            "url": "http://yann.lecun.com/exdb/mnist/",
            "description": "Database of handwritten digits, perfect for learning image classification.",
            "tags": ["digits", "classification", "beginner", "benchmark"]
        },
        {
            "title": "Boston Housing",
            "type": "Regression",
            "topic": "Machine Learning",
            "size": "50KB",
            "url": "https://www.cs.toronto.edu/~delve/data/boston/bostonDetail.html",
            "description": "Housing prices in Boston for regression analysis.",
            "tags": ["regression", "housing", "prices", "classic"]
        },
        {
            "title": "Common Crawl",
            "type": "Text Corpus",
            "topic": "Natural Language Processing",
            "size": "Petabyte scale",
            "url": "https://commoncrawl.org/",
            "description": "Open repository of web crawl data for NLP research.",
            "tags": ["text", "web", "corpus", "large-scale"]
        }
    ],
    "Tools": [
        {
            "title": "Jupyter Notebooks",
            "category": "Development Environment",
            "topic": "Data Science",
            "url": "https://jupyter.org/",
            "description": "Interactive computing environment for data science and ML.",
            "tags": ["notebook", "python", "interactive", "development"]
        },
        {
            "title": "TensorFlow",
            "category": "ML Framework",
            "topic": "Deep Learning",
            "url": "https://www.tensorflow.org/",
            "description": "Open-source platform for machine learning and deep learning.",
            "tags": ["framework", "deep learning", "google", "production"]
        },
        {
            "title": "PyTorch",
            "category": "ML Framework",
            "topic": "Deep Learning",
            "url": "https://pytorch.org/",
            "description": "Dynamic neural network framework with strong research focus.",
            "tags": ["framework", "deep learning", "research", "dynamic"]
        },
        {
            "title": "Scikit-learn",
            "category": "ML Library",
            "topic": "Machine Learning",
            "url": "https://scikit-learn.org/",
            "description": "Simple and efficient tools for data mining and analysis.",
            "tags": ["library", "machine learning", "python", "classical"]
        },
        {
            "title": "Pandas",
            "category": "Data Manipulation",
            "topic": "Data Science",
            "url": "https://pandas.pydata.org/",
            "description": "Data structures and analysis tools for Python.",
            "tags": ["dataframes", "data manipulation", "python", "analysis"]
        },
        {
            "title": "Hugging Face Transformers",
            "category": "NLP Library",
            "topic": "Natural Language Processing",
            "url": "https://huggingface.co/transformers/",
            "description": "State-of-the-art NLP models and tools.",
            "tags": ["transformers", "nlp", "pretrained", "models"]
        }
    ],
    "Books": [
        {
            "title": "Pattern Recognition and Machine Learning",
            "author": "Christopher Bishop",
            "topic": "Machine Learning",
            "difficulty": "Advanced",
            "url": "https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/",
            "description": "Comprehensive mathematical treatment of machine learning.",
            "tags": ["theory", "mathematics", "comprehensive", "advanced"]
        },
        {
            "title": "The Elements of Statistical Learning",
            "author": "Hastie, Tibshirani, Friedman",
            "topic": "Machine Learning",
            "difficulty": "Advanced",
            "url": "https://web.stanford.edu/~hastie/ElemStatLearn/",
            "description": "Statistical perspective on machine learning and data mining.",
            "tags": ["statistics", "theory", "comprehensive", "free"]
        },
        {
            "title": "Deep Learning",
            "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
            "topic": "Deep Learning",
            "difficulty": "Advanced",
            "url": "https://www.deeplearningbook.org/",
            "description": "Comprehensive introduction to deep learning.",
            "tags": ["deep learning", "theory", "comprehensive", "free"]
        },
        {
            "title": "Hands-On Machine Learning",
            "author": "Aurélien Géron",
            "topic": "Machine Learning",
            "difficulty": "Intermediate",
            "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/",
            "description": "Practical guide to ML with Scikit-learn and TensorFlow.",
            "tags": ["practical", "scikit-learn", "tensorflow", "hands-on"]
        },
        {
            "title": "Python Machine Learning",
            "author": "Sebastian Raschka",
            "topic": "Machine Learning",
            "difficulty": "Intermediate",
            "url": "https://sebastianraschka.com/books.html",
            "description": "ML concepts and implementations with Python.",
            "tags": ["python", "implementation", "practical", "intermediate"]
        }
    ]
}

def filter_resources(resource_type, topic_filter=None, difficulty_filter=None, search_query=None):
    """Filter resources based on criteria."""
    resources = RESOURCE_LIBRARY.get(resource_type, [])
    
    filtered = []
    for resource in resources:
        # Topic filter
        if topic_filter and topic_filter != "All":
            if resource.get('topic', '').lower() != topic_filter.lower():
                continue
        
        # Difficulty filter
        if difficulty_filter and difficulty_filter != "All":
            if resource.get('difficulty', '').lower() != difficulty_filter.lower():
                continue
        
        # Search query
        if search_query:
            search_fields = [
                resource.get('title', ''),
                resource.get('description', ''),
                ' '.join(resource.get('tags', []))
            ]
            if not any(search_query.lower() in field.lower() for field in search_fields):
                continue
        
        filtered.append(resource)
    
    return filtered

def display_resource_card(resource, resource_type):
    """Display a resource card with consistent formatting."""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Title with link
            if resource.get('url'):
                st.markdown(f"**[{resource['title']}]({resource['url']})**")
            else:
                st.markdown(f"**{resource['title']}**")
            
            # Author/Provider info
            if resource_type == "Papers" and resource.get('authors'):
                st.markdown(f"*{resource['authors']} ({resource.get('year', 'N/A')})*")
            elif resource_type == "Tutorials" and resource.get('provider'):
                st.markdown(f"*{resource['provider']}*")
            elif resource_type == "Books" and resource.get('author'):
                st.markdown(f"*{resource['author']}*")
            elif resource_type == "Tools" and resource.get('category'):
                st.markdown(f"*{resource['category']}*")
            elif resource_type == "Datasets" and resource.get('type'):
                st.markdown(f"*{resource['type']} • {resource.get('size', 'N/A')}*")
            
            # Description
            st.markdown(resource.get('description', 'No description available.'))
            
            # Tags
            if resource.get('tags'):
                tag_str = ' • '.join([f"`{tag}`" for tag in resource['tags'][:5]])
                st.markdown(f"**Tags:** {tag_str}")
        
        with col2:
            # Topic and difficulty
            if resource.get('topic'):
                st.markdown(f"**Topic:** {resource['topic']}")
            if resource.get('difficulty'):
                difficulty_color = {
                    'Beginner': '🟢',
                    'Intermediate': '🟡',
                    'Advanced': '🔴'
                }
                color = difficulty_color.get(resource['difficulty'], '⚪')
                st.markdown(f"**Level:** {color} {resource['difficulty']}")
            
            # Action button
            if resource.get('url'):
                st.link_button("View Resource", resource['url'])
        
        st.markdown("---")

def main():
    st.title("📚 AI/ML Resource Library")
    st.markdown("Curated collection of papers, tutorials, datasets, and tools for AI/ML learning.")
    
    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Resource type selection
        resource_types = list(RESOURCE_LIBRARY.keys())
        selected_type = st.selectbox("Resource Type", resource_types)
        
        # Search
        search_query = st.text_input("Search", placeholder="Enter keywords...")
        
        # Topic filter
        all_topics = set()
        for resources in RESOURCE_LIBRARY.values():
            for resource in resources:
                if resource.get('topic'):
                    all_topics.add(resource['topic'])
        
        topic_options = ["All"] + sorted(list(all_topics))
        topic_filter = st.selectbox("Topic", topic_options)
        
        # Difficulty filter
        difficulty_options = ["All", "Beginner", "Intermediate", "Advanced"]
        difficulty_filter = st.selectbox("Difficulty", difficulty_options)
        
        # Resource statistics
        st.markdown("---")
        st.subheader("📊 Library Stats")
        for rtype, resources in RESOURCE_LIBRARY.items():
            st.metric(rtype, len(resources))
    
    # Main content
    resources = filter_resources(selected_type, topic_filter, difficulty_filter, search_query)
    
    # Header with count
    st.subheader(f"{selected_type} ({len(resources)} resources)")
    
    if not resources:
        st.warning("No resources found matching your criteria. Try adjusting the filters.")
        return
    
    # Resource type specific information
    if selected_type == "Papers":
        st.info("📄 Research papers are fundamental for understanding the theoretical foundations of AI/ML. "
               "Start with survey papers and gradually move to specific techniques.")
    elif selected_type == "Tutorials":
        st.info("🎓 Tutorials and courses provide structured learning paths. "
               "Choose based on your current level and learning style.")
    elif selected_type == "Datasets":
        st.info("📊 Datasets are essential for hands-on practice. "
               "Start with clean, well-documented datasets before tackling real-world messy data.")
    elif selected_type == "Tools":
        st.info("🔧 Tools and frameworks are the building blocks of ML projects. "
               "Master the fundamentals before exploring specialized tools.")
    elif selected_type == "Books":
        st.info("📖 Books provide comprehensive and in-depth knowledge. "
               "Great for building strong theoretical foundations.")
    
    # Display resources
    for resource in resources:
        display_resource_card(resource, selected_type)
    
    # Additional sections
    if selected_type == "Papers":
        st.subheader("📈 Research Trends")
        
        # Create topic distribution chart
        topics = [r.get('topic', 'Unknown') for r in RESOURCE_LIBRARY['Papers']]
        topic_counts = pd.Series(topics).value_counts()
        
        fig = px.bar(
            x=topic_counts.values,
            y=topic_counts.index,
            orientation='h',
            title="Research Papers by Topic",
            labels={'x': 'Number of Papers', 'y': 'Topic'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    elif selected_type == "Datasets":
        st.subheader("💾 Dataset Categories")
        
        # Create type distribution chart
        dataset_types = [r.get('type', 'Unknown') for r in RESOURCE_LIBRARY['Datasets']]
        type_counts = pd.Series(dataset_types).value_counts()
        
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Datasets by Type"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Learning path integration
    st.subheader("🛤️ Integration with Learning Paths")
    
    # Show how resources relate to learning topics
    if 'user_id' in st.session_state:
        from database import get_user_progress
        progress_data = get_user_progress(st.session_state.user_id)
        
        if progress_data:
            st.markdown("**Resources for your current topics:**")
            
            current_topics = [p['topic_id'] for p in progress_data if 0 < p['progress'] < 100]
            
            for topic_id in current_topics[:3]:  # Show top 3 current topics
                topic = get_topic_by_id(topic_id)
                if topic:
                    st.markdown(f"**{topic['title']}:**")
                    
                    # Find relevant resources
                    relevant_resources = []
                    for rtype, rlist in RESOURCE_LIBRARY.items():
                        for resource in rlist:
                            if (resource.get('topic', '').lower() in topic['category'].lower() or
                                any(tag in topic['title'].lower() for tag in resource.get('tags', []))):
                                relevant_resources.append((rtype, resource))
                    
                    if relevant_resources:
                        for rtype, resource in relevant_resources[:2]:  # Show top 2 per topic
                            st.markdown(f"• [{resource['title']}]({resource.get('url', '#')}) ({rtype})")
                    else:
                        st.markdown("• No specific resources found for this topic")
    else:
        st.info("Set up your profile to see personalized resource recommendations based on your learning progress!")

if __name__ == "__main__":
    main()
