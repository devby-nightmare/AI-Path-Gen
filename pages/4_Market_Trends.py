import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="AI Market Trends",
    page_icon="📈",
    layout="wide"
)

def generate_trend_data():
    """Generate simulated market trend data"""
    # Skills trend data
    skills_data = {
        'Skill': ['Machine Learning', 'Deep Learning', 'Natural Language Processing', 
                 'Computer Vision', 'MLOps', 'Data Engineering', 'AI Ethics', 
                 'Reinforcement Learning', 'Edge AI', 'Quantum ML'],
        'Growth_Rate': [25, 35, 45, 30, 55, 40, 20, 15, 60, 10],
        'Job_Demand': [1200, 800, 600, 700, 400, 900, 150, 200, 300, 50],
        'Avg_Salary': [12, 15, 16, 14, 18, 13, 14, 17, 20, 25],
        'Difficulty': ['Medium', 'Hard', 'Hard', 'Medium', 'Medium', 'Medium', 'Easy', 'Hard', 'Hard', 'Very Hard']
    }
    
    # Salary trend data over time
    months = pd.date_range(start='2023-01', end='2024-12', freq='M')
    salary_trends = {}
    
    base_salaries = {
        'Data Scientist': 12,
        'ML Engineer': 15,
        'AI Research': 18,
        'Data Engineer': 11,
        'AI Product Manager': 20
    }
    
    for role, base in base_salaries.items():
        # Generate realistic salary progression with some noise
        trend = []
        current = base
        for i, month in enumerate(months):
            growth = 0.002 * i + random.uniform(-0.01, 0.01)  # ~2.4% annual growth with noise
            current = current * (1 + growth)
            trend.append(current)
        salary_trends[role] = trend
    
    # Industry adoption data
    industries = ['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing', 
                 'Automotive', 'Education', 'Government', 'Entertainment', 'Agriculture']
    adoption_rates = [85, 75, 60, 55, 45, 70, 35, 25, 40, 30]
    
    # Regional data
    regions = ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America', 'Africa']
    job_opportunities = [4500, 3200, 5800, 800, 600, 300]
    
    return {
        'skills': pd.DataFrame(skills_data),
        'salary_trends': pd.DataFrame(salary_trends, index=months),
        'industries': pd.DataFrame({'Industry': industries, 'AI_Adoption': adoption_rates}),
        'regions': pd.DataFrame({'Region': regions, 'Job_Opportunities': job_opportunities})
    }

