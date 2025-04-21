// laborEquipment.js

let confirmedUsageData = [];
let manualWorkerMode = false;
let manualEquipMode = false;

// ----------------------
// 1. Main Initialization Function
// ----------------------
export function initLaborEquipmentTab() {
  console.log("Initializing Labor & Equipment Tab...");

  document.getElementById('addEntryBtn')?.addEventListener('click', addUsageLine);
  document.getElementById('confirmEntriesBtn')?.addEventListener('click', confirmUsageLines);
  document.getElementById("manualEntryToggle")?.addEventListener("click", toggleManualWorkerEntry);
  document.getElementById("manualEquipToggle")?.addEventListener("click", toggleManualEquipEntry);

  const projectId = document.getElementById("projectNumber")?.value;
  const reportDate = document.getElementById("dateSelector")?.value;

  if (projectId && reportDate) {
    loadPendingEntries(projectId, reportDate);
  }

  /// Ensure inputs are hidden on init
  resetFormUI();

  // Ensure inputs are hidden on init
  // document.getElementById("manualWorkerName").style.display = "none";
  // document.getElementById("manualEquipmentName").style.display = "none";
  // document.getElementById("manualWorkerName").classList.add("hidden");
  // document.getElementById("manualEquipmentName").classList.add("hidden")
}
function toggleManualEntry(mode) {
  const dropdown = document.getElementById("workerName");
  const manualWorkerInput = document.getElementById("manualWorkerName");
  const manualEquipInput = document.getElementById("manualEquipmentName");

  manualWorkerMode = (mode === 'worker');
  manualEquipMode = (mode === 'equipment');

  dropdown.disabled = true;
  dropdown.classList.add("hidden");

  if (manualWorkerMode) {
    manualWorkerInput.classList.remove("hidden");
    manualWorkerInput.style.display = "inline-block";
    manualWorkerInput.focus();
    manualEquipInput.style.display = "none";
    manualEquipInput.classList.add("hidden");
    manualEquipInput.value = "";
    console.log("✅ Manual Worker Mode ON");
  } else if (manualEquipMode) {
    manualEquipInput.classList.remove("hidden");
    manualEquipInput.style.display = "inline-block";
    manualEquipInput.focus();
    manualWorkerInput.style.display = "none";
    manualWorkerInput.classList.add("hidden");
    manualWorkerInput.value = "";
    console.log("✅ Manual Equipment Mode ON");
  }
}

//function toggleManualWorkerEntry() {
  //const dropdown = document.getElementById("workerName");
  //const manualWorkerInput = document.getElementById("manualWorkerName");
  //const manualEquipInput = document.getElementById("manualEquipmentName");

  // Reset manual input states
  //manualWorkerMode = true;
  //manualEquipMode = false;

  // Hide dropdown
  //dropdown.disabled = true;
  //dropdown.classList.add("hidden");

  // Show manual worker input
  //manualWorkerInput.classList.remove("hidden");
  //manualWorkerInput.style.display = "inline-block";
  //manualWorkerInput.focus();

  // Hide equipment input
  //manualEquipInput.classList.add("hidden");
  //manualEquipInput.style.display = "none";
  //manualEquipInput.value = "";

  //console.log("Manual Worker mode ON");
//}

//function toggleManualEquipEntry() {
  //const dropdown = document.getElementById("workerName");
  //const manualWorkerInput = document.getElementById("manualWorkerName");
  //const manualEquipInput = document.getElementById("manualEquipmentName");

  //manualEquipMode = true;
  //manualWorkerMode = false;

  //dropdown.disabled = true;
  //dropdown.classList.add("hidden");

  //manualEquipInput.classList.remove("hidden");
  //manualEquipInput.style.display = "inline-block";
  //manualEquipInput.focus();

  //manualWorkerInput.classList.add("hidden");
  //manualWorkerInput.style.display = "none";
  //manualWorkerInput.value = "";
  //console.log("Manual Equipment mode ON");
//}

function resetFormUI() {
  const dropdown = document.getElementById("workerName");
  const manualWorkerInput = document.getElementById("manualWorkerName");
  const manualEquipInput = document.getElementById("manualEquipmentName");

  dropdown.disabled = false;
  dropdown.classList.remove("hidden");
  dropdown.selectedIndex = 0;

  manualWorkerInput.style.display = "none";
  manualWorkerInput.classList.add("hidden");
  manualWorkerInput.value = "";

  manualEquipInput.style.display = "none";
  manualEquipInput.classList.add("hidden");
  manualEquipInput.value = "";

  document.getElementById("laborHours").value = "";
  document.getElementById("activityCode").selectedIndex = 0;

  manualWorkerMode = false;
  manualEquipMode = false;
}

