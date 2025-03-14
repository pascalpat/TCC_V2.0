// workers.js
// Helper function to fetch and render workers
export async function fetchAndRenderWorkers() {
    console.log("Fetching workers from session...");
    try {
        // Fetch workers from session
        console.log("Fetching workers...workers.js line 7");
        const response = await fetch('/workers/session-list');
        if (!response.ok) {
            throw new Error(`Failed to fetch workers: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Session workers fetched:workers.js line 14", data);

        
        // Render the workers in the table
        const workersTable = document.getElementById('workersTable');
        if (!workersTable) {
            console.error("Table with ID 'workersTable' not found in DOM.workers,js line 20");
            return;
        }

        workersTable.innerHTML = ''; // Clear the table

        data.workers.forEach(worker => {
            if (worker.workerName || worker.laborHours || worker.activityCode) {
                const row = workersTable.insertRow();
                row.innerHTML = `
                    <td>${worker.workerName || 'N/A'}</td>
                    <td>${worker.laborHours || 'N/A'}</td>
                    <td>${worker.activityCode || 'N/A'}</td>
                `;
            }
        });
    } catch (error) {
        console.error("Error fetching workers:", error);
        alert("Unable to load workers. Please try again later.");
    }
}

export async function addWorker() {
    console.log("Add Worker button clicked...workers.js line 43");

    // Fetch DOM elements
    const addWorkerBtn = document.getElementById('addWorkerBtn');
    const workerDropdown = document.getElementById('workerName');
    const laborHoursInput = document.getElementById('laborHours');
    const activityCodeInput = document.getElementById('activityCode');

    // Get input values
    const workerName = workerDropdown?.value;
    const laborHours = laborHoursInput?.value;
    const activityCode = activityCodeInput?.value || 'N/A'; // Default to 'N/A' if not provided

    // Input validation
    if (!workerName || !laborHours) {
        alert("Please fill in all required worker details (Name and Hours).");
        return;
    }

    if (isNaN(laborHours) || laborHours <= 0) {
        alert("Please enter a valid number for hours worked.");
        return;
    }

    if (typeof workerName !== 'string' || typeof laborHours !== 'string' || isNaN(Number(laborHours))) {
        alert("Invalid data format. Please check your input.");
        return;
    }
    
    // Check for duplicates in the table
    //const existingWorkers = Array.from(
        //document.querySelectorAll('#workersTable tbody tr td:first-child')
    //).map(cell => cell.textContent.trim());

    //if (existingWorkers.includes(workerName)) {
        //alert('This worker is already added.');
        //return;
    //}

    // Disable the button and show a loading state
    addWorkerBtn.disabled = true;
    addWorkerBtn.textContent = 'Adding...workers.js line 84';

    // Submit worker data to the server
    try {
        // Log the payload being sent for debugging
        const payload = { workerName, laborHours, activityCode };
        console.log("Payload sent to server:workers.js line 90", payload);

        const response = await fetch('/workers/add-worker', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        // Handle server response
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Failed to add worker: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Worker added successfully. Server response:workers.js line 107", data);

        // Re-render the workers table with the updated list from the session
        await fetchAndRenderWorkers();

        // Reset form inputs after successful submission
        workerDropdown.selectedIndex = 0; // Reset dropdown to placeholder
        laborHoursInput.value = ''; // Clear input field
        alert('Worker added successfully! workers.js line 115');
    } catch (error) {
        console.error("Error adding worker:", error);
        alert(`Error adding worker: ${error.message}`);
    } finally {
        // Re-enable the button and reset its text
        addWorkerBtn.disabled = false;
        addWorkerBtn.textContent = 'Add Worker';
    }

    
}


export async function confirmWorkers() {
    console.log("Confirming workers...workers.js line 130");
    try {
        // Fetch worker data from the table
        const workersTableRows = Array.from(document.querySelectorAll('#workersTable tbody tr'));
        const workers = workersTableRows.map(row => {
            const cells = row.querySelectorAll('td');
            return {
                workerName: cells[0].textContent.trim(),
                laborHours: cells[1].textContent.trim(),
                activityCode: cells[2].textContent.trim()
            };
        });

        if (workers.length === 0) {
            alert("No workers to confirm.");
            return;
        }

        console.log("Payload to be sent to the server:", { workers });

        const response = await fetch('/workers/confirm-workers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ workers }) // Ensure valid JSON payload
        });

        if (!response.ok) throw new Error('Failed to confirm workers');

        const data = await response.json();
        console.log("Workers confirmed successfully:", data);
        alert('Workers confirmed successfully!');

        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        if (progressBar && data.progressPercentage !== undefined) {
            progressBar.style.width = `${data.progressPercentage}%`;
            console.log(`Progress updated: ${data.progressPercentage}%`);
        }
    } catch (error) {
        console.error('Error confirming workers:', error);
        alert('Failed to confirm workers. Please try again.');
    }


}