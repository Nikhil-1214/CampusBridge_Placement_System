from db_connection import cursor, server, run, show
import hashlib


def hash_password(password):
    """Simple SHA-256 hash for passwords."""
    return hashlib.sha256(password.encode()).hexdigest()


# ── AUTH: Admin Users ──
def add_admin(nsut_id, full_name, email, password):
    return run("""INSERT INTO admin_users (nsut_id, full_name, email, password_hash)
                  VALUES (%s, %s, %s, %s)""",
               (nsut_id, full_name, email, hash_password(password)))

def authenticate_admin(nsut_id, password):
    rows = show("SELECT * FROM admin_users WHERE nsut_id = %s AND password_hash = %s",
                (nsut_id, hash_password(password)))
    return rows[0] if rows else None

def view_admins():
    return show("SELECT admin_id, nsut_id, full_name, email, created_at FROM admin_users")


# ── AUTH: Student Users ──
def add_student_user(nsut_id, student_id, password):
    return run("""INSERT INTO student_users (nsut_id, student_id, password_hash)
                  VALUES (%s, %s, %s)""",
               (nsut_id, student_id, hash_password(password)))

def authenticate_student(nsut_id, password):
    rows = show("""SELECT su.*, s.full_name, s.roll_number, s.email, s.cgpa,
                          s.active_backlogs, s.graduation_year, s.department_id, s.phone
                   FROM student_users su
                   JOIN students s ON s.student_id = su.student_id
                   WHERE su.nsut_id = %s AND su.password_hash = %s""",
                (nsut_id, hash_password(password)))
    return rows[0] if rows else None

def view_student_users():
    return show("""SELECT su.student_user_id, su.nsut_id, s.full_name, s.roll_number, su.created_at
                   FROM student_users su
                   LEFT JOIN students s ON s.student_id = su.student_id""")


def seed_initial_data():
    """Seed initial admin, departments, sample student and jobs if database is empty."""
    # 1. Admin
    admin_rows = show("SELECT COUNT(*) AS cnt FROM admin_users")
    if admin_rows and admin_rows[0]["cnt"] == 0:
        add_admin("ADMIN001", "System Administrator", "admin@nsut.ac.in", "admin123")
        print("Default admin seeded: NSUT ID = ADMIN001, Password = admin123")

    # 2. Departments (NSUT Delhi Branches)
    dept_rows = show("SELECT COUNT(*) AS cnt FROM departments")
    if dept_rows and dept_rows[0]["cnt"] == 0:
        nsut_branches = [
            ("Computer Science and Engineering", "CSE"),
            ("Computer Science and Engineering (Artificial Intelligence)", "CSAI"),
            ("Computer Science and Engineering (Data Science)", "CSDS"),
            ("Computer Science and Engineering (Big Data Analytics)", "CSDA"),
            ("Information Technology", "IT"),
            ("Information Technology (Network & Info Security)", "ITNS"),
            ("Mathematics and Computing", "MAC"),
            ("Electronics and Communication Engineering", "ECE"),
            ("Electronics and Communication (Internet of Things)", "EIOT"),
            ("Electronics and Communication (AI & ML)", "ECAM"),
            ("Electrical Engineering", "EE"),
            ("Instrumentation and Control Engineering", "ICE"),
            ("Mechanical Engineering", "ME"),
            ("Mechanical Engineering (Electric Vehicles)", "MEEV"),
            ("Biotechnology", "BT"),
            ("Civil Engineering", "CE"),
            ("Geoinformatics", "GI"),
        ]
        for name, code in nsut_branches:
            add_department(name, code)

    # 3. Sample Student & Student Login
    stu_rows = show("SELECT COUNT(*) AS cnt FROM students")
    if stu_rows and stu_rows[0]["cnt"] == 0:
        depts = view_departments()
        dept_id = depts[0]["department_id"] if depts else 1
        add_student(dept_id, "2024CS001", "Rohan Sharma", "rohan.sharma@nsut.ac.in", "9876543210", 8.85, 0, 2026)
        new_stu = show("SELECT student_id FROM students WHERE roll_number = '2024CS001'")
        if new_stu:
            sid = new_stu[0]["student_id"]
            add_student_user("2024NSUT1001", sid, "student123")
            print("Default student seeded: NSUT ID = 2024NSUT1001, Password = student123")

    # 4. Sample Companies & Jobs
    comp_rows = show("SELECT COUNT(*) AS cnt FROM companies")
    if comp_rows and comp_rows[0]["cnt"] == 0:
        add_company("Google India", "Technology", "https://careers.google.com", "campus-india@google.com")
        add_company("Microsoft IDC", "Technology", "https://careers.microsoft.com", "idc-campus@microsoft.com")
        comps = view_companies()
        if comps:
            c1_id = comps[0]["company_id"]
            add_job(c1_id, "Software Development Engineer", "Full-time", "Bengaluru / Hyderabad", 28.5, 7.5, 0, "2026, 2027", "2026-12-31")
            if len(comps) > 1:
                c2_id = comps[1]["company_id"]
                add_job(c2_id, "Cloud & Systems Engineer", "Full-time", "Noida", 22.0, 7.0, 1, "2026, 2027", "2026-12-31")

