import streamlit as st
import json
import pandas as pd
from datetime import datetime
import time
import os

# Page configuration
st.set_page_config(
    page_title="Student Test LMS",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File paths
QUESTIONS_FILE = 'questions.json'
RESULTS_FILE = 'test_results.csv'
ADMIN_CREDENTIALS_FILE = 'admin_credentials.json'

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'student_name' not in st.session_state:
    st.session_state.student_name = ''
if 'matric_number' not in st.session_state:
    st.session_state.matric_number = ''
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'test_submitted' not in st.session_state:
    st.session_state.test_submitted = False
if 'test_duration' not in st.session_state:
    st.session_state.test_duration = 1800  # 30 minutes in seconds
if 'show_results_page' not in st.session_state:
    st.session_state.show_results_page = False
if 'test_results_data' not in st.session_state:
    st.session_state.test_results_data = {}
if 'time_up' not in st.session_state:
    st.session_state.time_up = False
if 'confirm_submit' not in st.session_state:
    st.session_state.confirm_submit = False
if 'answered_questions' not in st.session_state:
    st.session_state.answered_questions = 0

PROGRESS_DIR = "progress"
os.makedirs(PROGRESS_DIR, exist_ok=True)

def get_progress_file(matric):
    return os.path.join(PROGRESS_DIR, f"progress_{matric}.json")

def save_progress(matric):
    data = {
        "start_time": st.session_state.start_time,
        "answers": st.session_state.answers,
        "test_started": st.session_state.test_started,
        "test_duration": st.session_state.test_duration
    }
    with open(get_progress_file(matric), "w") as f:
        json.dump(data, f)

def load_progress(matric):
    file = get_progress_file(matric)
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return None

def clear_progress(matric):
    file = get_progress_file(matric)
    if os.path.exists(file):
        os.remove(file)

# Initialize files
def initialize_files():
    # Questions file
    if not os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'w') as f:
            json.dump([], f)
    
    # Results file
    if not os.path.exists(RESULTS_FILE):
        df = pd.DataFrame(columns=['Timestamp', 'Student Name', 'Matric Number', 
                                   'Score', 'Total Questions', 'Percentage', 'Time Taken (seconds)'])
        df.to_csv(RESULTS_FILE, index=False)
    
    # Admin credentials
    if not os.path.exists(ADMIN_CREDENTIALS_FILE):
        default_admin = {
            'username': 'admin',
            'password': 'admin123'
        }
        with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
            json.dump(default_admin, f)

initialize_files()

# Load questions
def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Save questions
def save_questions(questions):
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(questions, f, indent=2)

# Load admin credentials
def load_admin_credentials():
    try:
        with open(ADMIN_CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'username': 'admin', 'password': 'admin123'}

# Save result to CSV
def save_result(name, matric, score, total, percentage, time_taken):
    result = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Student Name': name,
        'Matric Number': matric,
        'Score': score,
        'Total Questions': total,
        'Percentage': round(percentage, 2),
        'Time Taken (seconds)': time_taken
    }
    
    df = pd.read_csv(RESULTS_FILE)
    df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
    df.to_csv(RESULTS_FILE, index=False)

# Calculate remaining time
def get_remaining_time():
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, st.session_state.test_duration - elapsed)
        return int(remaining)
    return st.session_state.test_duration

