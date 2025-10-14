import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# -----------------------------
# File paths
# -----------------------------
ATTENDANCE_FILE = "attendance.csv"
LECTURE_FILE = "lectures.csv"
CLASSWORK_FILE = "classwork_submissions.csv"
SEMINAR_FILE = "seminar_submissions.csv"
MODULES_DIR = "modules"
SEMINAR_DIR = os.path.join(MODULES_DIR, "seminars")
CLASSWORK_STATUS_FILE = "classwork_status.csv"

os.makedirs(MODULES_DIR, exist_ok=True)
os.makedirs(SEMINAR_DIR, exist_ok=True)

# -----------------------------
# Hide default Streamlit UI
# -----------------------------
st.markdown("""
<style>
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
.viewerBadge_container__1QSob,
.viewerBadge_link__1S137,
.viewerBadge_text__1JaDK {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Initialize lectures CSV if missing
# -----------------------------
if not os.path.exists(LECTURE_FILE):
    lecture_data = {
         "Week": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6",
                 "Week 7", "Week 8", "Week 9", "Week 10–11", "Week 12–14", "Week 15"],
        
        "Brief": [""] * 12,
        "Assignment": [""] * 12,
        "Classwork": [""] * 12
    }
    pd.DataFrame(lecture_data).to_csv(LECTURE_FILE, index=False)

lectures_df = pd.read_csv(LECTURE_FILE)

# -----------------------------
# Initialize classwork status file
# -----------------------------
if not os.path.exists(CLASSWORK_STATUS_FILE):
    df_status = pd.DataFrame(columns=["Week", "IsOpen", "OpenTime"])
    df_status.to_csv(CLASSWORK_STATUS_FILE, index=False)

# -----------------------------
# Helper Functions
# -----------------------------
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
    entry = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "Matric Number": matric, "Name": name, "Week": week, "Answers": "; ".join(answers)}
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(CLASSWORK_FILE, index=False)
    st.success("✅ Classwork submitted successfully!")
    return True

def save_seminar(name, matric, file):
    df = pd.read_csv(SEMINAR_FILE) if os.path.exists(SEMINAR_FILE) else pd.DataFrame(columns=["Timestamp", "Matric Number", "Name", "Filename"])
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

# -----------------------------
# Classwork status helpers
# -----------------------------
def is_classwork_open(week):
    if not os.path.exists(CLASSWORK_STATUS_FILE):
        return False
    df = pd.read_csv(CLASSWORK_STATUS_FILE)
    if week not in df["Week"].values:
        return False
    row = df[df["Week"] == week].iloc[0]
    return row["IsOpen"] == 1

def open_classwork(week):
    now = datetime.now()
    df = pd.read_csv(CLASSWORK_STATUS_FILE) if os.path.exists(CLASSWORK_STATUS_FILE) else pd.DataFrame(columns=["Week","IsOpen","OpenTime"])
    if week in df["Week"].values:
        df.loc[df["Week"]==week, ["IsOpen","OpenTime"]] = [1, now]
    else:
        df = pd.concat([df, pd.DataFrame([{"Week":week,"IsOpen":1,"OpenTime":now}])], ignore_index=True)
    df.to_csv(CLASSWORK_STATUS_FILE, index=False)

def close_classwork_after_20min():
    if not os.path.exists(CLASSWORK_STATUS_FILE):
        return
    df = pd.read_csv(CLASSWORK_STATUS_FILE)
    now = datetime.now()
    for idx, row in df.iterrows():
        if row["IsOpen"]==1 and pd.notnull(row["OpenTime"]):
            open_time = pd.to_datetime(row["OpenTime"])
            if (now - open_time).total_seconds() > 20*60:
                df.at[idx,"IsOpen"]=0
                df.at[idx,"OpenTime"]=None
    df.to_csv(CLASSWORK_STATUS_FILE,index=False)

# -----------------------------
# PDF and seminar helpers
# -----------------------------
def display_module_pdf(week):
    pdf_path = f"{MODULES_DIR}/{week.replace(' ','_')}.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path,"rb") as f:
            st.download_button(label=f"📥 Download {week} Module PDF", data=f, file_name=f"{week}_module.pdf", mime="application/pdf")
    else:
        st.info("Lecture PDF module not yet uploaded.")

def display_seminar_upload(name, matric):
    today = date.today()
    if today >= date(today.year,10,20):
        seminar_file = st.file_uploader("Upload Seminar PPT", type=["ppt","pptx"])
        if seminar_file:
            save_seminar(name, matric, seminar_file)
        st.info("Seminar presentations will hold in the **3rd week of November**.")
    else:
        st.warning("Seminar submissions will open mid-semester.")

# -----------------------------
# Streamlit Layout
# -----------------------------
st.set_page_config(page_title="BCH 201 Portal", page_icon="🧬", layout="wide")
st.title("📘 BCH 201 General Biochemistry Course Portal")
st.subheader("Department of Biological Sciences Sikiru Adetona College of Education Omu-Ijebu")
mode = st.radio("Select Mode:", ["Student", "Teacher/Admin"])


# -----------------------------
# STUDENT MODE
# -----------------------------
if mode=="Student":
    st.subheader("🎓 Student Login & Attendance")
    with st.form("attendance_form"):
        name = st.text_input("Full Name")
        matric = st.text_input("Matric Number")
        week = st.selectbox("Select Lecture Week", lectures_df["Week"].tolist())
        mark = st.form_submit_button("Mark Attendance")
    
    if mark and name.strip() and matric.strip():
        marked = mark_attendance(name, matric, week)
        st.session_state["attended_week"] = week if marked else None

    if "attended_week" in st.session_state:
        week = st.session_state["attended_week"]
        st.success(f"Access granted for {week}")
        lecture_info = lectures_df[lectures_df["Week"]==week].iloc[0]
        st.subheader(f"📖 {week}: {lecture_info['Topic']}")
        if lecture_info["Brief"].strip(): st.write(f"**Lecture Brief:** {lecture_info['Brief']}")
        else: st.info("Lecture brief not yet available.")

        if lecture_info["Assignment"].strip():
            st.subheader("📚 Assignment")
            st.markdown(f"**Assignment:** {lecture_info['Assignment']}")
        else:
            st.info("Assignment not released yet.")

        display_module_pdf(week)

        # Classwork
        if lecture_info["Classwork"].strip():
            st.markdown("### 🧩 Classwork Questions")
            questions = [q.strip() for q in lecture_info["Classwork"].split(";") if q.strip()]
            with st.form("cw_form"):
                answers = [st.text_input(f"Q{i+1}: {q}") for i,q in enumerate(questions)]
                submit_cw = st.form_submit_button("Submit Answers", disabled=not is_classwork_open(week))
                if submit_cw: save_classwork(name, matric, week, answers)
        else: st.info("Classwork not yet released.")
            
        
import os
import streamlit as st
st.subheader("Upload Your Drawing / Diagram")
st.write("Draw the bacterial shapes (coccus, bacillus, spirillum, vibrio) on paper, take a photo, and upload it below.")

# --- Student Info ---
student_name = st.text_input("Enter your full name")
week = st.selectbox("Select Week", ["1", "2"])

# --- Drawing Upload ---
drawing = st.file_uploader(
    "Upload your drawing (jpg, png, pdf)", 
    type=["jpg","jpeg","png","pdf"], 
    key="week_drawing"
)

# --- Ensure folder exists ---
os.makedirs("submissions", exist_ok=True)

# --- Submit ---
if st.button("Submit Drawing"):
    if not student_name or student_name.strip() == "":
        st.error("❌ Please enter your name before submitting.")
    elif drawing is None:
        st.error("❌ Please upload a drawing.")
    else:
        ext = drawing.name.split('.')[-1]
        safe_name = student_name.replace(" ", "_")
        save_path = f"submissions/{safe_name}_week{week}_drawing.{ext}"
        with open(save_path, "wb") as f:
            f.write(drawing.getbuffer())
        st.success(f"✅ Drawing uploaded successfully as {drawing.name}")


        # Seminar upload
        st.divider()
        st.subheader("🎤 Mid-Semester Seminar Submission")
        display_seminar_upload(name, matric)
        
import streamlit as st
import os
import re

st.title("BCH 201 – General Biochemistry")
st.write("Submit your assignments for Week 1 and Week 2. Upload your files below.")

# --- Student Info ---
student_name = st.text_input("Enter your full name", key="student_name_input")
week = st.selectbox("Select Week", ["1", "2"], key="week_select")

# --- Ensure submissions folder exists ---
os.makedirs("submissions", exist_ok=True)

# --- File Upload ---
st.subheader(f"Upload Assignment for Week {week}")
uploaded_file = st.file_uploader(
    f"Choose file to upload for Week {week} (PDF, DOCX, or image)", 
    type=["pdf","docx","jpg","jpeg","png"], 
    key=f"file_uploader_week{week}"
)

# --- Submit Button ---
if st.button(f"Submit Week {week} Assignment", key=f"submit_week{week}"):
    if not student_name.strip():
        st.error("❌ Please enter your full name before submitting.")
    elif uploaded_file is None:
        st.error(f"❌ Please upload a file for Week {week}.")
    else:
        # Safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', student_name)
        ext = uploaded_file.name.split('.')[-1]
        save_path = f"submissions/{safe_name}_week{week}_assignment.{ext}"
        
        # Save the uploaded file
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Assignment for Week {week} uploaded successfully as {uploaded_file.name}")



# -----------------------------
# TEACHER/ADMIN MODE
# -----------------------------
if mode=="Teacher/Admin":
    st.subheader("🔐 Teacher/Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    ADMIN_PASS = "bimpe2025class"

    if password==ADMIN_PASS:
        st.success("✅ Logged in as Admin")
        # ---- Edit Lecture ----
        lecture_to_edit = st.selectbox("Select Lecture", lectures_df["Week"].unique())
        row_idx = lectures_df[lectures_df["Week"]==lecture_to_edit].index[0]
        brief = st.text_area("Lecture Brief", value=lectures_df.at[row_idx,"Brief"])
        assignment = st.text_area("Assignment", value=lectures_df.at[row_idx,"Assignment"])
        classwork = st.text_area("Classwork (Separate questions with ;)", value=lectures_df.at[row_idx,"Classwork"])
        if st.button("💾 Update Lecture"):
            lectures_df.at[row_idx,"Brief"]=brief
            lectures_df.at[row_idx,"Assignment"]=assignment
            lectures_df.at[row_idx,"Classwork"]=classwork
            lectures_df.to_csv(LECTURE_FILE,index=False)
            st.success(f"{lecture_to_edit} updated successfully!")

        # ---- PDF Upload ----
        st.subheader("📄 Upload Lecture PDF Module")
        pdf = st.file_uploader("Upload Lecture Module", type=["pdf"])
        if pdf:
            pdf_path = f"{MODULES_DIR}/{lecture_to_edit.replace(' ','_')}.pdf"
            with open(pdf_path,"wb") as f: f.write(pdf.getbuffer())
            st.success(f"✅ PDF uploaded for {lecture_to_edit}")

        # ---- Classwork Control ----
        st.subheader("📚 Classwork Control")
        week_to_control = st.selectbox("Select Week to Open/Close Classwork", lectures_df["Week"].unique())
        if st.button(f"Open Classwork for {week_to_control} (20 mins)"):
            open_classwork(week_to_control)
            st.success(f"Classwork for {week_to_control} is now open for 20 minutes.")
        close_classwork_after_20min()

        # ---- Records ----
        for file,label in [(ATTENDANCE_FILE,"Attendance Records"),
                           (CLASSWORK_FILE,"Classwork Submissions"),
                           (SEMINAR_FILE,"Seminar Submissions")]:
            st.divider()
            st.markdown(f"### {label}")
            if os.path.exists(file):
                df = pd.read_csv(file)
                st.dataframe(df)
                st.download_button(f"Download {label} CSV", df.to_csv(index=False).encode(), file)
            else: st.info(f"No {label.lower()} yet.")
    else:
        if password: st.error("❌ Incorrect password. Try again.")















