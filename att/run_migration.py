from migrations.add_section_id_to_attendance import migrate_attendance_data

if __name__ == "__main__":
    print("Starting migration to add section_id to attendance records...")
    migrate_attendance_data()
    print("Migration completed successfully!")
