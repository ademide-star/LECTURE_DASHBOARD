import streamlit as st

# Hide Streamlit style elements (GitHub, Menu, Footer)
hide_github_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1rs6os.edgvbvh3 {display: none;} /* old github button selector */
    .stActionButton {display: none !important;}
    </style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time
# -----------------------------------
# 🔧 File paths
ATTENDANCE_FILE = "attendance.csv"
LECTURE_FILE = "lectures.csv"
CLASSWORK_FILE = "classwork_submissions.csv"
SEMINAR_FILE = "seminar_submissions.csv"
MODULES_DIR = "modules"
SEMINAR_DIR = os.path.join(MODULES_DIR, "seminars")

os.makedirs(MODULES_DIR, exist_ok=True)
os.makedirs(SEMINAR_DIR, exist_ok=True)

import os
import pandas as pd
import streamlit as st

# -------------------- File Paths --------------------
LECTURE_FILE = "lectures.csv"
ATTENDANCE_FILE = "attendance.csv"



# -------------------- Attendance --------------------
def load_or_create_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        df = pd.DataFrame(columns=["Name", "Matric Number", "Week", "Timestamp"])
        df.to_csv(ATTENDANCE_FILE, index=False)
    else:
        df = pd.read_csv(ATTENDANCE_FILE)
    return df

def mark_attendance(name, matric_number, week):
    df = load_or_create_attendance()

    # Ensure required columns exist
    required_columns = ["Name", "Matric Number", "Week", "Timestamp"]
    for col in required_columns:
        if col not in df.columns:
            df = pd.DataFrame(columns=required_columns)
            df.to_csv(ATTENDANCE_FILE, index=False)
            break

    # Check if attendance already marked
    if ((df["Matric Number"] == matric_number) & (df["Week"] == week)).any():
        st.info("✅ Attendance already marked for this student this week.")
    else:
        new_row = pd.DataFrame([{
            "Name": name,
            "Matric Number": matric_number,
            "Week": week,
            "Timestamp": pd.Timestamp.now()
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
        st.success("🎉 Attendance marked successfully!")

    return df

# -----------------------------------
# ⚙️ Helper Functions
def mark_attendance(name, matric, week):
    df = pd.read_csv(ATTENDANCE_FILE) if os.path.exists(ATTENDANCE_FILE) else pd.DataFrame(columns=["Timestamp", "Matric Number", "Name", "Week"])
    if ((df["Matric Number"] == matric) & (df["Week"] == week)).any():
        st.warning(f"Attendance already marked for {week}.")
        return True
    new_entry = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Matric Number": matric, "Name": name, "Week": week}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(ATTENDANCE_FILE, index=False)
    st.success(f"Attendance marked for {name} ({matric}) - {week}")
    return True


def save_classwork(name, matric, week, answers):
    df = pd.read_csv(CLASSWORK_FILE) if os.path.exists(CLASSWORK_FILE) else pd.DataFrame(columns=["Timestamp", "Matric Number", "Name", "Week", "Answers"])
    if ((df["Matric Number"] == matric) & (df["Week"] == week)).any():
        st.warning("You’ve already submitted this classwork.")
        return False
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Matric Number": matric, "Name": name, "Week": week, "Answers": "; ".join(answers)
    }
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(CLASSWORK_FILE, index=False)
    st.success("✅ Classwork submitted successfully!")
    return True


def save_seminar(name, matric, file):
    if not os.path.exists(SEMINAR_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Matric Number", "Name", "Filename"])
    else:
        df = pd.read_csv(SEMINAR_FILE)

    if (df["Matric Number"] == matric).any():
        st.warning("You’ve already submitted your seminar.")
        return False
    filename = f"{matric}_{file.name}"
    path = os.path.join(SEMINAR_DIR, filename)
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    df = pd.concat([df, pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Matric Number": matric, "Name": name, "Filename": filename
    }])], ignore_index=True)
    df.to_csv(SEMINAR_FILE, index=False)
    st.success("✅ Seminar submitted successfully!")
    return True
