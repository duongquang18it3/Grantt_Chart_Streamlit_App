import sqlite3

def create_database():
    # Tạo kết nối đến cơ sở dữ liệu SQLite. Nếu file chưa tồn tại, SQLite sẽ tự động tạo file mới.
    conn = sqlite3.connect('project_management.db')
    c = conn.cursor()
    
    # Tạo bảng projects
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            project_name TEXT NOT NULL,
            created_by TEXT NOT NULL
        )
    ''')
    
    # Tạo bảng tasks
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY,
            project_id INTEGER,
            task_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (project_id)
        )
    ''')
    
    # Tạo bảng project_users để liên kết người dùng với các dự án
    c.execute('''
        CREATE TABLE IF NOT EXISTS project_users (
        project_id INTEGER,
        username TEXT,
        role TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (project_id)
    )
    ''')

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()

# Gọi hàm để tạo cơ sở dữ liệu khi chạy ứng dụng
create_database()