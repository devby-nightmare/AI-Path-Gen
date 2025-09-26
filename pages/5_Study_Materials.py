import streamlit as st
from ai_service import generate_study_material, explain_concept
from learning_data import get_topic_by_id, get_learning_topics
from database import update_user_progress, get_user_progress
import json

st.set_page_config(page_title="Study Materials", page_icon="📖", layout="wide")

def initialize_study_session():
    """Initialize study session state variables."""
    if 'current_material' not in st.session_state:
        st.session_state.current_material = None
    if 'study_topic' not in st.session_state:
        st.session_state.study_topic = None
    if 'concept_explanations' not in st.session_state:
        st.session_state.concept_explanations = {}

def render_study_material(material):
    """Render the study material in a structured format."""
    if not material:
        return
    
    # Title and Overview
    st.title(f"📖 {material.get('title', 'Study Material')}")
    
    with st.expander("📋 Overview", expanded=True):
        st.markdown(material.get('overview', 'No overview available.'))
    
    # Key Concepts
    if material.get('key_concepts'):
        st.subheader("🔑 Key Concepts")
        
        for i, concept in enumerate(material['key_concepts'], 1):
            with st.expander(f"{i}. {concept.get('concept', 'Concept')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Definition:** {concept.get('definition', 'No definition provided.')}")
                    st.markdown(f"**Importance:** {concept.get('importance', 'No importance description.')}")
                    
                    if concept.get('examples'):
                        st.markdown("**Examples:**")
                        for example in concept['examples']:
                            st.markdown(f"• {example}")
                
                with col2:
                    # Interactive concept explanation
                    if st.button(f"Explain in Detail", key=f"explain_{i}"):
                        concept_name = concept.get('concept', '')
                        if concept_name:
                            with st.spinner("Generating detailed explanation..."):
                                try:
                                    user_level = getattr(st.session_state, 'experience_level', 'Intermediate')
                                    explanation = explain_concept(concept_name, user_level, st.session_state.study_topic)
                                    st.session_state.concept_explanations[concept_name] = explanation
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error generating explanation: {str(e)}")
                    
                    # Show cached explanation if available
                    concept_name = concept.get('concept', '')
                    if concept_name in st.session_state.concept_explanations:
                        st.markdown("**Detailed Explanation:**")
                        st.markdown(st.session_state.concept_explanations[concept_name])
    
    # Step-by-step Guide
    if material.get('step_by_step_guide'):
        st.subheader("📝 Step-by-Step Guide")
        
        for step in material['step_by_step_guide']:
            with st.expander(f"Step {step.get('step', 'N/A')}: {step.get('title', 'Step')}"):
                st.markdown(step.get('description', 'No description provided.'))
                
                if step.get('code_example'):
                    st.markdown("**Code Example:**")
                    st.code(step['code_example'], language='python')
    
    # Common Pitfalls
    if material.get('common_pitfalls'):
        st.subheader("⚠️ Common Pitfalls")
        
        for i, pitfall in enumerate(material['common_pitfalls'], 1):
            with st.expander(f"Pitfall {i}: {pitfall.get('pitfall', 'Common Mistake')[:50]}..."):
                st.markdown(f"**Problem:** {pitfall.get('pitfall', 'No description provided.')}")
                st.markdown(f"**Solution:** {pitfall.get('solution', 'No solution provided.')}")
    
    # Practical Exercises
    if material.get('practical_exercises'):
        st.subheader("💻 Practical Exercises")
        
        for i, exercise in enumerate(material['practical_exercises'], 1):
            with st.expander(f"Exercise {i}: {exercise.get('difficulty', 'Unknown')} Level"):
                st.markdown(f"**Exercise:** {exercise.get('exercise', 'No exercise description.')}")
                st.markdown(f"**Difficulty:** {exercise.get('difficulty', 'Unknown')}")
                st.markdown(f"**Expected Outcome:** {exercise.get('expected_outcome', 'No outcome specified.')}")
                
                # Exercise completion tracking
                exercise_key = f"exercise_{st.session_state.study_topic}_{i}"
                completed = st.checkbox(f"Mark as completed", key=exercise_key)
                
                if completed:
                    st.success("Great job! Exercise marked as completed.")
    
    # Further Reading
    if material.get('further_reading'):
        st.subheader("📚 Further Reading")
        
        for resource in material['further_reading']:
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.markdown(f"**{resource.get('title', 'Resource')}**")
            
            with col2:
                resource_type = resource.get('type', 'Unknown')
                type_emoji = {
                    'Paper': '📄',
                    'Tutorial': '🎓',
                    'Documentation': '📋',
                    'Book': '📖'
                }
                st.markdown(f"{type_emoji.get(resource_type, '📎')} {resource_type}")
            
            with col3:
                st.markdown(resource.get('description', 'No description available.'))

