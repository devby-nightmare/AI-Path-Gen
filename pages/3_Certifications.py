import streamlit as st
import io
import base64
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image
from data_persistence import save_session_to_file, auto_save_session
try:
    import qrcode
    import qrcode.constants
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

st.set_page_config(
    page_title="AI Learning Certifications",
    page_icon="🏆",
    layout="wide"
)

def generate_qr_code(data: str) -> str:
    """Generate QR code and return as base64 encoded string"""
    if not QR_AVAILABLE:
        raise ImportError("QR code library not available")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def main():
    st.title("🏆 AI Learning Certifications")
    st.markdown("Track your achievements and generate certificates for completed courses")
    st.markdown("---")
    
    # Initialize session state for certifications
    if 'certifications' not in st.session_state:
        # Try to load from persistence first
        from data_persistence import load_session_from_file
        if not st.session_state.get('user_name') or not load_session_from_file():
            # Fallback to default data only if no saved data exists
            st.session_state.certifications = [
                {
                    'id': 'CERT001',
                    'course': 'Python for Data Science Fundamentals',
                    'completion_date': datetime.now() - timedelta(days=30),
                    'score': 95,
                    'level': 'Beginner',
                    'status': 'Completed'
                },
                {
                    'id': 'CERT002',
                    'course': 'Machine Learning Basics',
                    'completion_date': datetime.now() - timedelta(days=15),
                    'score': 88,
                    'level': 'Intermediate',
                    'status': 'Completed'
                },
                {
                    'id': 'CERT003',
                    'course': 'Deep Learning with TensorFlow',
                    'completion_date': None,
                    'score': None,
                    'level': 'Advanced',
                    'status': 'In Progress'
                }
            ]
    
    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 Filter Certifications")
        
        status_filter = st.selectbox(
            "Status",
            ["All", "Completed", "In Progress", "Not Started"]
        )
        
        level_filter = st.selectbox(
            "Level",
            ["All", "Beginner", "Intermediate", "Advanced"]
        )
        
        # Add new certification
        st.subheader("➕ Add New Course")
        with st.form("add_course"):
            course_name = st.text_input("Course Name")
            course_level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
            
            if st.form_submit_button("Add Course"):
                if course_name:  # Only add if course name is provided
                    new_cert = {
                        'id': f'CERT{len(st.session_state.certifications)+1:03d}',
                        'course': course_name,
                        'completion_date': None,
                        'score': None,
                        'level': course_level,
                        'status': 'Not Started'
                    }
                    st.session_state.certifications.append(new_cert)
                    auto_save_session()  # Save new course
                    st.success(f"Added {course_name} to your learning path!")
                    st.rerun()
                else:
                    st.error("Please enter a course name")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Certifications overview
        st.subheader("📜 Your Certifications")
        
        # Filter certifications
        filtered_certs = st.session_state.certifications
        if status_filter != "All":
            filtered_certs = [cert for cert in filtered_certs if cert['status'] == status_filter]
        if level_filter != "All":
            filtered_certs = [cert for cert in filtered_certs if cert['level'] == level_filter]
        
        if not filtered_certs:
            st.info("No certifications found with the selected filters.")
        else:
            for cert in filtered_certs:
                with st.expander(f"🎓 {cert['course']}", expanded=cert['status'] == 'Completed'):
                    cert_col1, cert_col2 = st.columns([2, 1])
                    
                    with cert_col1:
                        st.write(f"**Certificate ID:** {cert['id']}")
                        st.write(f"**Level:** {cert['level']}")
                        st.write(f"**Status:** {cert['status']}")
                        
                        if cert['completion_date']:
                            st.write(f"**Completed:** {cert['completion_date'].strftime('%Y-%m-%d')}")
                        if cert['score']:
                            st.write(f"**Score:** {cert['score']}%")
                        
                        # Action buttons
                        if cert['status'] == 'Completed':
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("Generate Certificate", key=f"gen_{cert['id']}"):
                                    st.session_state.selected_cert = cert['id']
                            with col_btn2:
                                if QR_AVAILABLE:
                                    if st.button("Download QR Code", key=f"qr_{cert['id']}"):
                                        st.session_state.qr_cert = cert['id']
                                else:
                                    st.caption("QR codes unavailable")
                        elif cert['status'] == 'In Progress':
                            if st.button("Mark as Completed", key=f"complete_{cert['id']}"):
                                cert['status'] = 'Completed'
                                cert['completion_date'] = datetime.now()
                                cert['score'] = 85 + (hash(cert['course']) % 15)  # Simulated score
                                auto_save_session()  # Save progress
                                st.success("Congratulations! Course completed!")
                                st.rerun()
                    
                    with cert_col2:
                        # Progress indicator
                        if cert['status'] == 'Completed':
                            st.success("✅ Completed")
                            if cert['score']:
                                st.metric("Score", f"{cert['score']}%")
                        elif cert['status'] == 'In Progress':
                            st.warning("🔄 In Progress")
                            # Simulated progress
                            progress = hash(cert['course']) % 80 + 10
                            st.progress(progress / 100)
                            st.write(f"{progress}% Complete")
                        else:
                            st.info("⏳ Not Started")
        
        # Certificate Generation
        if 'selected_cert' in st.session_state:
            selected = next((c for c in st.session_state.certifications if c['id'] == st.session_state.selected_cert), None)
            if selected and selected['status'] == 'Completed':
                st.subheader("🎖️ Generated Certificate")
                
                # Certificate content
                cert_container = st.container()
                with cert_container:
                    st.markdown("""
                    <div style='border: 3px solid #gold; padding: 30px; text-align: center; background-color: #f9f9f9; margin: 20px 0;'>
                        <h1 style='color: #2E8B57; font-family: serif;'>🏆 CERTIFICATE OF COMPLETION 🏆</h1>
                        <hr style='border: 2px solid #gold;'>
                        <h3>This is to certify that</h3>
                        <h2 style='color: #1E90FF; text-decoration: underline;'>{user_name}</h2>
                        <h3>has successfully completed</h3>
                        <h2 style='color: #FF6347; font-weight: bold;'>{course}</h2>
                        <p><strong>Score:</strong> {score}% | <strong>Level:</strong> {level}</p>
                        <p><strong>Completion Date:</strong> {date}</p>
                        <p><strong>Certificate ID:</strong> {cert_id}</p>
                        <hr style='border: 1px solid #gold;'>
                        <p style='font-style: italic;'>AI Learning Career Dashboard</p>
                    </div>
                    """.format(
                        user_name=st.session_state.get('user_name', 'Student'),
                        course=selected['course'],
                        score=selected['score'],
                        level=selected['level'],
                        date=selected['completion_date'].strftime('%B %d, %Y'),
                        cert_id=selected['id']
                    ), unsafe_allow_html=True)
                
                # Generate verification URL
                verification_url = f"https://ai-dashboard.verify/{selected['id']}"
                st.write(f"**Verification URL:** {verification_url}")
                
                # Clear selection
                if st.button("Close Certificate"):
                    del st.session_state.selected_cert
                    st.rerun()
        
        # QR Code Generation
        if 'qr_cert' in st.session_state:
            qr_cert = next((c for c in st.session_state.certifications if c['id'] == st.session_state.qr_cert), None)
            if qr_cert:
                st.subheader("📱 Certificate QR Code")
                
                # Generate QR code data
                qr_data = f"Certificate: {qr_cert['course']}\nID: {qr_cert['id']}\nScore: {qr_cert['score']}%\nVerify: https://ai-dashboard.verify/{qr_cert['id']}"
                
                if QR_AVAILABLE:
                    try:
                        qr_base64 = generate_qr_code(qr_data)
                        st.markdown(f'<img src="data:image/png;base64,{qr_base64}" width="200">', unsafe_allow_html=True)
                        st.write("Scan this QR code to verify the certificate")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download QR Code",
                            data=base64.b64decode(qr_base64),
                            file_name=f"certificate_qr_{qr_cert['id']}.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"Error generating QR code: {str(e)}")
                else:
                    st.warning("QR code generation not available. Please install the qrcode library.")
                
                if st.button("Close QR Code"):
                    del st.session_state.qr_cert
                    st.rerun()
    
    with col2:
        # Statistics
        st.subheader("📊 Certification Statistics")
        
        completed = len([c for c in st.session_state.certifications if c['status'] == 'Completed'])
        in_progress = len([c for c in st.session_state.certifications if c['status'] == 'In Progress'])
        total = len(st.session_state.certifications)
        
        st.metric("Total Courses", total)
        st.metric("Completed", completed, delta=completed)
        st.metric("In Progress", in_progress)
        st.metric("Completion Rate", f"{(completed/total*100):.1f}%" if total > 0 else "0%")
        
        # Level distribution
        st.subheader("📈 Level Distribution")
        level_counts = {}
        for cert in st.session_state.certifications:
            level = cert['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        if level_counts:
            levels_df = pd.DataFrame.from_dict(level_counts, orient='index', columns=['Count'])
            st.bar_chart(levels_df)
        
        # Recent achievements
        st.subheader("🎯 Recent Achievements")
        recent_completed = [c for c in st.session_state.certifications if c['status'] == 'Completed']
        recent_completed.sort(key=lambda x: x['completion_date'] or datetime.min, reverse=True)
        
        for cert in recent_completed[:3]:
            with st.container():
                st.write(f"🏆 **{cert['course']}**")
                st.caption(f"Completed: {cert['completion_date'].strftime('%Y-%m-%d')} | Score: {cert['score']}%")
                st.markdown("---")
        
        # Badges
        st.subheader("🏅 Achievement Badges")
        
        badges = []
        if completed >= 1:
            badges.append("🌟 First Certificate")
        if completed >= 3:
            badges.append("🚀 Learning Enthusiast")
        if completed >= 5:
            badges.append("🎓 Learning Master")
        if any(c['score'] and c['score'] > 90 for c in st.session_state.certifications):
            badges.append("⭐ Excellence Award")
        
        for badge in badges:
            st.success(badge)
        
        if not badges:
            st.info("Complete courses to earn badges!")

if __name__ == "__main__":
    main()
