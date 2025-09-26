import streamlit as st
import json
from datetime import datetime, timedelta
from database import get_user_progress
from learning_data import get_topic_by_id, get_learning_topics as get_all_topics
import sqlite3

st.set_page_config(page_title="Community", page_icon="👥", layout="wide")

# Database setup for community features
def init_community_database():
    """Initialize community-specific database tables."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    # Discussion topics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id TEXT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0
        )
    ''')
    
    # Discussion replies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discussion_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discussion_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            FOREIGN KEY (discussion_id) REFERENCES discussions (id)
        )
    ''')
    
    # Shared learning paths table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            topics TEXT NOT NULL,
            difficulty TEXT,
            estimated_hours INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            followers INTEGER DEFAULT 0,
            is_public BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Study groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            creator_id TEXT NOT NULL,
            topic_focus TEXT,
            max_members INTEGER DEFAULT 10,
            current_members INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Study group memberships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role TEXT DEFAULT 'member',
            FOREIGN KEY (group_id) REFERENCES study_groups (id),
            UNIQUE(group_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_discussion(topic_id, user_id, title, content, category):
    """Create a new discussion topic."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO discussions (topic_id, user_id, title, content, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic_id, user_id, title, content, category))
    
    discussion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return discussion_id

def get_discussions(topic_id=None, category=None, limit=20):
    """Get discussions with optional filtering."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    query = '''
        SELECT id, topic_id, user_id, title, content, category, 
               created_at, updated_at, likes, replies
        FROM discussions
        WHERE 1=1
    '''
    params = []
    
    if topic_id:
        query += " AND topic_id = ?"
        params.append(topic_id)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    discussions = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0], 'topic_id': row[1], 'user_id': row[2],
            'title': row[3], 'content': row[4], 'category': row[5],
            'created_at': row[6], 'updated_at': row[7],
            'likes': row[8], 'replies': row[9]
        }
        for row in discussions
    ]

def add_discussion_reply(discussion_id, user_id, content):
    """Add a reply to a discussion."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    # Add reply
    cursor.execute('''
        INSERT INTO discussion_replies (discussion_id, user_id, content)
        VALUES (?, ?, ?)
    ''', (discussion_id, user_id, content))
    
    # Update reply count
    cursor.execute('''
        UPDATE discussions 
        SET replies = replies + 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (discussion_id,))
    
    conn.commit()
    conn.close()

def get_discussion_replies(discussion_id):
    """Get replies for a discussion."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, user_id, content, created_at, likes
        FROM discussion_replies
        WHERE discussion_id = ?
        ORDER BY created_at ASC
    ''', (discussion_id,))
    
    replies = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0], 'user_id': row[1], 'content': row[2],
            'created_at': row[3], 'likes': row[4]
        }
        for row in replies
    ]

def create_shared_path(user_id, title, description, topics, difficulty, estimated_hours):
    """Create a shared learning path."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO shared_paths 
        (user_id, title, description, topics, difficulty, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, description, json.dumps(topics), difficulty, estimated_hours))
    
    path_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return path_id

def get_shared_paths(limit=20):
    """Get shared learning paths."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, user_id, title, description, topics, difficulty, 
               estimated_hours, created_at, likes, followers
        FROM shared_paths
        WHERE is_public = TRUE
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    paths = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0], 'user_id': row[1], 'title': row[2],
            'description': row[3], 'topics': json.loads(row[4]),
            'difficulty': row[5], 'estimated_hours': row[6],
            'created_at': row[7], 'likes': row[8], 'followers': row[9]
        }
        for row in paths
    ]

