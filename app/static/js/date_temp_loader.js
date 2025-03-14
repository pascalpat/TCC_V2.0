// Get the current date and update the DOM
export function getCurrentDate() {
    // Create the current date object
    const today = new Date();

    // Format for display
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = today.toLocaleDateString(undefined, options);

    // Update the date display element
    const currentDateElement = document.getElementById('currentDate');
    if (currentDateElement) {
        currentDateElement.textContent = formattedDate;
    } else {
        console.error("'currentDate' element not found.");
    }

    // Update the date selector
    const dateSelector = document.getElementById('dateSelector');
    if (dateSelector) {
        dateSelector.value = today.toISOString().split("T")[0];
    } else {
        console.error("'dateSelector' element not found.");
    }
}
window.getCurrentDate = getCurrentDate; // Add this line


// Highlight completed and in-progress dates on the calendar
export async function highlightDates() {
   

    // Check if datesData is valid
    if (!datesData || !Array.isArray(datesData) || datesData.length === 0) {
        console.warn('No dates available to highlight.');
        return; // Exit the function early if there's no valid data
    }

    if (!datesData || !Array.isArray(datesData)) {
        console.error('Invalid dates data provided to highlightDates:', datesData);
        return; // Exit gracefully
    }
    
    try { 
        const response = await fetch('/data-entry/days-status');
        if (!response.ok) throw new Error('Failed to fetch day statuses.');

        const responseData = await response.json();

        const completedDays = responseData.completedDays || [];
        const incompleteDays = responseData.incompleteDays || [];

        const dateSelector = document.getElementById('dateSelector');
        if (!dateSelector) {
            console.error("'dateSelector' element not found.");
            return;
        }

        const options = dateSelector.options;
        for (let i = 0; i < options.length; i++) {
            const optionDate = options[i].value;

            if (completedDays.includes(optionDate)) {
                options[i].style.backgroundColor = "green"; // Completed
            } else if (incompleteDays.includes(optionDate)) {
                options[i].style.backgroundColor = "orange"; // In-progress
            } else {
                options[i].style.backgroundColor = ""; // Default
            }
        }
    } catch (error) {
        console.error('Error highlighting dates: ${error.message}', error);
    }
}

// Confirm the selected date and initialize it in the session
export async function confirmDateSelection(SelectedDate) {
    // Call the backend or perform other logic with the selected date
    fetch('/data-entry/initialize-day', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: selectedDate }),
    })
    .then((response) => {
        if (!response.ok) throw new Error('Failed to initialize date');
        return response.json();
    })
    .then((data) => {
        // Perform any additional logic (e.g., updating the session, enabling tabs)
    })
    .catch((error) => {
        console.error('Error confirming date:', error);
    });
}


// Fetch the temperature and update the DOM
export async function getTemperature() {
    try {
        // Fetch the API key from the backend
        const keyResponse = await fetch('/api/get-weather-key');
        const keyData = await keyResponse.json();
        const apiKey = keyData.apiKey;

        if (!apiKey) {
            console.error('Weather API key not found!');
            return;
        }

        // Fetch the weather data
        const city = 'Montreal';
        const weatherResponse = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`
        );

        if (!weatherResponse.ok) throw new Error('Failed to fetch weather data.');

        const data = await weatherResponse.json();

        // Update the DOM with weather data
        const currentTempElement = document.getElementById('currentTemperature');
        if (currentTempElement) {
            currentTempElement.textContent = `${data.main.temp}°C in ${city}`;
        } else {
            console.error("'currentTemperature' element not found.");
        }

        const weatherIcon = document.getElementById('weatherIcon');
        if (weatherIcon) {
            weatherIcon.src = `http://openweathermap.org/img/w/${data.weather[0].icon}.png`;
            weatherIcon.alt = data.weather[0].description;
        } else {
            console.error("'weatherIcon' element not found.");
        }
    } catch (error) {
        console.error('Error fetching temperature:', error);
    }
}
window.getTemperature = getTemperature;


export async function markTabComplete(tabName) {
    try {
        const response = await fetch('/update-progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tab: tabName })
        });

        if (!response.ok) throw new Error('Failed to update progress');

        const data = await response.json();

        // Update UI for the completed tab
        updateTabUI(tabName);

        // Update the progress bar
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = `${data.progressPercentage}%`;
        }
    } catch (error) {
        console.error(`Error updating progress for tab ${tabName}:`, error);
    }
}

// Function to update the UI for a completed tab
function updateTabUI(tabName) {
    const tabElement = document.getElementById(`tab${tabName}`);
    const statusElement = document.getElementById(`status${tabName}`);

    if (tabElement && !tabElement.classList.contains('completed')) {
        tabElement.classList.add('completed');
    }
    if (statusElement) {
        statusElement.innerHTML = '✔';
        statusElement.style.color = 'green';
    }
}


//###################################################### Moved code from the clean up o th html file to here
// Function to restore progress from the server
export async function restoreProgress() {
    try {
        const response = await fetch('/update-progress/get-progress');
        if (!response.ok) throw new Error('Failed to fetch progress data');

        const data = await response.json();

        // Update the progress bar
        const progressBar = document.getElementById('progress-bar');
        if (progressBar && data.progressPercentage) {
            progressBar.style.width = `${data.progressPercentage}%`;
        }

        // Mark each completed tab
        if (Array.isArray(data.completedTabs)) {
            data.completedTabs.forEach(tabName => markTabComplete(tabName));
        }
    } catch (error) {
        console.error('Error restoring progress:', error);
    }
}
// Fetch completed tabs from the server and mark them as completed
try { 
    const response = await fetch('/update-progress/get-completed-tabs');
    if (!response.ok) throw new Error(`EE Failed to fetch completed tabs: ${response.statusText}`);
    const data = await response.json(); // Correctly placed here, after checking response status
    data.completedTabs.forEach(tab => markTabComplete(tab)); // Properly mark tabs as complete

} catch (error) {
    console.error("DD Error fetching completed tabs:", error);
}
window.restoreProgress = restoreProgress; // Expose globally