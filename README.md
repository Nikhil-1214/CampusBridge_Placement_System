# CampusBridge

## NSUT Placement Management System

CampusBridge is a centralized placement management platform that connects students, administrators, and recruiting companies in one system. It replaces scattered spreadsheets and manual coordination with a structured, transparent, and data-driven placement workflow.

## How the project works

1. **Academic setup**
   The administrator maintains departments, student profiles, CGPA, active backlogs, graduation years, and skills.

2. **Recruiter and job management**
   Companies, interviewers, job profiles, packages, locations, application deadlines, and required eligibility criteria are recorded in the system.

3. **Automatic eligibility checking**
   The system compares each student's academic details with a job's minimum CGPA, allowed backlogs, and eligible batch year to identify suitable opportunities.

4. **Placement drive scheduling**
   Administrators schedule placement drives, select the venue or online mode, and manage drive status.

5. **Student applications**
   Eligible students can view relevant jobs, apply for them, withdraw applications when required, and track application progress.

6. **Assessments and interviews**
   Administrators can create assessments, record results, schedule interview rounds, assign interviewers, and add round feedback.

7. **Offer management**
   Placement offers are linked to applications. Administrators can record package details and joining dates, while students can view and respond to their offers.

8. **Placement analytics**
   The system generates reports for placed and unplaced students, department-wise performance, company packages, top packages, and overall placement percentage.

## Main user roles

### Administrator

The administrator controls the complete placement lifecycle:

- Maintains academic and student records
- Manages companies, jobs, skills, and placement drives
- Checks eligibility and monitors applications
- Coordinates assessments and interview rounds
- Issues and updates placement offers
- Reviews placement analytics and reports
- Manages administrator and student accounts

### Student

The student gets a personalized placement workspace to:

- View their academic profile
- See only the jobs for which they are eligible
- Apply for opportunities
- Track application and interview status
- View placement offers and respond to them

## Unique selling proposition (USP)

### 1. Complete placement lifecycle in one platform

CampusBridge manages the entire journey—from student data and job creation to eligibility, applications, interviews, offers, and final placement reports—without requiring separate tools.

### 2. Eligibility-driven opportunities

Students do not need to manually inspect every job. The system filters opportunities using academic rules such as CGPA, active backlogs, and graduation batch, making the process faster and fairer.

### 3. Single source of truth

Student, recruiter, job, interview, and offer data are connected through a relational MySQL database. This reduces duplicate records, inconsistent spreadsheets, and manual errors.

### 4. Transparent student experience

Students can independently see eligible jobs, submit applications, and follow their progress. Administrators and students work from the same up-to-date placement information.

### 5. Actionable analytics

Placement teams can evaluate outcomes by department, company, package, and placement percentage. These reports support better planning and institutional decision-making.

### 6. Modular and extensible architecture

The FastAPI backend exposes organized operations for academics, recruitment, applications, interviews, offers, and reports. The frontend is separated into role-based administrator and student dashboards, making future features easier to add.

## Core technology

- **Backend:** Python, FastAPI, Pydantic, and Uvicorn
- **Database:** MySQL
- **Frontend:** HTML, CSS, and vanilla JavaScript
- **Architecture:** REST-style API with role-based browser dashboards

## Project outcome

CampusBridge provides a reliable digital foundation for managing campus placements. It improves coordination for administrators, gives students better visibility into opportunities, and turns placement data into useful insights for the institution.
