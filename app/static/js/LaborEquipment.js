// static/js/LaborEquipment.js

import { populateDropdowns } from './populate_drop_downs.js';

// In-memory staging of new (preview) lines
let confirmedUsageData = [];
let manualWorkerMode = false;
let manualEquipMode  = false;

/**
 * 1) Initialize the tab:
 *    • Populate all dropdowns
 *    • Wire up Add / Confirm / Manual-toggle buttons
 *    • Load any pending entries for the selected project & date
 */
export function initLaborEquipmentTab() {
  console.log("Initializing Labor & Equipment Tab…");
  populateDropdowns().then(() => {
    document.getElementById('addEntryBtn')
      .addEventListener('click', addUsageLine);
    document.getElementById('confirmEntriesBtn')
      .addEventListener('click', confirmUsageLines);
    document.getElementById('manualEntryToggle')
      .addEventListener('click', () => toggleManualEntry('worker'));
    document.getElementById('manualEquipToggle')
      .addEventListener('click', () => toggleManualEntry('equipment'));

    const projectId  = document.getElementById('projectNumber')?.value;
    const reportDate = document.getElementById('dateSelector')?.value;
    if (projectId && reportDate) {
      loadPendingEntries(projectId, reportDate);
    }

    // Reset to pristine state
    resetFormUI();
  });
}

/**
 * 2) Toggle between dropdown-only vs manual entry modes
 */
function toggleManualEntry(mode) {
  manualWorkerMode = (mode === 'worker')    ? !manualWorkerMode : false;
  manualEquipMode  = (mode === 'equipment') ? !manualEquipMode  : false;

  const dd = document.getElementById('workerName');
  const wi = document.getElementById('manualWorkerName');
  const ei = document.getElementById('manualEquipmentName');
  const any = manualWorkerMode || manualEquipMode;

  // Disable main dropdown if manual
  dd.disabled = any;
  dd.classList.toggle('hidden', any);

  // Show/hide the appropriate manual input
  wi.classList.toggle('hidden', !manualWorkerMode);
  ei.classList.toggle('hidden', !manualEquipMode);
}

/**
 * 3) Reset all form fields & modes
 */
function resetFormUI() {
  const dd = document.getElementById('workerName');
  dd.disabled = false;
  dd.classList.remove('hidden');
  dd.selectedIndex = 0;

  ['manualWorkerName', 'manualEquipmentName'].forEach(id => {
    const el = document.getElementById(id);
    el.value = '';
    el.classList.add('hidden');
  });

  document.getElementById('laborHours').value = '';
  document.getElementById('activityCode').selectedIndex      = 0;
  document.getElementById('payment_item_id').selectedIndex   = 0;
  document.getElementById('cwp_code').selectedIndex          = 0;

  manualWorkerMode = manualEquipMode = false;
}

/**
 * 4) “Add to preview” — stage a line in-memory
 */
function addUsageLine(e) {
  e.preventDefault();

  const dd    = document.getElementById('workerName');
  const wi    = document.getElementById('manualWorkerName');
  const ei    = document.getElementById('manualEquipmentName');
  const hrs   = document.getElementById('laborHours').value.trim();
  const act   = document.getElementById('activityCode');
  const pay   = document.getElementById('payment_item_id');
  const cwpEl = document.getElementById('cwp_code');

  let type, entityId, name;
  // manual‐worker
  if (manualWorkerMode && wi.value.trim()) {
    type     = 'worker'; entityId = null; name = wi.value.trim();
  }
  // manual‐equipment
  else if (manualEquipMode && ei.value.trim()) {
    type     = 'equipment'; entityId = null; name = ei.value.trim();
  }
  // dropdown
  else if (dd.value) {
    [type, entityId] = dd.value.split('|');
    name = dd.selectedOptions[0].text;
  }
  else {
    return alert("Veuillez remplir tous les champs.");
  }

  // Validate required fields
  if (!hrs || !act.value) {
    return alert("Veuillez remplir tous les champs.");
  }

  // Stage it
  confirmedUsageData.push({
    type,
    entryId:       null,                    // new preview
    entityId,
    name,
    hours:         parseFloat(hrs),
    activityCode:  act.value,               // code string
    paymentItemId: pay.value || null,
    cwpCode:       cwpEl.value || null,
    manual:        !entityId,
    manual_name:   entityId ? null : name
  });

  renderPreviewTable();
  resetFormUI();
}

