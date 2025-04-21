// Function to populate all dropdowns
export async function populateDropdowns() {
    console.log("[populateDropdowns] Starting to populate dropdowns...");
    await populateWorkersAndEquipmentDropdown(); // Combined function
    await populateActivityDropdown();  // ✅ Correctly calling activity dropdowns
    await populateFormFromSession(); // ✅ Now correctly exported
    console.log("[populateDropdowns] All dropdowns populated.");
}

async function populateWorkersAndEquipmentDropdown() {
    try {
        console.log("[populateWorkersAndEquipmentDropdown] Fetching /workers/list & /equipment/list...");
        const [workersResponse, equipmentResponse] = await Promise.all([
            fetch('/workers/list'),
            fetch('/equipment/list')
        ]);

        if (!workersResponse.ok) {
            throw new Error(`Failed to fetch workers (status ${workersResponse.status})`);
        }
        if (!equipmentResponse.ok) {
            throw new Error(`Failed to fetch equipment (status ${equipmentResponse.status})`);
        }

        const workersData = await workersResponse.json();
        const equipmentData = await equipmentResponse.json();
        console.log("[populateWorkersAndEquipmentDropdown] Workers fetched:", workersData);
        console.log("[populateWorkersAndEquipmentDropdown] Equipment fetched:", equipmentData);

        const dropdown = document.getElementById('workerName');
        if (!dropdown) {
            console.error("[populateWorkersAndEquipmentDropdown] #workerName element not found!");
            return;
        }
        dropdown.innerHTML = '<option value="" disabled selected>-- Sélectionner Employé ou Équipement --</option>';

        let workerGroup = document.createElement("optgroup");
        workerGroup.label = "👤 Employés";
        workersData.workers.forEach(worker => {
            let option = document.createElement("option");
            option.value = `worker|${worker.id}`;
            option.textContent = `👤 ${worker.name}`;
            workerGroup.appendChild(option);
        });
        dropdown.appendChild(workerGroup);

        let equipmentGroup = document.createElement("optgroup");
        equipmentGroup.label = "🛠️ Équipements";
        equipmentData.equipment.forEach(equipment => {
            let option = document.createElement("option");
            option.value = `equipment|${equipment.id}`;
            option.textContent = `🛠️ ${equipment.name}`;
            equipmentGroup.appendChild(option);
        });
        dropdown.appendChild(equipmentGroup);

        console.log("[populateWorkersAndEquipmentDropdown] Successfully populated dropdown with workers and equipment.");
    } catch (error) {
        console.error("[populateWorkersAndEquipmentDropdown] Error:", error);
    }
}

export async function populateActivityDropdown() {
    console.log("[populateActivityDropdown] Running...");
    try {
        const response = await fetch('/activity-codes/get_activity_codes');
        if (!response.ok) {
            throw new Error(`Failed to fetch activity codes (status ${response.status})`);
        }
        const data = await response.json();
        console.log("[populateActivityDropdown] Data received:", data);

        if (!data.activity_codes || data.activity_codes.length === 0) {
            console.warn("[populateActivityDropdown] No activity codes found!");
            return;
        }

        const activityDropdowns = [
            document.getElementById("activityCode"),
            document.getElementById("materialActivityCode"),
            document.getElementById("subcontractorActivityCode")
        ];

        activityDropdowns.forEach(dropdown => {
            if (dropdown) {
                populateDropdown(dropdown, data.activity_codes);
            }
        });

        console.log("[populateActivityDropdown] Dropdowns update complete!");
    } catch (error) {
        console.error("[populateActivityDropdown] ERROR:", error);
    }
}

function populateDropdown(dropdown, data) {
    dropdown.innerHTML = '<option value="" disabled selected>-- Sélectionner Code Activité --</option>';
    data.forEach(activity => {
        if (activity.code.trim() !== "") {
            const option = document.createElement("option");
            option.value = activity.code;
            option.textContent = `${activity.code} - ${activity.description}`;
            dropdown.appendChild(option);
        }
    });
    console.log(`[populateActivityDropdown] ${dropdown.id} populated with ${data.length} items.`);
}

export async function populateFormFromSession() {
    console.log("[populateFormFromSession] Fetching session data...");
    try {
        const response = await fetch('/debug/session');
        if (!response.ok) {
            throw new Error(`Failed to fetch session data (status ${response.status})`);
        }
        const sessionData = await response.json();
        console.log("[populateFormFromSession] Data received:", sessionData);

        if (sessionData.current_reporting_date) {
            document.getElementById("dateSelector").value = sessionData.current_reporting_date;
        }

        const dateKey = sessionData.current_reporting_date;
        if (sessionData.daily_data && sessionData.daily_data[dateKey]) {
            const dayObj = sessionData.daily_data[dateKey];

            if (dayObj.workers && dayObj.workers.length > 0) {
                const tableBody = document.getElementById("workersTable").getElementsByTagName('tbody')[0];
                tableBody.innerHTML = "";
                dayObj.workers.forEach(worker => {
                    let newRow = tableBody.insertRow();
                    newRow.innerHTML = `
                        <td>${worker.worker}</td>
                        <td>${worker.status}</td>
                        <td>${worker.newEntry}</td>
                    `;
                });
                console.log("[populateFormFromSession] Workers table updated!");
            } else {
                console.log("[populateFormFromSession] No workers array found for date:", dateKey);
            }
        } else {
            console.log("[populateFormFromSession] No data found for date:", dateKey);
        }
    } catch (error) {
        console.error("[populateFormFromSession] ERROR:", error);
    }
}