def seed_default_admin():
    seed_initial_data()


# 1. DEPARTMENTS
def add_department(name, code):
    return run("INSERT INTO departments (department_name, department_code) VALUES (%s, %s)",
               (name, code))

def view_departments():
    return show("SELECT * FROM departments")

def update_department(dept_id, name=None, code=None, department_name=None, department_code=None):
    name = department_name if name is None else name
    code = department_code if code is None else code
    return run("""UPDATE departments SET
                  department_name = COALESCE(%s, department_name),
                  department_code = COALESCE(%s, department_code)
                  WHERE department_id = %s""",
               (name, code, dept_id))

def delete_department(dept_id):
    run("UPDATE students SET department_id = NULL WHERE department_id = %s", (dept_id,))
    return run("DELETE FROM departments WHERE department_id = %s", (dept_id,))

def get_department_by_id(dept_id):
    rows = show("SELECT * FROM departments WHERE department_id = %s", (dept_id,))
    return rows[0] if rows else None


# 2. STUDENTS
def add_student(dept, roll, name, email, phone, cgpa, backlogs, year):
    return run("""INSERT INTO students (department_id, roll_number, full_name, email,
                  phone, cgpa, active_backlogs, graduation_year)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
               (dept, roll, name, email, phone, cgpa, backlogs, year))

def view_students():
    return show("""SELECT s.student_id, s.department_id, d.department_name, d.department_code,
                          s.roll_number, s.full_name, s.email, s.phone, s.cgpa,
                          s.active_backlogs, s.graduation_year
                   FROM students s
                   LEFT JOIN departments d ON d.department_id = s.department_id
                   ORDER BY s.student_id ASC""")

def update_student(sid, cgpa=None, backlogs=None, dept=None, roll=None,
                   name=None, email=None, phone=None, year=None):
    return run("""UPDATE students SET
                  department_id = COALESCE(%s, department_id),
                  roll_number = COALESCE(%s, roll_number),
                  full_name = COALESCE(%s, full_name),
                  email = COALESCE(%s, email),
                  phone = COALESCE(%s, phone),
                  cgpa = COALESCE(%s, cgpa),
                  active_backlogs = COALESCE(%s, active_backlogs),
                  graduation_year = COALESCE(%s, graduation_year)
                  WHERE student_id = %s""",
               (dept, roll, name, email, phone, cgpa, backlogs, year, sid))

def delete_student(sid):
    run("DELETE FROM student_users WHERE student_id = %s", (sid,))
    return run("DELETE FROM students WHERE student_id = %s", (sid,))

def search_student(roll):
    return show("SELECT * FROM students WHERE roll_number = %s", (roll,))

def get_student_by_id(sid):
    return show("SELECT * FROM students WHERE student_id = %s", (sid,))


# 3. SKILLS
def add_skill(name):
    return run("INSERT INTO skills (skill_name) VALUES (%s)", (name,))

def view_skills():
    return show("SELECT * FROM skills")

def update_skill(skid, name):
    return run("UPDATE skills SET skill_name = %s WHERE skill_id = %s", (name, skid))

def delete_skill(skid):
    return run("DELETE FROM skills WHERE skill_id = %s", (skid,))

def add_student_skill(sid, skid, level):
    return run("INSERT INTO student_skills VALUES (%s, %s, %s)", (sid, skid, level))

def view_student_skills(sid):
    return show("""SELECT s.skill_name, ss.proficiency_level
                   FROM student_skills ss
                   JOIN skills s ON s.skill_id = ss.skill_id
                   WHERE ss.student_id = %s""", (sid,))


# 4. COMPANIES
def add_company(name, industry, website, email):
    return run("""INSERT INTO companies (company_name, industry, website, contact_email)
                  VALUES (%s, %s, %s, %s)""", (name, industry, website, email))

def view_companies():
    return show("SELECT * FROM companies")

def update_company(cid, name=None, industry=None, website=None, email=None,
                   company_name=None, contact_email=None):
    name = company_name if name is None else name
    email = contact_email if email is None else email
    return run("""UPDATE companies SET
                  company_name = COALESCE(%s, company_name),
                  industry = COALESCE(%s, industry),
                  website = COALESCE(%s, website),
                  contact_email = COALESCE(%s, contact_email)
                  WHERE company_id = %s""",
               (name, industry, website, email, cid))

def delete_company(cid):
    return run("DELETE FROM companies WHERE company_id = %s", (cid,))


# 5. JOBS
def add_job(cid, title, jtype, loc, package, min_cgpa, max_back, years, deadline):
    return run("""INSERT INTO job_profiles (company_id, job_title, job_type, location,
                  package_lpa, min_cgpa, max_backlogs_allowed, eligible_batch_year,
                  application_deadline) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
               (cid, title, jtype, loc, package, min_cgpa, max_back, years, deadline))