def check_attendance(matric, week):
    df = pd.read_csv(ATTENDANCE_FILE)
    return ((df["Matric Number"] == matric) & (df["Week"] == week)).any()

# -----------------------------------
# 🎓 Streamlit Layout
st.set_page_config(page_title="BIO 203 Portal", page_icon="🧬", layout="wide")
st.title("📘 BIO 203: General Physiology Course Portal")
# --- APP HEADER ---
st.subheader("Department of Biological Sciences Sikiru Adetona College of Education Omu-Ijebu")
mode = st.radio("Select Mode:", ["Student", "Teacher/Admin"])

with st.expander("About this Portal"):
    st.info("""
    Welcome to the BIO 203 Course Portal.
    - ✅ Mark your attendance each week.
    - 📚 Access lecture briefs and modules.
    - 🧪 Participate in weekly classwork and assignments.
    - 💬 Submit your seminar slides after mid-semester.
    - 🧠 Tests and interactive activities will be enabled as scheduled.
    """)

# -----------------------------------
# -------------------- Attendance Form --------------------
st.markdown("## 📝 Mark Attendance")

with st.form("attendance_form"):
    name = st.text_input("Full Name")
    matric_number = st.text_input("Matric Number")
    week = st.selectbox("Week", lectures_df["Week"].tolist())

    submitted = st.form_submit_button("Mark Attendance")
    if submitted:
        if not name.strip() or not matric_number.strip():
            st.error("Please enter both Name and Matric Number.")
        else:
            mark_attendance(name.strip(), matric_number.strip(), week)

# -------------------- Initialize Lectures CSV --------------------
if not os.path.exists(LECTURE_FILE):
    lecture_data = {
        "Week": [
            "Week 1–2", "Week 3–4", "Week 5–6", "Week 7–8",
            "Week 9", "Week 10–11", "Week 12", "Week 13–14", "Week 15"
        ],
        "Topic": [
            "Chemicals of Life: Carbohydrates, lipids, proteins, nucleic acids, and biological significance.",
            "Enzymology: Characteristics, mechanism, factors affecting activity, enzyme classification.",
            "Nutrition, Digestion, and Absorption in plants and animals.",
            "Biosynthesis: Photosynthesis (light & dark reactions) and Protein Synthesis (transcription & translation).",
            "Cell Membrane Structure & Function: Lipid bilayer, membrane proteins, transport, signal transduction.",
            "Osmoregulation, Excretion, and Transport in Animals: Kidney function, circulatory & respiratory transport.",
            "Plant Growth Hormones and Regulation: Auxins, gibberellins, cytokinins, abscisic acid, ethylene.",
            "Homeostasis in Animals: Nervous & endocrine coordination, temperature, blood glucose, water balance.",
            "Plant Water Relations and Growth: Water uptake, transport, transpiration, growth regulation, stress responses."
        ],
        "Brief": [""] * 9,
        "Assignment": [""] * 9,
        "Classwork": [""] * 9
    }
    pd.DataFrame(lecture_data).to_csv(LECTURE_FILE, index=False)

lectures_df = pd.read_csv(LECTURE_FILE)

# -------------------- Lecture Info --------------------
# Pick first lecture row (example)
lecture_info = lectures_df.iloc[0].to_dict()

# Hardcoded defaults
hardcoded_info = {
    "Brief": "Introduction to proteins, amino acids, and their biological roles.",
    "Assignment": "Answer Q1-Q5 on amino acid properties; prepare a short report on protein structures.",
    "Classwork": "Discuss protein structures in groups; submit summary."
}

# Fill empty CSV fields safely
for key, value in hardcoded_info.items():
    if not str(lecture_info.get(key, "")).strip():  # convert to string to avoid AttributeError
        lecture_info[key] = value

# Display lecture info safely
st.title(f"📚 {lecture_info.get('Topic', 'Untitled Lecture')}")

