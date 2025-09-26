import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "learning_progress.db"

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # User progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            topic_id TEXT NOT NULL,
            progress REAL DEFAULT 0,
            completed_lessons TEXT DEFAULT '[]',
            quiz_scores TEXT DEFAULT '[]',
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            difficulty TEXT,
            UNIQUE(user_id, topic_id)
        )
    ''')
    
    # Quiz results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            topic_id TEXT NOT NULL,
            quiz_data TEXT NOT NULL,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            experience_level TEXT,
            interests TEXT,
            study_goals TEXT,
            preferred_difficulty TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_progress(user_id: str) -> List[Dict]:
    """Get all progress data for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT topic_id, progress, completed_lessons, quiz_scores, 
               last_accessed, difficulty
        FROM user_progress 
        WHERE user_id = ?
        ORDER BY last_accessed DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    progress_data = []
    for row in results:
        progress_data.append({
            'topic_id': row[0],
            'progress': row[1],
            'completed_lessons': json.loads(row[2]),
            'quiz_scores': json.loads(row[3]),
            'last_accessed': row[4],
            'difficulty': row[5]
        })
    
    return progress_data

def update_user_progress(user_id: str, topic_id: str, progress: float, 
                        completed_lessons: List[str] = None, 
                        quiz_score: float = None, difficulty: str = None):
    """Update user progress for a specific topic."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute('''
        SELECT completed_lessons, quiz_scores FROM user_progress 
        WHERE user_id = ? AND topic_id = ?
    ''', (user_id, topic_id))
    
    existing = cursor.fetchone()
    
    if existing:
        current_lessons = json.loads(existing[0])
        current_scores = json.loads(existing[1])
        
        if completed_lessons:
            current_lessons.extend([l for l in completed_lessons if l not in current_lessons])
        
        if quiz_score is not None:
            current_scores.append({
                'score': quiz_score,
                'timestamp': datetime.now().isoformat()
            })
        
        cursor.execute('''
            UPDATE user_progress 
            SET progress = ?, completed_lessons = ?, quiz_scores = ?, 
                last_accessed = CURRENT_TIMESTAMP, difficulty = ?
            WHERE user_id = ? AND topic_id = ?
        ''', (progress, json.dumps(current_lessons), json.dumps(current_scores), 
              difficulty, user_id, topic_id))
    else:
        lessons = json.dumps(completed_lessons or [])
        scores = json.dumps([{'score': quiz_score, 'timestamp': datetime.now().isoformat()}] if quiz_score is not None else [])
        
        cursor.execute('''
            INSERT INTO user_progress 
            (user_id, topic_id, progress, completed_lessons, quiz_scores, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, topic_id, progress, lessons, scores, difficulty))
    
    conn.commit()
    conn.close()

def save_quiz_result(user_id: str, topic_id: str, quiz_data: Dict, 
                    score: float, total_questions: int):
    """Save quiz result to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO quiz_results 
        (user_id, topic_id, quiz_data, score, total_questions)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, topic_id, json.dumps(quiz_data), score, total_questions))
    
    conn.commit()
    conn.close()

def get_quiz_history(user_id: str, topic_id: str = None) -> List[Dict]:
    """Get quiz history for a user, optionally filtered by topic."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if topic_id:
        cursor.execute('''
            SELECT topic_id, score, total_questions, timestamp
            FROM quiz_results 
            WHERE user_id = ? AND topic_id = ?
            ORDER BY timestamp DESC
        ''', (user_id, topic_id))
    else:
        cursor.execute('''
            SELECT topic_id, score, total_questions, timestamp
            FROM quiz_results 
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'topic_id': row[0],
            'score': row[1],
            'total_questions': row[2],
            'timestamp': row[3]
        }
        for row in results
    ]

def save_user_preferences(user_id: str, experience_level: str, 
                         interests: List[str], study_goals: str = None):
    """Save user preferences."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_preferences 
        (user_id, experience_level, interests, study_goals)
        VALUES (?, ?, ?, ?)
    ''', (user_id, experience_level, json.dumps(interests), study_goals))
    
    conn.commit()
    conn.close()

def get_user_preferences(user_id: str) -> Optional[Dict]:
    """Get user preferences."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT experience_level, interests, study_goals
        FROM user_preferences 
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'experience_level': result[0],
            'interests': json.loads(result[1]),
            'study_goals': result[2]
        }
    return None
