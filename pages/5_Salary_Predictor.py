import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from salary_predictor import get_salary_prediction_dashboard_data, SalaryPredictor

st.set_page_config(
    page_title="AI Salary Predictor",
    page_icon="💰",
    layout="wide"
)

def main():
    st.title("💰 AI Salary Predictor & Career Analytics")
    st.markdown("Advanced salary predictions and career progression analytics based on your profile")
    st.markdown("---")
    
    # Get user profile from session state
    user_education = st.session_state.get('user_education', 'Bachelor\'s')
    user_experience = st.session_state.get('user_experience', 'Beginner (0-1 years)')
    user_interests = st.session_state.get('user_interests', ['Machine Learning', 'Data Science'])
    
    # Sidebar for customization
    with st.sidebar:
        st.header("🔧 Prediction Parameters")
        
        # Override profile if needed
        education = st.selectbox(
            "Education Level",
            ["High School", "Diploma", "Bachelor's", "Master's", "PhD"],
            index=["High School", "Diploma", "Bachelor's", "Master's", "PhD"].index(user_education)
        )
        
        experience = st.selectbox(
            "Experience Level",
            ["Beginner (0-1 years)", "Intermediate (2-4 years)", "Advanced (5+ years)"],
            index=["Beginner (0-1 years)", "Intermediate (2-4 years)", "Advanced (5+ years)"].index(user_experience)
        )
        
        interests = st.multiselect(
            "Skills & Interests",
            ["Machine Learning", "Deep Learning", "Natural Language Processing", 
             "Computer Vision", "Data Science", "Robotics", "AI Ethics", "MLOps"],
            default=user_interests
        )
        
        # Additional factors
        st.subheader("📍 Additional Factors")
        
        location = st.selectbox(
            "Location",
            ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Other Metro", "Tier 2 Cities"],
            index=0
        )
        
        company_size = st.selectbox(
            "Company Size",
            ["Startup (1-50)", "Small (51-200)", "Medium (201-1000)", "Large (1001-5000)", "Enterprise (5000+)"],
            index=2
        )
        
        if st.button("🔄 Update Predictions"):
            st.rerun()
    
    # Get prediction data
    try:
        prediction_data = get_salary_prediction_dashboard_data(education, experience, interests)
        predictor = SalaryPredictor()
        
        # Current salary prediction with custom factors
        current_prediction = predictor.predict_current_salary(
            education, experience, interests, location, company_size
        )
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💰 Current Salary", "📈 Career Progression", "🎯 Role Analysis", "💡 Recommendations"])
        
        with tab1:
            st.subheader("💰 Current Salary Prediction")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Main prediction display
                st.metric(
                    "Predicted Salary", 
                    f"₹{current_prediction['predicted_salary']} LPA",
                    delta=f"₹{current_prediction['predicted_salary'] - prediction_data['insights']['market_comparison']['market_average']:.1f} vs market avg"
                )
                
                # Salary range
                salary_range = current_prediction['salary_range']
                st.write(f"**Range:** ₹{salary_range['min']} - ₹{salary_range['max']} LPA")
                st.write(f"**Confidence:** {current_prediction['confidence']*100:.0f}%")
                
                # Salary breakdown chart
                factors = current_prediction['factors']
                
                fig_factors = go.Figure(go.Waterfall(
                    name="Salary Components",
                    orientation="v",
                    measure=["relative", "relative", "relative", "relative", "relative", "total"],
                    x=["Base Salary", "Experience", "Skills", "Location", "Company", "Final Salary"],
                    textposition="outside",
                    y=[
                        factors['base_salary'],
                        factors['base_salary'] * (factors['experience_factor'] - 1),
                        factors['base_salary'] * (factors['skill_bonus'] / 100),
                        factors['base_salary'] * (factors['location_factor'] - 1),
                        factors['base_salary'] * (factors['company_factor'] - 1),
                        current_prediction['predicted_salary']
                    ],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))
                
                fig_factors.update_layout(
                    title="Salary Breakdown Analysis",
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig_factors, use_container_width=True)
                
                # Market comparison
                st.subheader("📊 Market Comparison")
                market_comp = prediction_data['insights']['market_comparison']
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                with comp_col1:
                    st.metric("Your Prediction", f"₹{market_comp['your_prediction']} LPA")
                with comp_col2:
                    st.metric("Market Average", f"₹{market_comp['market_average']} LPA")
                with comp_col3:
                    st.metric("Percentile", f"{market_comp['percentile']}th")
            
            with col2:
                # Skill impact analysis
                st.subheader("🎯 Skill Impact")
                
                skill_impact = prediction_data['insights']['skill_impact']
                if skill_impact:
                    for skill, impact in skill_impact.items():
                        st.write(f"**{skill}**")
                        st.write(f"Impact: +{impact['impact_percentage']}%")
                        st.write(f"Potential: +₹{impact['potential_increase']} LPA")
                        st.write("---")
                else:
                    st.info("Select skills to see their salary impact")
                
                # Current level roles
                st.subheader("💼 Current Level Roles")
                current_roles = prediction_data['insights']['current_level_roles']
                for role in current_roles[:5]:
                    st.write(f"• {role}")
        
        with tab2:
            st.subheader("📈 5-Year Career Progression")
            
            progression = prediction_data['progression']
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Progression chart
                prog_df = pd.DataFrame(progression['progression'])
                
                fig_prog = px.line(
                    prog_df, 
                    x='year', 
                    y='salary',
                    title='Salary Progression Over 5 Years',
                    markers=True,
                    line_shape='spline'
                )
                
                fig_prog.update_layout(
                    xaxis_title='Year',
                    yaxis_title='Salary (LPA)',
                    height=400
                )
                
                st.plotly_chart(fig_prog, use_container_width=True)
                
                # NSQF level progression
                fig_nsqf = px.bar(
                    prog_df,
                    x='year',
                    y='nsqf_level',
                    title='NSQF Level Progression',
                    color='nsqf_level',
                    color_continuous_scale='Blues'
                )
                
                fig_nsqf.update_layout(height=300)
                st.plotly_chart(fig_nsqf, use_container_width=True)
            
            with col2:
                # Progression metrics
                st.metric("Total Growth", f"{progression['total_growth']}%")
                st.metric("Avg Annual Growth", f"{progression['annual_avg_growth']}%")
                
                if progression['target_achieved_year']:
                    st.metric("Target Achievement", f"Year {progression['target_achieved_year']}")
                
                st.subheader("📊 Year-by-Year")
                for year_data in progression['progression'][:6]:
                    with st.container():
                        st.write(f"**Year {year_data['year']}**")
                        st.write(f"Salary: ₹{year_data['salary']} LPA")
                        st.write(f"Level: NSQF {year_data['nsqf_level']}")
                        if year_data['growth_rate'] > 0:
                            st.write(f"Growth: +{year_data['growth_rate']}%")
                        st.write("---")
        
        with tab3:
            st.subheader("🎯 Role-Based Salary Analysis")
            
            role_predictions = prediction_data['role_predictions']
            
            if role_predictions:
                # Create role comparison chart
                roles_df = pd.DataFrame([
                    {
                        'Role': role,
                        'Salary': data['salary'],
                        'NSQF Level': data['nsqf_level'],
                        'Confidence': data['confidence']
                    }
                    for role, data in role_predictions.items()
                ]).sort_values('Salary', ascending=True)
                
                fig_roles = px.bar(
                    roles_df,
                    x='Salary',
                    y='Role',
                    orientation='h',
                    title='Salary by Role',
                    color='NSQF Level',
                    color_continuous_scale='Viridis'
                )
                
                fig_roles.update_layout(height=600)
                st.plotly_chart(fig_roles, use_container_width=True)
                
                # Role details
                st.subheader("📋 Detailed Role Analysis")
                
                for role, data in sorted(role_predictions.items(), key=lambda x: x[1]['salary'], reverse=True):
                    with st.expander(f"💼 {role} - ₹{data['salary']} LPA"):
                        col_role1, col_role2 = st.columns(2)
                        with col_role1:
                            st.write(f"**Salary:** ₹{data['salary']} LPA")
                            st.write(f"**NSQF Level:** {data['nsqf_level']}")
                        with col_role2:
                            st.write(f"**Confidence:** {data['confidence']*100:.0f}%")
                            if data['nsqf_level'] > current_prediction['nsqf_level']:
                                st.success("🚀 Growth opportunity")
                            else:
                                st.info("📍 Current level role")
            else:
                st.info("No role predictions available. Please select your interests to see role-based analysis.")
        
        with tab4:
            st.subheader("💡 Salary Improvement Recommendations")
            
            recommendations = prediction_data['insights']['recommendations']
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.success(f"{i}. {rec}")
            else:
                st.info("Complete your profile to get personalized recommendations")
            
            # Next level opportunity
            next_level = prediction_data['insights']['next_level_opportunity']
            if next_level:
                st.subheader("⬆️ Next Level Opportunity")
                
                with st.container():
                    st.write(f"**Target Level:** NSQF {next_level['level']}")
                    st.write(f"**Potential Salary:** ₹{next_level['avg_salary']} LPA")
                    st.write(f"**Salary Increase:** +₹{next_level['potential_increase']} LPA")
                    
                    st.write("**Top Roles:**")
                    for role in next_level['roles']:
                        st.write(f"• {role}")
            
            # Action plan
            st.subheader("📋 Action Plan")
            
            action_items = [
                "🎓 Complete advanced courses in your areas of interest",
                "💼 Gain hands-on experience through projects",
                "🤝 Network with professionals in target roles",
                "📜 Obtain relevant certifications",
                "🔄 Regular skill assessment and updates"
            ]
            
            for action in action_items:
                st.write(action)
    
    except Exception as e:
        st.error(f"Error generating salary predictions: {str(e)}")
        st.info("Please ensure your profile is complete in the main dashboard to get accurate predictions.")

if __name__ == "__main__":
    main()