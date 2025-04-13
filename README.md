# 🎓 Attendance Management System

A web-based solution to efficiently manage student attendance, sections, faculty assignments, leave requests, and reports — all in one unified platform. Built using **Flask** for the backend and **HTML/CSS/JS** for the frontend, this project streamlines educational administration with role-based dashboards and secure access control.

---

## ✨ Features

- 🔐 **User Authentication**  
  Separate logins for Admins, Faculty, and Students.

- 🏫 **Section Management**  
  Create and assign students, teachers, and courses to sections.

- 🧑‍🏫 **Faculty Dashboard**  
  Mark attendance, manage assigned sections, view reports.

- 🎓 **Student Dashboard**  
  View personal attendance, submit leave requests.

- 📅 **Leave Request System**  
  Students can request leave; faculty/admin can approve or reject.

- 📊 **Attendance Reports**  
  Generate and export daily, weekly, or monthly reports by section or student.

- 🧾 **Export Options**  
  Download reports in CSV or PDF format.

- 🎨 **Responsive UI**  
  Sidebar navigation, toggle support, and a clean light/dark theme design.

- 🛠️ **Role-Based Access Control**  
  Permissions enforced based on user roles for added security.

---

## 📁 Project Structure

```
attendance-management-system/
├── app.py                  # Main Flask application file (entry point)
├── models.py               # Database models (SQLAlchemy)
├── extensions.py           # Flask extension initializations (e.g., db, login_manager)
│
├── routes/                 # Route handlers, separated by user roles and features
│   ├── admin.py            # Admin-specific routes (dashboard, user management)
│   ├── faculty.py          # Faculty routes (mark attendance, reports)
│   ├── student.py          # Student routes (view attendance, leave requests)
│   └── section.py          # Routes for managing sections and assignments
│
├── static/                 # Frontend static files
│   ├── css/                # Custom stylesheets (themes, layout)
│   ├── js/                 # JavaScript files (e.g., sidebar toggle, form validation)
│   └── img/                # Image assets (logos, backgrounds)
│
├── templates/              # HTML templates grouped by user role
│   ├── admin/              # Admin dashboard and management templates
│   ├── faculty/            # Faculty interface templates
│   ├── student/            # Student interface templates
│   └── section/            # Section management and assignment templates
│
├── utils/                  # Utility modules for common logic
│   ├── export.py           # Report export utilities (PDF, Excel)
│   └── helpers.py          # Reusable helper functions (e.g., date/time, filters)
│
└── requirements.txt        # Python dependencies list
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   https://github.com/manish12ys/Attendance-Management-System.git
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
   Open your browser and navigate to:  
   `http://127.0.0.1:5000`

---

## 🔐 Default Admin Credentials

Use the following credentials for the first login:

- **Email**: `admin@example.com`  
- **Password**: `admin123`

> ⚠️ **Important:** Change the default admin credentials after first login.

---

## 📌 Future Enhancements

- ✅ Section-wise attendance analytics (charts)
---

## 🧑‍💻 Technologies Used

- **Backend**: Python, Flask, SQLAlchemy  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: SQLite (easily upgradable to PostgreSQL/MySQL)  
- **Extensions**: Flask-Login, Flask-WTF, Flask-Migrate (optional)


---
