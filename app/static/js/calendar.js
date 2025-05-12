// static/js/calendar.js

// State
let selectedYear    = new Date().getFullYear();
let selectedMonth   = new Date().getMonth() + 1; // 1–12
let selectedDate    = null;
let selectedProject = null;

document.addEventListener("DOMContentLoaded", () => {
  // Wire month navigation
  document.getElementById("prevMonthBtn").onclick = () => changeMonth(-1);
  document.getElementById("nextMonthBtn").onclick = () => changeMonth(+1);

  // Cache form elements
  const form    = document.getElementById("calendarForm");
  const confirm = document.getElementById("confirmDateBtn");

  // Prevent submit until both date & project chosen
  form.addEventListener("submit", e => {
    if (!selectedDate || !selectedProject) {
      e.preventDefault();
      alert("Please select both a date and a project.");
    }
  });

  // Initial load
  updateCalendar();
});

async function fetchCalendarData(year, month) {
  try {
    const url  = `${window.API_CALENDAR_DATA_URL}?year=${year}&month=${month}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const { calendar, projects } = await resp.json();

    if (!calendar || !projects) {
      throw new Error("Malformed calendar data");
    }

    const days = generateFullCalendar(year, month);
    renderCalendar(days, calendar, projects);
  } catch (err) {
    console.error("Error fetching calendar data:", err);
    alert("Failed to load calendar. Check console for details.");
  }
}

function changeMonth(delta) {
  selectedMonth += delta;
  if (selectedMonth < 1)  { selectedMonth = 12; selectedYear--; }
  if (selectedMonth > 12) { selectedMonth = 1;  selectedYear++; }
  updateCalendar();
}

function updateCalendar() {
  // Update header label
  document.getElementById("currentMonth").textContent =
    new Date(selectedYear, selectedMonth - 1)
      .toLocaleString("en-US", { month: "long", year: "numeric" });

  // Fetch & redraw
  fetchCalendarData(selectedYear, selectedMonth);
}

function generateFullCalendar(year, month) {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay  = new Date(year, month, 0);
  const days     = [];

  // Pad beginning of week
  for (let i = 0; i < firstDay.getDay(); i++) days.push(null);
  // Actual days
  for (let d = 1; d <= lastDay.getDate(); d++) {
    days.push(new Date(year, month - 1, d));
  }
  // Pad end of week
  for (let i = lastDay.getDay() + 1; i < 7; i++) days.push(null);

  return days;
}

function renderCalendar(days, calendarData, projectList) {
  const grid = document.getElementById("calendar-grid");
  grid.innerHTML = ""; // clear any existing cells

  days.forEach(date => {
    const cell = document.createElement("div");
    cell.className = "calendar-date";

    if (date) {
      const iso = date.toISOString().slice(0,10);
      cell.innerHTML = `<strong>${date.getDate()}</strong>`;

      // If there are project statuses for this date
      if (calendarData[iso]) {
        const statuses = calendarData[iso]; // { projectId: status }
        applyStatusClasses(cell, Object.values(statuses));

        const list = document.createElement("div");
        list.className = "project-list";

        Object.entries(statuses).forEach(([pid, status]) => {
          const btn = document.createElement("button");
          btn.textContent = `Project ${pid} (${status})`;
          btn.className = `status ${status.replace(/_/g,'-')}`;
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

      // Clicking the date itself still selects the date
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
  // Clear previous selection highlights
  document.querySelectorAll(".calendar-date.selected")
          .forEach(d => d.classList.remove("selected"));
  document.querySelectorAll(".project-list button.selected-project")
          .forEach(b => b.classList.remove("selected-project"));

  // Mark the newly chosen date+project
  cell.classList.add("selected");
  btn.classList.add("selected-project");

  // Record into our form
  selectedProject = btn.dataset.projectId;
  selectedDate    = btn.dataset.date;
  document.getElementById("selected_project").value = selectedProject;
  document.getElementById("selected_date") .value = selectedDate;

  // Enable the confirm button now that both are set
  document.getElementById("confirmDateBtn").disabled = false;
}
