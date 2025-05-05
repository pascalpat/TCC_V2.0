// static/js/LaborEquipment.js

import { populateDropdowns } from './populate_drop_downs.js';

let confirmedUsageData = [];
let manualWorkerMode = false;
let manualEquipMode = false;

// ----------------------
// 1. Main Initialization Function
// ----------------------
export function initLaborEquipmentTab() {
  console.log("Initializing Labor & Equipment Tab...");
  populateDropdowns().then(() => {
    document.getElementById('addEntryBtn')       .addEventListener('click', addUsageLine);
    document.getElementById('confirmEntriesBtn') .addEventListener('click', confirmUsageLines);
    document.getElementById('manualEntryToggle').addEventListener('click', () => toggleManualEntry('worker'));
    document.getElementById('manualEquipToggle').addEventListener('click', () => toggleManualEntry('equipment'));

    const projectId  = document.getElementById('projectNumber')?.value;
    const reportDate = document.getElementById('dateSelector')?.value;
    if (projectId && reportDate) loadPendingEntries(projectId, reportDate);

    resetFormUI();
  });
}

function toggleManualEntry(mode) {
  const dropdown       = document.getElementById('workerName');
  const manualWorkerIn = document.getElementById('manualWorkerName');
  const manualEquipIn  = document.getElementById('manualEquipmentName');

  manualWorkerMode = (mode === 'worker')    ? !manualWorkerMode : false;
  manualEquipMode  = (mode === 'equipment') ? !manualEquipMode  : false;

  const anyManual = manualWorkerMode || manualEquipMode;
  dropdown.disabled = anyManual;
  dropdown.classList.toggle('hidden', anyManual);

  manualWorkerIn.classList.toggle('hidden', !manualWorkerMode);
  manualWorkerIn.classList.toggle('visible', manualWorkerMode);
  if (manualWorkerMode) manualWorkerIn.focus();

  manualEquipIn.classList.toggle('hidden', !manualEquipMode);
  manualEquipIn.classList.toggle('visible', manualEquipMode);
  if (manualEquipMode) manualEquipIn.focus();

  console.log(
    manualWorkerMode ? '✅ Manual Worker Mode ON'
    : manualEquipMode  ? '✅ Manual Equipment Mode ON'
    :                     '↩️ Back to dropdown-only mode'
  );
}

function resetFormUI() {
  document.getElementById('workerName').disabled = false;
  document.getElementById('workerName').classList.remove('hidden');
  document.getElementById('workerName').selectedIndex = 0;

  document.getElementById('manualWorkerName').value = '';
  document.getElementById('manualWorkerName').classList.add('hidden');
  document.getElementById('manualWorkerName').classList.remove('visible');

  document.getElementById('manualEquipmentName').value = '';
  document.getElementById('manualEquipmentName').classList.add('hidden');
  document.getElementById('manualEquipmentName').classList.remove('visible');

  document.getElementById('laborHours').value = '';
  document.getElementById('activityCode').selectedIndex = 0;
  document.getElementById('payment_item_id').selectedIndex = 0;
  document.getElementById('cwp_code').selectedIndex = 0;

  manualWorkerMode = false;
  manualEquipMode  = false;
}

// ----------------------
// 2. Add Entry to Preview
// ----------------------
function addUsageLine(e) {
  e.preventDefault();

  const dropdown       = document.getElementById('workerName');
  const manualWorkerIn = document.getElementById('manualWorkerName');
  const manualEquipIn  = document.getElementById('manualEquipmentName');
  const hoursInput     = document.getElementById('laborHours');
  const activitySelect = document.getElementById('activityCode');
  const paymentSelect  = document.getElementById('payment_item_id');
  const cwpSelect      = document.getElementById('cwp_code');

  const hours        = hoursInput.value.trim();
  const activityCode = activitySelect.value;
  const activityText = activitySelect.selectedOptions[0]?.text || '';
  const paymentId    = paymentSelect.value || null;
  const paymentText  = paymentSelect.selectedOptions[0]?.text || '';
  const cwpCode      = cwpSelect.value || null;
  const cwpText      = cwpSelect.selectedOptions[0]?.text || '';

  let type, entityId, name;
  if (manualWorkerMode && manualWorkerIn.value.trim()) {
    type     = 'worker';
    entityId = null;
    name     = manualWorkerIn.value.trim();
  } else if (manualEquipMode && manualEquipIn.value.trim()) {
    type     = 'equipment';
    entityId = null;
    name     = manualEquipIn.value.trim();
  } else if (dropdown.value) {
    [type, entityId] = dropdown.value.split('|');
    name = dropdown.selectedOptions[0].text;
  } else {
    return alert('Veuillez remplir tous les champs.');
  }

  if (!hours || !activityCode) {
    return alert('Veuillez remplir tous les champs.');
  }

  confirmedUsageData.push({
    type,
    entityId,
    name,
    hours,
    activityCode,
    activityText,
    paymentId,
    paymentText,
    cwpCode,
    cwpText,
    isManual: !entityId,
    manual_name: !entityId ? name : null
  });

  renderPreviewTable();
  resetFormUI();
}