def main():
    st.title("📖 AI-Generated Study Materials")
    
    initialize_study_session()
    
    # Sidebar for topic selection and progress
    with st.sidebar:
        st.header("Study Session")
        
        # Topic selection
        topics = get_learning_topics()
        
        # Check if a topic was selected from another page
        if hasattr(st.session_state, 'current_topic') and st.session_state.current_topic:
            default_topic = st.session_state.current_topic
        else:
            default_topic = None
        
        topic_options = {f"{topic['title']} ({topic['difficulty']})": topic['id'] for topic in topics}
        
        if default_topic:
            # Find the display name for the default topic
            default_display = None
            for display_name, topic_id in topic_options.items():
                if topic_id == default_topic:
                    default_display = display_name
                    break
            
            if default_display:
                default_index = list(topic_options.keys()).index(default_display)
            else:
                default_index = 0
        else:
            default_index = 0
        
        selected_topic_display = st.selectbox(
            "Select Topic to Study",
            list(topic_options.keys()),
            index=default_index
        )
        selected_topic_id = topic_options[selected_topic_display]
        selected_topic = get_topic_by_id(selected_topic_id)
        
        st.session_state.study_topic = selected_topic_id
        
        # Topic information
        if selected_topic:
            st.markdown("---")
            st.markdown(f"**Topic:** {selected_topic['title']}")
            st.markdown(f"**Category:** {selected_topic['category']}")
            st.markdown(f"**Difficulty:** {selected_topic['difficulty']}")
            st.markdown(f"**Estimated Time:** {selected_topic['estimated_hours']} hours")
            
            # Prerequisites
            if selected_topic.get('prerequisites'):
                st.markdown("**Prerequisites:**")
                for prereq_id in selected_topic['prerequisites']:
                    prereq_topic = get_topic_by_id(prereq_id)
                    if prereq_topic:
                        st.markdown(f"• {prereq_topic['title']}")
        
        # Progress tracking
        if 'user_id' in st.session_state:
            st.markdown("---")
            st.subheader("📊 Progress")
            
            progress_data = get_user_progress(st.session_state.user_id)
            current_progress = 0
            
            for p in progress_data:
                if p['topic_id'] == selected_topic_id:
                    current_progress = p['progress']
                    break
            
            st.progress(current_progress / 100)
            st.markdown(f"Current: {current_progress:.0f}%")
            
            # Progress update
            new_progress = st.slider(
                "Update Progress",
                0, 100, int(current_progress),
                help="Update your learning progress for this topic"
            )
            
            if new_progress != current_progress:
                if st.button("💾 Save Progress"):
                    update_user_progress(
                        st.session_state.user_id,
                        selected_topic_id,
                        new_progress,
                        difficulty=selected_topic['difficulty']
                    )
                    st.success("Progress updated!")
                    st.rerun()
    
    # Main content area
    if not st.session_state.current_material or st.session_state.study_topic != selected_topic_id:
        # Topic selection and material generation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Study: {selected_topic['title']}" if selected_topic else "Select a Topic")
            
            if selected_topic:
                st.markdown(f"**Description:** {selected_topic['description']}")
                
                # Learning objectives
                st.markdown("**Learning Objectives:**")
                for objective in selected_topic['learning_objectives']:
                    st.markdown(f"• {objective}")
                
                # Generate study material button
                user_level = getattr(st.session_state, 'experience_level', 'Intermediate')
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("📚 Generate Study Material", type="primary"):
                        with st.spinner("Generating comprehensive study material..."):
                            try:
                                material = generate_study_material(
                                    selected_topic['title'],
                                    user_level,
                                    selected_topic['category']
                                )
                                st.session_state.current_material = material
                                st.session_state.study_topic = selected_topic_id
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating study material: {str(e)}")
                                st.info("Please check your internet connection and try again.")
                
                with col_b:
                    specific_concept = st.text_input(
                        "Focus on specific concept (optional)",
                        placeholder="e.g., gradient descent, transformers"
                    )
                    
                    if specific_concept and st.button("🎯 Generate Focused Material"):
                        with st.spinner(f"Generating material focused on {specific_concept}..."):
                            try:
                                material = generate_study_material(
                                    selected_topic['title'],
                                    user_level,
                                    specific_concept
                                )
                                st.session_state.current_material = material
                                st.session_state.study_topic = selected_topic_id
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating focused material: {str(e)}")
        
        with col2:
            st.subheader("📋 Study Tips")
            
            tips = [
                "Take notes while reading the material",
                "Work through all code examples",
                "Complete the practical exercises",
                "Review common pitfalls carefully",
                "Use additional resources for deeper understanding",
                "Test your knowledge with quizzes"
            ]
            
            for tip in tips:
                st.markdown(f"💡 {tip}")
            
            # Quick actions
            st.markdown("---")
            st.subheader("🚀 Quick Actions")
            
            if st.button("🧠 Take Quiz"):
                st.session_state.current_topic = selected_topic_id
                st.switch_page("pages/2_Quiz_System.py")
            
            if st.button("📚 View Resources"):
                st.switch_page("pages/4_Resource_Library.py")
            
            if st.button("📊 Check Progress"):
                st.switch_page("pages/3_Progress_Tracking.py")
    
    else:
        # Display generated study material
        material = st.session_state.current_material
        
        # Action buttons at the top
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Regenerate Material"):
                st.session_state.current_material = None
                st.rerun()
        
        with col2:
            if st.button("🧠 Take Quiz"):
                st.session_state.current_topic = selected_topic_id
                st.switch_page("pages/2_Quiz_System.py")
        
        with col3:
            if st.button("📚 Find Resources"):
                st.switch_page("pages/4_Resource_Library.py")
        
        with col4:
            if st.button("📊 View Progress"):
                st.switch_page("pages/3_Progress_Tracking.py")
        
        st.markdown("---")
        
        # Render the study material
        render_study_material(material)
        
        # Study session completion
        st.markdown("---")
        st.subheader("✅ Complete Study Session")
        
        col1, col2 = st.columns(2)
        
        with col1:
            satisfaction = st.selectbox(
                "How helpful was this material?",
                ["Very Helpful", "Helpful", "Somewhat Helpful", "Not Helpful"]
            )
        
        with col2:
            if st.button("Complete Session", type="primary"):
                # Update progress based on session completion
                if 'user_id' in st.session_state:
                    progress_data = get_user_progress(st.session_state.user_id)
                    current_progress = 0
                    
                    for p in progress_data:
                        if p['topic_id'] == selected_topic_id:
                            current_progress = p['progress']
                            break
                    
                    # Increase progress by 10-20% based on satisfaction
                    progress_increase = {
                        "Very Helpful": 20,
                        "Helpful": 15,
                        "Somewhat Helpful": 10,
                        "Not Helpful": 5
                    }
                    
                    new_progress = min(100, current_progress + progress_increase[satisfaction])
                    
                    update_user_progress(
                        st.session_state.user_id,
                        selected_topic_id,
                        new_progress,
                        completed_lessons=[f"Study Session - {material.get('title', 'Session')}"],
                        difficulty=selected_topic['difficulty']
                    )
                    
                    st.success(f"Study session completed! Progress updated to {new_progress:.0f}%")
                    
                    # Clear current material to allow new generation
                    st.session_state.current_material = None
                    
                    st.balloons()
        
        # Feedback section
        st.markdown("---")
        st.subheader("💭 Session Feedback")
        
        feedback = st.text_area(
            "Any feedback on the study material?",
            placeholder="What was most helpful? What could be improved?"
        )
        
        if feedback and st.button("Submit Feedback"):
            st.success("Thank you for your feedback! It helps improve the learning experience.")

if __name__ == "__main__":
    main()