// ----------------------
// 2. Add Entry to Table
// ----------------------
function addUsageLine(event) {
  event.preventDefault();

  const workerSelect = document.getElementById("workerName");
  const manualWorkerInput = document.getElementById("manualWorkerName");
  const manualEquipInput = document.getElementById("manualEquipmentName");
  const hoursInput = document.getElementById("laborHours");
  const activitySelect = document.getElementById("activityCode");

  const hours = hoursInput.value;
  const activityCode = activitySelect.value;
  const activityText = activitySelect.options[activitySelect.selectedIndex]?.text || "";

  let type, entityId, name;

  if (manualWorkerMode && manualWorkerInput.value.trim()) {
    type = "worker";
    entityId = null;
    name = manualWorkerInput.value.trim();
  } else if (manualEquipMode && manualEquipInput.value.trim()) {
    type = "equipment";
    entityId = null;
    name = manualEquipInput.value.trim();
  } else if (workerSelect.value) {
    const selectedValue = workerSelect.value;
    const selectedText = workerSelect.options[workerSelect.selectedIndex]?.text || "";
    const [parsedType, parsedId] = selectedValue.split('|');
    type = parsedType;
    entityId = parsedId;
    name = selectedText;
  } else {
    alert("Veuillez remplir tous les champs.");
    return;
  }

  if (!hours || !activityCode) {
    alert("Veuillez remplir tous les champs.");
    return;
  }

  const usageTableBody = document.querySelector("#workersTable tbody");
  const row = usageTableBody.insertRow();
  row.innerHTML = `
    <td data-type="${type}" data-id="${entityId ?? ''}">${name}</td>
    <td>${hours}</td>
    <td data-actval="${activityCode}">${activityText}</td>
  `;

  resetFormUI();
}

// ----------------------
// 3. Confirm and Save Entries
// ----------------------
async function confirmUsageLines(event) {
  event.preventDefault();

  const usageTableBody = document.querySelector('#workersTable tbody');
  const rows = usageTableBody.querySelectorAll('tr');
  if (rows.length === 0) {
    alert('Aucune entrée à confirmer.');
    return;
  }

  const usageArr = [];

  rows.forEach(row => {
    if (row.classList.contains('confirmed-row')) return;

    const cells = row.querySelectorAll('td');
    const type = cells[0].getAttribute('data-type');
    const entityId = cells[0].getAttribute('data-id');
    const name = cells[0].textContent.trim();
    const hours = cells[1].textContent.trim();
    const actCode = cells[2].getAttribute('data-actval');
    const isManual = !entityId || entityId === "undefined" || entityId === "";

    // Manual entry must have a name
    if (!type || !hours || !actCode || (isManual && !name)) {
      console.warn("Skipping malformed row:", { type, entityId, name, hours, actCode });
      return;
    }

    usageArr.push({
      type,
      entityId: isManual ? null : entityId,
      hours,
      activityCode: actCode,
      isManual,
      manual_name: isManual ? name : null
    });
  });

  try {
    const projectId = document.getElementById("projectNumber").value;
    const reportDate = document.getElementById("dateSelector").value;

    const resp = await fetch('/labor-equipment/confirm-labor-equipment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        usage: usageArr,
        project_id: projectId,
        date_of_report: reportDate
      }),
    });

    if (!resp.ok) {
      const errData = await resp.json();
      throw new Error(errData.error || 'Erreur de confirmation');
    }

    alert("Les données ont été confirmées.");
    loadPendingEntries(projectId, reportDate);

  } catch (error) {
    console.error('Erreur lors de la confirmation :', error);
    alert('Erreur : ' + error.message);
  }
}

// ----------------------
// 4. Load From Backend
// ----------------------
async function loadPendingEntries(projectId, reportDate) {
  try {
    const resp = await fetch(`/labor-equipment/by-project-date?project_id=${projectId}&date=${reportDate}`);
    if (!resp.ok) throw new Error("Impossible de charger les données du serveur.");

    const data = await resp.json();
    renderConfirmedTableFromServer(data.workers, data.equipment);
  } catch (err) {
    console.error("Erreur lors du chargement des entrées :", err);
  }
}

// ----------------------
// 5. Render Confirmed Table From Server
// ----------------------
function renderConfirmedTableFromServer(workers = [], equipment = []) {
  const tableBody = document.querySelector("#workersTable tbody");
  tableBody.innerHTML = "";

  [...workers, ...equipment].forEach(entry => {
    const isWorker = entry.worker_id !== undefined;
    const type = isWorker ? "worker" : "equipment";
    const entityId = isWorker ? entry.worker_id : entry.equipment_id;
    const name = entry.worker_name ?? entry.equipment_name ?? `ID-${entityId}`;
    const hours = entry.hours ?? entry.hours_worked ?? entry.hours_used ?? '??';
    const activity = entry.activity_code
      ? `${entry.activity_code} - ${entry.activity_description || ''}`
      : "<em>Code-undefined</em>";

    const row = document.createElement("tr");
    row.classList.add("confirmed-row");

    row.innerHTML = `
      <td data-type="${type}" data-id="${entityId}">${name}</td>
      <td>${hours}</td>
      <td data-actval="${entry.activity_id}">${activity}</td>
      <td class="actions">
        <button class="edit-btn" data-entry-id="${entry.id}" data-type="${type}">✏️</button>
        <button class="delete-btn" data-entry-id="${entry.id}" data-type="${type}">🗑️</button>
      </td>
    `;

    tableBody.appendChild(row);
  });

  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', handleEditConfirmedRow);
  });
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', handleDeleteConfirmedRow);
  });
}

