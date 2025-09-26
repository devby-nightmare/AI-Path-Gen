import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from nsqf import (
    get_nsqf_level_by_education, 
    get_career_pathway, 
    get_nsqf_data, 
    get_all_job_roles,
    get_next_levels,
    NSQF_DATA
)

st.set_page_config(
    page_title="NSQF Career Pathway",
    page_icon="🎯",
    layout="wide"
)

def main():
    st.title("🎯 NSQF Career Pathway")
    st.markdown("Discover your career progression path based on the National Skills Qualifications Framework")
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Pathway Configuration")
        
        # Education level input
        education_level = st.selectbox(
            "Select Your Education Level",
            ["High School", "Diploma", "Bachelor's", "Master's", "PhD"],
            index=2
        )
        
        # Target role selection
        all_roles = get_all_job_roles()
        target_role = st.selectbox(
            "Select Target Role (Optional)",
            [""] + all_roles
        )
        
        # Number of progression levels to show
        progression_levels = st.slider(
            "Progression Levels to Display",
            min_value=1,
            max_value=3,
            value=2
        )
    
    # Get current NSQF level
    current_nsqf_level = get_nsqf_level_by_education(education_level)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Current Level Overview
        st.subheader(f"📊 Your Current NSQF Level: {current_nsqf_level}")
        current_data = get_nsqf_data(current_nsqf_level)
        
        if current_data:
            # Current level details
            level_col1, level_col2 = st.columns(2)
            
            with level_col1:
                st.info(f"**Level Title:** {current_data['title']}")
                st.info(f"**Salary Range:** {current_data['salary_range']}")
            
            with level_col2:
                st.info(f"**Education Base:** {education_level}")
                st.info(f"**Available Roles:** {len(current_data['job_roles'])}")
            
            # Current level competencies and skills
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                st.write("**🎯 Core Competencies:**")
                for comp in current_data['competencies']:
                    st.write(f"• {comp}")
            
            with comp_col2:
                st.write("**🛠️ Key Skills:**")
                for skill in current_data['skills']:
                    st.write(f"• {skill}")
        
        # Career Progression Pathway
        st.subheader("🚀 Career Progression Pathway")
        
        if target_role:
            # Generate pathway for target role
            pathway = get_career_pathway(current_nsqf_level, target_role)
            
            if pathway['progression']:
                st.success(f"Pathway to **{target_role}** (Target Level: {pathway['target_level']})")
                
                # Create progression visualization
                levels = [step['level'] for step in pathway['progression']]
                titles = [step['title'] for step in pathway['progression']]
                
                fig = go.Figure()
                
                # Add progression line
                fig.add_trace(go.Scatter(
                    x=levels,
                    y=[1] * len(levels),
                    mode='lines+markers',
                    marker=dict(size=20, color='lightblue'),
                    line=dict(color='blue', width=3),
                    name='Progression Path',
                    text=titles,
                    textposition='top center'
                ))
                
                fig.update_layout(
                    title='NSQF Level Progression',
                    xaxis_title='NSQF Level',
                    yaxis=dict(visible=False),
                    height=200,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed progression steps
                for i, step in enumerate(pathway['progression']):
                    with st.expander(f"Level {step['level']}: {step['title']}", expanded=(i == 0)):
                        step_col1, step_col2 = st.columns(2)
                        
                        with step_col1:
                            st.write("**📚 Key Topics:**")
                            for topic in step['topics']:
                                st.write(f"• {topic}")
                            
                            st.write("**💼 Job Roles:**")
                            for role in step['job_roles']:
                                if role == target_role:
                                    st.write(f"• **{role}** ⭐")
                                else:
                                    st.write(f"• {role}")
                        
                        with step_col2:
                            st.write("**🎯 Competencies:**")
                            for comp in step['competencies']:
                                st.write(f"• {comp}")
                            
                            st.write("**💰 Salary Range:**")
                            st.write(step['salary_range'])
            else:
                st.warning("No progression pathway found for the selected role.")
        else:
            # Show next levels without specific target
            next_levels = get_next_levels(current_nsqf_level, progression_levels)
            
            if next_levels:
                st.info("**Next Career Levels Available:**")
                
                for level in next_levels:
                    level_data = get_nsqf_data(level)
                    if level_data:
                        with st.expander(f"Level {level}: {level_data['title']}", expanded=True):
                            prog_col1, prog_col2 = st.columns(2)
                            
                            with prog_col1:
                                st.write("**📚 Topics to Master:**")
                                for topic in level_data['topics'][:5]:
                                    st.write(f"• {topic}")
                                
                                st.write("**💼 Potential Roles:**")
                                for role in level_data['job_roles'][:4]:
                                    st.write(f"• {role}")
                            
                            with prog_col2:
                                st.write("**🛠️ Skills Required:**")
                                for skill in level_data['skills'][:4]:
                                    st.write(f"• {skill}")
                                
                                st.metric("Salary Range", level_data['salary_range'])
            else:
                st.info("You are at the highest NSQF level!")
    
    with col2:
        # NSQF Overview
        st.subheader("📋 NSQF Framework Overview")
        
        # NSQF levels summary
        levels_data = []
        for level, data in NSQF_DATA.items():
            levels_data.append({
                'Level': level,
                'Title': data['title'],
                'Roles': len(data['job_roles']),
                'Current': '✅' if level == current_nsqf_level else ''
            })
        
        df = pd.DataFrame(levels_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Quick Stats
        st.subheader("📊 Quick Statistics")
        
        total_roles = sum(len(data['job_roles']) for data in NSQF_DATA.values())
        total_skills = sum(len(data['skills']) for data in NSQF_DATA.values())
        
        st.metric("Total Career Roles", total_roles)
        st.metric("Total Skills Tracked", total_skills)
        st.metric("Your Current Level", current_nsqf_level)
        
        # Salary progression chart
        st.subheader("💰 Salary Progression")
        
        salary_data = []
        for level, data in NSQF_DATA.items():
            # Extract numeric values from salary range
            salary_range = data['salary_range']
            if '₹' in salary_range and '-' in salary_range:
                try:
                    min_sal = salary_range.split('₹')[1].split('-')[0]
                    if 'LPA' in min_sal:
                        min_val = float(min_sal.replace('LPA', '').strip())
                    else:
                        min_val = float(min_sal)
                    salary_data.append({'Level': level, 'Min Salary (LPA)': min_val})
                except:
                    salary_data.append({'Level': level, 'Min Salary (LPA)': 0})
        
        if salary_data:
            sal_df = pd.DataFrame(salary_data)
            fig_salary = px.line(
                sal_df, 
                x='Level', 
                y='Min Salary (LPA)',
                title='Minimum Salary by NSQF Level',
                markers=True
            )
            fig_salary.update_layout(height=300)
            st.plotly_chart(fig_salary, use_container_width=True)
        
        # Action buttons
        st.subheader("🎯 Take Action")
        
        if st.button("📝 Generate Learning Plan", type="primary"):
            st.success("Learning plan generated! Check your dashboard.")
        
        if st.button("📊 Compare Roles"):
            st.info("Role comparison feature coming soon!")
        
        if st.button("🔄 Update Goals"):
            st.session_state.show_goals = True
            st.success("Goals updated in session!")

if __name__ == "__main__":
    main()
