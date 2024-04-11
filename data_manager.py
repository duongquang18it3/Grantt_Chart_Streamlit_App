import pandas as pd
import streamlit as st
import sqlite3

def load_projects(user, task_only=False):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        if task_only:
            query = """
                SELECT task_name AS Task, start_date AS Start, end_date AS Finish, assigned_to AS Resource
                FROM tasks t JOIN project_users pu ON t.project_id = pu.project_id
                WHERE pu.username = ?
            """
        else:
            query = """
                SELECT p.project_name AS Task, t.start_date AS Start, t.end_date AS Finish, t.assigned_to AS Resource
                FROM tasks t 
                JOIN projects p ON t.project_id = p.project_id 
                JOIN project_users pu ON t.project_id = pu.project_id
                WHERE pu.username = ?
            """
        c.execute(query, (user,))
        results = c.fetchall()
        if results:
            return pd.DataFrame(results, columns=['Task', 'Start', 'Finish', 'Resource'])
        else:
            return pd.DataFrame(columns=['Task', 'Start', 'Finish', 'Resource'])  # Return empty DataFrame if no results

def add_project(project_name, creator):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO projects (project_name, created_by) VALUES (?, ?)", (project_name, creator))
        project_id = c.lastrowid
        for user in ['admin', 'manager', 'employee1', 'employee2']:
            c.execute("INSERT INTO project_users (project_id, username) VALUES (?, ?)", (project_id, user))
        conn.commit()
        return project_id

def assign_project_to_user(project_id, username, role):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO project_users (project_id, username, role) VALUES (?, ?, ?)", (project_id, username, role))
        conn.commit()

def add_task(project_id, task_name, start_date, end_date, assigned_to):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (project_id, task_name, start_date, end_date, assigned_to) VALUES (?, ?, ?, ?, ?)",
                  (project_id, task_name, start_date, end_date, assigned_to))
        conn.commit()

def load_tasks(project_id):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_id, task_name, start_date, end_date, assigned_to FROM tasks WHERE project_id = ?", (project_id,))
        tasks = c.fetchall()
        if tasks:
            return tasks
        else:
            return []  # Return empty list if no tasks

        
def load_assigned_projects(username, role):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        query = """
            SELECT DISTINCT p.project_name
            FROM projects p
            JOIN project_users pu ON p.project_id = pu.project_id
            WHERE pu.username = ? AND pu.role = ?
        """
        c.execute(query, (username, role))
        results = c.fetchall()
        if results:
            return [result[0] for result in results]
        else:
            return []###

def load_projects_by_name(project_name):
    with sqlite3.connect('project_management.db') as conn:
        c = conn.cursor()
        query = """
            SELECT task_name AS Task, start_date AS Start, end_date AS Finish, assigned_to AS Resource
            FROM tasks t 
            JOIN projects p ON t.project_id = p.project_id
            WHERE p.project_name = ?
        """
        c.execute(query, (project_name,))
        results = c.fetchall()
        if results:
            return pd.DataFrame(results, columns=['Task', 'Start', 'Finish', 'Resource'])
        else:
            return pd.DataFrame(columns=['Task', 'Start', 'Finish', 'Resource'])  # Return empty DataFrame if no results


# Trong hàm create_task_form của data_manager.py
def create_task_form(container, username):
    with container.form("task_form"):
        new_project = container.text_input("Enter New Project Name")
        task_name = container.text_input("Task Name")
        start_date = container.date_input("Start Date")
        end_date = container.date_input("End Date")
        assignees = container.multiselect("Assign to", ["manager", "employee1", "employee2"])
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if new_project:
                project_id = add_project(new_project, username)
                for user in assignees:
                    role = user  # assuming the role is same as the username for simplicity
                    assign_project_to_user(project_id, user, role)
            else:
                st.error("Project name is required.")
                return None

            for assignee in assignees:
                add_task(project_id, task_name, start_date, end_date, assignee)

            task_df = [(task_name, start_date, end_date, assignee) for assignee in assignees]
            return task_df

    return None