def create_study_group(name, description, creator_id, topic_focus, max_members=10):
    """Create a new study group."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    # Create group
    cursor.execute('''
        INSERT INTO study_groups 
        (name, description, creator_id, topic_focus, max_members)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, description, creator_id, topic_focus, max_members))
    
    group_id = cursor.lastrowid
    
    # Add creator as member
    cursor.execute('''
        INSERT INTO study_group_members (group_id, user_id, role)
        VALUES (?, ?, 'creator')
    ''', (group_id, creator_id))
    
    conn.commit()
    conn.close()
    
    return group_id

def get_study_groups(topic_focus=None, limit=20):
    """Get available study groups."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    query = '''
        SELECT id, name, description, creator_id, topic_focus, 
               max_members, current_members, created_at, is_active
        FROM study_groups
        WHERE is_active = TRUE
    '''
    params = []
    
    if topic_focus:
        query += " AND topic_focus = ?"
        params.append(topic_focus)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    groups = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0], 'name': row[1], 'description': row[2],
            'creator_id': row[3], 'topic_focus': row[4],
            'max_members': row[5], 'current_members': row[6],
            'created_at': row[7], 'is_active': row[8]
        }
        for row in groups
    ]

def main():
    st.title("👥 Learning Community")
    st.markdown("Connect with fellow learners, share knowledge, and grow together!")
    
    # Initialize community database
    init_community_database()
    
    # Sidebar for community navigation
    with st.sidebar:
        st.header("🌟 Community Features")
        
        community_section = st.selectbox(
            "Select Section",
            ["📝 Discussions", "🛤️ Shared Learning Paths", "👥 Study Groups", "🏆 Leaderboards"]
        )
        
        st.markdown("---")
        
        # User's community stats
        if 'user_id' in st.session_state:
            st.subheader("📊 Your Activity")
            
            # Get user's discussions and contributions
            user_discussions = get_discussions(limit=100)
            user_posts = len([d for d in user_discussions if d['user_id'] == st.session_state.user_id])
            
            st.metric("Discussions Created", user_posts)
            st.metric("Community Points", user_posts * 10 + 50)  # Simple point system
            
            # Progress badge
            if user_posts >= 10:
                st.success("🏆 Community Expert")
            elif user_posts >= 5:
                st.info("🌟 Active Contributor")
            elif user_posts >= 1:
                st.info("🌱 Community Member")
            else:
                st.info("👋 Welcome to Community!")
    
    # Main content based on selected section
    if community_section == "📝 Discussions":
        st.subheader("💬 Community Discussions")
        
        # Create new discussion
        with st.expander("✏️ Start a New Discussion"):
            if 'user_id' not in st.session_state:
                st.warning("Please set up your profile in the main dashboard to participate in discussions.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    discussion_title = st.text_input("Discussion Title")
                    topics = get_all_topics()
                    topic_options = {f"{topic['title']}": topic['id'] for topic in topics}
                    selected_topic = st.selectbox("Related Topic (Optional)", ["General"] + list(topic_options.keys()))
                
                with col2:
                    category = st.selectbox(
                        "Category",
                        ["Question", "Discussion", "Study Tips", "Project Showcase", "Career Advice"]
                    )
                
                discussion_content = st.text_area("Your message", height=100)
                
                if st.button("🚀 Post Discussion"):
                    if discussion_title and discussion_content:
                        topic_id = topic_options.get(selected_topic) if selected_topic != "General" else None
                        
                        discussion_id = create_discussion(
                            topic_id,
                            st.session_state.user_id,
                            discussion_title,
                            discussion_content,
                            category
                        )
                        
                        st.success("Discussion created successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in both title and content.")
        
        # Filter discussions
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox("Filter by Category", 
                ["All", "Question", "Discussion", "Study Tips", "Project Showcase", "Career Advice"])
        with col2:
            topics = get_all_topics()
            topic_filter_options = {f"{topic['title']}": topic['id'] for topic in topics}
            filter_topic = st.selectbox("Filter by Topic", ["All"] + list(topic_filter_options.keys()))
        
        # Get and display discussions
        category_filter = None if filter_category == "All" else filter_category
        topic_filter_id = None if filter_topic == "All" else topic_filter_options.get(filter_topic)
        
        discussions = get_discussions(topic_id=topic_filter_id, category=category_filter)
        
        if discussions:
            for discussion in discussions:
                with st.expander(f"💬 {discussion['title']} | {discussion['category']} | {discussion['likes']} ❤️"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**By:** {discussion['user_id']}")
                        st.markdown(f"**Posted:** {discussion['created_at'][:16]}")
                        if discussion['topic_id']:
                            topic = get_topic_by_id(discussion['topic_id'])
                            if topic:
                                st.markdown(f"**Topic:** {topic['title']}")
                    
                    with col2:
                        st.markdown(f"**Replies:** {discussion['replies']}")
                        st.markdown(f"**Likes:** {discussion['likes']}")
                    
                    with col3:
                        if st.button("👍 Like", key=f"like_{discussion['id']}"):
                            # Increment likes (simplified)
                            conn = sqlite3.connect("learning_progress.db")
                            cursor = conn.cursor()
                            cursor.execute('UPDATE discussions SET likes = likes + 1 WHERE id = ?', (discussion['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    
                    st.markdown("---")
                    st.markdown(discussion['content'])
                    
                    # Replies section
                    st.markdown("**💬 Replies:**")
                    replies = get_discussion_replies(discussion['id'])
                    
                    if replies:
                        for reply in replies:
                            st.markdown(f"**{reply['user_id']}** *({reply['created_at'][:16]})*:")
                            st.markdown(f"> {reply['content']}")
                            st.markdown("")
                    
                    # Add reply
                    if 'user_id' in st.session_state:
                        reply_content = st.text_area("Add a reply", key=f"reply_{discussion['id']}", height=80)
                        if st.button("💬 Reply", key=f"submit_reply_{discussion['id']}"):
                            if reply_content:
                                add_discussion_reply(discussion['id'], st.session_state.user_id, reply_content)
                                st.success("Reply added!")
                                st.rerun()
        else:
            st.info("No discussions found. Be the first to start a conversation!")
    
    elif community_section == "🛤️ Shared Learning Paths":
        st.subheader("🗺️ Community Learning Paths")
        
        # Create new learning path
        with st.expander("🎯 Share Your Learning Path"):
            if 'user_id' not in st.session_state:
                st.warning("Please set up your profile to share learning paths.")
            else:
                path_title = st.text_input("Path Title")
                path_description = st.text_area("Description")
                
                col1, col2 = st.columns(2)
                with col1:
                    difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
                with col2:
                    estimated_hours = st.number_input("Estimated Hours", min_value=1, max_value=200, value=20)
                
                # Topic selection
                all_topics = get_all_topics()
                selected_topics = st.multiselect(
                    "Select Topics for Your Path",
                    options=[topic['id'] for topic in all_topics],
                    format_func=lambda x: next(topic['title'] for topic in all_topics if topic['id'] == x)
                )
                
                if st.button("📤 Share Learning Path"):
                    if path_title and path_description and selected_topics:
                        path_id = create_shared_path(
                            st.session_state.user_id,
                            path_title,
                            path_description,
                            selected_topics,
                            difficulty,
                            estimated_hours
                        )
                        st.success("Learning path shared successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields.")
        
        # Display shared paths
        shared_paths = get_shared_paths()
        
        if shared_paths:
            for path in shared_paths:
                with st.expander(f"🛤️ {path['title']} | {path['difficulty']} | {path['estimated_hours']}h"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Created by:** {path['user_id']}")
                        st.markdown(f"**Description:** {path['description']}")
                        st.markdown(f"**Difficulty:** {path['difficulty']}")
                        st.markdown(f"**Estimated Time:** {path['estimated_hours']} hours")
                        
                        # Display topics in path
                        st.markdown("**Topics in this path:**")
                        for topic_id in path['topics']:
                            topic = get_topic_by_id(topic_id)
                            if topic:
                                st.markdown(f"• {topic['title']} ({topic['difficulty']})")
                    
                    with col2:
                        st.metric("Likes", path['likes'])
                        st.metric("Followers", path['followers'])
                        
                        if st.button("⭐ Follow Path", key=f"follow_{path['id']}"):
                            # Increment followers (simplified)
                            conn = sqlite3.connect("learning_progress.db")
                            cursor = conn.cursor()
                            cursor.execute('UPDATE shared_paths SET followers = followers + 1 WHERE id = ?', (path['id'],))
                            conn.commit()
                            conn.close()
                            st.success("Following this learning path!")
                            st.rerun()
                        
                        if st.button("👍 Like", key=f"like_path_{path['id']}"):
                            # Increment likes (simplified)
                            conn = sqlite3.connect("learning_progress.db")
                            cursor = conn.cursor()
                            cursor.execute('UPDATE shared_paths SET likes = likes + 1 WHERE id = ?', (path['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
        else:
            st.info("No shared learning paths yet. Be the first to share your learning journey!")
    
    elif community_section == "👥 Study Groups":
        st.subheader("📚 Study Groups")
        
        # Create new study group
        with st.expander("➕ Create Study Group"):
            if 'user_id' not in st.session_state:
                st.warning("Please set up your profile to create study groups.")
            else:
                group_name = st.text_input("Group Name")
                group_description = st.text_area("Description")
                
                col1, col2 = st.columns(2)
                with col1:
                    all_topics = get_all_topics()
                    topic_focus = st.selectbox(
                        "Focus Topic",
                        options=[topic['category'] for topic in all_topics],
                        help="Main topic area for this study group"
                    )
                with col2:
                    max_members = st.number_input("Max Members", min_value=2, max_value=50, value=10)
                
                if st.button("🏗️ Create Group"):
                    if group_name and group_description:
                        group_id = create_study_group(
                            group_name,
                            group_description,
                            st.session_state.user_id,
                            topic_focus,
                            max_members
                        )
                        st.success("Study group created successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields.")
        
        # Display study groups
        study_groups = get_study_groups()
        
        if study_groups:
            for group in study_groups:
                with st.expander(f"👥 {group['name']} | {group['topic_focus']} | {group['current_members']}/{group['max_members']} members"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {group['description']}")
                        st.markdown(f"**Focus Area:** {group['topic_focus']}")
                        st.markdown(f"**Created:** {group['created_at'][:10]}")
                        st.markdown(f"**Creator:** {group['creator_id']}")
                    
                    with col2:
                        st.metric("Members", f"{group['current_members']}/{group['max_members']}")
                        
                        if group['current_members'] < group['max_members']:
                            if st.button("🤝 Join Group", key=f"join_{group['id']}"):
                                # Add member (simplified)
                                conn = sqlite3.connect("learning_progress.db")
                                cursor = conn.cursor()
                                try:
                                    cursor.execute('''
                                        INSERT INTO study_group_members (group_id, user_id)
                                        VALUES (?, ?)
                                    ''', (group['id'], st.session_state.get('user_id', 'anonymous')))
                                    cursor.execute('''
                                        UPDATE study_groups 
                                        SET current_members = current_members + 1 
                                        WHERE id = ?
                                    ''', (group['id'],))
                                    conn.commit()
                                    st.success("Joined study group!")
                                    st.rerun()
                                except:
                                    st.info("You're already a member of this group!")
                                finally:
                                    conn.close()
                        else:
                            st.info("Group is full")
        else:
            st.info("No study groups yet. Create the first one!")
    
    elif community_section == "🏆 Leaderboards":
        st.subheader("🏅 Community Leaderboards")
        
        # Learning progress leaderboard
        st.markdown("### 📊 Learning Progress Leaders")
        
        # This would show top learners by various metrics
        # For now, showing mock data
        leaderboard_data = [
            {"rank": 1, "user": "Alex_ML", "completed_topics": 15, "quiz_avg": 92.5, "community_points": 450},
            {"rank": 2, "user": "DataScientist99", "completed_topics": 12, "quiz_avg": 89.2, "community_points": 380},
            {"rank": 3, "user": "AI_Enthusiast", "completed_topics": 10, "quiz_avg": 95.1, "community_points": 320},
            {"rank": 4, "user": "CodeNewbie", "completed_topics": 8, "quiz_avg": 78.3, "community_points": 280},
            {"rank": 5, "user": "MLExplorer", "completed_topics": 9, "quiz_avg": 86.7, "community_points": 250},
        ]
        
        for entry in leaderboard_data:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
            
            with col1:
                if entry["rank"] == 1:
                    st.markdown("🥇")
                elif entry["rank"] == 2:
                    st.markdown("🥈")
                elif entry["rank"] == 3:
                    st.markdown("🥉")
                else:
                    st.markdown(f"#{entry['rank']}")
            
            with col2:
                st.markdown(f"**{entry['user']}**")
            
            with col3:
                st.markdown(f"📚 {entry['completed_topics']} topics")
            
            with col4:
                st.markdown(f"🧠 {entry['quiz_avg']:.1f}% avg")
            
            with col5:
                st.markdown(f"⭐ {entry['community_points']} pts")
        
        st.markdown("---")
        
        # Weekly challenges
        st.markdown("### 🎯 Weekly Community Challenges")
        
        challenges = [
            {
                "title": "Quiz Master Challenge",
                "description": "Complete 5 quizzes with 85%+ average score",
                "reward": "50 community points + Quiz Master badge",
                "participants": 23,
                "time_left": "3 days"
            },
            {
                "title": "Discussion Starter",
                "description": "Start 3 meaningful discussions this week",
                "reward": "30 community points + Community Leader badge",
                "participants": 15,
                "time_left": "5 days"
            },
            {
                "title": "Learning Streak",
                "description": "Study for 7 consecutive days",
                "reward": "40 community points + Dedicated Learner badge",
                "participants": 31,
                "time_left": "6 days"
            }
        ]
        
        for challenge in challenges:
            with st.expander(f"🎯 {challenge['title']} | {challenge['participants']} participants"):
                st.markdown(f"**Goal:** {challenge['description']}")
                st.markdown(f"**Reward:** {challenge['reward']}")
                st.markdown(f"**Time Left:** {challenge['time_left']}")
                
                if st.button("🚀 Join Challenge", key=f"challenge_{challenge['title']}"):
                    st.success("Challenge accepted! Good luck! 🍀")

if __name__ == "__main__":
    main()