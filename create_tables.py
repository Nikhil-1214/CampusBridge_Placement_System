from db_connection import cursor, server

TABLES = [
    """CREATE TABLE IF NOT EXISTS admin_users (
        admin_id INT AUTO_INCREMENT PRIMARY KEY,
        nsut_id VARCHAR(20) UNIQUE NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",

    """CREATE TABLE IF NOT EXISTS departments (
        department_id INT AUTO_INCREMENT PRIMARY KEY,
        department_name VARCHAR(100) UNIQUE,
        department_code VARCHAR(20) UNIQUE)""",

    """CREATE TABLE IF NOT EXISTS students (
        student_id INT AUTO_INCREMENT PRIMARY KEY,
        department_id INT,
        roll_number VARCHAR(20) UNIQUE,
        full_name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        phone VARCHAR(15),
        cgpa DECIMAL(3,2),
        active_backlogs INT,
        graduation_year YEAR,
        FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL)""",

    """CREATE TABLE IF NOT EXISTS student_users (
        student_user_id INT AUTO_INCREMENT PRIMARY KEY,
        nsut_id VARCHAR(20) UNIQUE NOT NULL,
        student_id INT,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS skills (
        skill_id INT AUTO_INCREMENT PRIMARY KEY,
        skill_name VARCHAR(100) UNIQUE)""",

    """CREATE TABLE IF NOT EXISTS student_skills (
        student_id INT,
        skill_id INT,
        proficiency_level VARCHAR(50),
        PRIMARY KEY (student_id, skill_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS companies (
        company_id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(100),
        industry VARCHAR(100),
        website VARCHAR(100),
        contact_email VARCHAR(100))""",

    """CREATE TABLE IF NOT EXISTS job_profiles (
        job_id INT AUTO_INCREMENT PRIMARY KEY,
        company_id INT,
        job_title VARCHAR(100),
        job_type VARCHAR(50),
        location VARCHAR(100),
        package_lpa DECIMAL(10,2),
        min_cgpa DECIMAL(3,2),
        max_backlogs_allowed INT,
        eligible_batch_year VARCHAR(20),
        application_deadline DATE,
        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS job_skills (
        job_id INT,
        skill_id INT,
        required_level VARCHAR(50),
        is_mandatory BOOLEAN,
        PRIMARY KEY (job_id, skill_id),
        FOREIGN KEY (job_id) REFERENCES job_profiles(job_id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS interviewers (
        interviewer_id INT AUTO_INCREMENT PRIMARY KEY,
        company_id INT,
        full_name VARCHAR(100),
        designation VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS applications (
        application_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        job_id INT,
        applied_at DATE,
        status VARCHAR(50),
        UNIQUE (student_id, job_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES job_profiles(job_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS interview_rounds (
        round_id INT AUTO_INCREMENT PRIMARY KEY,
        application_id INT,
        interviewer_id INT,
        round_number INT,
        round_type VARCHAR(50),
        scheduled_at DATETIME,
        result VARCHAR(50),
        feedback TEXT,
        UNIQUE (application_id, round_number),
        FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
        FOREIGN KEY (interviewer_id) REFERENCES interviewers(interviewer_id) ON DELETE SET NULL)""",

    """CREATE TABLE IF NOT EXISTS placement_drives (
        drive_id INT AUTO_INCREMENT PRIMARY KEY,
        job_id INT,
        drive_date DATE,
        venue_or_mode VARCHAR(50),
        drive_status VARCHAR(50),
        FOREIGN KEY (job_id) REFERENCES job_profiles(job_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS drive_registrations (
        registration_id INT AUTO_INCREMENT PRIMARY KEY,
        drive_id INT,
        student_id INT,
        registration_date DATE,
        status VARCHAR(50),
        UNIQUE (drive_id, student_id),
        FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS assessments (
        assessment_id INT AUTO_INCREMENT PRIMARY KEY,
        drive_id INT,
        assessment_type VARCHAR(50),
        scheduled_at DATETIME,
        maximum_marks INT,
        FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS assessment_results (
        result_id INT AUTO_INCREMENT PRIMARY KEY,
        assessment_id INT,
        student_id INT,
        marks_obtained DECIMAL(5,2),
        result_status VARCHAR(50),
        evaluated_at DATETIME,
        UNIQUE (assessment_id, student_id),
        FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE)""",

    """CREATE TABLE IF NOT EXISTS placement_offers (
        offer_id INT AUTO_INCREMENT PRIMARY KEY,
        application_id INT UNIQUE,
        offered_lpa DECIMAL(10,2),
        offer_date DATE,
        offer_status VARCHAR(50),
        joining_date DATE,
        FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE)""",
]


TABLE_NAMES = [
    "admin_users",
    "departments", "students", "student_users", "skills", "student_skills", "companies",
    "job_profiles", "job_skills", "interviewers", "applications",
    "interview_rounds", "placement_drives", "drive_registrations",
    "assessments", "assessment_results", "placement_offers",
]


def create_tables():
    for t in TABLES:
        cursor.execute(t)
    server.commit()
    print("All tables are ready.")


def drop_tables():
    """Deletes all tables (children first). Use only for a fresh start."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for name in reversed(TABLE_NAMES):
        cursor.execute("DROP TABLE IF EXISTS " + name)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    server.commit()
    print("All tables dropped.")


if __name__ == "__main__":
    create_tables()