def view_jobs():
    return show("""SELECT j.job_id, c.company_name, j.job_title, j.job_type,
                          j.location, j.package_lpa, j.min_cgpa, j.application_deadline
                   FROM job_profiles j JOIN companies c ON c.company_id = j.company_id""")

def update_job(jid, cid=None, title=None, jtype=None, loc=None, package=None,
               min_cgpa=None, max_back=None, years=None, deadline=None,
               company_id=None, job_title=None, job_type=None, location=None,
               package_lpa=None, max_backlogs_allowed=None, eligible_batch_year=None,
               application_deadline=None):
    cid = company_id if cid is None else cid
    title = job_title if title is None else title
    jtype = job_type if jtype is None else jtype
    loc = location if loc is None else loc
    package = package_lpa if package is None else package
    max_back = max_backlogs_allowed if max_back is None else max_back
    years = eligible_batch_year if years is None else years
    deadline = application_deadline if deadline is None else deadline
    return run("""UPDATE job_profiles SET
                  company_id = COALESCE(%s, company_id),
                  job_title = COALESCE(%s, job_title),
                  job_type = COALESCE(%s, job_type),
                  location = COALESCE(%s, location),
                  package_lpa = COALESCE(%s, package_lpa),
                  min_cgpa = COALESCE(%s, min_cgpa),
                  max_backlogs_allowed = COALESCE(%s, max_backlogs_allowed),
                  eligible_batch_year = COALESCE(%s, eligible_batch_year),
                  application_deadline = COALESCE(%s, application_deadline)
                  WHERE job_id = %s""",
               (cid, title, jtype, loc, package, min_cgpa, max_back, years, deadline, jid))

def add_job_skill(jid, skid, level, mandatory):
    return run("INSERT INTO job_skills VALUES (%s, %s, %s, %s)", (jid, skid, level, mandatory))

def delete_job(jid):
    return run("DELETE FROM job_profiles WHERE job_id = %s", (jid,))


# 6. ELIGIBILITY
def jobs_for_student(sid):
    return show("""SELECT j.job_id, c.company_name, j.job_title, j.package_lpa
                   FROM job_profiles j
                   JOIN companies c ON c.company_id = j.company_id
                   JOIN students s ON s.student_id = %s
                   WHERE s.cgpa >= j.min_cgpa
                     AND s.active_backlogs <= j.max_backlogs_allowed
                     AND FIND_IN_SET(s.graduation_year, REPLACE(j.eligible_batch_year, ' ', ''))
                     AND j.application_deadline >= CURDATE()""", (sid,))

def students_for_job(jid):
    return show("""SELECT s.student_id, s.full_name, s.cgpa
                   FROM students s
                   JOIN job_profiles j ON j.job_id = %s
                   WHERE s.cgpa >= j.min_cgpa
                     AND s.active_backlogs <= j.max_backlogs_allowed
                     AND FIND_IN_SET(s.graduation_year, REPLACE(j.eligible_batch_year, ' ', ''))""", (jid,))


