import streamlit as st
import sqlite3
import json
import io
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Any
from database import get_user_progress, update_user_progress
from learning_data import get_topic_by_id, get_learning_topics
from ai_service import generate_quiz_questions

st.set_page_config(page_title="Coding Exercises", page_icon="💻", layout="wide")

# Sample coding exercises data
CODING_EXERCISES = {
    "python_basics": [
        {
            "id": "hello_world",
            "title": "Hello World",
            "difficulty": "Beginner",
            "description": "Write a function that returns 'Hello, World!'",
            "starter_code": "def hello_world():\n    # Write your code here\n    pass",
            "solution": "def hello_world():\n    return 'Hello, World!'",
            "test_cases": [
                {"input": [], "expected": "Hello, World!", "description": "Should return 'Hello, World!'"}
            ],
            "hints": [
                "Use the return statement to return a string",
                "The string should be exactly 'Hello, World!'"
            ]
        },
        {
            "id": "calculator",
            "title": "Simple Calculator",
            "difficulty": "Beginner",
            "description": "Write functions for basic arithmetic operations",
            "starter_code": """def add(a, b):\n    # Write your code here\n    pass\n\ndef subtract(a, b):\n    # Write your code here\n    pass\n\ndef multiply(a, b):\n    # Write your code here\n    pass\n\ndef divide(a, b):\n    # Write your code here\n    pass""",
            "solution": """def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    else:\n        return None""",
            "test_cases": [
                {"input": [5, 3], "expected": 8, "description": "add(5, 3) should return 8", "function": "add"},
                {"input": [10, 4], "expected": 6, "description": "subtract(10, 4) should return 6", "function": "subtract"},
                {"input": [3, 7], "expected": 21, "description": "multiply(3, 7) should return 21", "function": "multiply"},
                {"input": [15, 3], "expected": 5, "description": "divide(15, 3) should return 5", "function": "divide"}
            ],
            "hints": [
                "Use basic arithmetic operators: +, -, *, /",
                "Be careful with division by zero",
                "Return None for division by zero"
            ]
        }
    ],
    "ml_basics": [
        {
            "id": "linear_regression",
            "title": "Simple Linear Regression",
            "difficulty": "Intermediate",
            "description": "Implement a simple linear regression from scratch",
            "starter_code": """import numpy as np\n\ndef linear_regression(X, y):\n    \"\"\"\n    Implement simple linear regression\n    X: input features (1D array)\n    y: target values (1D array)\n    Returns: slope, intercept\n    \"\"\"\n    # Calculate slope and intercept\n    # Hint: slope = cov(X,y) / var(X)\n    # intercept = mean(y) - slope * mean(X)\n    pass""",
            "solution": """import numpy as np\n\ndef linear_regression(X, y):\n    X_mean = np.mean(X)\n    y_mean = np.mean(y)\n    \n    # Calculate slope\n    numerator = np.sum((X - X_mean) * (y - y_mean))\n    denominator = np.sum((X - X_mean) ** 2)\n    slope = numerator / denominator\n    \n    # Calculate intercept\n    intercept = y_mean - slope * X_mean\n    \n    return slope, intercept""",
            "test_cases": [
                {
                    "input": [[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]], 
                    "expected": (2.0, 0.0), 
                    "description": "Perfect linear relationship should give slope=2, intercept=0"
                }
            ],
            "hints": [
                "Use numpy functions for mathematical operations",
                "Remember the formula: slope = Σ((x-x̄)(y-ȳ)) / Σ((x-x̄)²)",
                "Intercept = ȳ - slope * x̄"
            ]
        }
    ],
    "data_science": [
        {
            "id": "data_cleaning",
            "title": "Data Cleaning",
            "difficulty": "Intermediate",
            "description": "Clean a dataset by handling missing values and outliers",
            "starter_code": """import pandas as pd\nimport numpy as np\n\ndef clean_data(df):\n    \"\"\"\n    Clean the dataset:\n    1. Remove rows with more than 50% missing values\n    2. Fill numeric columns missing values with median\n    3. Fill categorical columns missing values with mode\n    4. Remove outliers (values > 3 standard deviations from mean)\n    \"\"\"\n    # Your code here\n    pass""",
            "solution": """import pandas as pd\nimport numpy as np\n\ndef clean_data(df):\n    # Remove rows with more than 50% missing values\n    threshold = len(df.columns) * 0.5\n    df = df.dropna(thresh=threshold)\n    \n    # Handle missing values\n    for column in df.columns:\n        if df[column].dtype in ['int64', 'float64']:\n            # Fill numeric columns with median\n            df[column].fillna(df[column].median(), inplace=True)\n        else:\n            # Fill categorical columns with mode\n            mode_value = df[column].mode()\n            if not mode_value.empty:\n                df[column].fillna(mode_value[0], inplace=True)\n    \n    # Remove outliers for numeric columns\n    for column in df.select_dtypes(include=[np.number]).columns:\n        mean = df[column].mean()\n        std = df[column].std()\n        df = df[abs(df[column] - mean) <= 3 * std]\n    \n    return df""",
            "test_cases": [
                {
                    "input": "sample_dataframe", 
                    "expected": "cleaned_dataframe", 
                    "description": "Should clean data according to specifications"
                }
            ],
            "hints": [
                "Use pandas dropna() with thresh parameter",
                "Use fillna() method with median() and mode()",
                "Calculate outliers using mean ± 3*standard_deviation"
            ]
        }
    ]
}

