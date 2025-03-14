
export async function fetchAndRenderEquipment() {
    try {
        const response = await fetch('/equipment/list');
        if (!response.ok) {
            throw new Error('Failed to fetch equipment data');
        }
        const equipmentData = await response.json();

        const equipmentContainer = document.getElementById('equipmentContainer');
        if (!equipmentContainer) {
            console.error("Equipment container not found!");
            return;
        }

        equipmentContainer.innerHTML = equipmentData.map((equipment, index) => `
            <div class="equipmentEntry">
                <label for="equipmentName_${index}">Equipment Name:</label>
                <select id="equipmentName_${index}" name="equipmentName_${index}">
                    <option value="${equipment.equipment_id}">${equipment.equipment_name}</option>
                </select><br><br>

                <label for="equipmentHours_${index}">Hours Used:</label>
                <input type="number" id="equipmentHours_${index}" name="equipmentHours_${index}" min="0" step="0.1"><br><br>

                <label for="equipmentCode_${index}">Activity Code:</label>
                <select id="equipmentCode_${index}" name="equipmentCode_${index}">
                    <!-- Populate activity codes dynamically -->
                </select><br><br>
            </div>
        `).join('');
    } catch (error) {
        console.error("Error fetching and rendering equipment:", error);
    }
}


let equipmentCount = 0;

export function addEquipment() {
    equipmentCount++;
    const container = document.getElementById('equipmentContainer');
    if (!container) {
        console.error("Equipment container not found!");
        return;
    }

    const equipmentEntry = document.createElement('div');
    equipmentEntry.className = 'equipmentEntry';

    equipmentEntry.innerHTML = `
        <label for="equipmentName_${equipmentCount}">Equipment Name:</label>
        <select id="equipmentName_${equipmentCount}" name="equipmentName_${equipmentCount}">
            <!-- Options will be dynamically populated -->
        </select><br><br>

        <label for="equipmentHours_${equipmentCount}">Hours Used:</label>
        <input type="number" id="equipmentHours_${equipmentCount}" name="equipmentHours_${equipmentCount}" min="0" step="0.1"><br><br>

        <label for="equipmentCode_${equipmentCount}">Activity Code:</label>
        <select id="equipmentCode_${equipmentCount}" name="equipmentCode_${equipmentCount}">
            <!-- Options will be dynamically populated -->
        </select><br><br>
    `;

    container.appendChild(equipmentEntry);
   
}
