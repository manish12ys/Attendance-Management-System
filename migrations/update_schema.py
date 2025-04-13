import sqlite3
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

def update_schema():
    """
    Update the database schema to add section_id to the attendance table
    """
    app = create_app()

    with app.app_context():
        # Connect to the database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'attendance.db')
        print(f"Connecting to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if section_id column exists
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

if __name__ == "__main__":
    update_schema()