for key, title in [("Brief", "Lecture Brief"),
                   ("Assignment", "Assignment Questions"),
                   ("Classwork", "Classwork Questions")]:
    text = str(lecture_info.get(key, ""))
    if text.strip():
        st.markdown(f"### {title}")
        st.write(text)
# 👩‍🎓 STUDENT MODE
if mode == "Student":
    st.subheader("🎓 Student Login & Attendance")
    with st.form("attendance_form"):
        name = st.text_input("Full Name")
        matric = st.text_input("Matric Number")
        week = st.selectbox("Select Lecture Week", lectures_df["Week"].tolist())
        mark = st.form_submit_button("Mark Attendance")

    if mark:
        if name.strip() and matric.strip():
            marked = mark_attendance(name, matric, week)
            
            st.session_state["attended_week"] = week if marked else None
        else:
            st.error("Please enter both Name and Matric Number.")

    # Gate access
    if "attended_week" in st.session_state and st.session_state["attended_week"]:
        week = st.session_state["attended_week"]
        st.success(f"Access granted for {week}")
        lecture_info = lectures_df[lectures_df["Week"] == week].iloc[0]
        st.subheader(f"📖 {week}: {lecture_info['Topic']}")
        if lecture_info["Brief"].strip():
            st.write(f"**Lecture Brief:**\n{lecture_info['Brief']}")
        else:
            st.info("Lecture brief not yet available.")
        # Assignments
        if lecture_info["Assignment"].strip():
            st.subheader("📚 Assignment")
            st.info(f"✅ Assignment to be submitted by next class.")
            st.markdown(f"**Assignment:** {lecture_info['Assignment']}")
        else:
            st.info("Assignment not released yet.")
      
# --- PDF Download ---
            pdf_path = f"{MODULES_DIR}/{week.replace(' ', '_')}.pdf"
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"Download {week} Module PDF",
                        data=f,
                        file_name=f"{week}_module.pdf",
                        mime="application/pdf"
                        )
            else:
                    st.info("Lecture PDF module not yet uploaded by the instructor.")
# PDF Module
        pdf_path = f"{MODULES_DIR}/{week.replace(' ', '_')}.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download Lecture Module PDF", f, file_name=f"{week}_module.pdf", mime="application/pdf")
        else:
            st.info("Lecture PDF not yet uploaded.")
        # Seminar upload (opens mid-semester, presentation in November 3rd week)
        st.divider()
        st.subheader("🎤 Mid-Semester Seminar Submission")
        today = date.today()
        if today >= date(today.year, 10, 20):  # Opens around mid-November
            seminar_file = st.file_uploader("Upload Seminar PPT (after mid-semester)", type=["ppt", "pptx"])
            if seminar_file:
                save_seminar(name, matric, seminar_file)
            st.info("Seminar presentations will hold in the **3rd week of November**.")
        else:
            st.warning("Seminar submissions will open mid-semester (around 4th November).")

# -----------------------------------
 # PDF download
            pdf_path = f"{MODULES_DIR}/{week.replace(' ', '_')}.pdf"
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"Download {week} Module PDF",
                        data=f,
                        file_name=f"{week}_module.pdf",
                        mime="application/pdf"
                            )
            else:
                st.info("Lecture PDF module not yet uploaded by the instructor.")
        

# Example timing configuration
TOTAL_DURATION = 60 * 60           # 1 hour lecture
SHOW_TIMER_THRESHOLD = 20 * 60     # only show classwork in last 20 minutes

# Initialize timer state once per session
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

elapsed = time.time() - st.session_state.start_time
remaining = TOTAL_DURATION - elapsed

# ---- Time logic ----
if remaining <= 0:
    st.error("⏰ Lecture ended. Classwork closed.")
    st.stop()

