// laborEquipment.js

// ------------- 1. Main Entry Point -------------
export function initLaborEquipmentTab() {
  console.log("Initializing Labor & Equipment Tab...");

  // Hook up the radio buttons to hide/show the correct dropdown
  const usageWorkerRadio = document.getElementById('usageWorker');
  const usageEquipmentRadio = document.getElementById('usageEquipment');
  const workerDropdownContainer = document.getElementById('workerDropdownContainer');
  const equipmentDropdownContainer = document.getElementById('equipmentDropdownContainer');

  // This function toggles which dropdown is visible
  function toggleDropdowns() {
    if (usageWorkerRadio.checked) {
      workerDropdownContainer.style.display = 'block';
      equipmentDropdownContainer.style.display = 'none';
    } else {
      workerDropdownContainer.style.display = 'none';
      equipmentDropdownContainer.style.display = 'block';
    }
  }
  // Attach listeners
  usageWorkerRadio.addEventListener('change', toggleDropdowns);
  usageEquipmentRadio.addEventListener('change', toggleDropdowns);

  // “Add” button logic
  const addUsageBtn = document.getElementById('addUsageBtn');
  addUsageBtn.addEventListener('click', addUsageLine);

  // “Confirm” button logic
  const confirmUsageBtn = document.getElementById('confirmUsageBtn');
  confirmUsageBtn.addEventListener('click', confirmUsageLines);

  // Populate the three dropdowns (Workers, Equipment, Activity Codes)
  fetchAndPopulateAllDropdowns();

  // Optionally call toggleDropdowns at startup to ensure correct visibility
  toggleDropdowns();
}


// ------------- 2. Fetch & Populate the 3 Dropdowns -------------
async function fetchAndPopulateAllDropdowns() {
  try {
    // 1) Fetch Workers from /workers/list
    const workerRes = await fetch('/workers/list');
    if (!workerRes.ok) throw new Error(`Workers list fetch failed: ${workerRes.status}`);
    const workerData = await workerRes.json();

    // 2) Fill the #workerId <select>
    const workerName = document.getElementById('workerId');
    if (workerName && workerData.workers) {
      workerName.innerHTML = `<option value="" disabled selected>-- Sélectionner Employé --</option>`;
      workerData.workers.forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.id;   // store the worker ID
        opt.textContent = w.name;
        workerName.appendChild(opt);
      });
    }

    // 3) Fetch Equipment from /equipment/list
    const equipRes = await fetch('/equipment/list');
    if (!equipRes.ok) throw new Error(`Equipment list fetch failed: ${equipRes.status}`);
    const equipData = await equipRes.json();

    // 4) Fill the #equipmentId <select>
    const equipmentSelect = document.getElementById('equipmentId');
    if (equipmentSelect && equipData.equipment) {
      equipmentSelect.innerHTML = `<option value="" disabled selected>-- Sélectionner Équipement --</option>`;
      equipData.equipment.forEach(eq => {
        const opt = document.createElement('option');
        opt.value = eq.id;     // store the equipment ID
        opt.textContent = eq.name;
        equipmentSelect.appendChild(opt);
      });
    }

    // 5) Fetch Activity Codes from /activity_codes/list (adjust if your route differs)
    const actRes = await fetch('/activity_codes/list');
    if (!actRes.ok) throw new Error(`Activity codes fetch failed: ${actRes.status}`);
    const actData = await actRes.json();

    // 6) Fill the #activityCode <select>
    const activitySelect = document.getElementById('activityCode');
    if (activitySelect && actData.activity_codes) {
      activitySelect.innerHTML = `<option value="" disabled selected>-- Sélectionner Code --</option>`;
      actData.activity_codes.forEach(ac => {
        const opt = document.createElement('option');
        opt.value = ac.code; // store code
        // You can combine code & description if you want
        opt.textContent = `${ac.code} - ${ac.description || ''}`;
        activitySelect.appendChild(opt);
      });
    }

    console.log('Dropdowns have been successfully populated.');
  } catch (error) {
    console.error('Error fetching/poplating dropdowns:', error);
  }
}


