import os
import sqlite3

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')
print(f"Connecting to database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if tables:
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"  Columns in {table[0]}:")
        for column in columns:
            print(f"    - {column[1]} ({column[2]})")
else:
    print("No tables found in the database.")

# Close the connection
conn.close()
