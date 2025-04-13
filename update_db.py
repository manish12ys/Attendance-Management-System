import os
import sqlite3
from app import create_app

def update_database():
    """
    Update the database schema to add section_id to the attendance table
    """
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')
    print(f"Connecting to database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    # Create a default section if none exists
    cursor.execute("SELECT COUNT(*) FROM section")
    section_count = cursor.fetchone()[0]
    
    if section_count == 0:
        print("Creating a default section...")
        cursor.execute("""
            INSERT INTO section (name, description, created_at, created_by)
            VALUES ('Default Section', 'Default section for all students and courses', datetime('now'), 1)
        """)
        conn.commit()
        print("Default section created.")
    
    # Get the default section ID
    cursor.execute("SELECT id FROM section LIMIT 1")
    default_section_id = cursor.fetchone()[0]
    print(f"Default section ID: {default_section_id}")
    
    # Update all attendance records to use the default section
    cursor.execute("UPDATE attendance SET section_id = ? WHERE section_id IS NULL", (default_section_id,))
    updated_rows = cursor.rowcount
    conn.commit()
    print(f"Updated {updated_rows} attendance records with default section ID.")
    
    # Add section_id foreign key constraint
    try:
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("BEGIN TRANSACTION")
        
        # Create a temporary table with the correct schema
        cursor.execute("""
            CREATE TABLE attendance_new (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL,
                marked_by INTEGER NOT NULL,
                marked_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (course_id) REFERENCES course (id),
                FOREIGN KEY (section_id) REFERENCES section (id),
                FOREIGN KEY (marked_by) REFERENCES user (id)
            )
        """)
        
        # Copy data from the old table to the new table
        cursor.execute("""
            INSERT INTO attendance_new (id, user_id, course_id, section_id, date, status, marked_by, marked_at)
            SELECT id, user_id, course_id, section_id, date, status, marked_by, marked_at FROM attendance
        """)
        
        # Drop the old table
        cursor.execute("DROP TABLE attendance")
        
        # Rename the new table to the original name
        cursor.execute("ALTER TABLE attendance_new RENAME TO attendance")
        
        cursor.execute("COMMIT")
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("Added foreign key constraint for section_id.")
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Error adding foreign key constraint: {e}")
    
    # Close the connection
    conn.close()
    
    print("Database update completed successfully.")

if __name__ == "__main__":
    update_database()