# Format time
def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
    }

    .timer-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    .timer-normal { color: #27ae60; background-color: #d4edda; }
    .timer-warning { color: #f39c12; background-color: #fff3cd; }
    .timer-danger { color: #e74c3c; background-color: #f8d7da; }

    .question-card {
        background-color: rgba(128,128,128,0.08);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1.5rem;
    }

    /* 🔥 FIX: RADIO ANSWERS VISIBILITY */
    div[role="radiogroup"] > label {
        color: inherit !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center;
    }

    div[role="radiogroup"] span {
        color: inherit !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    input[type="radio"] {
        accent-color: #667eea;
    }

    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #5568d3;
    }
    
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .result-passed {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
    }
    
    .result-failed {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

def has_taken_test(matric):
    if not os.path.exists(RESULTS_FILE):
        return False
    try:
        df = pd.read_csv(RESULTS_FILE)
        return matric in df['Matric Number'].astype(str).values
    except:
        return False

# Login Page
def show_login():
    st.markdown("<h1 class='main-header'>📚 Student Test LMS</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Student Login")
        st.write("Enter your details to start the test")
        
        with st.form("login_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            matric = st.text_input("Matric Number", placeholder="Enter your matric number")
            submit = st.form_submit_button("Start Test", use_container_width=True)
            
            if submit:
                if name and matric:
                    if has_taken_test(matric):
                        st.error("❌ You have already completed this test.")
                        return

                    progress = load_progress(matric)

                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.student_name = name
                    st.session_state.matric_number = matric
                    st.session_state.test_submitted = False
                    st.session_state.time_up = False
                    st.session_state.confirm_submit = False

                    if progress:
                        st.session_state.test_started = progress["test_started"]
                        st.session_state.start_time = progress["start_time"]
                        st.session_state.answers = progress["answers"]
                        if "test_duration" in progress:
                            st.session_state.test_duration = progress["test_duration"]
                    else:
                        st.session_state.test_started = False
                        st.session_state.answers = {}
                        st.session_state.start_time = None

                    st.rerun()

        
        st.markdown("---")
        if st.button("Admin Login", use_container_width=True):
            st.session_state.show_admin_login = True
            st.rerun()

# Admin Login Page
def show_admin_login():
    st.markdown("<h1 class='main-header'>🔐 Admin Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Admin Access")
        
        with st.form("admin_login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                admin_creds = load_admin_credentials()
                if username == admin_creds['username'] and password == admin_creds['password']:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.student_name = 'Administrator'
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.info("**Default credentials:** Username: admin, Password: admin123")
        
        if st.button("Back to Student Login", use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()

# Test Page
def show_test():
    questions = load_questions()
    
    if not questions:
        st.error("No questions available. Please contact your instructor.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        return
    
    # Start test
    if not st.session_state.test_started:
        st.session_state.test_started = True
        st.session_state.start_time = time.time()
        save_progress(st.session_state.matric_number)
    
    # Calculate remaining time
    remaining_time = get_remaining_time()
    
    # Check if time is up
    if remaining_time <= 0 and not st.session_state.time_up:
        st.session_state.time_up = True
        st.warning("⏰ Time's up! Your test will be submitted automatically.")
        time.sleep(2)
        submit_test(questions)
        return
    
    # Display header
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 👤 {st.session_state.student_name}")
        st.write(f"**Matric Number:** {st.session_state.matric_number}")
    
    with col2:
        # Timer styling based on remaining time
        if remaining_time > 600:
            timer_class = "timer-normal"
        elif remaining_time > 300:
            timer_class = "timer-warning"
        else:
            timer_class = "timer-danger"
        
        st.markdown(f"""
        <div class='timer-display {timer_class}'>
            ⏱️ {format_time(remaining_time)}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Time Remaining</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check for confirm submit warning
    if st.session_state.confirm_submit:
        answered = len(st.session_state.answers)
        total = len(questions)
        unanswered = total - answered
        
        st.markdown(f"""
        <div class='warning-box'>
            <h4>⚠️ Confirm Submission</h4>
            <p>You have {unanswered} unanswered question(s). Are you sure you want to submit?</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("✅ Yes, Submit Anyway", use_container_width=True, type="primary"):
                submit_test(questions)
        with col2:
            if st.button("❌ No, Continue Test", use_container_width=True):
                st.session_state.confirm_submit = False
                st.rerun()
    
    # Display questions
    for idx, q in enumerate(questions):
        st.markdown(f"""
        <div class='question-card'>
            <p style='color: #667eea; font-weight: 600; margin-bottom: 0.5rem;'>
                QUESTION {idx + 1} OF {len(questions)}
            </p>
            <p style='font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;'>
                {q['question']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Options
        option_labels = ['A', 'B', 'C', 'D']
        options_display = [f"{option_labels[i]}. {opt}" for i, opt in enumerate(q['options'])]
        
        # Get current answer if exists
        current_answer = st.session_state.answers.get(str(q['id']), None)
        current_index = None
        if current_answer:
            try:
                current_index = option_labels.index(current_answer)
            except:
                current_index = None
        
        answer = st.radio(
            f"Select your answer for Question {idx + 1}:",
            options=options_display,
            key=f"q_{q['id']}",
            index=current_index,
            label_visibility="collapsed"
        )

        if answer:
            # Extract A, B, C, or D from "A. option text"
            st.session_state.answers[str(q['id'])] = answer.split(".")[0]
            save_progress(st.session_state.matric_number)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Submit Test", use_container_width=True, type="primary"):
            answered = len(st.session_state.answers)
            total = len(questions)
            
            if answered < total:
                # Show confirmation warning
                st.session_state.confirm_submit = True
                st.rerun()
            else:
                # Submit directly if all questions answered
                submit_test(questions)

# Submit test function
def submit_test(questions):
    # Calculate score
    score = 0
    total = len(questions)
    
    for q in questions:
        q_id = str(q['id'])
        if q_id in st.session_state.answers:
            if st.session_state.answers[q_id] == q['correct_answer']:
                score += 1
    
    percentage = (score / total * 100) if total > 0 else 0
    time_taken = int(time.time() - st.session_state.start_time)
    
    # Save result
    save_result(
        st.session_state.student_name,
        st.session_state.matric_number,
        score,
        total,
        percentage,
        time_taken
    )
    
    # Clear progress file
    clear_progress(st.session_state.matric_number)
    
    # Store results in session state
    st.session_state.test_submitted = True
    st.session_state.test_results_data = {
        'score': score,
        'total': total,
        'percentage': percentage,
        'time_taken': time_taken
    }
    
    # Rerun to show results
    st.rerun()

# Show results
def show_results_page():
    st.markdown("<h1 class='main-header'>✅ Test Submitted Successfully!</h1>", unsafe_allow_html=True)
    
    # Get results from session state
    results = st.session_state.test_results_data
    score = results['score']
    total = results['total']
    percentage = results['percentage']
    time_taken = results['time_taken']
    
    passed = percentage >= 50
    result_class = "result-passed" if passed else "result-failed"
    status_emoji = "✅" if passed else "❌"
    status_text = "PASSED" if passed else "FAILED"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.success("🎉 Your test has been submitted successfully!")
        
        st.markdown(f"""
        <div class='result-card {result_class}'>
            <h2 style="font-size: 2rem; margin-bottom: 1rem;">{status_emoji} {status_text}</h2>
            <h1 style='font-size: 4rem; margin: 1rem 0;'>{score}/{total}</h1>
            <h3 style="font-size: 2rem; margin: 1rem 0;">{percentage:.1f}%</h3>
            <p style='margin-top: 1rem; font-size: 1.1rem;'>
                {'Congratulations! You passed the test.' if passed else 'Unfortunately, you did not pass. Keep studying!'}
            </p>
            <p style='color: rgba(255,255,255,0.9); margin-top: 1rem;'>
                Time taken: {format_time(time_taken)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show answer summary
        st.markdown("### 📊 Your Performance")
        
        # Calculate stats
        questions = load_questions()
        correct = score
        incorrect = total - score
        unanswered = total - len(st.session_state.answers)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Correct Answers", f"{correct}", delta=f"{percentage:.1f}%")
        with col2:
            st.metric("Incorrect Answers", f"{incorrect}")
        with col3:
            st.metric("Time Taken", f"{format_time(time_taken)}")
        
        st.markdown("---")
        
        if st.button("🏁 Finish", use_container_width=True, type="primary"):
            # Clear all session state
            st.session_state.clear()
            st.rerun()

# Admin Dashboard
def show_admin_dashboard():
    st.sidebar.title("📊 Admin Dashboard")
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.student_name}")
    
    menu = st.sidebar.radio(
        "Navigation",
        ["Manage Questions", "View Results", "Settings"]
    )
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    if menu == "Manage Questions":
        show_question_management()
    elif menu == "View Results":
        show_results_dashboard()
    elif menu == "Settings":
        show_settings()

# Question Management
def show_question_management():
    st.markdown("<h1 class='main-header'>📝 Manage Questions</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Bulk Upload", "Current Questions"])
    
    with tab1:
        st.markdown("### Bulk Upload Questions")
        st.info("Upload multiple questions at once using JSON format")
        
        with st.expander("📋 View Example Format"):
            st.code("""[
  {
    "id": 1,
    "question": "What is the capital of France?",
    "options": ["London", "Paris", "Berlin", "Madrid"],
    "correct_answer": "B"
  },
  {
    "id": 2,
    "question": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "correct_answer": "B"
  }
]""", language="json")
        
        questions_json = st.text_area(
            "Paste JSON Questions:",
            height=300,
            placeholder="Paste your questions in JSON format here..."
        )
        
        if st.button("Upload Questions", use_container_width=True):
            try:
                questions = json.loads(questions_json)
                
                # Validate
                if not isinstance(questions, list):
                    st.error("Questions must be an array")
                else:
                    for q in questions:
                        if not all(k in q for k in ['id', 'question', 'options', 'correct_answer']):
                            st.error("Each question must have: id, question, options, correct_answer")
                            return
                    
                    save_questions(questions)
                    st.success(f"✅ {len(questions)} questions uploaded successfully!")
                    
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your input.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with tab2:
        st.markdown("### Current Questions")
        questions = load_questions()
        
        if not questions:
            st.info("No questions available. Upload questions to get started.")
        else:
            st.success(f"**Total Questions:** {len(questions)}")
            
            for idx, q in enumerate(questions):
                with st.expander(f"Question {idx + 1} (ID: {q['id']})"):
                    st.markdown(f"**Question:** {q['question']}")
                    st.markdown("**Options:**")
                    option_labels = ['A', 'B', 'C', 'D']
                    for i, opt in enumerate(q['options']):
                        is_correct = option_labels[i] == q['correct_answer']
                        prefix = "✅" if is_correct else "⚪"
                        st.markdown(f"{prefix} {option_labels[i]}. {opt}")

# Results Dashboard
def show_results_dashboard():
    st.markdown("<h1 class='main-header'>📈 Student Results</h1>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(RESULTS_FILE)
        
        if df.empty:
            st.info("No test results yet.")
        else:
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Submissions", len(df))
            with col2:
                st.metric("Average Score", f"{df['Percentage'].mean():.1f}%")
            with col3:
                pass_rate = (df['Percentage'] >= 50).sum() / len(df) * 100
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
            with col4:
                avg_time = df['Time Taken (seconds)'].mean() / 60
                st.metric("Avg Time", f"{avg_time:.1f} min")
            
            st.markdown("---")
            
            # Results table
            st.markdown("### All Results")
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv,
                file_name=f"test_results_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error loading results: {str(e)}")

# Settings
def show_settings():
    st.markdown("<h1 class='main-header'>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    st.markdown("### Test Duration")
    duration_minutes = st.number_input(
        "Test duration (minutes)",
        min_value=5,
        max_value=180,
        value=30,
        step=5
    )
    
    if st.button("Save Duration"):
        st.session_state.test_duration = duration_minutes * 60
        st.success(f"Test duration set to {duration_minutes} minutes")
    
    st.markdown("---")
    
    st.markdown("### Admin Credentials")
    st.warning("⚠️ Change default credentials for security!")
    
    with st.form("change_credentials"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Update Credentials"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            elif new_username and new_password:
                credentials = {
                    'username': new_username,
                    'password': new_password
                }
                with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
                    json.dump(credentials, f)
                st.success("Credentials updated successfully!")
            else:
                st.error("Please fill in all fields")
    
    st.markdown("---")
    
    st.markdown("### Danger Zone")
    if st.button("Clear All Results", type="secondary"):
        if st.checkbox("I understand this will delete all results"):
            df = pd.DataFrame(columns=['Timestamp', 'Student Name', 'Matric Number', 
                                       'Score', 'Total Questions', 'Percentage', 'Time Taken (seconds)'])
            df.to_csv(RESULTS_FILE, index=False)
            st.success("All results cleared")
            st.rerun()

# Main App Logic
def main():
    if 'show_admin_login' not in st.session_state:
        st.session_state.show_admin_login = False
    
    if not st.session_state.logged_in:
        if st.session_state.show_admin_login:
            show_admin_login()
        else:
            show_login()
    else:
        if st.session_state.is_admin:
            show_admin_dashboard()
        else:
            if st.session_state.test_submitted:
                show_results_page()
            else:
                show_test()

if __name__ == "__main__":
    main()