# 7. INTERVIEWERS
def add_interviewer(cid, name, desig, email):
    return run("""INSERT INTO interviewers (company_id, full_name, designation, email)
                  VALUES (%s, %s, %s, %s)""", (cid, name, desig, email))

def view_interviewers():
    return show("SELECT * FROM interviewers")

def update_interviewer(iid, cid=None, name=None, desig=None, email=None,
                       company_id=None, full_name=None, designation=None):
    cid = company_id if cid is None else cid
    name = full_name if name is None else name
    desig = designation if desig is None else desig
    return run("""UPDATE interviewers SET
                  company_id = COALESCE(%s, company_id),
                  full_name = COALESCE(%s, full_name),
                  designation = COALESCE(%s, designation),
                  email = COALESCE(%s, email)
                  WHERE interviewer_id = %s""",
               (cid, name, desig, email, iid))

def delete_interviewer(iid):
    run("UPDATE interview_rounds SET interviewer_id = NULL WHERE interviewer_id = %s", (iid,))
    return run("DELETE FROM interviewers WHERE interviewer_id = %s", (iid,))


# 8. PLACEMENT DRIVES
def add_drive(jid, date, venue):
    return run("""INSERT INTO placement_drives (job_id, drive_date, venue_or_mode, drive_status)
                  VALUES (%s, %s, %s, 'Scheduled')""", (jid, date, venue))

def view_drives():
    return show("""SELECT d.drive_id, c.company_name, j.job_title, d.drive_date,
                          d.venue_or_mode, d.drive_status
                   FROM placement_drives d
                   JOIN job_profiles j ON j.job_id = d.job_id
                   JOIN companies c ON c.company_id = j.company_id""")

def update_drive(did, jid=None, date=None, venue=None, status=None):
    return run("""UPDATE placement_drives SET
                  job_id = COALESCE(%s, job_id),
                  drive_date = COALESCE(%s, drive_date),
                  venue_or_mode = COALESCE(%s, venue_or_mode),
                  drive_status = COALESCE(%s, drive_status)
                  WHERE drive_id = %s""",
               (jid, date, venue, status, did))

def update_drive_status(did, status):
    return run("UPDATE placement_drives SET drive_status = %s WHERE drive_id = %s", (status, did))

def delete_drive(did):
    return run("DELETE FROM placement_drives WHERE drive_id = %s", (did,))

def register_for_drive(did, sid):
    return run("""INSERT INTO drive_registrations (drive_id, student_id, registration_date, status)
                  VALUES (%s, %s, CURDATE(), 'Registered')""", (did, sid))

def view_drive_registrations(did):
    return show("""SELECT s.student_id, s.full_name, r.status
                   FROM drive_registrations r
                   JOIN students s ON s.student_id = r.student_id
                   WHERE r.drive_id = %s""", (did,))


# 9. APPLICATIONS
def apply_for_job(sid, jid):
    rows = show("""SELECT (s.cgpa >= j.min_cgpa
                           AND s.active_backlogs <= j.max_backlogs_allowed
                           AND FIND_IN_SET(s.graduation_year, REPLACE(j.eligible_batch_year, ' ', '')) > 0
                           AND j.application_deadline >= CURDATE()) AS eligible
                   FROM students s, job_profiles j
                   WHERE s.student_id = %s AND j.job_id = %s""", (sid, jid))
    if not rows:
        return False, "Student or job not found."
    eligible = rows[0].get("eligible")
    if not eligible:
        return False, "Sorry, student is NOT eligible (or deadline is over)."
    ok = run("""INSERT INTO applications (student_id, job_id, applied_at, status)
                VALUES (%s, %s, CURDATE(), 'Applied')""", (sid, jid))
    if not ok:
        return False, "You have already applied for this job."
    return True, "Applied successfully!"

def view_all_applications():
    return show("""SELECT a.application_id, a.student_id, s.full_name, s.roll_number,
                          j.job_id, c.company_name, j.job_title, a.applied_at, a.status
                   FROM applications a
                   JOIN students s ON s.student_id = a.student_id
                   JOIN job_profiles j ON j.job_id = a.job_id
                   JOIN companies c ON c.company_id = j.company_id""")

