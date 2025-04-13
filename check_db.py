import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')
print(f"Connecting to database at: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(f"- {table[0]}")

# Close the connection
conn.close()