def init_coding_exercises_database():
    """Initialize database for coding exercises."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    # Coding exercise submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coding_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            code TEXT NOT NULL,
            status TEXT NOT NULL,
            test_results TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time REAL
        )
    ''')
    
    # Exercise progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            attempts INTEGER DEFAULT 0,
            best_score REAL DEFAULT 0,
            last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, exercise_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def execute_code(code: str, exercise: Dict) -> Dict:
    """Execute code in a safe environment and return results."""
    result = {
        "success": False,
        "output": "",
        "error": "",
        "test_results": []
    }
    
    # Capture output
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        # Create a restricted environment
        exec_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "sum": sum,
                "abs": abs,
                "min": min,
                "max": max,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set
            },
            "numpy": __import__("numpy") if "numpy" in code else None,
            "np": __import__("numpy") if "np" in code else None,
            "pandas": __import__("pandas") if "pandas" in code else None,
            "pd": __import__("pandas") if "pd" in code else None
        }
        
        # Execute the code
        exec(code, exec_globals)
        
        # Run test cases
        for test_case in exercise.get("test_cases", []):
            try:
                if "function" in test_case:
                    # Test specific function
                    func_name = test_case["function"]
                    if func_name in exec_globals:
                        func = exec_globals[func_name]
                        actual_result = func(*test_case["input"])
                    else:
                        raise NameError(f"Function '{func_name}' not found")
                else:
                    # Test main function (usually the first function defined)
                    func_names = [name for name in exec_globals if callable(exec_globals.get(name)) and not name.startswith('_')]
                    if func_names:
                        func = exec_globals[func_names[0]]
                        actual_result = func(*test_case["input"])
                    else:
                        raise NameError("No function found to test")
                
                expected = test_case["expected"]
                passed = actual_result == expected
                
                result["test_results"].append({
                    "description": test_case["description"],
                    "passed": passed,
                    "expected": expected,
                    "actual": actual_result
                })
                
            except Exception as e:
                result["test_results"].append({
                    "description": test_case["description"],
                    "passed": False,
                    "expected": test_case["expected"],
                    "actual": f"Error: {str(e)}"
                })
        
        result["success"] = True
        result["output"] = stdout_capture.getvalue()
        
    except Exception as e:
        result["error"] = str(e)
        result["output"] = stdout_capture.getvalue()
        
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return result

def save_submission(user_id: str, exercise_id: str, code: str, result: Dict):
    """Save code submission to database."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    status = "passed" if result["success"] and all(t["passed"] for t in result["test_results"]) else "failed"
    
    cursor.execute('''
        INSERT INTO coding_submissions 
        (user_id, exercise_id, code, status, test_results)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, exercise_id, code, status, json.dumps(result)))
    
    # Update exercise progress
    score = len([t for t in result["test_results"] if t["passed"]]) / len(result["test_results"]) * 100 if result["test_results"] else 0
    completed = status == "passed"
    
    cursor.execute('''
        INSERT OR REPLACE INTO exercise_progress 
        (user_id, exercise_id, completed, attempts, best_score)
        VALUES (?, ?, ?, 
                COALESCE((SELECT attempts FROM exercise_progress WHERE user_id = ? AND exercise_id = ?), 0) + 1,
                MAX(?, COALESCE((SELECT best_score FROM exercise_progress WHERE user_id = ? AND exercise_id = ?), 0)))
    ''', (user_id, exercise_id, completed, user_id, exercise_id, score, user_id, exercise_id))
    
    conn.commit()
    conn.close()

def get_exercise_progress(user_id: str, exercise_id: str) -> Dict:
    """Get user's progress on a specific exercise."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT completed, attempts, best_score, last_attempt
        FROM exercise_progress
        WHERE user_id = ? AND exercise_id = ?
    ''', (user_id, exercise_id))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "completed": result[0],
            "attempts": result[1],
            "best_score": result[2],
            "last_attempt": result[3]
        }
    else:
        return {"completed": False, "attempts": 0, "best_score": 0, "last_attempt": None}