def view_student_applications(sid):
    return show("""SELECT a.application_id, c.company_name, j.job_title, a.status
                    FROM applications a
                    JOIN job_profiles j ON j.job_id = a.job_id
                    JOIN companies c ON c.company_id = j.company_id
                    WHERE a.student_id = %s""", (sid,))

def view_job_applicants(jid):
    return show("""SELECT a.application_id, s.full_name, a.status
                   FROM applications a JOIN students s ON s.student_id = a.student_id
                   WHERE a.job_id = %s""", (jid,))

def update_application_status(aid, status):
    return run("UPDATE applications SET status = %s WHERE application_id = %s", (status, aid))

def withdraw_application(aid):
    return run("DELETE FROM applications WHERE application_id = %s", (aid,))


# 10. ASSESSMENTS
def add_assessment(did, atype, when, marks):
    return run("""INSERT INTO assessments (drive_id, assessment_type, scheduled_at, maximum_marks)
                  VALUES (%s, %s, %s, %s)""", (did, atype, when, marks))

def view_assessments():
    return show("SELECT * FROM assessments")

def update_assessment(aid, did=None, atype=None, when=None, marks=None,
                      drive_id=None, assessment_type=None, scheduled_at=None, maximum_marks=None):
    did = drive_id if did is None else did
    atype = assessment_type if atype is None else atype
    when = scheduled_at if when is None else when
    marks = maximum_marks if marks is None else marks
    return run("""UPDATE assessments SET
                  drive_id = COALESCE(%s, drive_id),
                  assessment_type = COALESCE(%s, assessment_type),
                  scheduled_at = COALESCE(%s, scheduled_at),
                  maximum_marks = COALESCE(%s, maximum_marks)
                  WHERE assessment_id = %s""",
               (did, atype, when, marks, aid))

def delete_assessment(aid):
    return run("DELETE FROM assessments WHERE assessment_id = %s", (aid,))

def add_result(aid, sid, marks, cutoff):
    status = "Pass" if float(marks) >= float(cutoff) else "Fail"
    return run("""INSERT INTO assessment_results
                  (assessment_id, student_id, marks_obtained, result_status, evaluated_at)
                  VALUES (%s, %s, %s, %s, NOW())""", (aid, sid, marks, status))

def view_rank_list(aid):
    return show("""SELECT s.full_name, r.marks_obtained, r.result_status
                   FROM assessment_results r
                   JOIN students s ON s.student_id = r.student_id
                   WHERE r.assessment_id = %s
                   ORDER BY r.marks_obtained DESC""", (aid,))


# 11. INTERVIEW ROUNDS
def schedule_round(aid, iid, num, rtype, when):
    return run("""INSERT INTO interview_rounds
                  (application_id, interviewer_id, round_number, round_type, scheduled_at)
                  VALUES (%s, %s, %s, %s, %s)""", (aid, iid, num, rtype, when))

def update_round_result(rid, result, feedback):
    return run("UPDATE interview_rounds SET result = %s, feedback = %s WHERE round_id = %s",
               (result, feedback, rid))

def update_round(rid, aid=None, iid=None, num=None, rtype=None, when=None, result=None, feedback=None):
    if result is not None and feedback is not None and aid is None and iid is None and num is None and rtype is None and when is None:
        return update_round_result(rid, result, feedback)
    return run("""UPDATE interview_rounds SET
                  application_id = COALESCE(%s, application_id),
                  interviewer_id = COALESCE(%s, interviewer_id),
                  round_number = COALESCE(%s, round_number),
                  round_type = COALESCE(%s, round_type),
                  scheduled_at = COALESCE(%s, scheduled_at),
                  result = COALESCE(%s, result),
                  feedback = COALESCE(%s, feedback)
                  WHERE round_id = %s""",
               (aid, iid, num, rtype, when, result, feedback, rid))

def delete_round(rid):
    return run("DELETE FROM interview_rounds WHERE round_id = %s", (rid,))

def view_rounds(aid):
    return show("""SELECT round_id, round_number, round_type, scheduled_at, result, feedback
                   FROM interview_rounds WHERE application_id = %s
                   ORDER BY round_number""", (aid,))

def view_all_rounds():
    return show("""SELECT r.round_id, r.application_id, r.interviewer_id, i.full_name AS interviewer_name,
                          r.round_number, r.round_type, r.scheduled_at, r.result, r.feedback
                   FROM interview_rounds r
                   LEFT JOIN interviewers i ON i.interviewer_id = r.interviewer_id
                   ORDER BY r.scheduled_at DESC""")


