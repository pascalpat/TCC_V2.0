// laborEquipment.js

import { populateFormFromSession } from './populate_drop_downs.js';


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
  document.getElementById("manualEntryToggle")?.addEventListener("click", () => toggleManualEntry("worker"));
  document.getElementById("manualEquipToggle")?.addEventListener("click", () => toggleManualEntry("equipment"));


  const projectId = document.getElementById("projectNumber")?.value;
  const reportDate = document.getElementById("dateSelector")?.value;

  if (projectId && reportDate) {
    ///populateFormFromSession(projectId, reportDate, renderConfirmedTableFromServer);
    loadPendingEntries(projectId, reportDate);
  }

  /// Ensure inputs are hidden on init
  resetFormUI();

}
function toggleManualEntry(mode) {
  const dropdown       = document.getElementById("workerName");
  const manualWorkerIn = document.getElementById("manualWorkerName");
  const manualEquipIn  = document.getElementById("manualEquipmentName");

  // 1) Toggle flags
  if (mode === 'worker') {
    manualWorkerMode = !manualWorkerMode;
    manualEquipMode  = false;
  } else {
    manualEquipMode  = !manualEquipMode;
    manualWorkerMode = false;
  }

  // 2) Dropdown visible only when no manual mode
  const anyManual = manualWorkerMode || manualEquipMode;
  dropdown.disabled = anyManual;
  dropdown.classList.toggle("hidden", anyManual);

  // 3) Worker input
  manualWorkerIn.classList.toggle("hidden",  !manualWorkerMode);
  manualWorkerIn.classList.toggle("visible", manualWorkerMode);
  if (manualWorkerMode) manualWorkerIn.focus();

  // 4) Equipment input
  manualEquipIn.classList.toggle("hidden",  !manualEquipMode);
  manualEquipIn.classList.toggle("visible", manualEquipMode);
  if (manualEquipMode) manualEquipIn.focus();

  console.log(
    manualWorkerMode ? "✅ Manual Worker Mode ON"
  : manualEquipMode  ? "✅ Manual Equipment Mode ON"
  :                     "↩️ Back to dropdown-only mode"
  );
}


function resetFormUI() {
  const dropdown         = document.getElementById("workerName");
  const manualWorkerIn   = document.getElementById("manualWorkerName");
  const manualEquipIn    = document.getElementById("manualEquipmentName");

  // Restore the worker/equipment selector
  dropdown.disabled = false;
  dropdown.classList.remove("hidden");
  dropdown.selectedIndex = 0;

  // Clear manual‐entry inputs
  manualWorkerIn.value = "";
  manualWorkerIn.classList.add("hidden");
  manualWorkerIn.classList.remove("visible");

  manualEquipIn.value = "";
  manualEquipIn.classList.add("hidden");
  manualEquipIn.classList.remove("visible");

  // Clear the hours & activity code
  document.getElementById("laborHours").value = "";
  document.getElementById("activityCode").selectedIndex = 0;

  // ← NEW: reset bordereau & CWP selects
  document.getElementById("payment_item_id").selectedIndex = 0;
  document.getElementById("cwp_code").selectedIndex       = 0;

  // Reset toggles
  manualWorkerMode = false;
  manualEquipMode  = false;
}

