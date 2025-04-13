import os
import sqlite3
from app import create_app

def fix_sections():
    """
    Fix the sections implementation by modifying the Attendance model query
    """
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')
    print(f"Connecting to database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if attendance table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
    if not cursor.fetchone():
        print("Attendance table does not exist. Creating it...")
        cursor.execute("""
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL,
                marked_by INTEGER NOT NULL,
                marked_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (course_id) REFERENCES course (id),
                FOREIGN KEY (marked_by) REFERENCES user (id)
            )
        """)
        conn.commit()
        print("Attendance table created.")
    
    # Check if section_id column exists in attendance table
    cursor.execute("PRAGMA table_info(attendance)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'section_id' not in column_names:
        print("Adding section_id column to attendance table...")
        cursor.execute("ALTER TABLE attendance ADD COLUMN section_id INTEGER")
        conn.commit()
        print("Column added successfully.")
    else:
        print("section_id column already exists.")
    
    # Close the connection
    conn.close()
    
    print("Sections fix completed successfully.")

if __name__ == "__main__":
    fix_sections()
