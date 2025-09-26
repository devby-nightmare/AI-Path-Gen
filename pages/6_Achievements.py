import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from achievement_system import AchievementSystem, update_user_achievements
from data_persistence import save_session_to_file, get_user_id

st.set_page_config(
    page_title="Achievements & Milestones",
    page_icon="🏆",
    layout="wide"
)

def main():
    st.title("🏆 Achievements & Milestones")
    st.markdown("Track your learning journey and celebrate your accomplishments!")
    st.markdown("---")
    
    # Get user data from session
    user_data = {
        'profile': {
            'name': st.session_state.get('user_name', ''),
            'education': st.session_state.get('user_education', ''),
            'experience': st.session_state.get('user_experience', ''),
            'interests': st.session_state.get('user_interests', [])
        },
        'progress': st.session_state.get('learning_progress', {}),
        'activities': st.session_state.get('recent_activities', []),
        'certifications': st.session_state.get('certifications', []),
        'achievements': st.session_state.get('achievements', []),
        'milestones': st.session_state.get('milestones', [])
    }
    
    # Update achievements
    achievement_updates = update_user_achievements(user_data)
    
    # Save any new achievements to session
    if achievement_updates['new_achievements'] or achievement_updates['new_milestones']:
        st.session_state.achievements = user_data['achievements']
        st.session_state.milestones = user_data['milestones']
        save_session_to_file()  # Persist achievements
    
    # Display new achievements popup
    if achievement_updates['new_achievements']:
        achievement_system = AchievementSystem()
        for ach_id in achievement_updates['new_achievements']:
            if ach_id in achievement_system.achievement_definitions:
                ach = achievement_system.achievement_definitions[ach_id]
                st.success(f"🎉 **New Achievement Unlocked!** {ach['name']} - {ach['description']} (+{ach['points']} points)")
    
    if achievement_updates['new_milestones']:
        achievement_system = AchievementSystem()
        for mil_id in achievement_updates['new_milestones']:
            if mil_id in achievement_system.milestone_definitions:
                mil = achievement_system.milestone_definitions[mil_id]
                st.balloons()
                st.success(f"🌟 **Milestone Achieved!** {mil['name']} - {mil['description']} (+{mil['rewards']['points']} points)")
    
    display_data = achievement_updates['display_data']
    
    # Main dashboard
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Overview metrics
        st.subheader("📊 Achievement Overview")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Total Achievements", display_data['total_achievements'])
        with metric_col2:
            st.metric("Milestones Reached", display_data['total_milestones'])
        with metric_col3:
            st.metric("Total Points", display_data['total_points'])
        with metric_col4:
            st.metric("Current Level", display_data['level'])
        
        # Level progress
        st.subheader("📈 Level Progress")
        
        progress_bar = st.progress(display_data['level_progress'] / 100)
        st.write(f"Level {display_data['level']} - {display_data['level_progress']:.1f}% to next level")
        
        # Achievements by category
        st.subheader("🏅 Your Achievements")
        
        if display_data['categorized_achievements']:
            for category, achievements in display_data['categorized_achievements'].items():
                with st.expander(f"{category} ({len(achievements)} achievements)", expanded=(category == "Getting Started")):
                    for ach in achievements:
                        col_ach1, col_ach2 = st.columns([3, 1])
                        with col_ach1:
                            st.write(f"**{ach['name']}**")
                            st.caption(ach['description'])
                        with col_ach2:
                            st.write(f"**{ach['points']} pts**")
                        st.write("---")
        else:
            st.info("Start completing courses and activities to earn your first achievements!")
        
        # Recent milestones
        if display_data['recent_milestones']:
            st.subheader("🌟 Recent Milestones")
            
            for milestone in display_data['recent_milestones']:
                with st.container():
                    st.success(f"**{milestone['name']}** - {milestone['description']} (+{milestone['points']} points)")
    
    with col2:
        # Next achievements to unlock
        st.subheader("🎯 Next Achievements")
        
        if display_data['next_achievements']:
            for next_ach in display_data['next_achievements']:
                with st.container():
                    st.write(f"**{next_ach['name']}**")
                    st.caption(next_ach['description'])
                    
                    # Progress bar
                    progress = next_ach['progress'] / 100
                    st.progress(progress)
                    st.write(f"{next_ach['progress']:.0f}% complete ({next_ach['points']} pts)")
                    st.write("---")
        else:
            st.info("Keep learning to unlock more achievements!")
        
        # Achievement statistics
        st.subheader("📈 Statistics")
        
        if display_data['categorized_achievements']:
            # Category distribution
            category_counts = {cat: len(achs) for cat, achs in display_data['categorized_achievements'].items()}
            
            fig_categories = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                title="Achievements by Category"
            )
            fig_categories.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig_categories, use_container_width=True)
        
        # Points breakdown
        if display_data['categorized_achievements']:
            category_points = {}
            for cat, achs in display_data['categorized_achievements'].items():
                category_points[cat] = sum(ach['points'] for ach in achs)
            
            fig_points = px.bar(
                x=list(category_points.values()),
                y=list(category_points.keys()),
                orientation='h',
                title="Points by Category"
            )
            fig_points.update_layout(height=250)
            st.plotly_chart(fig_points, use_container_width=True)
        
        # Motivation section
        st.subheader("💪 Keep Going!")
        
        motivational_messages = [
            "Every expert was once a beginner!",
            "Consistency beats perfection!",
            "Your future self will thank you!",
            "Learning is a journey, not a destination!",
            "Small progress is still progress!"
        ]
        
        import random
        message = random.choice(motivational_messages)
        st.info(f"💡 {message}")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        if st.button("🎓 View Available Courses"):
            st.switch_page("pages/3_Certifications.py")
        
        if st.button("📊 Check Progress"):
            st.switch_page("app.py")
        
        if st.button("🎯 Explore Career Path"):
            st.switch_page("pages/2_NSQF_Pathway.py")
    
    # Achievement gallery
    st.markdown("---")
    st.subheader("🖼️ Achievement Gallery")
    
    if display_data['categorized_achievements']:
        # Create a visual gallery of all achievements
        all_achievements = []
        for achievements in display_data['categorized_achievements'].values():
            all_achievements.extend(achievements)
        
        # Display in grid
        cols = st.columns(4)
        for i, ach in enumerate(all_achievements):
            col_idx = i % 4
            with cols[col_idx]:
                st.markdown(f"""
                <div style="border: 2px solid #gold; border-radius: 10px; padding: 10px; margin: 5px; text-align: center; background-color: #f0f0f0;">
                    <h4 style="margin: 5px;">{ach['name']}</h4>
                    <p style="font-size: 12px; margin: 5px;">{ach['description']}</p>
                    <p style="font-weight: bold; color: #2E8B57; margin: 5px;">{ach['points']} pts</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Start your learning journey to fill up your achievement gallery!")
    
    # Footer with tips
    st.markdown("---")
    st.subheader("💡 Tips to Earn More Achievements")
    
    tips = [
        "🎯 **Complete courses regularly** - Consistency is key to building streaks",
        "🌟 **Aim for high scores** - Quality learning earns performance achievements",
        "📚 **Explore different topics** - Diversify your skills to unlock variety achievements",
        "⏰ **Set learning schedules** - Early birds and night owls get special recognition",
        "🎓 **Finish course series** - Completing related courses unlocks specialty badges"
    ]
    
    for tip in tips:
        st.write(tip)

if __name__ == "__main__":
    main()