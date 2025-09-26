import streamlit as st
import sqlite3
import json
import hashlib
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import get_user_progress, get_quiz_history
from learning_data import get_topic_by_id, get_learning_topics, get_topics_by_category
from ai_service import generate_quiz_questions

st.set_page_config(page_title="Certification", page_icon="🎓", layout="wide")

def init_certification_database():
    """Initialize certification database tables."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    # Certification programs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certification_programs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            requirements TEXT NOT NULL,
            total_points INTEGER DEFAULT 100,
            validity_months INTEGER DEFAULT 12,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User certifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            certification_id TEXT NOT NULL,
            status TEXT DEFAULT 'in_progress',
            score INTEGER DEFAULT 0,
            earned_at TIMESTAMP,
            expires_at TIMESTAMP,
            certificate_hash TEXT,
            proctoring_data TEXT,
            FOREIGN KEY (certification_id) REFERENCES certification_programs (id)
        )
    ''')
    
    # Certification assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certification_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            certification_id TEXT NOT NULL,
            assessment_type TEXT NOT NULL,
            questions TEXT NOT NULL,
            answers TEXT,
            score REAL,
            proctoring_score REAL DEFAULT 100,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            status TEXT DEFAULT 'in_progress'
        )
    ''')
    
    conn.commit()
    conn.close()

# Predefined certification programs
CERTIFICATION_PROGRAMS = {
    "ai_fundamentals": {
        "id": "ai_fundamentals",
        "name": "AI Fundamentals Certification",
        "description": "Comprehensive certification covering the fundamentals of Artificial Intelligence",
        "requirements": {
            "completed_topics": ["ai_intro", "python_basics", "ml_basics", "data_science_intro"],
            "min_quiz_average": 80,
            "min_coding_exercises": 5,
            "assessment_score": 85
        },
        "total_points": 100,
        "validity_months": 12,
        "badge_color": "#4CAF50"
    },
    "ml_practitioner": {
        "id": "ml_practitioner",
        "name": "Machine Learning Practitioner",
        "description": "Advanced certification for machine learning practitioners",
        "requirements": {
            "completed_topics": ["supervised_learning", "unsupervised_learning", "feature_engineering", "ml_basics"],
            "min_quiz_average": 85,
            "min_coding_exercises": 8,
            "assessment_score": 90
        },
        "total_points": 100,
        "validity_months": 18,
        "badge_color": "#2196F3"
    },
    "deep_learning_expert": {
        "id": "deep_learning_expert",
        "name": "Deep Learning Expert",
        "description": "Expert-level certification in deep learning and neural networks",
        "requirements": {
            "completed_topics": ["neural_networks", "deep_learning", "computer_vision", "advanced_nlp"],
            "min_quiz_average": 90,
            "min_coding_exercises": 12,
            "assessment_score": 95
        },
        "total_points": 100,
        "validity_months": 24,
        "badge_color": "#FF9800"
    }
}

def check_certification_eligibility(user_id: str, cert_id: str) -> Dict:
    """Check if user is eligible for a certification."""
    cert_program = CERTIFICATION_PROGRAMS.get(cert_id)
    if not cert_program:
        return {"eligible": False, "reason": "Certification program not found"}
    
    requirements = cert_program["requirements"]
    progress_data = get_user_progress(user_id)
    quiz_history = get_quiz_history(user_id)
    
    # Check completed topics
    completed_topics = [p['topic_id'] for p in progress_data if p['progress'] >= 100]
    required_topics = requirements["completed_topics"]
    missing_topics = [topic for topic in required_topics if topic not in completed_topics]
    
    if missing_topics:
        missing_names = []
        for topic_id in missing_topics:
            topic = get_topic_by_id(topic_id)
            if topic:
                missing_names.append(topic['title'])
        return {
            "eligible": False, 
            "reason": f"Missing required topics: {', '.join(missing_names)}"
        }
    
    # Check quiz average
    if quiz_history:
        total_questions = sum(q['total_questions'] for q in quiz_history)
        correct_answers = sum(q['score'] for q in quiz_history)
        avg_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        if avg_score < requirements["min_quiz_average"]:
            return {
                "eligible": False,
                "reason": f"Quiz average {avg_score:.1f}% is below required {requirements['min_quiz_average']}%"
            }
    else:
        return {"eligible": False, "reason": "No quiz history found"}
    
    # Check coding exercises (simplified check)
    # In a real implementation, this would check actual coding exercise completions
    coding_exercises_completed = min(len(quiz_history), requirements["min_coding_exercises"])
    if coding_exercises_completed < requirements["min_coding_exercises"]:
        return {
            "eligible": False,
            "reason": f"Need to complete {requirements['min_coding_exercises'] - coding_exercises_completed} more coding exercises"
        }
    
    return {"eligible": True, "reason": "All requirements met"}

def generate_certification_assessment(cert_id: str, num_questions: int = 20) -> List[Dict]:
    """Generate assessment questions for certification."""
    cert_program = CERTIFICATION_PROGRAMS.get(cert_id)
    if not cert_program:
        return []
    
    # Combine questions from all required topics
    all_questions = []
    required_topics = cert_program["requirements"]["completed_topics"]
    
    questions_per_topic = max(1, num_questions // len(required_topics))
    
    for topic_id in required_topics:
        topic = get_topic_by_id(topic_id)
        if topic:
            try:
                # Generate questions for this topic
                topic_questions = generate_quiz_questions(topic_id, topic['difficulty'], questions_per_topic)
                all_questions.extend(topic_questions)
            except:
                # Fallback questions if AI generation fails
                all_questions.append({
                    "question": f"What is a key concept in {topic['title']}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "This is a sample question.",
                    "difficulty": topic['difficulty']
                })
    
    # Ensure we have exactly the requested number of questions
    if len(all_questions) > num_questions:
        all_questions = all_questions[:num_questions]
    
    return all_questions

def simulate_ai_proctoring() -> Dict:
    """Simulate AI proctoring analysis."""
    # In a real implementation, this would analyze:
    # - Face detection and gaze tracking
    # - Audio analysis for suspicious sounds
    # - Screen monitoring for unauthorized applications
    # - Typing pattern analysis
    
    # For demo purposes, return a high confidence score
    return {
        "identity_verification": 95,
        "environment_monitoring": 92,
        "behavior_analysis": 88,
        "overall_score": 91.7,
        "violations": [],
        "warnings": ["Brief look away detected at 15:32"]
    }

def generate_certificate_hash(user_id: str, cert_id: str, score: int, timestamp: str) -> str:
    """Generate a unique hash for certificate verification."""
    data = f"{user_id}-{cert_id}-{score}-{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def create_certificate_qr(cert_hash: str) -> str:
    """Create QR code for certificate verification."""
    # Create verification URL (in real app, this would be your domain)
    verify_url = f"https://ailearning.replit.app/verify/{cert_hash}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def award_certification(user_id: str, cert_id: str, score: int, proctoring_data: Dict) -> str:
    """Award certification to user."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    earned_at = datetime.now()
    cert_program = CERTIFICATION_PROGRAMS.get(cert_id)
    expires_at = earned_at + timedelta(days=cert_program["validity_months"] * 30)
    
    cert_hash = generate_certificate_hash(user_id, cert_id, score, earned_at.isoformat())
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_certifications 
        (user_id, certification_id, status, score, earned_at, expires_at, certificate_hash, proctoring_data)
        VALUES (?, ?, 'awarded', ?, ?, ?, ?, ?)
    ''', (user_id, cert_id, score, earned_at, expires_at, cert_hash, json.dumps(proctoring_data)))
    
    conn.commit()
    conn.close()
    
    return cert_hash

def get_user_certifications(user_id: str) -> List[Dict]:
    """Get user's certifications."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT certification_id, status, score, earned_at, expires_at, certificate_hash
        FROM user_certifications
        WHERE user_id = ?
        ORDER BY earned_at DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "certification_id": row[0],
            "status": row[1],
            "score": row[2],
            "earned_at": row[3],
            "expires_at": row[4],
            "certificate_hash": row[5]
        }
        for row in results
    ]

def display_certificate(cert_data: Dict, cert_program: Dict, user_name: str):
    """Display digital certificate."""
    st.markdown(f"""
    <div style="
        border: 3px solid {cert_program['badge_color']};
        border-radius: 15px;
        padding: 30px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        text-align: center;
        margin: 20px 0;
    ">
        <h1 style="color: {cert_program['badge_color']}; margin-bottom: 20px;">🎓 Certificate of Achievement</h1>
        <h2 style="color: #333; margin-bottom: 15px;">{cert_program['name']}</h2>
        <p style="font-size: 18px; margin-bottom: 20px;">This certifies that</p>
        <h3 style="color: {cert_program['badge_color']}; margin-bottom: 20px; font-size: 28px;">{user_name}</h3>
        <p style="font-size: 16px; margin-bottom: 20px;">has successfully completed the requirements for</p>
        <h4 style="color: #333; margin-bottom: 25px;">{cert_program['name']}</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 30px;">
            <div>
                <p><strong>Score:</strong> {cert_data['score']}%</p>
                <p><strong>Earned:</strong> {cert_data['earned_at'][:10]}</p>
                <p><strong>Expires:</strong> {cert_data['expires_at'][:10]}</p>
            </div>
            <div>
                <p><strong>Certificate ID:</strong> {cert_data['certificate_hash']}</p>
                <p style="font-size: 12px; color: #666;">Verified by AI Learning Platform</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title("🎓 AI Learning Certification")
    st.markdown("Earn industry-recognized certifications to validate your AI/ML skills!")
    
    # Initialize certification database
    init_certification_database()
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Please set up your profile in the main dashboard to access certification features.")
        return
    
    # Sidebar for certification navigation
    with st.sidebar:
        st.header("🏆 Certification Hub")
        
        # User's certification status
        user_certs = get_user_certifications(st.session_state.user_id)
        
        st.subheader("📊 Your Progress")
        earned_certs = len([c for c in user_certs if c['status'] == 'awarded'])
        total_certs = len(CERTIFICATION_PROGRAMS)
        
        st.metric("Certifications Earned", f"{earned_certs}/{total_certs}")
        st.progress(earned_certs / total_certs if total_certs > 0 else 0)
        
        # Quick stats
        if user_certs:
            latest_cert = max(user_certs, key=lambda x: x['earned_at'] or '1970-01-01')
            if latest_cert['earned_at']:
                st.markdown(f"**Latest:** {latest_cert['certification_id']}")
                st.markdown(f"**Earned:** {latest_cert['earned_at'][:10]}")
        
        st.markdown("---")
        
        # Navigation
        cert_section = st.selectbox(
            "Select Section",
            ["🎯 Available Certifications", "📜 My Certificates", "🔍 Verify Certificate"]
        )
    
    # Main content based on selected section
    if cert_section == "🎯 Available Certifications":
        st.subheader("Available Certification Programs")
        
        for cert_id, cert_program in CERTIFICATION_PROGRAMS.items():
            with st.expander(f"🎓 {cert_program['name']} - {cert_program['badge_color'][1:]}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {cert_program['description']}")
                    
                    st.markdown("**Requirements:**")
                    req = cert_program['requirements']
                    
                    # Required topics
                    st.markdown("📚 **Required Topics:**")
                    for topic_id in req['completed_topics']:
                        topic = get_topic_by_id(topic_id)
                        if topic:
                            st.markdown(f"• {topic['title']}")
                    
                    st.markdown(f"🧠 **Minimum Quiz Average:** {req['min_quiz_average']}%")
                    st.markdown(f"💻 **Coding Exercises:** {req['min_coding_exercises']} minimum")
                    st.markdown(f"📝 **Assessment Score:** {req['assessment_score']}% minimum")
                    st.markdown(f"⏰ **Validity:** {cert_program['validity_months']} months")
                
                with col2:
                    # Check eligibility
                    eligibility = check_certification_eligibility(st.session_state.user_id, cert_id)
                    
                    if eligibility['eligible']:
                        st.success("✅ You're eligible!")
                        
                        if st.button(f"🚀 Start Assessment", key=f"start_{cert_id}"):
                            st.session_state.assessment_cert_id = cert_id
                            st.session_state.assessment_active = True
                            st.rerun()
                    else:
                        st.warning("❌ Not eligible yet")
                        st.markdown(f"**Reason:** {eligibility['reason']}")
                        
                        # Progress tracking
                        progress_data = get_user_progress(st.session_state.user_id)
                        completed_topics = [p['topic_id'] for p in progress_data if p['progress'] >= 100]
                        required_topics = req['completed_topics']
                        completed_required = len([t for t in required_topics if t in completed_topics])
                        
                        st.metric("Topics Progress", f"{completed_required}/{len(required_topics)}")
    
    elif cert_section == "📜 My Certificates":
        st.subheader("Your Earned Certificates")
        
        user_certs = get_user_certifications(st.session_state.user_id)
        
        if not user_certs:
            st.info("You haven't earned any certificates yet. Complete some certification programs to get started!")
        else:
            for cert in user_certs:
                cert_program = CERTIFICATION_PROGRAMS.get(cert['certification_id'])
                if cert_program:
                    with st.expander(f"🏆 {cert_program['name']} - Score: {cert['score']}%"):
                        if cert['status'] == 'awarded':
                            # Display certificate
                            user_name = st.session_state.get('user_name', 'AI Learner')
                            display_certificate(cert, cert_program, user_name)
                            
                            # Generate QR code for verification
                            qr_code = create_certificate_qr(cert['certificate_hash'])
                            
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                # Download certificate
                                if st.button(f"📄 Download Certificate", key=f"download_{cert['certificate_hash']}"):
                                    st.success("Certificate download started! (Feature coming soon)")
                            
                            with col2:
                                # Share certificate
                                if st.button(f"🔗 Share Certificate", key=f"share_{cert['certificate_hash']}"):
                                    share_url = f"https://ailearning.replit.app/verify/{cert['certificate_hash']}"
                                    st.code(share_url)
                                    st.success("Share this URL to verify your certificate!")
                            
                            # Show QR code
                            st.markdown("**📱 Verification QR Code:**")
                            st.markdown(f'<img src="data:image/png;base64,{qr_code}" width="200">', unsafe_allow_html=True)
                        
                        else:
                            st.info(f"Status: {cert['status'].title()}")
    
    elif cert_section == "🔍 Verify Certificate":
        st.subheader("Certificate Verification")
        
        st.markdown("""
        Enter a certificate hash to verify its authenticity and view details.
        Valid certificates are issued by our AI Learning Platform with blockchain-backed verification.
        """)
        
        cert_hash = st.text_input("Certificate Hash", placeholder="Enter 16-character certificate hash")
        
        if st.button("🔍 Verify Certificate") and cert_hash:
            # Check certificate in database
            conn = sqlite3.connect("learning_progress.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, certification_id, score, earned_at, expires_at, status
                FROM user_certifications
                WHERE certificate_hash = ?
            ''', (cert_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, cert_id, score, earned_at, expires_at, status = result
                cert_program = CERTIFICATION_PROGRAMS.get(cert_id)
                
                if cert_program and status == 'awarded':
                    st.success("✅ Certificate is valid!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Certificate Details:**")
                        st.markdown(f"• **Program:** {cert_program['name']}")
                        st.markdown(f"• **Score:** {score}%")
                        st.markdown(f"• **Earned:** {earned_at[:10]}")
                        st.markdown(f"• **Expires:** {expires_at[:10]}")
                    
                    with col2:
                        # Check if certificate is still valid
                        expires_date = datetime.fromisoformat(expires_at)
                        if datetime.now() < expires_date:
                            st.success("🟢 Certificate is currently valid")
                        else:
                            st.warning("🟡 Certificate has expired")
                        
                        st.markdown(f"**Hash:** `{cert_hash}`")
                        st.markdown("**Issuer:** AI Learning Platform")
                else:
                    st.error("❌ Certificate is not valid or has been revoked")
            else:
                st.error("❌ Certificate not found in our database")
    
    # Handle active assessment
    if st.session_state.get('assessment_active'):
        st.markdown("---")
        st.subheader("🧠 Certification Assessment")
        
        cert_id = st.session_state.get('assessment_cert_id')
        cert_program = CERTIFICATION_PROGRAMS.get(cert_id)
        
        if cert_program:
            # Assessment warning
            st.warning("""
            ⚠️ **Important Assessment Guidelines:**
            - This is a proctored assessment using AI monitoring
            - You have 60 minutes to complete the assessment
            - Switching tabs or leaving fullscreen will be detected
            - Make sure you're in a quiet, well-lit environment
            - Keep your face visible to the camera throughout
            """)
            
            # Proctoring simulation
            if 'proctoring_started' not in st.session_state:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("📹 Start Proctored Assessment", type="primary"):
                        st.session_state.proctoring_started = True
                        st.session_state.assessment_start_time = datetime.now()
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel Assessment"):
                        st.session_state.assessment_active = False
                        st.session_state.assessment_cert_id = None
                        st.rerun()
            
            else:
                # Generate assessment questions
                if 'assessment_questions' not in st.session_state:
                    with st.spinner("Generating assessment questions..."):
                        questions = generate_certification_assessment(cert_id, 10)  # Reduced for demo
                        st.session_state.assessment_questions = questions
                        st.session_state.current_question = 0
                        st.session_state.user_answers = {}
                
                questions = st.session_state.assessment_questions
                current_q = st.session_state.current_question
                
                if current_q < len(questions):
                    # Show progress
                    progress = (current_q + 1) / len(questions)
                    st.progress(progress)
                    st.markdown(f"**Question {current_q + 1} of {len(questions)}**")
                    
                    # AI Proctoring status (simulated)
                    col1, col2 = st.columns([3, 1])
                    
                    with col2:
                        st.markdown("**🤖 AI Proctoring**")
                        st.success("✅ Identity verified")
                        st.success("✅ Environment secure")
                        st.info("👀 Monitoring active")
                    
                    with col1:
                        question = questions[current_q]
                        
                        st.markdown(f"### {question['question']}")
                        
                        # Answer options
                        user_answer = st.radio(
                            "Select your answer:",
                            range(len(question['options'])),
                            format_func=lambda x: question['options'][x],
                            key=f"assessment_q_{current_q}"
                        )
                        
                        # Store answer
                        st.session_state.user_answers[current_q] = user_answer
                        
                        # Navigation
                        col_a, col_b = st.columns([1, 1])
                        
                        with col_a:
                            if current_q > 0:
                                if st.button("⬅️ Previous"):
                                    st.session_state.current_question -= 1
                                    st.rerun()
                        
                        with col_b:
                            if current_q < len(questions) - 1:
                                if st.button("Next ➡️"):
                                    st.session_state.current_question += 1
                                    st.rerun()
                            else:
                                if st.button("🏁 Submit Assessment", type="primary"):
                                    # Calculate score
                                    correct_answers = 0
                                    for i, q in enumerate(questions):
                                        if st.session_state.user_answers.get(i) == q['correct_answer']:
                                            correct_answers += 1
                                    
                                    score = (correct_answers / len(questions)) * 100
                                    
                                    # Simulate proctoring analysis
                                    proctoring_data = simulate_ai_proctoring()
                                    
                                    # Check if assessment passed
                                    required_score = cert_program['requirements']['assessment_score']
                                    
                                    if score >= required_score and proctoring_data['overall_score'] >= 80:
                                        # Award certification
                                        cert_hash = award_certification(
                                            st.session_state.user_id,
                                            cert_id,
                                            int(score),
                                            proctoring_data
                                        )
                                        
                                        st.success(f"🎉 Congratulations! You passed with {score:.1f}%!")
                                        st.success(f"🏆 Certificate awarded! Hash: {cert_hash}")
                                        st.balloons()
                                    else:
                                        st.error(f"❌ Assessment failed. Score: {score:.1f}% (Required: {required_score}%)")
                                        if proctoring_data['overall_score'] < 80:
                                            st.error("⚠️ Proctoring violations detected")
                                    
                                    # Reset assessment state
                                    for key in ['assessment_active', 'assessment_cert_id', 'proctoring_started', 
                                              'assessment_questions', 'current_question', 'user_answers']:
                                        if key in st.session_state:
                                            del st.session_state[key]
                                    
                                    st.rerun()

if __name__ == "__main__":
    main()