def main():
    st.title("📈 AI Market Trends & Insights")
    st.markdown("Stay updated with the latest trends in AI job market and skill demands")
    st.markdown("---")
    
    # Generate data
    data = generate_trend_data()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Trending Skills", "💰 Salary Trends", "🏢 Industry Adoption", "🌍 Global Insights"])
    
    with tab1:
        st.subheader("🚀 Most In-Demand AI Skills")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Skills growth chart
            fig_growth = px.bar(
                data['skills'].sort_values('Growth_Rate', ascending=True),
                x='Growth_Rate',
                y='Skill',
                orientation='h',
                title='Skills by Growth Rate (%)',
                color='Growth_Rate',
                color_continuous_scale='Viridis'
            )
            fig_growth.update_layout(height=500)
            st.plotly_chart(fig_growth, use_container_width=True)
            
            # Job demand vs Average salary scatter plot
            fig_scatter = px.scatter(
                data['skills'],
                x='Job_Demand',
                y='Avg_Salary',
                size='Growth_Rate',
                hover_name='Skill',
                title='Job Demand vs Average Salary (LPA)',
                color='Difficulty',
                color_discrete_map={
                    'Easy': 'green',
                    'Medium': 'orange', 
                    'Hard': 'red',
                    'Very Hard': 'darkred'
                }
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Top skills table
            st.subheader("📊 Skills Overview")
            
            # Metrics for top skills
            top_growth = data['skills'].loc[data['skills']['Growth_Rate'].idxmax()]
            highest_salary = data['skills'].loc[data['skills']['Avg_Salary'].idxmax()]
            highest_demand = data['skills'].loc[data['skills']['Job_Demand'].idxmax()]
            
            st.metric("Fastest Growing", top_growth['Skill'], f"+{top_growth['Growth_Rate']}%")
            st.metric("Highest Salary", highest_salary['Skill'], f"₹{highest_salary['Avg_Salary']} LPA")
            st.metric("Highest Demand", highest_demand['Skill'], f"{highest_demand['Job_Demand']} jobs")
            
            # Skills by difficulty
            st.subheader("🎯 Skills by Difficulty")
            difficulty_counts = data['skills']['Difficulty'].value_counts()
            
            fig_diff = px.pie(
                values=difficulty_counts.values,
                names=difficulty_counts.index,
                title='Skill Distribution by Difficulty'
            )
            fig_diff.update_layout(height=300)
            st.plotly_chart(fig_diff, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            
            # Find skills with high growth but medium difficulty
            recommended = data['skills'][
                (data['skills']['Growth_Rate'] > 30) & 
                (data['skills']['Difficulty'].isin(['Easy', 'Medium']))
            ].sort_values(by='Growth_Rate', ascending=False)
            
            st.write("**🎯 Recommended Skills to Learn:**")
            for _, skill in recommended.head(3).iterrows():
                st.success(f"**{skill['Skill']}** - {skill['Growth_Rate']}% growth")
    
    with tab2:
        st.subheader("💰 AI Salary Trends Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Salary trends over time
            fig_salary = go.Figure()
            
            for role in data['salary_trends'].columns:
                fig_salary.add_trace(go.Scatter(
                    x=data['salary_trends'].index,
                    y=data['salary_trends'][role],
                    mode='lines+markers',
                    name=role,
                    line=dict(width=3)
                ))
            
            fig_salary.update_layout(
                title='AI Role Salary Trends (2023-2024)',
                xaxis_title='Month',
                yaxis_title='Average Salary (LPA)',
                height=400
            )
            st.plotly_chart(fig_salary, use_container_width=True)
            
            # Salary comparison by role
            latest_salaries = data['salary_trends'].iloc[-1].sort_values(ascending=True)
            
            fig_compare = px.bar(
                x=latest_salaries.values,
                y=latest_salaries.index,
                orientation='h',
                title='Current Average Salaries by Role (LPA)',
                color=latest_salaries.values,
                color_continuous_scale='Blues'
            )
            fig_compare.update_layout(height=350)
            st.plotly_chart(fig_compare, use_container_width=True)
        
        with col2:
            # Salary insights
            st.subheader("📊 Salary Insights")
            
            current_avg = data['salary_trends'].iloc[-1].mean()
            prev_avg = data['salary_trends'].iloc[-13].mean()  # 12 months ago
            growth = ((current_avg - prev_avg) / prev_avg) * 100
            
            st.metric("Average AI Salary", f"₹{current_avg:.1f} LPA", f"+{growth:.1f}%")
            
            highest_role = data['salary_trends'].iloc[-1].idxmax()
            highest_salary = data['salary_trends'].iloc[-1].max()
            st.metric("Highest Paying Role", highest_role, f"₹{highest_salary:.1f} LPA")
            
            # Salary growth rates
            st.subheader("📈 Salary Growth Rates")
            for role in data['salary_trends'].columns:
                start_salary = data['salary_trends'][role].iloc[0]
                end_salary = data['salary_trends'][role].iloc[-1]
                role_growth = ((end_salary - start_salary) / start_salary) * 100
                st.write(f"**{role}:** +{role_growth:.1f}%")
            
            # Prediction
            st.subheader("🔮 Salary Predictions")
            st.info("Based on current trends, AI salaries are expected to grow by 15-20% annually.")
            
            # Factors affecting salary
            st.subheader("🎯 Salary Factors")
            factors = [
                "Experience Level",
                "Technical Skills",
                "Company Size", 
                "Location",
                "Industry Domain",
                "Education Background"
            ]
            
            for factor in factors:
                st.write(f"• {factor}")
    
    with tab3:
        st.subheader("🏢 AI Adoption Across Industries")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Industry adoption chart
            fig_industry = px.bar(
                data['industries'].sort_values('AI_Adoption', ascending=True),
                x='AI_Adoption',
                y='Industry',
                orientation='h',
                title='AI Adoption Rate by Industry (%)',
                color='AI_Adoption',
                color_continuous_scale='Greens'
            )
            fig_industry.update_layout(height=500)
            st.plotly_chart(fig_industry, use_container_width=True)
            
            # Industry insights
            st.subheader("🔍 Industry Insights")
            
            insights_data = {
                'Technology': "Leading in AI innovation with focus on automation and ML products",
                'Finance': "Heavy investment in fraud detection, algorithmic trading, and risk assessment",
                'Healthcare': "Growing adoption in diagnostics, drug discovery, and patient care",
                'Retail': "E-commerce personalization, inventory management, and customer analytics",
                'Manufacturing': "Predictive maintenance, quality control, and supply chain optimization"
            }
            
            for industry, insight in insights_data.items():
                with st.expander(f"💼 {industry}"):
                    st.write(insight)
                    industry_data = data['industries'][data['industries']['Industry'] == industry]
                    if not industry_data.empty:
                        adoption_rate = industry_data['AI_Adoption'].iloc[0]
                        st.metric("Adoption Rate", f"{adoption_rate}%")
        
        with col2:
            # Top adopting industries
            st.subheader("🏆 Top AI Adopters")
            
            top_industries = data['industries'].nlargest(5, 'AI_Adoption')
            
            for _, industry in top_industries.iterrows():
                st.success(f"**{industry['Industry']}** - {industry['AI_Adoption']}%")
            
            # Adoption trends
            st.subheader("📊 Adoption Trends")
            
            # Simulate monthly adoption growth
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            adoption_growth = [65, 67, 69, 71, 73, 75]
            
            fig_trend = px.line(
                x=months,
                y=adoption_growth,
                title='Overall AI Adoption Growth',
                markers=True
            )
            fig_trend.update_layout(height=200)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Investment insights
            st.subheader("💰 Investment Insights")
            st.info("Global AI investment reached $200B+ in 2024")
            st.info("Enterprise AI spending growing at 35% CAGR")
            st.info("80% of enterprises plan AI initiatives by 2025")
    
    with tab4:
        st.subheader("🌍 Global AI Market Insights")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Regional job opportunities
            fig_regional = px.bar(
                data['regions'].sort_values('Job_Opportunities', ascending=True),
                x='Job_Opportunities',
                y='Region',
                orientation='h',
                title='AI Job Opportunities by Region',
                color='Job_Opportunities',
                color_continuous_scale='Blues'
            )
            fig_regional.update_layout(height=400)
            st.plotly_chart(fig_regional, use_container_width=True)
            
            # Global market size
            st.subheader("📊 Global AI Market Size")
            
            years = [2020, 2021, 2022, 2023, 2024, 2025]
            market_size = [50, 65, 85, 110, 140, 180]  # in billions USD
            
            fig_market = px.area(
                x=years,
                y=market_size,
                title='Global AI Market Size (Billion USD)',
                color_discrete_sequence=['lightblue']
            )
            fig_market.update_layout(height=300)
            st.plotly_chart(fig_market, use_container_width=True)
            
            # Key statistics
            st.subheader("🔢 Key Global Statistics")
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                st.metric("AI Companies Worldwide", "15,000+", "+25%")
                st.metric("AI Patents Filed (2024)", "65,000+", "+18%")
            
            with stats_col2:
                st.metric("AI Professionals", "2.3M+", "+22%")
                st.metric("Countries with AI Strategy", "60+", "+12")
            
            with stats_col3:
                st.metric("AI Startups (2024)", "4,500+", "+30%")
                st.metric("AI Research Papers", "180,000+", "+15%")
        
        with col2:
            # Regional insights
            st.subheader("🌎 Regional Highlights")
            
            regional_insights = {
                'Asia-Pacific': {
                    'highlight': 'Fastest growing AI market',
                    'growth': '+45% YoY',
                    'focus': 'Manufacturing & Healthcare'
                },
                'North America': {
                    'highlight': 'Highest AI investment',
                    'growth': '+35% YoY', 
                    'focus': 'Tech & Finance'
                },
                'Europe': {
                    'highlight': 'Leading AI regulation',
                    'growth': '+28% YoY',
                    'focus': 'Ethics & Automotive'
                }
            }
            
            for region, info in regional_insights.items():
                with st.expander(f"🌍 {region}"):
                    st.write(f"**Highlight:** {info['highlight']}")
                    st.write(f"**Growth:** {info['growth']}")
                    st.write(f"**Focus Areas:** {info['focus']}")
            
            # Market predictions
            st.subheader("🔮 Market Predictions")
            
            predictions = [
                "AI market to reach $500B by 2027",
                "50% of enterprises using AI by 2026",
                "AI creating 12M new jobs by 2025",
                "Edge AI market growing 25% annually"
            ]
            
            for prediction in predictions:
                st.success(f"📈 {prediction}")
            
            # Action items
            st.subheader("🎯 Action Items")
            
            actions = [
                "Focus on high-growth regions",
                "Develop skills in emerging technologies",
                "Build cross-industry expertise",
                "Stay updated with regulations"
            ]
            
            for action in actions:
                st.write(f"• {action}")
    
    # Footer with data disclaimer
    st.markdown("---")
    st.caption("📊 Data shown is for demonstration purposes. Real market data may vary. Last updated: " + datetime.now().strftime("%Y-%m-%d"))

if __name__ == "__main__":
    main()
