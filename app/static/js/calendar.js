// JavaScript for rendering a dynamic project calendar with month navigation

// Global variables for tracking the selected month and year
let selectedYear = new Date().getFullYear();
let selectedMonth = new Date().getMonth() + 1; // Months are 1-based
let selectedDate = null;
let selectedProject = null;

document.addEventListener("DOMContentLoaded", () => {
    updateCalendar();
});

async function fetchCalendarData(year, month) {
    try {
        const response = await fetch(`/calendar/calendar-data?year=${year}&month=${month}`);
        if (!response.ok) throw new Error('Failed to fetch calendar data.');
        const data = await response.json();

        if (!data.calendar) throw new Error('No calendar data available.');
        if (!data.projects) throw new Error('No project data available.');

        const calendar = generateFullCalendar(year, month);
        renderCalendar(calendar, data.calendar);
    } catch (error) {
        alert('Failed to load calendar data. Please try again.');
        console.error('Error fetching calendar data:', error);
    }
}

function generateFullCalendar(year, month) {
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);

    const daysInMonth = [];
    let day = new Date(firstDay);

    // Add empty days for the first row
    for (let i = 0; i < firstDay.getDay(); i++) {
        daysInMonth.push(null);
    }

    // Add all days of the month
    while (day <= lastDay) {
        daysInMonth.push(new Date(day));
        day.setDate(day.getDate() + 1);
    }

    // Add empty days for the last row
    for (let i = lastDay.getDay() + 1; i < 7; i++) {
        daysInMonth.push(null);
    }

    return daysInMonth;
}

function renderCalendar(days, calendarData) {
    const calendarGrid = document.getElementById('calendar-grid');
    if (!calendarGrid) {
        console.error("Element with ID 'calendar-grid' not found.");
        return;
    }
    calendarGrid.innerHTML = ''; // Clear existing content

    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize time to midnight for comparison

    days.forEach(date => {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'calendar-date';

        if (date) {
            const dateString = date.toISOString().split('T')[0];
            dateDiv.innerHTML = `<strong>${date.getDate()}</strong>`;

            if (calendarData[dateString]) {
                applyStatusClasses(dateDiv, calendarData[dateString]);

                const projectList = document.createElement('div');
                projectList.className = 'project-list';
                Object.entries(calendarData[dateString]).forEach(([projectId, status]) => {
                    const projectButton = document.createElement('button');
                    projectButton.textContent = `Project ${projectId} (${status})`;
                    projectButton.className = `status ${status.replace('_', '-')}`;
                    projectButton.dataset.projectId = projectId;
                    projectButton.dataset.date = dateString;

                    // Ensure project selection is updated
                    projectButton.addEventListener('click', (e) => {
                        e.preventDefault();
                        selectedProject = projectId;
                        selectedDate = dateString;

                        document.getElementById('selected_date').value = selectedDate;
                        document.getElementById('selected_project').value = selectedProject;

                        highlightSelection(dateDiv, projectButton);
                    });

                    projectList.appendChild(projectButton);
                });
                dateDiv.appendChild(projectList);
            }

            dateDiv.addEventListener('click', () => {
                selectedDate = dateString;
                document.getElementById('selected_date').value = selectedDate;
            });
        } else {
            dateDiv.classList.add('empty');
        }

        calendarGrid.appendChild(dateDiv);
    });

    document.getElementById('calendarForm').addEventListener('submit', (event) => {
        if (!selectedDate || !selectedProject) {
            event.preventDefault();
            alert('Please select both a date and a project.');
        }
    });
}


function applyStatusClasses(dateDiv, projects) {
    const statuses = Object.values(projects);
    if (statuses.every(status => status === 'completed')) {
        dateDiv.classList.add('completed');
    } else if (statuses.some(status => status === 'in_progress')) {
        dateDiv.classList.add('in-progress');
    } else {
        dateDiv.classList.add('not-started');
    }
}

function highlightSelection(dateDiv, projectButton) {
    document.querySelectorAll('.calendar-date').forEach(div => div.classList.remove('selected'));
    document.querySelectorAll('.project-list button').forEach(button => button.classList.remove('selected-project'));
    dateDiv.classList.add('selected');
    projectButton.classList.add('selected-project');
}

// Navigation buttons for changing months
document.getElementById("prevMonthBtn").addEventListener("click", () => {
    selectedMonth--;
    if (selectedMonth < 1) {
        selectedMonth = 12;
        selectedYear--;
    }
    updateCalendar();
});

document.getElementById("nextMonthBtn").addEventListener("click", () => {
    selectedMonth++;
    if (selectedMonth > 12) {
        selectedMonth = 1;
        selectedYear++;
    }
    updateCalendar();
});

function updateCalendar() {
    document.getElementById("currentMonth").textContent = 
        new Date(selectedYear, selectedMonth - 1).toLocaleString('en-US', { month: 'long', year: 'numeric' });
    fetchCalendarData(selectedYear, selectedMonth);
}