def get_user_submissions(user_id: str, exercise_id: str, limit: int = 10) -> List[Dict]:
    """Get user's recent submissions for an exercise."""
    conn = sqlite3.connect("learning_progress.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT code, status, test_results, submitted_at
        FROM coding_submissions
        WHERE user_id = ? AND exercise_id = ?
        ORDER BY submitted_at DESC
        LIMIT ?
    ''', (user_id, exercise_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "code": row[0],
            "status": row[1],
            "test_results": json.loads(row[2]) if row[2] else [],
            "submitted_at": row[3]
        }
        for row in results
    ]

def display_exercise(exercise: Dict, category: str):
    """Display a coding exercise with interactive editor."""
    st.subheader(f"💻 {exercise['title']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Difficulty:** {exercise['difficulty']}")
        st.markdown(f"**Description:** {exercise['description']}")
        
        # Show hints if requested
        if st.button("💡 Show Hints", key=f"hints_{exercise['id']}"):
            st.session_state[f"show_hints_{exercise['id']}"] = True
        
        if st.session_state.get(f"show_hints_{exercise['id']}", False):
            st.markdown("**💡 Hints:**")
            for i, hint in enumerate(exercise.get('hints', []), 1):
                st.markdown(f"{i}. {hint}")
    
    with col2:
        # Exercise progress
        if 'user_id' in st.session_state:
            progress = get_exercise_progress(st.session_state.user_id, exercise['id'])
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Attempts", progress['attempts'])
            with col_b:
                st.metric("Best Score", f"{progress['best_score']:.1f}%")
            
            if progress['completed']:
                st.success("✅ Completed!")
            else:
                st.info("🔄 In Progress")
    
    # Code editor
    st.markdown("---")
    st.markdown("### 📝 Code Editor")
    
    # Load previous submission or starter code
    initial_code = exercise['starter_code']
    if 'user_id' in st.session_state:
        submissions = get_user_submissions(st.session_state.user_id, exercise['id'], 1)
        if submissions:
            initial_code = submissions[0]['code']
    
    code = st.text_area(
        "Write your code here:",
        value=initial_code,
        height=300,
        key=f"code_{exercise['id']}"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("▶️ Run Code", key=f"run_{exercise['id']}", type="primary"):
            if code.strip():
                with st.spinner("Executing code..."):
                    result = execute_code(code, exercise)
                    
                    if 'user_id' in st.session_state:
                        save_submission(st.session_state.user_id, exercise['id'], code, result)
                    
                    st.session_state[f"result_{exercise['id']}"] = result
                    st.rerun()
            else:
                st.error("Please write some code first!")
    
    with col2:
        if st.button("🔄 Reset Code", key=f"reset_{exercise['id']}"):
            st.session_state[f"code_{exercise['id']}"] = exercise['starter_code']
            st.rerun()
    
    with col3:
        if st.button("💡 Show Solution", key=f"solution_{exercise['id']}"):
            st.session_state[f"show_solution_{exercise['id']}"] = True
    
    # Show solution if requested
    if st.session_state.get(f"show_solution_{exercise['id']}", False):
        st.markdown("### 🎯 Solution")
        st.code(exercise['solution'], language='python')
    
    # Display results
    if f"result_{exercise['id']}" in st.session_state:
        result = st.session_state[f"result_{exercise['id']}"]
        
        st.markdown("---")
        st.markdown("### 📊 Execution Results")
        
        if result["success"]:
            st.success("✅ Code executed successfully!")
        else:
            st.error(f"❌ Execution failed: {result['error']}")
        
        # Show output
        if result["output"]:
            st.markdown("**Output:**")
            st.code(result["output"])
        
        # Show test results
        if result["test_results"]:
            st.markdown("**Test Results:**")
            
            passed_tests = sum(1 for t in result["test_results"] if t["passed"])
            total_tests = len(result["test_results"])
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Tests Passed", f"{passed_tests}/{total_tests}")
            
            with col2:
                if passed_tests == total_tests:
                    st.success("🎉 All tests passed!")
                elif passed_tests > 0:
                    st.warning(f"⚠️ {total_tests - passed_tests} tests failed")
                else:
                    st.error("❌ All tests failed")
            
            # Detailed test results
            for i, test in enumerate(result["test_results"], 1):
                with st.expander(f"Test {i}: {'✅ Passed' if test['passed'] else '❌ Failed'}"):
                    st.markdown(f"**Description:** {test['description']}")
                    st.markdown(f"**Expected:** `{test['expected']}`")
                    st.markdown(f"**Actual:** `{test['actual']}`")

def main():
    st.title("💻 Interactive Coding Exercises")
    st.markdown("Practice your programming skills with hands-on coding challenges!")
    
    # Initialize database
    init_coding_exercises_database()
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("🎯 Exercise Categories")
        
        categories = list(CODING_EXERCISES.keys())
        category_names = {
            "python_basics": "🐍 Python Basics",
            "ml_basics": "🤖 Machine Learning",
            "data_science": "📊 Data Science"
        }
        
        selected_category = st.selectbox(
            "Select Category",
            categories,
            format_func=lambda x: category_names.get(x, x)
        )
        
        st.markdown("---")
        
        # Progress overview
        if 'user_id' in st.session_state:
            st.subheader("📈 Your Progress")
            
            total_exercises = sum(len(exercises) for exercises in CODING_EXERCISES.values())
            completed_exercises = 0
            
            conn = sqlite3.connect("learning_progress.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM exercise_progress 
                WHERE user_id = ? AND completed = TRUE
            ''', (st.session_state.user_id,))
            result = cursor.fetchone()
            if result:
                completed_exercises = result[0]
            conn.close()
            
            st.metric("Completed", f"{completed_exercises}/{total_exercises}")
            st.progress(completed_exercises / total_exercises if total_exercises > 0 else 0)
        
        st.markdown("---")
        
        # Quick tips
        st.subheader("💡 Quick Tips")
        st.markdown("""
        - Read the problem description carefully
        - Start with the hints if you're stuck
        - Test your code step by step
        - Don't peek at the solution too early!
        - Practice makes perfect 🚀
        """)
    
    # Main content
    exercises = CODING_EXERCISES.get(selected_category, [])
    
    if not exercises:
        st.info("No exercises available for this category yet. More coming soon!")
        return
    
    st.subheader(f"📚 {category_names.get(selected_category, selected_category)} Exercises")
    
    # Exercise tabs
    if len(exercises) == 1:
        display_exercise(exercises[0], selected_category)
    else:
        exercise_tabs = st.tabs([f"{ex['title']} ({ex['difficulty']})" for ex in exercises])
        
        for i, exercise in enumerate(exercises):
            with exercise_tabs[i]:
                display_exercise(exercise, selected_category)
    
    # Additional features
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Achievements")
        
        # Mock achievements
        achievements = [
            {"name": "First Steps", "description": "Complete your first exercise", "unlocked": True},
            {"name": "Python Master", "description": "Complete all Python basics exercises", "unlocked": False},
            {"name": "Data Scientist", "description": "Complete all data science exercises", "unlocked": False},
            {"name": "ML Engineer", "description": "Complete all ML exercises", "unlocked": False},
            {"name": "Perfect Score", "description": "Get 100% on any exercise", "unlocked": False}
        ]
        
        for achievement in achievements:
            icon = "🏆" if achievement["unlocked"] else "🔒"
            status = "Unlocked" if achievement["unlocked"] else "Locked"
            
            st.markdown(f"{icon} **{achievement['name']}** - {status}")
            st.markdown(f"   _{achievement['description']}_")
    
    with col2:
        st.subheader("📊 Leaderboard")
        
        # Mock leaderboard
        leaderboard = [
            {"rank": 1, "name": "CodeMaster", "score": 1250},
            {"rank": 2, "name": "PythonPro", "score": 1100},
            {"rank": 3, "name": "DataNinja", "score": 950},
            {"rank": 4, "name": "MLWizard", "score": 875},
            {"rank": 5, "name": "DevGuru", "score": 820}
        ]
        
        for entry in leaderboard:
            medal = "🥇" if entry["rank"] == 1 else "🥈" if entry["rank"] == 2 else "🥉" if entry["rank"] == 3 else f"#{entry['rank']}"
            st.markdown(f"{medal} **{entry['name']}** - {entry['score']} pts")

if __name__ == "__main__":
    main()