# ---- Before last 20 minutes ----
elif remaining > SHOW_TIMER_THRESHOLD:
    mins_hidden = int((remaining - SHOW_TIMER_THRESHOLD) // 60)
    st.info(f"✅ Classwork will open {mins_hidden} minutes before the end of lecture.")
else:
    # ---- Show classwork form when 20 minutes remain ----
    st.subheader("📚 Classwork")
    st.markdown("### 🧩 Classwork Section")
    mins, secs = divmod(int(remaining), 60)
    st.markdown(f"⏳ Time remaining: **{mins:02d}:{secs:02d}**")

    # --- Classwork ---
    if lecture_info["Classwork"].strip():
        st.markdown("### 🧩 Classwork Questions")
        questions = [q.strip() for q in lecture_info["Classwork"].split(";") if q.strip()]

        with st.form("cw_form"):
            answers = [
                st.text_input(f"Q{i+1}: {q}") for i, q in enumerate(questions)
            ]
            submit_cw = st.form_submit_button("Submit Answers")

            if submit_cw:
                save_classwork(name, matric, week, answers)
                st.success("✅ Classwork submitted successfully!")
    else:
        st.info("Classwork not yet released.")

        
# ===============================================================
# 👩‍🏫 TEACHER / ADMIN MODE
# ===============================================================
if mode == "Teacher/Admin":
    st.subheader("🔐 Teacher/Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    ADMIN_PASS = "bimpe2025class"
    if password == ADMIN_PASS:
        st.success("✅ Logged in as Admin")

        # ---- Edit Lecture ----
        lecture_to_edit = st.selectbox("Select Lecture", lectures_df["Week"].tolist())
        row_idx = lectures_df[lectures_df["Week"] == lecture_to_edit].index[0]

        brief = st.text_area("Lecture Brief", value=lectures_df.at[row_idx, "Brief"])
        assignment = st.text_area("Assignment", value=lectures_df.at[row_idx, "Assignment"])
        classwork = st.text_area("Classwork (Separate questions with ;)", value=lectures_df.at[row_idx, "Classwork"])

        if st.button("💾 Update Lecture"):
            lectures_df.at[row_idx, "Brief"] = brief
            lectures_df.at[row_idx, "Assignment"] = assignment
            lectures_df.at[row_idx, "Classwork"] = classwork
            lectures_df.to_csv(LECTURE_FILE, index=False)
            st.success(f"{lecture_to_edit} updated successfully!")

        # ---- PDF Upload ----
        st.subheader("📄 Upload Lecture PDF Module")
        pdf = st.file_uploader("Upload Lecture Module", type=["pdf"])
        if pdf:
            os.makedirs(MODULES_DIR, exist_ok=True)
            pdf_path = f"{MODULES_DIR}/{lecture_to_edit.replace(' ', '_')}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(pdf.getbuffer())
            st.success(f"✅ PDF uploaded for {lecture_to_edit}")

        # ---- Attendance Records ----
        st.divider()
        st.markdown("### 🧾 Attendance Records")
        if os.path.exists(ATTENDANCE_FILE):
            att = pd.read_csv(ATTENDANCE_FILE)
            st.dataframe(att)
            st.download_button("Download Attendance CSV", att.to_csv(index=False).encode(), "attendance.csv")
        else:
            st.info("No attendance records yet.")

        # ---- Classwork Submissions ----
        st.markdown("### 🧠 Classwork Submissions")
        if os.path.exists(CLASSWORK_FILE):
            cw = pd.read_csv(CLASSWORK_FILE)
            st.dataframe(cw)
            st.download_button("Download Classwork CSV", cw.to_csv(index=False).encode(), "classwork_submissions.csv")
        else:
            st.info("No classwork submissions yet.")

        # ---- Seminar Submissions ----
        st.markdown("### 🎤 Seminar Submissions")
        if os.path.exists(SEMINAR_FILE):
            sem = pd.read_csv(SEMINAR_FILE)
            st.dataframe(sem)
            st.download_button("Download Seminar CSV", sem.to_csv(index=False).encode(), "seminar_submissions.csv")
        else:
            st.info("No seminar submissions yet.")

    else:
        if password:
            st.error("❌ Incorrect password. Try again.")




   