// ------------- 3. Add a Usage Line to the Table -------------
function addUsageLine() {
  console.log('addUsageLine() triggered');

  // 1) Determine type: worker or equipment
  const usageType = document.querySelector('input[name="usageType"]:checked')?.value;
  if (!usageType) {
    alert('Please select either “Employé” or “Équipement”');
    return;
  }

  // 2) Based on usageType, read the ID from workerId or equipmentId
  let selectedId = '';
  let selectedName = '';
  if (usageType === 'worker') {
    const workerName = document.getElementById('workerId');
    selectedId = workerName.value;
    // If you also want to store the text, do:
    selectedName = workerName.options[workerName.selectedIndex].text;
  } else {
    const equipSelect = document.getElementById('equipmentId');
    selectedId = equipSelect.value;
    selectedName = equipSelect.options[equipSelect.selectedIndex].text;
  }

  // 3) Grab hours & activity code
  const usageHours = document.getElementById('usageHours').value || '';
  const activitySelect = document.getElementById('activityCode');
  const activityVal = activitySelect?.value || '';
  const activityText = activitySelect.options[activitySelect.selectedIndex]?.text || '';

  // Basic validation
  if (!selectedId || !usageHours || !activityVal) {
    alert('Please select a valid name, enter hours, and pick an activity code.');
    return;
  }

  // 4) Insert row in #usageTable
  const usageTableBody = document.querySelector('#usageTable tbody');
  const newRow = usageTableBody.insertRow();
  newRow.innerHTML = `
    <td>${usageType === 'worker' ? 'Employé' : 'Équipement'}</td>
    <td data-id="${selectedId}">${selectedName}</td>
    <td>${usageHours}</td>
    <td data-actval="${activityVal}">${activityText}</td>
  `;

  // 5) Optionally reset the form
  document.getElementById('usageHours').value = '';
  if (usageType === 'worker') {
    document.getElementById('workerId').selectedIndex = 0;
  } else {
    document.getElementById('equipmentId').selectedIndex = 0;
  }
  document.getElementById('activityCode').selectedIndex = 0;

  console.log('Usage line added to table.', usageType, selectedId, usageHours, activityVal);
}


// ------------- 4. Confirm and POST usage lines -------------
async function confirmUsageLines() {
  console.log('confirmUsageLines() triggered');
  try {
    // 1) Grab all rows from #usageTable
    const usageTableBody = document.querySelector('#usageTable tbody');
    const rows = usageTableBody.querySelectorAll('tr');
    if (rows.length === 0) {
      alert('No lines to confirm');
      return;
    }

    const usageArr = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      const typeCell = cells[0].textContent.trim();         // “Employé” or “Équipement”
      const nameCell = cells[1];                            // has data-id
      const hoursCell = cells[2].textContent.trim();
      const actCell = cells[3];                             // has data-actval

      usageArr.push({
        type: typeCell,                                     // "Employé" or "Équipement"
        name: nameCell.textContent.trim(),                  // for display
        entityId: nameCell.getAttribute('data-id'),         // the actual ID
        hours: hoursCell,
        activityCode: actCell.getAttribute('data-actval'),
      });
    });

    console.log('Payload for confirm:', usageArr);

    // 2) POST to your backend route
    const resp = await fetch('/labor_equipment/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usage: usageArr }),
    });

    if (!resp.ok) {
      const errData = await resp.json();
      throw new Error(errData.error || 'Failed to confirm usage lines');
    }

    const data = await resp.json();
    alert(data.message || 'Usage lines confirmed!');

    // 3) Optionally clear table rows
    usageTableBody.innerHTML = '';

  } catch (error) {
    console.error('Error confirming usage lines:', error);
    alert('Error: ' + error.message);
  }
}

async function fetchAndPopulateAllDropdowns() {
  try {
    // 1. Fetch workers
    const workersRes = await fetch('/workers/list');
    const workersData = await workersRes.json();
    const workerName = document.getElementById('workerId');
    if (workerName && workersData.workers) {
      workersData.workers.forEach(w => {
        const option = document.createElement('option');
        option.value = w.id;        // store ID
        option.textContent = w.name; // display name
        workerName.appendChild(option);
      });
    }

    // 2. Fetch equipment
    const equipRes = await fetch('/equipment/list');
    const equipData = await equipRes.json();
    const equipmentSelect = document.getElementById('equipmentId');
    if (equipmentSelect && equipData.equipment) {
      equipData.equipment.forEach(eq => {
        const option = document.createElement('option');
        option.value = eq.id;          // store ID
        option.textContent = eq.name;  // display name
        equipmentSelect.appendChild(option);
      });
    }

    // 3. Fetch activity codes
    const activityRes = await fetch('/activity_codes/list');
    const activityData = await activityRes.json();
    const activitySelect = document.getElementById('activityCode');
    if (activitySelect && activityData.activity_codes) {
      activityData.activity_codes.forEach(ac => {
        const option = document.createElement('option');
        option.value = ac.code;
        option.textContent = ac.code + ' - ' + (ac.description || '');
        activitySelect.appendChild(option);
      });
    }

  } catch (error) {
    console.error('Error fetching dropdown data:', error);
  }
}
