// static/js/calendar.js

// ─────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────
let selectedYear    = new Date().getFullYear();
let selectedMonth   = new Date().getMonth() + 1; // 1–12
let selectedDate    = null;
let selectedProject = null;

document.addEventListener("DOMContentLoaded", () => {
  // Wire month navigation
  document.getElementById("prevMonthBtn").onclick = () => changeMonth(-1);
  document.getElementById("nextMonthBtn").onclick = () => changeMonth(+1);

  // Prevent submit until both date & project chosen
  const form = document.getElementById("calendarForm");
  form.addEventListener("submit", e => {
    if (!selectedDate || !selectedProject) {
      e.preventDefault();
      alert("Please select both a date and a project.");
    }
  });

  // Initial calendar draw
  updateCalendar();
});

// ─────────────────────────────────────────────────────────────
// 1) Fetch calendar data from the server
// ─────────────────────────────────────────────────────────────
async function fetchCalendarData(year, month) {
  try {
    console.log("[calendar] API_CALENDAR_DATA_URL →", window.API_CALENDAR_DATA_URL);
    console.log("[calendar] API_BASE             →", window.API_BASE);

    const endpoint = window.API_CALENDAR_DATA_URL;
    if (!endpoint) throw new Error("Missing window.API_CALENDAR_DATA_URL");

    const base = window.API_BASE || "";
    const url = `${base}${endpoint}?year=${encodeURIComponent(year)}&month=${encodeURIComponent(month)}`;
    console.log("[calendar] fetching →", url);

    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Calendar API returned HTTP ${resp.status}`);

    const { calendar, projects } = await resp.json();
    console.log("[calendar] got JSON →", { calendar, projects });

    if (!calendar || !projects) {
      throw new Error("Malformed calendar payload");
    }

    const days = generateFullCalendar(year, month);
    renderCalendar(days, calendar, projects);

  } catch (err) {
    console.error("[calendar] fetchCalendarData error:", err);
    alert("Failed to load calendar. See console for details.");
  }
}

// ─────────────────────────────────────────────────────────────
// 2) Month navigation helpers
// ─────────────────────────────────────────────────────────────
function changeMonth(delta) {
  selectedMonth += delta;
  if (selectedMonth < 1)  { selectedMonth = 12; selectedYear--; }
  if (selectedMonth > 12) { selectedMonth = 1;  selectedYear++; }
  updateCalendar();
}

function updateCalendar() {
  document.getElementById("currentMonth").textContent =
    new Date(selectedYear, selectedMonth - 1)
      .toLocaleString(undefined, { month: "long", year: "numeric" });
  fetchCalendarData(selectedYear, selectedMonth);
}

// ─────────────────────────────────────────────────────────────
// 3) Build a full array of Date/null for grid alignment
// ─────────────────────────────────────────────────────────────
function generateFullCalendar(year, month) {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay  = new Date(year, month, 0);
  const days     = [];

  for (let i = 0; i < firstDay.getDay(); i++) days.push(null);
  for (let d = 1; d <= lastDay.getDate(); d++) {
    days.push(new Date(year, month - 1, d));
  }
  for (let i = lastDay.getDay() + 1; i < 7; i++) days.push(null);

  return days;
}

// ─────────────────────────────────────────────────────────────
// 4) Render the grid & handle selection
// ─────────────────────────────────────────────────────────────
function renderCalendar(days, calendarData, projectList) {
  const grid = document.getElementById("calendar-grid");
  grid.innerHTML = "";

  days.forEach(date => {
    const cell = document.createElement("div");
    cell.className = "calendar-date";

    if (date) {
      const iso = date.toISOString().slice(0,10);
      cell.innerHTML = `<strong>${date.getDate()}</strong>`;

      if (calendarData[iso]) {
        const statuses = calendarData[iso];
        applyStatusClasses(cell, Object.values(statuses));

        const list = document.createElement("div");
        list.className = "project-list";

        Object.entries(statuses).forEach(([pid, status]) => {
          const btn = document.createElement("button");
          btn.textContent = `Project ${pid} (${status})`;
          btn.className   = `status ${status.replace(/_/g,'-')}`;
          btn.dataset.projectId = pid;
          btn.dataset.date      = iso;

          btn.addEventListener("click", e => {
            e.stopPropagation();
            selectDateProject(cell, btn);
          });

          list.appendChild(btn);
        });

        cell.appendChild(list);
      }

      cell.addEventListener("click", () => {
        selectedDate = iso;
        document.getElementById("selected_date").value = iso;
      });
    } else {
      cell.classList.add("empty");
    }

    grid.appendChild(cell);
  });
}

function applyStatusClasses(cell, statuses) {
  if (statuses.every(s => s === "completed")) {
    cell.classList.add("completed");
  } else if (statuses.some(s => s === "in_progress")) {
    cell.classList.add("in-progress");
  } else {
    cell.classList.add("not-started");
  }
}

function selectDateProject(cell, btn) {
  document.querySelectorAll(".calendar-date.selected")
          .forEach(d => d.classList.remove("selected"));
  document.querySelectorAll(".project-list button.selected-project")
          .forEach(b => b.classList.remove("selected-project"));

  cell.classList.add("selected");
  btn.classList.add("selected-project");

  selectedProject = btn.dataset.projectId;
  selectedDate    = btn.dataset.date;
  document.getElementById("selected_project").value = selectedProject;
  document.getElementById("selected_date") .value = selectedDate;
  document.getElementById("confirmDateBtn").disabled = false;
}