// Edit and Save Handlers (as previously implemented)
function handleEditConfirmedRow(event) {
  const btn = event.currentTarget;
  const row = btn.closest("tr");
  const entryId = btn.getAttribute("data-entry-id");
  const type = btn.getAttribute("data-type");

  const cells = row.querySelectorAll("td");
  const currentHours = cells[1].textContent.trim();
  const currentActCode = cells[2].getAttribute("data-actval");

  cells[1].innerHTML = `<input type="number" min="0" step="0.1" value="${currentHours}" />`;

  const activitySelect = document.createElement("select");
  activitySelect.id = "editActivitySelect";

  fetch('/activity-codes/get_activity_codes')
    .then(resp => resp.json())
    .then(data => {
      if (!data.activity_codes) return;

      data.activity_codes.forEach(ac => {
        const opt = document.createElement("option");
        opt.value = ac.code;
        opt.textContent = `${ac.code} - ${ac.description}`;
        if (ac.id == currentActCode || ac.code == currentActCode) {
          opt.selected = true;
        }
        activitySelect.appendChild(opt);
      });

      cells[2].innerHTML = "";
      cells[2].appendChild(activitySelect);

      const actionsCell = cells[3];
      actionsCell.innerHTML = `
        <button class="save-edit-btn" data-entry-id="${entryId}" data-type="${type}">💾</button>
        <button class="cancel-edit-btn" data-entry-id="${entryId}" data-type="${type}">❌</button>
      `;

      actionsCell.querySelector(".save-edit-btn").addEventListener("click", handleSaveEditConfirmedRow);
      actionsCell.querySelector(".cancel-edit-btn").addEventListener("click", () => {
        const projectId = document.getElementById("projectNumber").value;
        const reportDate = document.getElementById("dateSelector").value;
        loadPendingEntries(projectId, reportDate);
      });
    });
}

function handleSaveEditConfirmedRow(event) {
  const btn = event.currentTarget;
  const row = btn.closest("tr");
  const entryId = btn.getAttribute("data-entry-id");
  const type = btn.getAttribute("data-type");

  const hours = row.querySelector("input[type='number']").value;
  const activityCode = row.querySelector("select").value;

  fetch(`/labor-equipment/update-entry/${type}/${entryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hours, activity_code: activityCode })
  })
    .then(resp => resp.json())
    .then(data => {
      if (data.message) {
        alert("Entrée mise à jour.");
        const projectId = document.getElementById("projectNumber").value;
        const reportDate = document.getElementById("dateSelector").value;
        loadPendingEntries(projectId, reportDate);
      } else {
        alert(data.error || "Erreur lors de la mise à jour.");
      }
    })
    .catch(err => {
      console.error("Erreur de mise à jour:", err);
      alert("Erreur côté serveur.");
    });
}

function handleDeleteConfirmedRow(event) {
  const btn = event.currentTarget;
  const entryId = btn.getAttribute("data-entry-id");
  const type = btn.getAttribute("data-type");

  if (!confirm("Voulez-vous supprimer cette entrée?")) return;

  fetch(`/labor-equipment/delete-entry/${type}/${entryId}`, {
    method: "DELETE"
  })
  .then(resp => resp.json())
  .then(data => {
    if (data.message) {
      alert("Entrée supprimée.");
      const projectId = document.getElementById("projectNumber").value;
      const reportDate = document.getElementById("dateSelector").value;
      loadPendingEntries(projectId, reportDate);
    } else {
      alert(data.error || "Erreur lors de la suppression.");
    }
  })
  .catch(err => {
    console.error("Erreur lors de la suppression:", err);
    alert("Erreur côté serveur.");
  });
}


// ----------------------
// Manual Entry Toggles for Worker & Equipment
// ----------------------
document.addEventListener("DOMContentLoaded", () => {
  const manualWorkerToggle = document.getElementById("manualEntryToggle");
  const manualEquipToggle = document.getElementById("manualEquipToggle");
  const manualWorkerInput = document.getElementById("manualWorkerName");
  const manualEquipInput = document.getElementById("manualEquipmentName");
  const dropdown = document.getElementById("workerName");

  function resetManualInputs() {
    manualWorkerInput.style.display = "none";
    manualEquipInput.style.display = "none";
    manualWorkerInput.value = "";
    manualEquipInput.value = "";
    dropdown.disabled = false;
    manualWorkerMode = false;
    manualEquipMode = false;
  }

  manualWorkerToggle?.addEventListener("click", () => {
      resetManualInputs();
      manualWorkerInput.style.display = "inline-block";
      dropdown.disabled = true;
      manualWorkerMode = true;
      console.log("✅ Manual worker mode ON");
    });
  

  manualEquipToggle?.addEventListener("click", () => {
      resetManualInputs();
      manualEquipInput.style.display = "inline-block";
      dropdown.disabled = true;
      manualEquipMode = true;
      console.log("✅ Manual equipment mode ON");
    });
  
});