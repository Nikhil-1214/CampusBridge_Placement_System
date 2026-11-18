/* ═══════════════════════════════════════════════════════════════
   CampusBridge Student Panel — JavaScript
   ═══════════════════════════════════════════════════════════════ */

function getApiBase() {
    if (window.location.protocol === "http:" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
        if (window.location.port === "8000") {
            return window.location.origin + "/api";
        }
    }
    if (window.location.protocol === "https:" || window.location.port === "8000") {
        return window.location.origin + "/api";
    }
    const host = (window.location.hostname && window.location.hostname !== "") ? window.location.hostname : "127.0.0.1";
    return `http://${host}:8000/api`;
}
const API = getApiBase();

// ── Auth Guard ──
let currentStudent = JSON.parse(sessionStorage.getItem("student") || "null");
if (!currentStudent || !currentStudent.student_id) {
    const isStatic = (window.location.port !== "8000" || window.location.protocol === "file:" || window.location.pathname.endsWith(".html"));
    window.location.href = isStatic ? "login.html?role=student" : "/login?role=student";
}

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
    const loaders = { profile: loadProfile, eligible_jobs: loadEligibleJobs, my_apps: loadMyApps, my_offers: loadMyOffers };
    if (loaders[id]) loaders[id]();
}

function logout() {
    sessionStorage.clear();
    const isLiveServer = (window.location.port === "5500" || window.location.pathname.endsWith(".html"));
    window.location.href = isLiveServer ? "index.html" : "/";
}

// ── Initialize ──
document.addEventListener("DOMContentLoaded", () => {
    if (currentStudent) {
        const nameEl = document.getElementById("stu_name");
        const idEl = document.getElementById("stu_nsut_id");
        if (nameEl) nameEl.textContent = currentStudent.full_name || "Student";
        if (idEl) idEl.textContent = currentStudent.nsut_id || currentStudent.roll_number || "";
        loadProfile();
    }
});

// ── Profile ──
async function loadProfile() {
    if (!currentStudent) return;
    try {
        const s = await api("GET", "/students/" + currentStudent.student_id);
        const container = document.getElementById("profile_cards");
        if (!container) return;
        container.innerHTML = "";
        const fields = [
            ["Student ID", s.student_id, "🆔"],
            ["Roll Number", s.roll_number, "🎫"],
            ["Full Name", s.full_name, "👤"],
            ["Email", s.email, "✉️"],
            ["Phone", s.phone || "—", "📞"],
            ["CGPA", s.cgpa, "📊"],
            ["Active Backlogs", s.active_backlogs, "📋"],
            ["Graduation Year", s.graduation_year, "🎓"],
        ];
        fields.forEach(([label, value, icon]) => {
            const div = document.createElement("div");
            div.className = "profile-item";
            div.innerHTML = `<div class="label">${icon} ${label}</div><div class="value">${value ?? "—"}</div>`;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Error loading profile:", e);
    }
}

// ── Eligible Jobs ──
async function loadEligibleJobs() {
    if (!currentStudent) return;
    const sid = currentStudent.student_id;
    const rows = await api("GET", "/eligibility/student/" + sid);
    fillTable("ej_table", rows, [
        "job_id", "company_name", "job_title", "package_lpa",
        (td, r) => {
            const b = document.createElement("button");
            b.textContent = "Apply";
            b.className = "btn btn-green";
            b.style.padding = "6px 14px"; b.style.fontSize = "12px";
            b.onclick = async () => {
                await api("POST", "/applications", { student_id: sid, job_id: r.job_id });
                toast("Applied successfully!"); loadEligibleJobs();
            };
            td.appendChild(b);
        }
    ]);
}

// ── My Applications ──
async function loadMyApps() {
    if (!currentStudent) return;
    const sid = currentStudent.student_id;
    const rows = await api("GET", "/applications/student/" + sid);
    fillTable("myapp_table", rows, [
        "application_id", "company_name", "job_title", "status",
        (td, r) => {
            if (r.status === "Applied") {
                const b = document.createElement("button");
                b.textContent = "Withdraw";
                b.className = "btn btn-red";
                b.style.padding = "6px 14px"; b.style.fontSize = "12px";
                b.onclick = async () => { await api("DELETE", "/applications/" + r.application_id); toast("Withdrawn!"); loadMyApps(); };
                td.appendChild(b);
            }
        }
    ]);
}

// ── My Offers ──
async function loadMyOffers() {
    if (!currentStudent) return;
    const allOffers = await api("GET", "/offers");
    const mine = allOffers.filter(o => o.student_id === currentStudent.student_id);
    const noP = document.getElementById("no_offers");
    const tbl = document.getElementById("myoffer_table");
    if (!mine.length) { noP.textContent = "No offers yet."; noP.style.display = "block"; tbl.style.display = "none"; return; }
    noP.style.display = "none"; tbl.style.display = "";
    fillTable("myoffer_table", mine, [
        "company_name",
        "offered_lpa",
        "offer_status",
        (td, r) => {
            if (r.offer_status === "Offered") {
                const accBtn = document.createElement("button");
                accBtn.textContent = "Accept";
                accBtn.className = "btn btn-green";
                accBtn.style.padding = "4px 10px";
                accBtn.style.fontSize = "12px";
                accBtn.onclick = async () => {
                    await api("PUT", "/offers/" + r.offer_id, { offer_status: "Accepted" });
                    toast("Offer Accepted! Congratulations!");
                    loadMyOffers();
                };

                const rejBtn = document.createElement("button");
                rejBtn.textContent = "Decline";
                rejBtn.className = "btn btn-red";
                rejBtn.style.padding = "4px 10px";
                rejBtn.style.fontSize = "12px";
                rejBtn.onclick = async () => {
                    await api("PUT", "/offers/" + r.offer_id, { offer_status: "Rejected" });
                    toast("Offer Declined.");
                    loadMyOffers();
                };

                td.appendChild(accBtn);
                td.appendChild(rejBtn);
            } else {
                const span = document.createElement("span");
                span.textContent = r.offer_status;
                span.style.fontWeight = "600";
                span.style.color = r.offer_status === "Accepted" ? "#86efac" : "#fca5a5";
                td.appendChild(span);
            }
        }
    ]);
}
