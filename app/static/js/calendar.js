// File: static/js/calendar.js
// JavaScript for rendering a dynamic project calendar with month navigation

// Global state
let selectedYear  = new Date().getFullYear();
let selectedMonth = new Date().getMonth() + 1; // 1-based
let selectedDate  = null;
let selectedProject = null;

document.addEventListener("DOMContentLoaded", () => {
  // wire up month nav buttons
  const prevBtn = document.getElementById("prevMonthBtn");
  const nextBtn = document.getElementById("nextMonthBtn");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      selectedMonth--;
      if (selectedMonth < 1) {
        selectedMonth = 12;
        selectedYear--;
      }
      updateCalendar();
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      selectedMonth++;
      if (selectedMonth > 12) {
        selectedMonth = 1;
        selectedYear++;
      }
      updateCalendar();
    });
  }

  // initial render
  updateCalendar();
});

async function fetchCalendarData(year, month) {
  try {
    // use the absolute, blueprint-correct URL injected via template
    const url = `${window.API.calendarData}?year=${year}&month=${month}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    if (!data.calendar)  throw new Error("No calendar data available.");
    if (!data.projects)  throw new Error("No project data available.");

    const calendar = generateFullCalendar(year, month);
    renderCalendar(calendar, data.calendar);
  } catch (err) {
    alert("Failed to load calendar data. Please try again.");
    console.error("Error fetching calendar data:", err);
  }
}

function generateFullCalendar(year, month) {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay  = new Date(year, month, 0);
  const daysInMonth = [];
  let cursor = new Date(firstDay);

  // leading blanks
  for (let i = 0; i < firstDay.getDay(); i++) {
    daysInMonth.push(null);
  }
  // actual days
  while (cursor <= lastDay) {
    daysInMonth.push(new Date(cursor));
    cursor.setDate(cursor.getDate() + 1);
  }
  // trailing blanks
  for (let i = lastDay.getDay() + 1; i < 7; i++) {
    daysInMonth.push(null);
  }
  return daysInMonth;
}

function renderCalendar(days, calendarData) {
  const grid = document.getElementById("calendar-grid");
  if (!grid) {
    console.error("Element #calendar-grid not found");
    return;
  }
  grid.innerHTML = "";

  days.forEach(date => {
    const cell = document.createElement("div");
    cell.className = "calendar-date";

    if (date) {
      const iso = date.toISOString().slice(0, 10);
      cell.innerHTML = `<strong>${date.getDate()}</strong>`;

      const dayData = calendarData[iso];
      if (dayData) {
        applyStatusClasses(cell, dayData);

        const list = document.createElement("div");
        list.className = "project-list";

        Object.entries(dayData).forEach(([projId, status]) => {
          const btn = document.createElement("button");
          btn.textContent = `Project ${projId} (${status})`;
          btn.className = `status ${status.replace("_", "-")}`;
          btn.dataset.projectId = projId;
          btn.dataset.date      = iso;

          btn.addEventListener("click", e => {
            e.preventDefault();
            selectedProject = projId;
            selectedDate    = iso;
            document.getElementById("selected_date").value    = iso;
            document.getElementById("selected_project").value = projId;
            highlightSelection(cell, btn);
          });

          list.appendChild(btn);
        });

        cell.appendChild(list);
      }

      // clicking date alone just picks date (for form)
      cell.addEventListener("click", () => {
        selectedDate = iso;
        document.getElementById("selected_date").value = iso;
      });

    } else {
      cell.classList.add("empty");
    }

    grid.appendChild(cell);
  });

  // prevent form‐submit unless date+project are chosen
  const form = document.getElementById("calendarForm");
  if (form) {
    form.addEventListener("submit", e => {
      if (!selectedDate || !selectedProject) {
        e.preventDefault();
        alert("Please select both a date and a project.");
      }
    });
  }
}

function applyStatusClasses(cell, projects) {
  const statuses = Object.values(projects);
  if (statuses.every(s => s === "completed")) {
    cell.classList.add("completed");
  } else if (statuses.some(s => s === "in_progress")) {
    cell.classList.add("in-progress");
  } else {
    cell.classList.add("not-started");
  }
}

function highlightSelection(cell, btn) {
  document.querySelectorAll(".calendar-date").forEach(d => d.classList.remove("selected"));
  document.querySelectorAll(".project-list button")
          .forEach(b => b.classList.remove("selected-project"));

  cell.classList.add("selected");
  btn.classList.add("selected-project");
}

function updateCalendar() {
  const label = document.getElementById("currentMonth");
  if (label) {
    label.textContent = new Date(selectedYear, selectedMonth - 1)
      .toLocaleString("en-US",{ month:"long",year:"numeric" });
  }
  fetchCalendarData(selectedYear, selectedMonth);
}
