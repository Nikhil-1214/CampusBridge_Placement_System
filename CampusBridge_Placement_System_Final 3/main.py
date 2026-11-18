import sys
from db_connection import cursor, server
from create_tables import create_tables
from crud_operations import *


def display(data):
    """Print query results in a clean human-readable format."""
    if not data:
        print("No records found.")
        return
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
        return
    if isinstance(data, list):
        for i, row in enumerate(data, 1):
            if isinstance(row, dict):
                print(f"[{i}] " + " | ".join(f"{k}: {v}" for k, v in row.items()))
            else:
                print(f"[{i}] {row}")


def run_menu(title, options):
    while True:
        print("\n----", title, "----")
        for number in options:
            print(number + ".", options[number][0])
        print("0. Back")
        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
        elif choice in options:
            try:
                options[choice][1]()
            except Exception as e:
                print("Error executing operation:", e)
        else:
            print("Invalid choice, try again.")


# ── 1. STUDENT & DEPARTMENT & SKILL MENU ──
def student_menu():
    def cli_add_student():
        dept = int(input("Department ID: "))
        roll = input("Roll Number: ")
        name = input("Full Name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        cgpa = float(input("CGPA: "))
        backlogs = int(input("Active Backlogs: "))
        year = int(input("Graduation Year: "))
        if add_student(dept, roll, name, email, phone, cgpa, backlogs, year):
            print("Student added successfully!")
        else:
            print("Failed to add student.")

    def cli_search_student():
        roll = input("Enter Roll Number: ").strip()
        display(search_student(roll))

    def cli_update_student():
        sid = int(input("Enter Student ID to update: "))
        cgpa_s = input("New CGPA (press Enter to keep unchanged): ").strip()
        back_s = input("New Backlogs (press Enter to keep unchanged): ").strip()
        cgpa = float(cgpa_s) if cgpa_s else None
        backlogs = int(back_s) if back_s else None
        if update_student(sid, cgpa=cgpa, backlogs=backlogs):
            print("Student updated successfully!")
        else:
            print("Failed to update student.")

    def cli_delete_student():
        sid = int(input("Enter Student ID to delete: "))
        if delete_student(sid):
            print("Student deleted successfully!")
        else:
            print("Failed to delete student.")

    def cli_add_dept():
        name = input("Department Name: ")
        code = input("Department Code: ")
        if add_department(name, code):
            print("Department added successfully!")
        else:
            print("Failed to add department.")

    def cli_update_dept():
        did = int(input("Department ID to update: "))
        name = input("New Department Name: ")
        code = input("New Department Code: ")
        if update_department(did, name, code):
            print("Department updated successfully!")
        else:
            print("Failed to update department.")

    def cli_delete_dept():
        did = int(input("Department ID to delete: "))
        if delete_department(did):
            print("Department deleted successfully!")
        else:
            print("Failed to delete department.")

    def cli_add_skill():
        name = input("Skill Name: ")
        if add_skill(name):
            print("Skill added successfully!")
        else:
            print("Failed to add skill.")

    def cli_update_skill():
        skid = int(input("Skill ID to update: "))
        name = input("New Skill Name: ")
        if update_skill(skid, name):
            print("Skill updated successfully!")
        else:
            print("Failed to update skill.")

    def cli_delete_skill():
        skid = int(input("Skill ID to delete: "))
        if delete_skill(skid):
            print("Skill deleted successfully!")
        else:
            print("Failed to delete skill.")

    def cli_add_stu_skill():
        sid = int(input("Student ID: "))
        skid = int(input("Skill ID: "))
        lvl = input("Proficiency Level (e.g. Beginner/Intermediate/Expert): ")
        if add_student_skill(sid, skid, lvl):
            print("Skill mapped to student!")
        else:
            print("Failed to map skill.")

    def cli_view_stu_skills():
        sid = int(input("Student ID: "))
        display(view_student_skills(sid))

    run_menu("STUDENT MENU", {
        "1": ("Add student", cli_add_student),
        "2": ("View all students", lambda: display(view_students())),
        "3": ("Search by roll number", cli_search_student),
        "4": ("Update student", cli_update_student),
        "5": ("Delete student", cli_delete_student),
        "6": ("Add department", cli_add_dept),
        "7": ("View departments", lambda: display(view_departments())),
        "8": ("Update department", cli_update_dept),
        "9": ("Delete department", cli_delete_dept),
        "10": ("Add skill", cli_add_skill),
        "11": ("View skills", lambda: display(view_skills())),
        "12": ("Update skill", cli_update_skill),
        "13": ("Delete skill", cli_delete_skill),
        "14": ("Add skill to student", cli_add_stu_skill),
        "15": ("View student's skills", cli_view_stu_skills),
    })


# ── 2. COMPANY & JOB & INTERVIEWER MENU ──
def company_menu():
    def cli_add_comp():
        name = input("Company Name: ")
        ind = input("Industry: ")
        web = input("Website: ")
        email = input("Contact Email: ")
        if add_company(name, ind, web, email):
            print("Company added successfully!")
        else:
            print("Failed to add company.")

    def cli_update_comp():
        cid = int(input("Company ID to update: "))
        name = input("Company Name: ")
        ind = input("Industry: ")
        web = input("Website: ")
        email = input("Contact Email: ")
        if update_company(cid, name, ind, web, email):
            print("Company updated successfully!")
        else:
            print("Failed to update company.")

    def cli_delete_comp():
        cid = int(input("Company ID to delete: "))
        if delete_company(cid):
            print("Company deleted successfully!")
        else:
            print("Failed to delete company.")

    def cli_add_job():
        cid = int(input("Company ID: "))
        title = input("Job Title: ")
        jtype = input("Job Type (e.g. Full-time/Internship): ")
        loc = input("Location: ")
        pkg = float(input("Package (LPA): "))
        cgpa = float(input("Minimum CGPA: "))
        back = int(input("Max Backlogs Allowed: "))
        batch = input("Eligible Batch Years (e.g. 2026, 2027): ")
        dead = input("Application Deadline (YYYY-MM-DD): ")
        if add_job(cid, title, jtype, loc, pkg, cgpa, back, batch, dead):
            print("Job added successfully!")
        else:
            print("Failed to add job.")

    def cli_update_job():
        jid = int(input("Job ID to update: "))
        cid = int(input("Company ID: "))
        title = input("Job Title: ")
        jtype = input("Job Type: ")
        loc = input("Location: ")
        pkg = float(input("Package (LPA): "))
        cgpa = float(input("Minimum CGPA: "))
        back = int(input("Max Backlogs Allowed: "))
        batch = input("Eligible Batch Years: ")
        dead = input("Application Deadline (YYYY-MM-DD): ")
        if update_job(jid, cid, title, jtype, loc, pkg, cgpa, back, batch, dead):
            print("Job updated successfully!")
        else:
            print("Failed to update job.")

    def cli_add_job_skill():
        jid = int(input("Job ID: "))
        skid = int(input("Skill ID: "))
        lvl = input("Required Level: ")
        mand = input("Is Mandatory? (1 for Yes, 0 for No): ").strip() == "1"
        if add_job_skill(jid, skid, lvl, mand):
            print("Required skill added to job!")
        else:
            print("Failed to add skill to job.")

    def cli_delete_job():
        jid = int(input("Job ID to delete: "))
        if delete_job(jid):
            print("Job deleted successfully!")
        else:
            print("Failed to delete job.")

    def cli_add_iv():
        cid = int(input("Company ID: "))
        name = input("Interviewer Full Name: ")
        desig = input("Designation: ")
        email = input("Email: ")
        if add_interviewer(cid, name, desig, email):
            print("Interviewer added successfully!")
        else:
            print("Failed to add interviewer.")

    def cli_update_iv():
        iid = int(input("Interviewer ID to update: "))
        cid = int(input("Company ID: "))
        name = input("Interviewer Full Name: ")
        desig = input("Designation: ")
        email = input("Email: ")
        if update_interviewer(iid, cid, name, desig, email):
            print("Interviewer updated successfully!")
        else:
            print("Failed to update interviewer.")

    def cli_delete_iv():
        iid = int(input("Interviewer ID to delete: "))
        if delete_interviewer(iid):
            print("Interviewer deleted successfully!")
        else:
            print("Failed to delete interviewer.")

    run_menu("COMPANY AND JOB MENU", {
        "1": ("Add company", cli_add_comp),
        "2": ("View companies", lambda: display(view_companies())),
        "3": ("Update company", cli_update_comp),
        "4": ("Delete company", cli_delete_comp),
        "5": ("Add job", cli_add_job),
        "6": ("View jobs", lambda: display(view_jobs())),
        "7": ("Update job", cli_update_job),
        "8": ("Add required skill to job", cli_add_job_skill),
        "9": ("Delete job", cli_delete_job),
        "10": ("Add interviewer", cli_add_iv),
        "11": ("View interviewers", lambda: display(view_interviewers())),
        "12": ("Update interviewer", cli_update_iv),
        "13": ("Delete interviewer", cli_delete_iv),
    })


# ── 3. ELIGIBILITY MENU ──
def eligibility_menu():
    def cli_jobs_for_stu():
        sid = int(input("Student ID: "))
        display(jobs_for_student(sid))

    def cli_stu_for_job():
        jid = int(input("Job ID: "))
        display(students_for_job(jid))

    run_menu("ELIGIBILITY MENU", {
        "1": ("Jobs a student is eligible for", cli_jobs_for_stu),
        "2": ("Students eligible for a job", cli_stu_for_job),
    })


# ── 4. PLACEMENT DRIVE MENU ──
def drive_menu():
    def cli_add_drive():
        jid = int(input("Job ID: "))
        date = input("Drive Date (YYYY-MM-DD): ")
        venue = input("Venue / Mode (e.g. Audi / Online): ")
        if add_drive(jid, date, venue):
            print("Drive created successfully!")
        else:
            print("Failed to create drive.")

    def cli_update_drive():
        did = int(input("Drive ID to update: "))
        venue = input("New Venue (press Enter to skip): ").strip() or None
        status = input("New Status (Scheduled/Ongoing/Completed/Cancelled, press Enter to skip): ").strip() or None
        if update_drive(did, venue=venue, status=status):
            print("Drive updated successfully!")
        else:
            print("Failed to update drive.")

    def cli_update_drive_status():
        did = int(input("Drive ID: "))
        status = input("New Status: ")
        if update_drive_status(did, status):
            print("Drive status updated!")
        else:
            print("Failed to update drive status.")

    def cli_delete_drive():
        did = int(input("Drive ID to delete: "))
        if delete_drive(did):
            print("Drive deleted successfully!")
        else:
            print("Failed to delete drive.")

    def cli_reg_drive():
        did = int(input("Drive ID: "))
        sid = int(input("Student ID: "))
        if register_for_drive(did, sid):
            print("Student registered for drive!")
        else:
            print("Registration failed.")

    def cli_view_drive_regs():
        did = int(input("Drive ID: "))
        display(view_drive_registrations(did))

    run_menu("PLACEMENT DRIVE MENU", {
        "1": ("Create drive", cli_add_drive),
        "2": ("View drives", lambda: display(view_drives())),
        "3": ("Update drive", cli_update_drive),
        "4": ("Update drive status", cli_update_drive_status),
        "5": ("Delete drive", cli_delete_drive),
        "6": ("Register student for drive", cli_reg_drive),
        "7": ("View drive registrations", cli_view_drive_regs),
    })


# ── 5. APPLICATION MENU ──
def application_menu():
    def cli_apply():
        sid = int(input("Student ID: "))
        jid = int(input("Job ID: "))
        ok, msg = apply_for_job(sid, jid)
        print(msg)

    def cli_stu_apps():
        sid = int(input("Student ID: "))
        display(view_student_applications(sid))

    def cli_job_apps():
        jid = int(input("Job ID: "))
        display(view_job_applicants(jid))

    def cli_update_app_status():
        aid = int(input("Application ID: "))
        status = input("New Status (Applied/Shortlisted/Selected/Rejected): ")
        if update_application_status(aid, status):
            print("Application status updated!")
        else:
            print("Failed to update status.")

    def cli_withdraw():
        aid = int(input("Application ID to withdraw: "))
        if withdraw_application(aid):
            print("Application withdrawn successfully!")
        else:
            print("Failed to withdraw application.")

    run_menu("APPLICATION MENU", {
        "1": ("Apply for job", cli_apply),
        "2": ("View all applications", lambda: display(view_all_applications())),
        "3": ("View a student's applications", cli_stu_apps),
        "4": ("View applicants of a job", cli_job_apps),
        "5": ("Update application status", cli_update_app_status),
        "6": ("Withdraw application", cli_withdraw),
    })


# ── 6. ASSESSMENT MENU ──
def assessment_menu():
    def cli_add_as():
        did = int(input("Drive ID: "))
        atype = input("Assessment Type (e.g. Aptitude/Coding): ")
        when = input("Scheduled At (YYYY-MM-DD HH:MM:SS): ")
        marks = int(input("Maximum Marks: "))
        if add_assessment(did, atype, when, marks):
            print("Assessment added successfully!")
        else:
            print("Failed to add assessment.")

    def cli_update_as():
        aid = int(input("Assessment ID to update: "))
        did = int(input("Drive ID: "))
        atype = input("Assessment Type: ")
        when = input("Scheduled At (YYYY-MM-DD HH:MM:SS): ")
        marks = int(input("Maximum Marks: "))
        if update_assessment(aid, did, atype, when, marks):
            print("Assessment updated successfully!")
        else:
            print("Failed to update assessment.")

    def cli_delete_as():
        aid = int(input("Assessment ID to delete: "))
        if delete_assessment(aid):
            print("Assessment deleted successfully!")
        else:
            print("Failed to delete assessment.")

    def cli_add_result():
        aid = int(input("Assessment ID: "))
        sid = int(input("Student ID: "))
        marks = float(input("Marks Obtained: "))
        cutoff = float(input("Cutoff Marks: "))
        if add_result(aid, sid, marks, cutoff):
            print("Result recorded successfully!")
        else:
            print("Failed to record result.")

    def cli_view_ranks():
        aid = int(input("Assessment ID: "))
        display(view_rank_list(aid))

    run_menu("ASSESSMENT MENU", {
        "1": ("Add assessment", cli_add_as),
        "2": ("View assessments", lambda: display(view_assessments())),
        "3": ("Update assessment", cli_update_as),
        "4": ("Delete assessment", cli_delete_as),
        "5": ("Enter student result", cli_add_result),
        "6": ("View rank list", cli_view_ranks),
    })


# ── 7. INTERVIEW MENU ──
def interview_menu():
    def cli_schedule_round():
        aid = int(input("Application ID: "))
        iid = int(input("Interviewer ID: "))
        num = int(input("Round Number: "))
        rtype = input("Round Type (Technical/HR): ")
        when = input("Scheduled At (YYYY-MM-DD HH:MM:SS): ")
        if schedule_round(aid, iid, num, rtype, when):
            print("Interview round scheduled!")
        else:
            print("Failed to schedule round.")

    def cli_update_round_result():
        rid = int(input("Round ID: "))
        res = input("Result (Pass/Fail/Pending): ")
        fb = input("Feedback: ")
        if update_round_result(rid, res, fb):
            print("Round result updated!")
        else:
            print("Failed to update round result.")

    def cli_delete_round():
        rid = int(input("Round ID to delete: "))
        if delete_round(rid):
            print("Round deleted successfully!")
        else:
            print("Failed to delete round.")

    def cli_view_rounds():
        aid = int(input("Application ID: "))
        display(view_rounds(aid))

    run_menu("INTERVIEW MENU", {
        "1": ("Schedule interview round", cli_schedule_round),
        "2": ("Update round result", cli_update_round_result),
        "3": ("Delete interview round", cli_delete_round),
        "4": ("View rounds of an application", cli_view_rounds),
        "5": ("View all rounds", lambda: display(view_all_rounds())),
    })


# ── 8. OFFER MENU ──
def offer_menu():
    def cli_give_offer():
        aid = int(input("Application ID: "))
        lpa = float(input("Offered Package (LPA): "))
        join = input("Joining Date (YYYY-MM-DD): ")
        if give_offer(aid, lpa, join):
            print("Offer issued successfully!")
        else:
            print("Failed to issue offer.")

    def cli_update_offer_status():
        oid = int(input("Offer ID: "))
        status = input("New Status (Offered/Accepted/Rejected): ")
        if update_offer_status(oid, status):
            print("Offer status updated!")
        else:
            print("Failed to update offer status.")

    def cli_delete_offer():
        oid = int(input("Offer ID to delete: "))
        if delete_offer(oid):
            print("Offer deleted successfully!")
        else:
            print("Failed to delete offer.")

    run_menu("OFFER MENU", {
        "1": ("Give offer", cli_give_offer),
        "2": ("Update offer status", cli_update_offer_status),
        "3": ("Delete offer", cli_delete_offer),
        "4": ("View all offers", lambda: display(view_offers())),
    })


# ── 9. REPORT MENU ──
def report_menu():
    run_menu("REPORTS MENU", {
        "1": ("Placed students", lambda: display(report_placed_students())),
        "2": ("Unplaced students", lambda: display(report_unplaced_students())),
        "3": ("Department-wise placements", lambda: display(report_department_wise())),
        "4": ("Company-wise packages", lambda: display(report_company_packages())),
        "5": ("Placement percentage", lambda: display(report_placement_percentage())),
        "6": ("Top 5 packages", lambda: display(report_top_packages())),
    })


# ── 10. AUTH & USER MANAGEMENT MENU ──
def auth_menu():
    def cli_add_admin():
        nid = input("Enter NSUT ID: ")
        name = input("Enter Full Name: ")
        email = input("Enter Email: ")
        pwd = input("Enter Password: ")
        if add_admin(nid, name, email, pwd):
            print("Admin added successfully!")
        else:
            print("Failed to add admin.")

    def cli_add_student_user():
        nid = input("Enter NSUT ID: ")
        sid = int(input("Enter Student ID: "))
        pwd = input("Enter Password: ")
        if add_student_user(nid, sid, pwd):
            print("Student login created successfully!")
        else:
            print("Failed to create student login.")

    run_menu("AUTH & USER MANAGEMENT MENU", {
        "1": ("Add Admin", cli_add_admin),
        "2": ("View All Admins", lambda: display(view_admins())),
        "3": ("Add Student Login Account", cli_add_student_user),
        "4": ("View Student Login Accounts", lambda: display(view_student_users())),
    })


def main():
    create_tables()
    seed_default_admin()
    run_menu("CAMPUS PLACEMENT MANAGEMENT SYSTEM", {
        "1": ("Students, Departments and Skills", student_menu),
        "2": ("Companies, Jobs and Interviewers", company_menu),
        "3": ("Check Eligibility", eligibility_menu),
        "4": ("Placement Drives", drive_menu),
        "5": ("Applications", application_menu),
        "6": ("Assessments", assessment_menu),
        "7": ("Interviews", interview_menu),
        "8": ("Offers", offer_menu),
        "9": ("Reports", report_menu),
        "10": ("User Management & Auth", auth_menu),
    })
    try:
        cursor.close()
        server.close()
    except Exception:
        pass
    print("Goodbye!")


if __name__ == "__main__":
    main()
