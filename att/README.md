# Attendance Management System

A comprehensive web-based solution for managing attendance in educational institutions and organizations. Built with Python Flask, this system offers role-based access control, real-time attendance tracking, and detailed reporting.

![Attendance Management System](static/img/readme-banner.png)

## Features

### Core Functionality
- **Role-Based Access Control**: Different interfaces for administrators, faculty, and students
- **Attendance Tracking**: Mark, update, and view attendance records
- **Section Management**: Create and manage sections with assigned students, teachers, and courses
- **Reporting**: Generate and export attendance reports in various formats
- **Leave Management**: Request and approve leaves with proper documentation

### User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Mode**: Choose between dark and light themes with a violet color scheme
- **Intuitive Interface**: User-friendly design for easy navigation and operation

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **Data Export**: CSV, PDF

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/attendance-management-system.git
   cd attendance-management-system
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Default Credentials

The system comes with a default admin account for initial setup:

- **Email**: admin@example.com
- **Password**: admin123

> **Important**: Change these credentials immediately after first login for security purposes.

## Usage Guide

### Administrator
- Manage users, courses, and sections
- View and generate attendance reports
- Approve leave requests
- Configure system settings

### Faculty
- Mark attendance for assigned courses
- View attendance statistics
- Manage assigned sections
- Submit leave requests

### Student
- View personal attendance records
- Check attendance statistics
- Submit leave requests

## Project Structure

```
attendance-management-system/
├── app.py                  # Main application file
├── models.py               # Database models
├── extensions.py           # Flask extensions
├── routes/                 # Route handlers
│   ├── admin.py            # Admin routes
│   ├── faculty.py          # Faculty routes
│   ├── student.py          # Student routes
│   └── section.py          # Section management routes
├── static/                 # Static files
│   ├── css/                # CSS files
│   ├── js/                 # JavaScript files
│   └── img/                # Images
├── templates/              # HTML templates
│   ├── admin/              # Admin templates
│   ├── faculty/            # Faculty templates
│   ├── student/            # Student templates
│   └── section/            # Section templates
├── utils/                  # Utility functions
│   ├── export.py           # Export utilities
│   └── helpers.py          # Helper functions
└── requirements.txt        # Project dependencies
```

## Customization

### Themes
The system supports both light and dark modes with a violet color scheme. You can customize the colors by modifying the `themes.css` file in the `static/css` directory.

### Adding New Features
The modular structure makes it easy to add new features:
1. Create new routes in the appropriate route file
2. Add corresponding templates in the templates directory
3. Update the navigation menu to include the new feature

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)

---

Developed with ❤️ for educational institutions and organizations.
# Attendance-Management-System
