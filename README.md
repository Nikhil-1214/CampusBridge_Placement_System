# CampusBridge — NSUT Placement Management System

A full-stack campus placement management portal built with **FastAPI**, **MySQL**, and modern **Glassmorphism UI** with authenticated portals for both Administrators and Students.

---

## 🌟 Key Features

1. **Authentication System (NSUT ID & Password)**:
   - **Admin Authentication**: Access to full database CRUD, drive scheduling, offer issuance, and user management.
   - **Student Authentication**: Access to academic profile, real-time eligibility checking, job applications, and offer acceptance/rejection.
   - SHA-256 hashed password storage in MySQL (`admin_users` and `student_users` tables).
2. **Glassmorphism Design**:
   - Modern dark gradient background with floating ambient light orbs.
   - Translucent frosted glass cards (`backdrop-filter: blur(20px)`), glowing accents, and responsive layout.
   - Interactive role switcher tabs on the login page with quick demo auto-fill.
3. **Database Schema & Placement Pipeline**:
   - Departments, Students, Skills, Student Skills
   - Companies, Job Profiles, Job Skills, Interviewers
   - Placement Drives, Drive Registrations, Assessments, Assessment Results
   - Applications, Interview Rounds, Placement Offers, Analytics & Reports

---

## 🔑 Default Credentials

| Role | NSUT ID | Password | Access Level |
|---|---|---|---|
| **Administrator** | `ADMIN001` | `admin123` | Full admin privileges |
| **Student** | `2024NSUT1001` | `student123` | Student portal (Rohan Sharma) |

*(Admins can create additional Admin and Student login accounts at any time from the **Users & Auth** tab).*

---

## 🚀 How to Run

### 1. Prerequisites
- Python 3.10+
- MySQL Server (running on `localhost:3306`)

### 2. Configure Database (if different from default)
Default connection parameters in `db_connection.py`:
- Host: `localhost`
- User: `root`
- Password: Supports `MYSQL_PASSWORD` env var, `nikhil`, or `27^Someswar_wirE`
- Database: `placement_db` (created automatically on startup)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
uvicorn app:app --reload --port 8000
```

### 5. Access the Web Application
Open your web browser and go to:
**http://localhost:8000**

- **Landing Page**: `http://localhost:8000/`
- **Login Page**: `http://localhost:8000/login`
- **Admin Dashboard**: `http://localhost:8000/admin`
- **Student Dashboard**: `http://localhost:8000/student`

---

## 💻 Terminal CLI Mode (Optional)
If you prefer running via the command line interface:
```bash
python main.py
```
