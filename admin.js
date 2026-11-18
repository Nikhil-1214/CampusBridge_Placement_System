/* ═══════════════════════════════════════════════════════════════
   CampusBridge Admin Panel — JavaScript
   ═══════════════════════════════════════════════════════════════ */

function getApiBase() {
    if (window.location.port === "8000") {
        return window.location.origin + "/api";
    }
    const host = (window.location.hostname && window.location.hostname !== "") ? window.location.hostname : "127.0.0.1";
    return `http://${host}:8000/api`;
}
const API = getApiBase();

// ── Auth Guard ──
const adminSession = JSON.parse(sessionStorage.getItem("admin") || "null");
if (!adminSession) {
    const isStatic = (window.location.port !== "8000" || window.location.protocol === "file:" || window.location.pathname.endsWith(".html"));
    window.location.href = isStatic ? "login.html?role=admin" : "/login?role=admin";
}

// Set greeting
document.addEventListener("DOMContentLoaded", () => {
    if (adminSession) {
        document.getElementById("adminGreeting").textContent = `Welcome, ${adminSession.full_name}`;
    }
});

// ── Helpers ──
function toast(msg, isError) {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = isError ? "error" : "";
    t.style.display = "block";
    setTimeout(() => t.style.display = "none", 3000);
}

async function api(method, path, body) {
    const opts = { method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    let res;
    try {
        res = await fetch(API + path, opts);
    } catch (netErr) {
        toast("Cannot connect to server. Is FastAPI running on port 8000?", true);
        throw netErr;
    }
    const text = await res.text();
    let data = {};
    try { data = JSON.parse(text); } catch (e) {
        toast("Server error (" + res.status + "): " + text, true);
        throw new Error(text);
    }
    if (!res.ok) { toast(data.detail || "Error", true); throw new Error(data.detail); }
    return data;
}

function fillTable(tableId, rows, cols) {
    const tbody = document.querySelector("#" + tableId + " tbody");
    tbody.innerHTML = "";
    if (!rows.length) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = cols.length;
        td.textContent = "No records found";
        td.style.textAlign = "center";
        td.style.color = "rgba(255,255,255,0.3)";
        td.style.padding = "24px";
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
    }
    rows.forEach(r => {
        const tr = document.createElement("tr");
        cols.forEach(c => {
            const td = document.createElement("td");
            if (typeof c === "function") { c(td, r); }
            else { td.textContent = r[c] ?? ""; }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function showSection(id, btnEl) {
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
    document.getElementById(id).classList.add("active");
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    if (btnEl) btnEl.classList.add("active");
    const loaders = {
        departments: loadDepartments, students: loadStudents, skills: loadSkills,
        companies: loadCompanies, jobs: loadJobs, drives: loadDrives,
        applications: loadAllApplications,
        interviewers: loadInterviewers, assessments: loadAssessments,
        rounds: loadAllRounds, offers: loadOffers,
        user_mgmt: () => { loadAdminUsers(); loadStudentUsers(); },
    };
    if (loaders[id]) loaders[id]();
}

function val(id) { return document.getElementById(id).value; }
function numVal(id) { return Number(val(id)); }
function formatDateTime(v) {
    if (!v) return "";
    let s = v.replace("T", " ");
    if (s.length === 16) s += ":00";
    return s;
}
function clearInputs(...ids) {
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}
function logout() {
    sessionStorage.clear();
    const isLiveServer = (window.location.port === "5500" || window.location.pathname.endsWith(".html"));
    window.location.href = isLiveServer ? "index.html" : "/";
}

// ── Departments ──
async function populateDepartmentDropdown() {
    const sel = document.getElementById("s_dept");
    if (!sel) return;
    try {
        const depts = await api("GET", "/departments");
        const cur = sel.value;
        sel.innerHTML = '<option value="">-- Select Department --</option>' +
            depts.map(d => `<option value="${d.department_id}">${d.department_name} (${d.department_code})</option>`).join("");
        if (cur) sel.value = cur;
    } catch (e) {
        console.error(e);
    }
}

async function loadDepartments() {
    fillTable("dept_table", await api("GET", "/departments"), [
        "department_id", "department_name", "department_code",
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/departments/" + r.department_id); toast("Deleted!"); loadDepartments(); };
            td.appendChild(b);
        }
    ]);
    populateDepartmentDropdown();
}
async function addDepartment() {
    await api("POST", "/departments", { department_name: val("dept_name"), department_code: val("dept_code") });
    toast("Department added!"); clearInputs("dept_name", "dept_code"); loadDepartments();
}

// ── Students ──
async function loadStudents() {
    await populateDepartmentDropdown();
    fillTable("stu_table", await api("GET", "/students"), [
        "student_id", "roll_number", "full_name",
        (td, r) => { td.textContent = r.department_code || r.department_name || (r.department_id ? `Dept #${r.department_id}` : "Unassigned"); },
        "cgpa", "active_backlogs", "graduation_year",
        (td, r) => { const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/students/" + r.student_id); toast("Deleted!"); loadStudents(); }; td.appendChild(b); }
    ]);
}
async function addStudent() {
    const deptId = numVal("s_dept");
    if (!deptId) {
        toast("Please select a department.", true);
        return;
    }
    await api("POST", "/students", {
        department_id: deptId, roll_number: val("s_roll"), full_name: val("s_name"),
        email: val("s_email"), phone: val("s_phone"), cgpa: numVal("s_cgpa"),
        active_backlogs: numVal("s_backlogs"), graduation_year: numVal("s_year"),
    });
    toast("Student added!"); clearInputs("s_roll","s_name","s_email","s_phone","s_cgpa","s_backlogs","s_year");
    document.getElementById("s_dept").value = "";
    loadStudents();
}

// ── Skills ──
async function loadSkills() {
    fillTable("skill_table", await api("GET", "/skills"), [
        "skill_id", "skill_name",
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/skills/" + r.skill_id); toast("Deleted!"); loadSkills(); };
            td.appendChild(b);
        }
    ]);
}
async function addSkill() { await api("POST", "/skills", { skill_name: val("sk_name") }); toast("Skill added!"); clearInputs("sk_name"); loadSkills(); }

// ── Companies ──
async function loadCompanies() {
    fillTable("comp_table", await api("GET", "/companies"), [
        "company_id", "company_name", "industry", "website", "contact_email",
        (td, r) => { const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/companies/" + r.company_id); toast("Deleted!"); loadCompanies(); }; td.appendChild(b); }
    ]);
}
async function addCompany() {
    await api("POST", "/companies", { company_name: val("c_name"), industry: val("c_industry"), website: val("c_website"), contact_email: val("c_email") });
    toast("Company added!"); clearInputs("c_name","c_industry","c_website","c_email"); loadCompanies();
}

// ── Jobs ──
async function loadJobs() {
    fillTable("job_table", await api("GET", "/jobs"), [
        "job_id", "company_name", "job_title", "job_type", "package_lpa", "min_cgpa", "application_deadline",
        (td, r) => { const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/jobs/" + r.job_id); toast("Deleted!"); loadJobs(); }; td.appendChild(b); }
    ]);
}
async function addJob() {
    await api("POST", "/jobs", {
        company_id: numVal("j_cid"), job_title: val("j_title"), job_type: val("j_type"),
        location: val("j_loc"), package_lpa: numVal("j_pkg"), min_cgpa: numVal("j_cgpa"),
        max_backlogs_allowed: numVal("j_back"), eligible_batch_year: val("j_batch"), application_deadline: val("j_dead"),
    });
    toast("Job added!"); clearInputs("j_cid","j_title","j_type","j_loc","j_pkg","j_cgpa","j_back","j_batch","j_dead"); loadJobs();
}

// ── Eligibility ──
async function jobsForStudent() { fillTable("elig_table1", await api("GET", "/eligibility/student/" + numVal("e_sid")), ["job_id", "company_name", "job_title", "package_lpa"]); }
async function studentsForJob() { fillTable("elig_table2", await api("GET", "/eligibility/job/" + numVal("e_jid")), ["student_id", "full_name", "cgpa"]); }

// ── Drives ──
async function loadDrives() {
    fillTable("drive_table", await api("GET", "/drives"), [
        "drive_id", "company_name", "job_title", "drive_date", "venue_or_mode",
        (td, r) => {
            const sel = document.createElement("select");
            ["Scheduled", "Ongoing", "Completed", "Cancelled"].forEach(s => {
                const o = document.createElement("option"); o.value = s; o.textContent = s;
                if (s === r.drive_status) o.selected = true;
                sel.appendChild(o);
            });
            const b = document.createElement("button"); b.textContent = "Save"; b.className = "btn btn-blue";
            b.style.padding = "4px 8px"; b.style.fontSize = "12px"; b.style.marginLeft = "6px";
            b.onclick = async () => {
                await api("PUT", "/drives/" + r.drive_id + "/status", { drive_status: sel.value });
                toast("Status updated!"); loadDrives();
            };
            td.appendChild(sel); td.appendChild(b);
        },
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/drives/" + r.drive_id); toast("Deleted!"); loadDrives(); };
            td.appendChild(b);
        }
    ]);
}
async function addDrive() {
    await api("POST", "/drives", { job_id: numVal("dr_jid"), drive_date: val("dr_date"), venue_or_mode: val("dr_venue") });
    toast("Drive added!"); clearInputs("dr_jid","dr_date","dr_venue"); loadDrives();
}

// ── Applications ──
async function loadStudentApps() {
    const sid = val("app_view_sid");
    if (!sid) { return loadAllApplications(); }
    const rows = await api("GET", "/applications/student/" + Number(sid));
    renderAppTable(rows);
}

async function loadAllApplications() {
    const rows = await api("GET", "/applications");
    renderAppTable(rows);
}

function renderAppTable(rows) {
    fillTable("app_table", rows, [
        "application_id",
        (td, r) => { td.textContent = r.full_name ? `${r.full_name} (${r.roll_number || r.student_id})` : (r.student_id ?? ""); },
        "company_name",
        "job_title",
        (td, r) => {
            const sel = document.createElement("select");
            ["Applied", "Shortlisted", "Selected", "Rejected"].forEach(s => {
                const opt = document.createElement("option"); opt.value = s; opt.textContent = s;
                if (s === r.status) opt.selected = true;
                sel.appendChild(opt);
            });
            const btn = document.createElement("button"); btn.textContent = "Save"; btn.className = "btn btn-blue";
            btn.style.padding = "4px 8px"; btn.style.fontSize = "12px"; btn.style.marginLeft = "6px";
            btn.onclick = async () => {
                await api("PUT", "/applications/" + r.application_id + "/status", { status: sel.value });
                toast("Status updated!");
                loadAllApplications();
            };
            td.appendChild(sel);
            td.appendChild(btn);
        },
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/applications/" + r.application_id); toast("Deleted!"); loadAllApplications(); };
            td.appendChild(b);
        }
    ]);
}

// ── Interviewers ──
async function loadInterviewers() {
    fillTable("iv_table", await api("GET", "/interviewers"), [
        "interviewer_id", "company_id", "full_name", "designation", "email",
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/interviewers/" + r.interviewer_id); toast("Deleted!"); loadInterviewers(); };
            td.appendChild(b);
        }
    ]);
}
async function addInterviewer() {
    await api("POST", "/interviewers", { company_id: numVal("iv_cid"), full_name: val("iv_name"), designation: val("iv_desig"), email: val("iv_email") });
    toast("Interviewer added!"); clearInputs("iv_cid","iv_name","iv_desig","iv_email"); loadInterviewers();
}

// ── Assessments ──
async function loadAssessments() {
    fillTable("as_table", await api("GET", "/assessments"), [
        "assessment_id", "drive_id", "assessment_type", "scheduled_at", "maximum_marks",
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/assessments/" + r.assessment_id); toast("Deleted!"); loadAssessments(); };
            td.appendChild(b);
        }
    ]);
}
async function addAssessment() {
    await api("POST", "/assessments", { drive_id: numVal("as_did"), assessment_type: val("as_type"), scheduled_at: formatDateTime(val("as_when")), maximum_marks: numVal("as_marks") });
    toast("Assessment added!"); clearInputs("as_did","as_type","as_when","as_marks"); loadAssessments();
}

// ── Interview Rounds ──
async function scheduleRound() {
    await api("POST", "/rounds", { application_id: numVal("r_aid"), interviewer_id: numVal("r_iid"), round_number: numVal("r_num"), round_type: val("r_type"), scheduled_at: formatDateTime(val("r_when")) });
    toast("Round scheduled!"); clearInputs("r_aid","r_iid","r_num","r_type","r_when"); loadAllRounds();
}
async function loadAllRounds() {
    renderRoundTable(await api("GET", "/rounds"));
}
async function loadRounds() {
    const aid = val("r_view_aid");
    if (!aid) { return loadAllRounds(); }
    renderRoundTable(await api("GET", "/rounds/" + Number(aid)));
}
function renderRoundTable(rows) {
    fillTable("round_table", rows, [
        "round_id", "round_number", "round_type", "scheduled_at",
        (td, r) => {
            const sel = document.createElement("select");
            ["Scheduled", "Pass", "Fail", "Pending"].forEach(s => {
                const opt = document.createElement("option"); opt.value = s; opt.textContent = s;
                if (s === (r.result || "Scheduled")) opt.selected = true;
                sel.appendChild(opt);
            });
            const b = document.createElement("button"); b.textContent = "Save"; b.className = "btn btn-blue";
            b.style.padding = "4px 8px"; b.style.fontSize = "12px"; b.style.marginLeft = "6px";
            b.onclick = async () => {
                await api("PUT", "/rounds/" + r.round_id + "/result", { result: sel.value, feedback: r.feedback || "" });
                toast("Result updated!"); loadAllRounds();
            };
            td.appendChild(sel); td.appendChild(b);
        },
        "feedback",
        (td, r) => {
            const b = document.createElement("button"); b.textContent = "Delete"; b.className = "btn btn-red";
            b.onclick = async () => { await api("DELETE", "/rounds/" + r.round_id); toast("Deleted!"); loadAllRounds(); };
            td.appendChild(b);
        }
    ]);
}

// ── Offers ──
async function loadOffers() {
    fillTable("offer_table", await api("GET", "/offers"), [
        "offer_id", "full_name", "company_name", "offered_lpa", "offer_status",
        (td, r) => {
            const sel = document.createElement("select");
            ["Offered","Accepted","Rejected"].forEach(s => { const o = document.createElement("option"); o.value = s; o.textContent = s; if (s === r.offer_status) o.selected = true; sel.appendChild(o); });
            const b = document.createElement("button"); b.textContent = "Update"; b.className = "btn btn-blue";
            b.style.padding = "6px 12px"; b.style.fontSize = "12px";
            b.onclick = async () => { await api("PUT", "/offers/" + r.offer_id, { offer_status: sel.value }); toast("Updated!"); loadOffers(); };
            
            const delBtn = document.createElement("button"); delBtn.textContent = "Delete"; delBtn.className = "btn btn-red";
            delBtn.style.padding = "6px 12px"; delBtn.style.fontSize = "12px"; delBtn.style.marginLeft = "6px";
            delBtn.onclick = async () => { await api("DELETE", "/offers/" + r.offer_id); toast("Deleted!"); loadOffers(); };
            
            td.appendChild(sel); td.appendChild(b); td.appendChild(delBtn);
        }
    ]);
}
async function giveOffer() {
    await api("POST", "/offers", { application_id: numVal("of_aid"), offered_lpa: numVal("of_lpa"), joining_date: val("of_join") });
    toast("Offer given!"); clearInputs("of_aid","of_lpa","of_join"); loadOffers();
}

// ── Reports ──
async function loadReport(name) {
    const data = await api("GET", "/reports/" + name);
    const out = document.getElementById("report_output");
    if (name === "placement-percentage") {
        out.innerHTML = `<div style="padding:20px;text-align:center;">
            <div style="font-size:48px;font-weight:800;color:#a5b4fc;">${data.percentage}%</div>
            <div style="color:rgba(255,255,255,0.5);margin-top:8px;">Total: ${data.total} · Placed: ${data.placed}</div>
        </div>`;
        return;
    }
    if (!Array.isArray(data) || !data.length) { out.innerHTML = "<p style='padding:20px;text-align:center;color:rgba(255,255,255,0.3);'>No records found.</p>"; return; }
    const keys = Object.keys(data[0]);
    let h = "<table><thead><tr>" + keys.map(k => `<th>${k.replace(/_/g, " ").toUpperCase()}</th>`).join("") + "</tr></thead><tbody>";
    data.forEach(r => { h += "<tr>" + keys.map(k => `<td>${r[k] ?? ""}</td>`).join("") + "</tr>"; });
    out.innerHTML = h + "</tbody></table>";
}

// ── User Management ──
async function registerAdmin() {
    await api("POST", "/auth/admin/register", {
        nsut_id: val("reg_admin_nsut"), full_name: val("reg_admin_name"),
        email: val("reg_admin_email"), password: val("reg_admin_pass"),
    });
    toast("Admin registered!"); clearInputs("reg_admin_nsut","reg_admin_name","reg_admin_email","reg_admin_pass");
    loadAdminUsers();
}
async function registerStudentUser() {
    await api("POST", "/auth/student/register", {
        nsut_id: val("reg_stu_nsut"), student_id: numVal("reg_stu_sid"), password: val("reg_stu_pass"),
    });
    toast("Student login created!"); clearInputs("reg_stu_nsut","reg_stu_sid","reg_stu_pass");
    loadStudentUsers();
}
async function loadAdminUsers() {
    fillTable("admin_users_table", await api("GET", "/auth/admins"), ["admin_id", "nsut_id", "full_name", "email", "created_at"]);
}
async function populateStudentDropdown() {
    const sel = document.getElementById("reg_stu_sid");
    if (!sel) return;
    try {
        const students = await api("GET", "/students");
        const cur = sel.value;
        sel.innerHTML = '<option value="">-- Select Student Profile --</option>' +
            students.map(s => `<option value="${s.student_id}">${s.full_name} (${s.roll_number}) - ID: ${s.student_id}</option>`).join("");
        if (cur) sel.value = cur;
    } catch (e) {
        console.error(e);
    }
}

async function loadStudentUsers() {
    await populateStudentDropdown();
    fillTable("student_users_table", await api("GET", "/auth/student-users"), ["student_user_id", "nsut_id", "full_name", "roll_number", "created_at"]);
}

// ── Load first section ──
loadDepartments();
populateDepartmentDropdown();
populateStudentDropdown();