# 12. OFFERS
def give_offer(aid, lpa, joining):
    ok = run("""INSERT INTO placement_offers
                (application_id, offered_lpa, offer_date, offer_status, joining_date)
                VALUES (%s, %s, CURDATE(), 'Offered', %s)""", (aid, lpa, joining))
    if ok:
        run("UPDATE applications SET status = 'Selected' WHERE application_id = %s", (aid,))
    return ok

def update_offer_status(oid, status):
    return run("UPDATE placement_offers SET offer_status = %s WHERE offer_id = %s", (status, oid))

def update_offer(oid, lpa=None, joining=None, status=None):
    if status is not None and lpa is None and joining is None:
        return update_offer_status(oid, status)
    return run("""UPDATE placement_offers SET
                  offered_lpa = COALESCE(%s, offered_lpa),
                  joining_date = COALESCE(%s, joining_date),
                  offer_status = COALESCE(%s, offer_status)
                  WHERE offer_id = %s""",
               (lpa, joining, status, oid))

def delete_offer(oid):
    return run("DELETE FROM placement_offers WHERE offer_id = %s", (oid,))

def view_offers():
    return show("""SELECT o.offer_id, s.full_name, s.student_id, c.company_name, o.offered_lpa, o.offer_status
                   FROM placement_offers o
                   JOIN applications a ON a.application_id = o.application_id
                   JOIN students s ON s.student_id = a.student_id
                   JOIN job_profiles j ON j.job_id = a.job_id
                   JOIN companies c ON c.company_id = j.company_id""")


# 13. REPORTS
def report_placed_students():
    return show("""SELECT s.full_name, d.department_name, c.company_name, o.offered_lpa
                   FROM placement_offers o
                   JOIN applications a ON a.application_id = o.application_id
                   JOIN students s ON s.student_id = a.student_id
                   JOIN departments d ON d.department_id = s.department_id
                   JOIN job_profiles j ON j.job_id = a.job_id
                   JOIN companies c ON c.company_id = j.company_id
                   WHERE o.offer_status = 'Accepted'""")

def report_unplaced_students():
    return show("""SELECT student_id, full_name FROM students
                   WHERE student_id NOT IN (
                       SELECT a.student_id FROM applications a
                       JOIN placement_offers o ON o.application_id = a.application_id
                       WHERE o.offer_status = 'Accepted')""")

def report_department_wise():
    return show("""SELECT d.department_name, COUNT(*) AS placed
                   FROM placement_offers o
                   JOIN applications a ON a.application_id = o.application_id
                   JOIN students s ON s.student_id = a.student_id
                   JOIN departments d ON d.department_id = s.department_id
                   WHERE o.offer_status = 'Accepted'
                   GROUP BY d.department_name""")

def report_company_packages():
    return show("""SELECT c.company_name,
                          ROUND(AVG(o.offered_lpa), 2) AS avg_lpa,
                          MAX(o.offered_lpa) AS max_lpa
                   FROM placement_offers o
                   JOIN applications a ON a.application_id = o.application_id
                   JOIN job_profiles j ON j.job_id = a.job_id
                   JOIN companies c ON c.company_id = j.company_id
                   GROUP BY c.company_name""")

def report_placement_percentage():
    tot_rows = show("SELECT COUNT(*) AS total FROM students")
    total = tot_rows[0].get("total", 0) if tot_rows else 0
    placed_rows = show("""SELECT COUNT(DISTINCT a.student_id) AS placed
                          FROM placement_offers o
                          JOIN applications a ON a.application_id = o.application_id
                          WHERE o.offer_status = 'Accepted'""")
    placed = placed_rows[0].get("placed", 0) if placed_rows else 0
    pct = round(placed * 100 / total, 2) if total > 0 else 0
    return {"total": total, "placed": placed, "percentage": pct}

def report_top_packages():
    return show("""SELECT s.full_name, c.company_name, o.offered_lpa
                   FROM placement_offers o
                   JOIN applications a ON a.application_id = o.application_id
                   JOIN students s ON s.student_id = a.student_id
                   JOIN job_profiles j ON j.job_id = a.job_id
                   JOIN companies c ON c.company_id = j.company_id
                   ORDER BY o.offered_lpa DESC LIMIT 5""")