function renderPreviewTable() {
  const tbody = document.querySelector('#workersTable tbody');
  tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

  confirmedUsageData.forEach(entry => {
    const tr = document.createElement('tr');
    tr.classList.add('preview-row');
    tr.innerHTML = `
      <td data-type="${entry.type}" data-id="${entry.entityId || ''}">${entry.name}</td>
      <td>${entry.hours}</td>
      <td data-actval="${entry.activityCode}">${entry.activityText}</td>
      <td data-payment-item-id="${entry.paymentId}">${entry.paymentText}</td>
      <td data-cwp-code="${entry.cwpCode}">${entry.cwpText}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ----------------------
// 3. Confirm & Save
// ----------------------
async function confirmUsageLines(e) {
  e.preventDefault();

  const rows = Array.from(
    document.querySelectorAll('#workersTable tbody tr')
  ).filter(tr => !tr.classList.contains('confirmed-row'));

  if (!rows.length) {
    return alert('Aucune entrée à confirmer.');
  }

  // Build usage array with the exact keys expected by the Flask route
  const usage = rows.map(tr => {
    const [nameCell, hoursCell, actCell, payCell, cwpCell] = tr.children;
    const type = nameCell.dataset.type;
    const id   = nameCell.dataset.id || null;

    return {
      // exactly one of these two
      employee_id:  type === 'worker'    ? id : null,
      equipment_id: type === 'equipment' ? id : null,

      // required
      hours:             parseFloat(hoursCell.textContent.trim()),
      activity_code_id:  actCell.dataset.actval,

      // optional
      payment_item_id:   payCell.dataset.paymentItemId || null,
      cwp_id:            cwpCell.dataset.cwpCode       || null,

      // manual-entry metadata
      is_manual:         !id,
      manual_name:       !id ? nameCell.textContent.trim() : null
    };
  });

  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;

  try {
    const resp = await fetch('/labor-equipment/confirm-labor-equipment', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, date_of_report: reportDate, usage })
    });
    const result = await resp.json();
    if (!resp.ok) throw new Error(result.error || 'Erreur serveur');

    alert(`${result.records.length} lignes confirmées.`);
    rows.forEach(tr => tr.classList.add('confirmed-row'));
    await loadPendingEntries(projectId, reportDate);
  } catch (err) {
    console.error('Erreur confirmation :', err);
    alert('Erreur : ' + err.message);
  }
}

// ----------------------
// 4. Load & Render from Server
// ----------------------
function renderConfirmedTableFromServer(workers = [], equipment = []) {
  const tbody = document.querySelector('#workersTable tbody');
  tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

  [...workers, ...equipment].forEach(entry => {
    const isWorker = entry.worker_id   !== undefined;
    const type     = isWorker ? 'worker' : 'equipment';
    const name     = entry.worker_name  || entry.equipment_name;
    const hours    = entry.hours;
    const activity = `${entry.activity_code} – ${entry.activity_description || ''}`;
    const payment  = entry.payment_item_code
      ? `${entry.payment_item_code} – ${entry.payment_item_name}`
      : '';
    const cwp      = entry.cwp;
    const row      = document.createElement('tr');

    row.classList.add(entry.is_manual ? 'manual-row' : 'confirmed-row');
    row.innerHTML = `
      <td data-type="${type}" data-id="${isWorker ? entry.worker_id : entry.equipment_id}">${name}</td>
      <td>${hours}</td>
      <td data-actval="${entry.activity_code}">${activity}</td>
      <td data-payment-item-id="${entry.payment_item_id}">${payment}</td>
      <td data-cwp-code="${entry.cwp}">${cwp}</td>
      <td class="actions">
        <button class="edit-btn"   data-entry-id="${entry.id}" data-type="${type}">✏️</button>
        <button class="delete-btn" data-entry-id="${entry.id}" data-type="${type}">🗑️</button>
      </td>
    `;
    tbody.appendChild(row);
  });

  tbody.querySelectorAll('.edit-btn')  .forEach(b => b.addEventListener('click', handleEditConfirmedRow));
  tbody.querySelectorAll('.delete-btn').forEach(b => b.addEventListener('click', handleDeleteConfirmedRow));
}

async function loadPendingEntries(projectId, reportDate) {
  try {
    const resp = await fetch(`/labor-equipment/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`);
    if (!resp.ok) throw new Error(await resp.text());
    const { workers, equipment } = await resp.json();
    renderConfirmedTableFromServer(workers, equipment);
  } catch (err) {
    console.error('Error loading pending entries:', err);
  }
}

// ... Edit/Delete handlers unchanged ...

function handleEditConfirmedRow(event) { /* ... */ }
function handleSaveEditConfirmedRow(event) { /* ... */ }
function handleDeleteConfirmedRow(event) { /* ... */ }
