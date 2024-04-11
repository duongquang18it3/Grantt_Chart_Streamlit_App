import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
from data_manager import assign_project_to_user, add_project, load_projects, create_task_form, add_task, load_tasks
from gantt_chart import display_gantt
from data_manager import load_assigned_projects, load_projects_by_name

# Page configuration
st.set_page_config(page_title="Epiklah", page_icon="favicon.ico", layout="wide")

def load_css():
    st.markdown("""
        <style>
        /* Add your CSS here */
        </style>
    """, unsafe_allow_html=True)

load_css()

# User data
name = ["Admin", "Manager", "Employee1", "Employee2"]
username = ["admin", "manager", "employee1", "employee2"]

# Load hashed passwords from a pickle file
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

# Setup authenticator
authenticator = stauth.Authenticate(name, username, hashed_passwords, "login_form1", "111111", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login('Login', 'main')

# Initialize or clear session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame()

if authentication_status:
    st.sidebar.title(f"Welcome {name}")
   
    authenticator.logout("Logout", "sidebar")

    if username == 'admin':
        projects = load_projects(username)
        
        st.sidebar.title("Project Management")
        st.sidebar.subheader("Create Task")
        task_df = create_task_form(st.sidebar, username)
        if task_df is not None:
            task_df = pd.DataFrame(task_df, columns=['Task', 'Start', 'Finish', 'Resource'])  # Chuyển đổi danh sách thành DataFrame
            st.session_state.tasks = pd.concat([st.session_state.tasks, task_df], ignore_index=True)

        # Hiển thị dropdown dự án
        project_selection = st.selectbox("Select Project", projects['Task'].unique())
        selected_project = projects[projects['Task'] == project_selection]

        # Hiển thị biểu đồ Gantt cho dự án được chọn
        if not selected_project.empty:
            display_gantt(selected_project)

    elif username in ['manager']:
        assigned_projects = load_assigned_projects(username, 'manager')
        if assigned_projects:
            project_selection = st.sidebar.selectbox("Select Project", assigned_projects)
            selected_project = load_projects_by_name(project_selection)
            if not selected_project.empty:
                st.write(f"Selected Project: {project_selection}")
                display_gantt(selected_project)
                
        else:
            st.sidebar.info("You have not been assigned to any projects.")
    elif username in ['employee1']:
        assigned_projects = load_assigned_projects(username, 'employee1')
        if assigned_projects:
            project_selection = st.sidebar.selectbox("Select Project", assigned_projects)
            selected_project = load_projects_by_name(project_selection)
            if not selected_project.empty:
                st.write(f"Selected Project: {project_selection}")
                display_gantt(selected_project)
                
        else:
            st.sidebar.info("You have not been assigned to any projects.")
    elif username in ['employee2']:
        assigned_projects = load_assigned_projects(username, 'employee2')
        if assigned_projects:
            project_selection = st.sidebar.selectbox("Select Project", assigned_projects)
            selected_project = load_projects_by_name(project_selection)
            if not selected_project.empty:
                st.write(f"Selected Project: {project_selection}")
                display_gantt(selected_project)
                
        else:
            st.sidebar.info("You have not been assigned to any projects.")
else:
    st.error("Username/password is incorrect")



def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False



if __name__ == "__main__":
    main()