/**
 * 5) Render the “preview” rows under the form
 */
function renderPreviewTable() {
  const tbody = document.querySelector('#workersTable tbody');
  // clear old
  tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

  confirmedUsageData.forEach(row => {
    const tr = document.createElement('tr');
    tr.classList.add('preview-row');
    tr.innerHTML = `
      <td data-type="${row.type}" data-id="${row.entityId||''}">${row.name}</td>
      <td>${row.hours}</td>
      <td data-actcode="${row.activityCode}">${row.activityCode}</td>
      <td data-payid="${row.paymentItemId||''}">${row.paymentItemId||''}</td>
      <td data-cwpc="${row.cwpCode||''}">${row.cwpCode||''}</td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * 6) Confirm all preview lines in one batch
 *    POST to /labor-equipment/confirm-labor-equipment
 */
async function confirmUsageLines(e) {
  e.preventDefault();

  // Only preview rows (not already-confirmed rows)
  const rows = Array.from(
    document.querySelectorAll('#workersTable tbody tr.preview-row')
  );
  if (!rows.length) return alert("Aucune entrée à confirmer.");

  // Build payload exactly matching the Flask confirm route
  const usage = rows.map(tr => {
    const [nameCell, hoursCell, actCell, payCell, cwpCell] = tr.children;
    const type = nameCell.dataset.type;           // "worker" or "equipment"
    const id   = nameCell.dataset.id || null;      // string or ""

    return {
      // server expects exactly one of these two
      employee_id:  type === 'worker'    ? parseInt(id, 10) : null,
      equipment_id: type === 'equipment' ? parseInt(id, 10) : null,

      // required
      hours:            parseFloat(hoursCell.textContent.trim()),
      activity_code_id: parseInt(actCell.dataset.actcode, 10),

      // optional
      payment_item_id:  payCell.dataset.payid || null,
      cwp_id:           cwpCell.dataset.cwpc || null,

      // manual‐entry metadata
      is_manual:        !id,
      manual_name:      !id ? nameCell.textContent.trim() : null
    };
  });

  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;

  try {
    const resp = await fetch('/labor-equipment/confirm-labor-equipment', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        project_id:     projectId,
        date_of_report: reportDate,
        usage
      })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur serveur');

    alert(`${data.records.length} lignes confirmées.`);
    confirmedUsageData = [];  // clear your in-memory preview
    await loadPendingEntries(projectId, reportDate);
  } catch (err) {
    console.error('Erreur confirmation :', err);
    alert("Erreur : " + err.message);
  }
}

/**
 * 7) Load pending entries from server
 *    GET /labor-equipment/by-project-date
 */
async function loadPendingEntries(projectId, reportDate) {
  try {
    const resp = await fetch(`/labor-equipment/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`);
    if (!resp.ok) throw new Error(await resp.text());
    const { workers, equipment } = await resp.json();
    renderConfirmedTable(workers, equipment);
  }
  catch(err) {
    console.error('Error loading pending entries:', err);
  }
}

/**
 * 8) Render confirmed (history) rows + hook edit/delete
 */
function renderConfirmedTable(workers = [], equipment = []) {
  const tbody = document.querySelector('#workersTable tbody');
  // clear old confirmed
  tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

  // mix them together
  const all = [
    ...workers.map(w => ({...w, _type:'worker'})),
    ...equipment.map(e => ({...e, _type:'equipment'}))
  ];

  all.forEach(entry => {
    const tr = document.createElement('tr');
    tr.classList.add('confirmed-row');
    tr.innerHTML = `
      <td>${entry._type==='worker'? entry.worker_name : entry.equipment_name}</td>
      <td>${entry.hours}</td>                                         <!-- use entry.hours not hours_worked :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5} -->
      <td>${entry.activity_code}${entry.activity_description ? ' – '+entry.activity_description : ''}</td>
      <td>${entry.payment_item_code || ''}</td>
      <td>${entry.cwp || ''}</td>
      <td class="actions">
        <button class="edit-btn"   data-id="${entry.id}" data-type="${entry._type}">✏️</button>
        <button class="delete-btn" data-id="${entry.id}" data-type="${entry._type}">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // wire up
  tbody.querySelectorAll('.edit-btn').forEach(b => b.addEventListener('click', handleEdit));
  tbody.querySelectorAll('.delete-btn').forEach(b => b.addEventListener('click', handleDelete));
}

/**
 * 9) Inline edit: swap to inputs / selects
 */
function handleEdit(evt) {
  const btn = evt.currentTarget;
  const tr  = btn.closest('tr');
  const id  = btn.dataset.id;
  const type= btn.dataset.type;
  // cells
  const hrsCell = tr.children[1];
  const actCell = tr.children[2];
  const actions = tr.children[5];

  // hours input
  const currentHrs = hrsCell.textContent.trim();
  hrsCell.innerHTML = `<input type="number" step="0.1" value="${currentHrs}" />`;

  // build activity select (value = PK id) to match /update-entry :contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}
  const actSelect = document.createElement('select');
  window.activityCodesList.forEach(ac => {
    const opt = new Option(`${ac.code} – ${ac.description}`, ac.id);
    // match by code string in cell text
    if (`${ac.code}` === actCell.textContent.split(' ')[0]) opt.selected = true;
    actSelect.appendChild(opt);
  });
  actCell.innerHTML = '';
  actCell.appendChild(actSelect);

  // swap action buttons
  actions.innerHTML = `
    <button class="save-btn">💾</button>
    <button class="cancel-btn">❌</button>
  `;
  actions.querySelector('.save-btn')
    .addEventListener('click', () => saveEdit(tr, id, type));
  actions.querySelector('.cancel-btn')
    .addEventListener('click', () => {
      const proj = document.getElementById('projectNumber').value;
      const date = document.getElementById('dateSelector').value;
      loadPendingEntries(proj, date);
    });
}

/**
 * 10) Save inline edit via PUT /labor-equipment/update-entry/<type>/<id>
 *     Expects JSON: { hours: <string>, activity_code_id: <id> }
 */
async function saveEdit(tr, entryId, entryType) {
  try {
    const hrs  = tr.children[1].querySelector('input').value.trim();
    const actId= tr.children[2].querySelector('select').value;
    if (!hrs || !actId) return alert("Veuillez fournir les heures et un code d'activité.");

    const resp = await fetch(`/labor-equipment/update-entry/${entryType}/${entryId}`, {
      method:  'PUT',
      headers: {'Content-Type':'application/json'},
      body:    JSON.stringify({ hours: hrs, activity_code_id: actId })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error||'Erreur update');

    alert("Entrée mise à jour.");
    const proj = document.getElementById('projectNumber').value;
    const date = document.getElementById('dateSelector').value;
    await loadPendingEntries(proj, date);
  }
  catch(err) {
    console.error("saveEdit()", err);
    alert("Erreur : " + err.message);
  }
}

/**
 * 11) Delete via DELETE /labor-equipment/delete-entry/<type>/<id>
 */
async function handleDelete(evt) {
  if (!confirm("Supprimer cette entrée ?")) return;
  const btn = evt.currentTarget;
  const id  = btn.dataset.id;
  const type= btn.dataset.type;

  try {
    const resp = await fetch(`/labor-equipment/delete-entry/${type}/${id}`, { method: 'DELETE' });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error||'Erreur delete');

    alert("Entrée supprimée.");
    const proj = document.getElementById('projectNumber').value;
    const date = document.getElementById('dateSelector').value;
    await loadPendingEntries(proj, date);
  }
  catch(err) {
    console.error("handleDelete()", err);
    alert("Erreur : " + err.message);
  }
}
