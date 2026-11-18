import os
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from create_tables import create_tables
import crud_operations as crud

app = FastAPI(title="CampusBridge Placement System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    try:
        create_tables()
        crud.seed_default_admin()
    except Exception as e:
        print("Note on startup table verification:", e)

@app.get("/health")
def health():
    return {"status": "ok"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Router (Mounted both at /api and at root for full compatibility) ──
api_router = APIRouter()


# ── Pydantic Models ──
class LoginBody(BaseModel):
    nsut_id: str
    password: str

class AdminRegisterBody(BaseModel):
    nsut_id: str
    full_name: str
    email: str
    password: str

class StudentRegisterBody(BaseModel):
    nsut_id: str
    student_id: int
    password: str

class DeptBody(BaseModel):
    department_name: str
    department_code: str

class DeptUpdateBody(BaseModel):
    department_name: Optional[str] = None
    department_code: Optional[str] = None

class StudentBody(BaseModel):
    department_id: int
    roll_number: str
    full_name: str
    email: str
    phone: Optional[str] = ""
    cgpa: float
    active_backlogs: int
    graduation_year: int

class StudentUpdateBody(BaseModel):
    department_id: Optional[int] = None
    roll_number: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cgpa: Optional[float] = None
    active_backlogs: Optional[int] = None
    graduation_year: Optional[int] = None

class SkillBody(BaseModel):
    skill_name: str

class CompanyBody(BaseModel):
    company_name: str
    industry: str
    website: str
    contact_email: str

class CompanyUpdateBody(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None

class JobBody(BaseModel):
    company_id: int
    job_title: str
    job_type: str
    location: str
    package_lpa: float
    min_cgpa: float
    max_backlogs_allowed: int
    eligible_batch_year: str
    application_deadline: str

class JobUpdateBody(BaseModel):
    company_id: Optional[int] = None
    job_title: Optional[str] = None
    job_type: Optional[str] = None
    location: Optional[str] = None
    package_lpa: Optional[float] = None
    min_cgpa: Optional[float] = None
    max_backlogs_allowed: Optional[int] = None
    eligible_batch_year: Optional[str] = None
    application_deadline: Optional[str] = None

class DriveBody(BaseModel):
    job_id: int
    drive_date: str
    venue_or_mode: str
    drive_status: Optional[str] = "Scheduled"

class DriveUpdateBody(BaseModel):
    job_id: Optional[int] = None
    drive_date: Optional[str] = None
    venue_or_mode: Optional[str] = None
    drive_status: Optional[str] = None

class AppBody(BaseModel):
    student_id: int
    job_id: int

class AppStatusBody(BaseModel):
    status: str

class InterviewerBody(BaseModel):
    company_id: int
    full_name: str
    designation: str
    email: str

class InterviewerUpdateBody(BaseModel):
    company_id: Optional[int] = None
    full_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None

class AssessmentBody(BaseModel):
    drive_id: int
    assessment_type: str
    scheduled_at: str
    maximum_marks: int

class AssessmentUpdateBody(BaseModel):
    drive_id: Optional[int] = None
    assessment_type: Optional[str] = None
    scheduled_at: Optional[str] = None
    maximum_marks: Optional[int] = None

class RoundBody(BaseModel):
    application_id: int
    interviewer_id: int
    round_number: int
    round_type: str
    scheduled_at: str

class RoundUpdateBody(BaseModel):
    application_id: Optional[int] = None
    interviewer_id: Optional[int] = None
    round_number: Optional[int] = None
    round_type: Optional[str] = None
    scheduled_at: Optional[str] = None
    result: Optional[str] = None
    feedback: Optional[str] = None

class RoundResultBody(BaseModel):
    result: str
    feedback: Optional[str] = ""

class OfferBody(BaseModel):
    application_id: int
    offered_lpa: float
    joining_date: str

class OfferStatusBody(BaseModel):
    offer_status: Optional[str] = None
    offered_lpa: Optional[float] = None
    joining_date: Optional[str] = None


# ── Authentication Endpoints ──
@api_router.post("/auth/admin/login")
def admin_login(body: LoginBody):
    user = crud.authenticate_admin(body.nsut_id, body.password)
    if not user:
        raise HTTPException(401, "Invalid NSUT ID or password.")
    return {"status": "ok", "admin_id": user["admin_id"], "full_name": user["full_name"], "nsut_id": user["nsut_id"]}

@api_router.post("/auth/student/login")
def student_login(body: LoginBody):
    user = crud.authenticate_student(body.nsut_id, body.password)
    if not user:
        raise HTTPException(401, "Invalid NSUT ID or password.")
    return {
        "status": "ok",
        "student_id": user["student_id"],
        "full_name": user["full_name"],
        "roll_number": user["roll_number"],
        "email": user["email"],
        "cgpa": str(user["cgpa"]),
        "active_backlogs": user["active_backlogs"],
        "graduation_year": user["graduation_year"],
        "department_id": user["department_id"],
        "phone": user["phone"],
        "nsut_id": user["nsut_id"],
    }

@api_router.post("/auth/admin/register")
def admin_register(body: AdminRegisterBody):
    if not crud.add_admin(body.nsut_id, body.full_name, body.email, body.password):
        raise HTTPException(400, "Could not register admin (NSUT ID or email may already exist).")
    return {"status": "ok"}

@api_router.post("/auth/student/register")
def student_register(body: StudentRegisterBody):
    stu = crud.get_student_by_id(body.student_id)
    if not stu:
        raise HTTPException(400, "Student ID not found. Admin must add the student first.")
    if not crud.add_student_user(body.nsut_id, body.student_id, body.password):
        raise HTTPException(400, "Could not register student user (NSUT ID may already exist).")
    return {"status": "ok"}

@api_router.get("/auth/admins")
def get_admins():
    return crud.view_admins()

@api_router.get("/auth/student-users")
def get_student_users():
    return crud.view_student_users()


# ── 1. Departments (Full CRUD) ──
@api_router.get("/departments")
def get_departments():
    return crud.view_departments()

@api_router.post("/departments")
def create_department(body: DeptBody):
    if not crud.add_department(body.department_name, body.department_code):
        raise HTTPException(400, "Could not add department (duplicate name/code).")
    return {"status": "ok"}

@api_router.put("/departments/{department_id}")
def edit_department(department_id: int, body: DeptUpdateBody):
    if not crud.update_department(department_id, body.department_name, body.department_code):
        raise HTTPException(400, "Could not update department.")
    return {"status": "ok"}

@api_router.delete("/departments/{department_id}")
def remove_department(department_id: int):
    if not crud.delete_department(department_id):
        raise HTTPException(400, "Could not delete department.")
    return {"status": "ok"}


# ── 2. Students (Full CRUD) ──
@api_router.get("/students")
def get_students():
    return crud.view_students()

@api_router.get("/students/search/{roll_number}")
def search_student(roll_number: str):
    return crud.search_student(roll_number)

@api_router.get("/students/{student_id}")
def get_student(student_id: int):
    rows = crud.get_student_by_id(student_id)
    if not rows:
        raise HTTPException(404, "Student not found.")
    return rows[0]

@api_router.post("/students")
def create_student(body: StudentBody):
    if not crud.get_department_by_id(body.department_id):
        raise HTTPException(400, f"Department ID {body.department_id} does not exist. Please choose an existing department.")
    if not crud.add_student(body.department_id, body.roll_number, body.full_name,
                            body.email, body.phone, body.cgpa, body.active_backlogs, body.graduation_year):
        raise HTTPException(400, "Could not add student (Roll Number or Email may already exist).")
    return {"status": "ok"}

@api_router.put("/students/{student_id}")
def edit_student(student_id: int, body: StudentUpdateBody):
    if not crud.update_student(student_id, cgpa=body.cgpa, backlogs=body.active_backlogs,
                               dept=body.department_id, roll=body.roll_number,
                               name=body.full_name, email=body.email,
                               phone=body.phone, year=body.graduation_year):
        raise HTTPException(400, "Could not update student.")
    return {"status": "ok"}

@api_router.delete("/students/{student_id}")
def remove_student(student_id: int):
    if not crud.delete_student(student_id):
        raise HTTPException(400, "Failed to delete student.")
    return {"status": "ok"}


# ── 3. Skills (Full CRUD) ──
@api_router.get("/skills")
def get_skills():
    return crud.view_skills()

@api_router.post("/skills")
def create_skill(body: SkillBody):
    if not crud.add_skill(body.skill_name):
        raise HTTPException(400, "Could not add skill.")
    return {"status": "ok"}

@api_router.put("/skills/{skill_id}")
def edit_skill(skill_id: int, body: SkillBody):
    if not crud.update_skill(skill_id, body.skill_name):
        raise HTTPException(400, "Could not update skill.")
    return {"status": "ok"}

@api_router.delete("/skills/{skill_id}")
def remove_skill(skill_id: int):
    if not crud.delete_skill(skill_id):
        raise HTTPException(400, "Could not delete skill.")
    return {"status": "ok"}


# ── 4. Companies (Full CRUD) ──
@api_router.get("/companies")
def get_companies():
    return crud.view_companies()

@api_router.post("/companies")
def create_company(body: CompanyBody):
    if not crud.add_company(body.company_name, body.industry, body.website, body.contact_email):
        raise HTTPException(400, "Could not add company.")
    return {"status": "ok"}

@api_router.put("/companies/{company_id}")
def edit_company(company_id: int, body: CompanyUpdateBody):
    if not crud.update_company(company_id, body.company_name, body.industry, body.website, body.contact_email):
        raise HTTPException(400, "Could not update company.")
    return {"status": "ok"}

@api_router.delete("/companies/{company_id}")
def remove_company(company_id: int):
    if not crud.delete_company(company_id):
        raise HTTPException(400, "Could not delete company.")
    return {"status": "ok"}


# ── 5. Jobs (Full CRUD) ──
@api_router.get("/jobs")
def get_jobs():
    return crud.view_jobs()

@api_router.post("/jobs")
def create_job(body: JobBody):
    if not crud.add_job(body.company_id, body.job_title, body.job_type, body.location,
                        body.package_lpa, body.min_cgpa, body.max_backlogs_allowed,
                        body.eligible_batch_year, body.application_deadline):
        raise HTTPException(400, "Could not add job (verify Company ID exists).")
    return {"status": "ok"}

@api_router.put("/jobs/{job_id}")
def edit_job(job_id: int, body: JobUpdateBody):
    if not crud.update_job(job_id, body.company_id, body.job_title, body.job_type, body.location,
                           body.package_lpa, body.min_cgpa, body.max_backlogs_allowed,
                           body.eligible_batch_year, body.application_deadline):
        raise HTTPException(400, "Could not update job.")
    return {"status": "ok"}

@api_router.delete("/jobs/{job_id}")
def remove_job(job_id: int):
    if not crud.delete_job(job_id):
        raise HTTPException(400, "Could not delete job.")
    return {"status": "ok"}


# ── 6. Eligibility (Read Only) ──
@api_router.get("/eligibility/student/{student_id}")
def eligible_jobs_for_student(student_id: int):
    return crud.jobs_for_student(student_id)

@api_router.get("/eligibility/job/{job_id}")
def eligible_students_for_job(job_id: int):
    return crud.students_for_job(job_id)


# ── 7. Drives (Full CRUD) ──
@api_router.get("/drives")
def get_drives():
    return crud.view_drives()

@api_router.post("/drives")
def create_drive(body: DriveBody):
    if not crud.add_drive(body.job_id, body.drive_date, body.venue_or_mode):
        raise HTTPException(400, "Could not add drive (verify Job ID exists).")
    return {"status": "ok"}

@api_router.put("/drives/{drive_id}")
def edit_drive(drive_id: int, body: DriveUpdateBody):
    if body.drive_status and not body.job_id and not body.drive_date and not body.venue_or_mode:
        if not crud.update_drive_status(drive_id, body.drive_status):
            raise HTTPException(400, "Could not update drive status.")
        return {"status": "ok"}
    if not crud.update_drive(drive_id, body.job_id, body.drive_date, body.venue_or_mode, body.drive_status):
        raise HTTPException(400, "Could not update drive.")
    return {"status": "ok"}

@api_router.put("/drives/{drive_id}/status")
def edit_drive_status(drive_id: int, body: DriveUpdateBody):
    status = body.drive_status or "Scheduled"
    if not crud.update_drive_status(drive_id, status):
        raise HTTPException(400, "Could not update drive status.")
    return {"status": "ok"}

@api_router.delete("/drives/{drive_id}")
def remove_drive(drive_id: int):
    if not crud.delete_drive(drive_id):
        raise HTTPException(400, "Could not delete drive.")
    return {"status": "ok"}


# ── 8. Applications (Full CRUD) ──
@api_router.get("/applications")
def get_all_applications():
    return crud.view_all_applications()

@api_router.get("/applications/student/{student_id}")
def get_student_apps(student_id: int):
    return crud.view_student_applications(student_id)

@api_router.get("/applications/job/{job_id}")
def get_job_applicants(job_id: int):
    return crud.view_job_applicants(job_id)

@api_router.post("/applications")
def apply_job(body: AppBody):
    ok, msg = crud.apply_for_job(body.student_id, body.job_id)
    if not ok:
        raise HTTPException(400, msg)
    return {"message": msg}

@api_router.put("/applications/{application_id}")
@api_router.put("/applications/{application_id}/status")
def change_application_status(application_id: int, body: AppStatusBody):
    if not crud.update_application_status(application_id, body.status):
        raise HTTPException(400, "Could not update application status.")
    return {"status": "ok"}

@api_router.delete("/applications/{application_id}")
def delete_application(application_id: int):
    if not crud.withdraw_application(application_id):
        raise HTTPException(400, "Could not withdraw application.")
    return {"status": "ok"}


# ── 9. Interviewers (Full CRUD) ──
@api_router.get("/interviewers")
def get_interviewers():
    return crud.view_interviewers()

@api_router.post("/interviewers")
def create_interviewer(body: InterviewerBody):
    if not crud.add_interviewer(body.company_id, body.full_name, body.designation, body.email):
        raise HTTPException(400, "Could not add interviewer.")
    return {"status": "ok"}

@api_router.put("/interviewers/{interviewer_id}")
def edit_interviewer(interviewer_id: int, body: InterviewerUpdateBody):
    if not crud.update_interviewer(interviewer_id, body.company_id, body.full_name, body.designation, body.email):
        raise HTTPException(400, "Could not update interviewer.")
    return {"status": "ok"}

@api_router.delete("/interviewers/{interviewer_id}")
def remove_interviewer(interviewer_id: int):
    if not crud.delete_interviewer(interviewer_id):
        raise HTTPException(400, "Could not delete interviewer.")
    return {"status": "ok"}


# ── 10. Assessments (Full CRUD) ──
@api_router.get("/assessments")
def get_assessments():
    return crud.view_assessments()

@api_router.post("/assessments")
def create_assessment(body: AssessmentBody):
    if not crud.add_assessment(body.drive_id, body.assessment_type, body.scheduled_at, body.maximum_marks):
        raise HTTPException(400, "Could not add assessment.")
    return {"status": "ok"}

@api_router.put("/assessments/{assessment_id}")
def edit_assessment(assessment_id: int, body: AssessmentUpdateBody):
    if not crud.update_assessment(assessment_id, body.drive_id, body.assessment_type, body.scheduled_at, body.maximum_marks):
        raise HTTPException(400, "Could not update assessment.")
    return {"status": "ok"}

@api_router.delete("/assessments/{assessment_id}")
def remove_assessment(assessment_id: int):
    if not crud.delete_assessment(assessment_id):
        raise HTTPException(400, "Could not delete assessment.")
    return {"status": "ok"}


# ── 11. Interview Rounds (Full CRUD) ──
@api_router.get("/rounds")
def get_all_rounds():
    return crud.view_all_rounds()

@api_router.get("/rounds/{application_id}")
def get_rounds(application_id: int):
    return crud.view_rounds(application_id)

@api_router.post("/rounds")
def create_round(body: RoundBody):
    if not crud.schedule_round(body.application_id, body.interviewer_id,
                               body.round_number, body.round_type, body.scheduled_at):
        raise HTTPException(400, "Could not schedule round (check App ID, Interviewer ID, or duplicate Round #).")
    return {"status": "ok"}

@api_router.put("/rounds/{round_id}")
def edit_round(round_id: int, body: RoundUpdateBody):
    if not crud.update_round(round_id, body.application_id, body.interviewer_id,
                             body.round_number, body.round_type, body.scheduled_at,
                             body.result, body.feedback):
        raise HTTPException(400, "Could not update round.")
    return {"status": "ok"}

@api_router.put("/rounds/{round_id}/result")
def edit_round_result(round_id: int, body: RoundResultBody):
    if not crud.update_round_result(round_id, body.result, body.feedback or ""):
        raise HTTPException(400, "Could not update round result.")
    return {"status": "ok"}

@api_router.delete("/rounds/{round_id}")
def remove_round(round_id: int):
    if not crud.delete_round(round_id):
        raise HTTPException(400, "Could not delete round.")
    return {"status": "ok"}


# ── 12. Offers (Full CRUD) ──
@api_router.get("/offers")
def get_offers():
    return crud.view_offers()

@api_router.post("/offers")
def create_offer(body: OfferBody):
    if not crud.give_offer(body.application_id, body.offered_lpa, body.joining_date):
        raise HTTPException(400, "Could not give offer (check Application ID or existing offer).")
    return {"status": "ok"}

@api_router.put("/offers/{offer_id}")
def edit_offer(offer_id: int, body: OfferStatusBody):
    if not crud.update_offer(offer_id, lpa=body.offered_lpa, joining=body.joining_date, status=body.offer_status):
        raise HTTPException(400, "Could not update offer.")
    return {"status": "ok"}

@api_router.delete("/offers/{offer_id}")
def remove_offer(offer_id: int):
    if not crud.delete_offer(offer_id):
        raise HTTPException(400, "Could not delete offer.")
    return {"status": "ok"}


# ── 13. Reports (Read Only) ──
@api_router.get("/reports/placed")
def get_report_placed():
    return crud.report_placed_students()

@api_router.get("/reports/unplaced")
def get_report_unplaced():
    return crud.report_unplaced_students()

@api_router.get("/reports/department-wise")
def get_report_dept():
    return crud.report_department_wise()

@api_router.get("/reports/company-packages")
def get_report_company():
    return crud.report_company_packages()

@api_router.get("/reports/placement-percentage")
def get_report_percentage():
    return crud.report_placement_percentage()

@api_router.get("/reports/top-packages")
def get_report_top():
    return crud.report_top_packages()


# Mount router both with prefix /api and without prefix for total compatibility
app.include_router(api_router, prefix="/api")
app.include_router(api_router)


# ── Serve Frontend HTML, CSS & JS Files Directly from FastAPI ──
@app.get("/")
@app.get("/index.html")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/login")
@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(BASE_DIR, "login.html"))

@app.get("/admin")
@app.get("/admin.html")
def serve_admin():
    return FileResponse(os.path.join(BASE_DIR, "admin.html"))

@app.get("/student")
@app.get("/student.html")
def serve_student():
    return FileResponse(os.path.join(BASE_DIR, "student.html"))

@app.get("/style.css")
def serve_css():
    return FileResponse(os.path.join(BASE_DIR, "style.css"))

@app.get("/admin.js")
@app.get("/static/admin.js")
def serve_admin_js():
    return FileResponse(os.path.join(BASE_DIR, "admin.js"))

@app.get("/student.js")
@app.get("/static/student.js")
def serve_student_js():
    return FileResponse(os.path.join(BASE_DIR, "student.js"))