// ----------------------
// 2. Add Entry to Table
// ----------------------
function addUsageLine(event) {
  event.preventDefault();

  // grab all inputs
  const workerSelect      = document.getElementById("workerName");
  const manualWorkerInput = document.getElementById("manualWorkerName");
  const manualEquipInput  = document.getElementById("manualEquipmentName");
  const hoursInput        = document.getElementById("laborHours");
  const activitySelect    = document.getElementById("activityCode");
  const paymentSelect     = document.getElementById('payment_item_id');
  const cwpSelect         = document.getElementById('cwp_code');

  const hours        = hoursInput.value;
  const activityCode = activitySelect.value;
  const activityText = activitySelect.options[activitySelect.selectedIndex]?.text || '';
  const payment_item_id = paymentSelect.value || null;
  const paymentText  = paymentSelect.options[paymentSelect.selectedIndex]?.text || '';
  const cwp_code     = cwpSelect.value || null;
  const cwpText      = cwpSelect.options[cwpSelect.selectedIndex]?.text || '';

  // determine type/name/id
  let type, entityId, name;
  if (manualWorkerMode && manualWorkerInput.value.trim()) {
    type     = 'worker';
    entityId = null;
    name     = manualWorkerInput.value.trim();
  } else if (manualEquipMode && manualEquipInput.value.trim()) {
    type     = 'equipment';
    entityId = null;
    name     = manualEquipInput.value.trim();
  } else if (workerSelect.value) {
    const [parsedType, parsedId] = workerSelect.value.split('|');
    type     = parsedType;
    entityId = parsedId;
    name     = workerSelect.options[workerSelect.selectedIndex].text;
  } else {
    return alert("Veuillez remplir tous les champs.");
  }

  if (!hours || !activityCode) {
    return alert("Veuillez remplir tous les champs.");
  }

  // push into our array
  confirmedUsageData.push({
    type,
    entityId,
    name,
    hours,
    activityCode,
    activityText,
    payment_item_id,
    paymentText,
    cwp_code,
    cwpText,
    isManual:    !entityId,
    manual_name: (!entityId ? name : null)
  });

  // re-render the preview table (just the preview rows)
  renderPreviewTable();

  // clear the form
  resetFormUI();
}

/**
 * Renders the unconfirmed rows from confirmedUsageData into the preview table
 */
function renderPreviewTable() {
  const tbody = document.querySelector('#workersTable tbody');

  // 1) Remove only the old preview rows
  tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

  // 2) Append the current preview entries
  confirmedUsageData.forEach(entry => {
    const row = document.createElement('tr');
    row.classList.add('preview-row'); // mark it!
    row.innerHTML = `
      <td data-type="${entry.type}" data-id="${entry.entityId || ''}">${entry.name}</td>
      <td>${entry.hours}</td>
      <td data-actval="${entry.activityCode}">${entry.activityText}</td>
      <td data-payment-id="${entry.payment_item_id}">${entry.paymentText}</td>
      <td data-cwp-id="${entry.cwp_code}">${entry.cwpText}</td>
    `;
    tbody.appendChild(row);
  });
}

// ----------------------
// 3. Confirm and Save Entries
// ----------------------
async function confirmUsageLines(event) {
  event.preventDefault();

  // 1️⃣ Grab all un-confirmed rows from the confirmed table
  const rows = Array.from(document.querySelectorAll('#workersTable tbody tr'))
    .filter(tr => !tr.classList.contains('confirmed-row'));

  if (rows.length === 0) {
    alert('Aucune entrée à confirmer.');
    return;
  }

  // 2️⃣ Build the payload from the DOM
  const usageArr = rows.map(tr => {
    // entryId comes from the edit-button data attribute
    const editBtn = tr.querySelector('.edit-btn');
    const entryId = editBtn ? editBtn.dataset.entryId : null;

    // cells: [ nameCell, hoursCell, activityCell, bordereauCell, cwpCell, actionsCell ]
    const [nameCell, hoursCell, activityCell, bordereauCell, cwpCell] =
      tr.querySelectorAll('td');

    const type        = nameCell.dataset.type;
    const entityId    = nameCell.dataset.id || null;
    const name        = nameCell.textContent.trim();
    const hours       = hoursCell.textContent.trim();
    const activity    = activityCell.dataset.actval;
    const paymentItem = bordereauCell.dataset.paymentItemId || null;
    const cwpCode     = cwpCell.dataset.cwpCode || null;

    const isManual    = !entityId; // true if manually added

    return {
      entryId,                // existing PK to update; null → insert
      type,                   // 'worker' or 'equipment'
      entityId: isManual ? null : entityId,
      hours,
      activityCode: activity,
      payment_item_id: paymentItem,
      cwp: cwpCode,
      isManual,
      manual_name: isManual ? name : null
    };
  });

  // 3️⃣ Send every un-confirmed row in one go
  try {
    const projectId  = document.getElementById('projectNumber').value;
    const reportDate = document.getElementById('dateSelector').value;

    const resp = await fetch(
      '/labor-equipment/confirm-labor-equipment',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          usage: usageArr,
          project_id: projectId,
          date_of_report: reportDate
        })
      }
    );
    const result = await resp.json();
    if (!resp.ok) throw new Error(result.error || 'Erreur inconnue');

    alert(`Les données ont été confirmées (${result.records.length} lignes).`);

    // 4️⃣ Mark them so they won’t be re-sent next time
    rows.forEach(tr => tr.classList.add('confirmed-row'));

    // 5️⃣ Reload from server to pick up any new IDs/updates
    await loadPendingEntries(projectId, reportDate);

  } catch (err) {
    console.error('Erreur lors de la confirmation :', err);
    alert('Erreur : ' + err.message);
  }
}

// ----------------------
// 5. Render Confirmed Table From Server
// ----------------------
function renderConfirmedTableFromServer(workers = [], equipment = []) {
  const tableBody = document.querySelector("#workersTable tbody");

  // Remove only the previous confirmed‐rows (leave previews intact)
  tableBody.querySelectorAll("tr.confirmed-row").forEach(r => r.remove());

  // merge workers + equipment
  [...workers, ...equipment].forEach(entry => {
    const isWorker   = entry.worker_id !== undefined;
    const type       = isWorker ? "worker" : "equipment";
    const entityId   = isWorker ? entry.worker_id : entry.equipment_id;
    const name       = entry.worker_name ?? entry.equipment_name ?? `ID-${entityId}`;
    const hours      = entry.hours ?? "??";
    const activity   = entry.activity_code
      ? `${entry.activity_code} – ${entry.activity_description || ""}`
      : "<em>—</em>";

    // pull bordereau & CWP from JSON
    const paymentId   = entry.payment_item_id || "";
    const bordereau   = (entry.payment_item_code && entry.payment_item_name)
      ? `${entry.payment_item_code} – ${entry.payment_item_name}`
      : "";
    const cwp         = entry.cwp || "";
    const cwpCode   = entry.cwp_code || entry.cwp || "";

    const row = document.createElement("tr");
    row.classList.add("confirmed-row"); // mark it!
    row.innerHTML = `
      <td data-type="${type}" data-id="${entityId}">${name}</td>
      <td>${hours}</td>
      <td data-actval="${entry.activity_id}">${activity}</td>
      <td data-payment-item-id="${paymentId}">${bordereau}</td>
      <td data-cwp-code="${cwpCode}">${cwpCode}</td>
      <td class="actions">
        <button class="edit-btn"   data-entry-id="${entry.id}" data-type="${type}">✏️</button>
        <button class="delete-btn" data-entry-id="${entry.id}" data-type="${type}">🗑️</button>
      </td>
    `;
    tableBody.appendChild(row);
  });

  // re-attach handlers
  document.querySelectorAll('.edit-btn').forEach(btn => btn.addEventListener('click', handleEditConfirmedRow));
  document.querySelectorAll('.delete-btn').forEach(btn => btn.addEventListener('click', handleDeleteConfirmedRow));
}

/**
 * Fetch pending entries (workers & equipment) from the server
 * and render them into the confirmed table.
 */
async function loadPendingEntries(projectId, reportDate) {
  try {
    const resp = await fetch(
      `/labor-equipment/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`
    );
    if (!resp.ok) {
      console.error('Failed to load pending entries', await resp.text());
      return;
    }
    const { workers, equipment } = await resp.json();
    renderConfirmedTableFromServer(workers, equipment);
  } catch (err) {
    console.error('Error loading pending entries:', err);
  }
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


