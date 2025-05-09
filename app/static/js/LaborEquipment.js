// static/js/LaborEquipment.js

import { populateDropdowns } from './populate_drop_downs.js';

// pull your endpoints off window.API
const {
  confirmLaborEquipment,        // e.g. '/labor-equipment/confirm-labor-equipment'
  getPendingLaborEquipment,     // e.g. '/labor-equipment/by-project-date'
  updateLaborEquipmentEntry,    // e.g. '/labor-equipment/update-entry'
  deleteLaborEquipmentEntry     // e.g. '/labor-equipment/delete-entry'
} = window.API || {};

// In-memory staging of new (preview) lines
let confirmedUsageData = [];
let manualWorkerMode   = false;
let manualEquipMode    = false;

/**
 * 1) Initialize the tab:
 *    • Populate all dropdowns
 *    • Wire up Add / Confirm / Manual-toggle buttons
 *    • Load any pending entries for the selected project & date
 */
export function initLaborEquipmentTab() {
  console.log("Initializing Labor & Equipment Tab…");

  document.getElementById('addEntryBtn')
    .addEventListener('click', addUsageLine);

  document.getElementById('confirmEntriesBtn')
    .addEventListener('click', confirmUsageLines);

  document.getElementById('manualEntryToggle')
    .addEventListener('click', () => toggleManualEntry('worker'));
  document.getElementById('manualEquipToggle')
    .addEventListener('click', () => toggleManualEntry('equipment'));

  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;
  if (projectId && reportDate) {
    loadPendingEntries(projectId, reportDate);
  }

  resetFormUI();
}

/**
 * 2) Toggle dropdown vs manual-entry
 */
function toggleManualEntry(mode) {
  manualWorkerMode = mode === 'worker'    ? !manualWorkerMode : false;
  manualEquipMode  = mode === 'equipment' ? !manualEquipMode  : false;

  document.getElementById('workerName').classList.toggle('hidden', manualWorkerMode || manualEquipMode);
  document.getElementById('workerName').disabled = manualWorkerMode || manualEquipMode;

  document.getElementById('manualWorkerName').classList.toggle('hidden', !manualWorkerMode);
  document.getElementById('manualEquipmentName').classList.toggle('hidden', !manualEquipMode);
}

/**
 * 3) Reset all form fields & modes
 */
function resetFormUI() {
  const dd = document.getElementById('workerName');
  dd.disabled = false;
  dd.classList.remove('hidden');
  dd.selectedIndex = 0;

  ['manualWorkerName','manualEquipmentName'].forEach(id => {
    const el = document.getElementById(id);
    el.value = '';
    el.classList.add('hidden');
  });

  document.getElementById('laborHours').value        = '';
  document.getElementById('activityCode').selectedIndex    = 0;
  document.getElementById('payment_item_id').selectedIndex = 0;
  document.getElementById('cwp_code').selectedIndex        = 0;

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
  if (manualWorkerMode && wi.value.trim()) {
    type     = 'worker';   entityId = null; name = wi.value.trim();
  } else if (manualEquipMode && ei.value.trim()) {
    type     = 'equipment';entityId = null; name = ei.value.trim();
  } else if (dd.value) {
    [type,entityId] = dd.value.split('|');
    name = dd.selectedOptions[0].text;
  } else {
    return alert("Veuillez remplir tous les champs.");
  }

  if (!hrs || !act.value) {
    return alert("Veuillez remplir tous les champs.");
  }

  confirmedUsageData.push({
    type,
    entryId:       null,
    entityId,
    name,
    hours:         parseFloat(hrs),
    activityCode:  act.value,
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
 */
async function confirmUsageLines(e) {
  e.preventDefault();
  if (!confirmLaborEquipment) throw new Error('Missing API.confirmLaborEquipment');

  const rows = Array.from(document.querySelectorAll('#workersTable tbody tr.preview-row'));
  if (rows.length === 0) return alert("Aucune entrée à confirmer.");

  const usage = rows.map(tr => {
    const [nameCell, hoursCell, actCell, payCell, cwpCell] = tr.children;
    const type     = nameCell.dataset.type;
    const id       = nameCell.dataset.id || null;
    const name     = nameCell.textContent.trim();

    return {
      employee_id:    type==='worker'    ? parseInt(id,10) : null,
      equipment_id:   type==='equipment' ? parseInt(id,10) : null,
      hours:          parseFloat(hoursCell.textContent.trim()),
      activity_code_id: parseInt(actCell.dataset.actcode,10),
      payment_item_id:  payCell.dataset.payid||null,
      cwp_id:           cwpCell.dataset.cwpc||null,
      manual_type:      type,
      is_manual:        !id,
      manual_name:      !id ? name : null
    };
  });

  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;

  try {
    const resp = await fetch(confirmLaborEquipment, {
      method:  'POST',
      headers: { 'Content-Type':'application/json' },
      body:    JSON.stringify({ project_id:projectId, date_of_report:reportDate, usage })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error||'Erreur serveur');

    alert(`${data.records.length} lignes confirmées.`);
    confirmedUsageData = [];
    renderPreviewTable();
    await loadPendingEntries(projectId, reportDate);
  } catch (err) {
    console.error('Erreur confirmation :', err);
    alert("Erreur : " + err.message);
  }
}

/**
 * 7) Load pending entries from server
 */
async function loadPendingEntries(projectId, reportDate) {
  if (!getPendingLaborEquipment) throw new Error('Missing API.getPendingLaborEquipment');
  try {
    const url = `${getPendingLaborEquipment}?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(await resp.text());
    const { workers, equipment } = await resp.json();
    renderConfirmedTable(workers, equipment);
  } catch(err) {
    console.error('Error loading pending entries:', err);
  }
}

/**
 * 8) Render confirmed (history) rows + wire edit/delete
 */
function renderConfirmedTable(workers = [], equipment = []) {
  const tbody = document.querySelector('#workersTable tbody');
  tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

  const all = [
    ...workers.map(w => ({ ...w, _type:'worker'   })),
    ...equipment.map(e => ({ ...e, _type:'equipment'}))
  ];

  all.forEach(entry => {
    const tr = document.createElement('tr');
    tr.classList.add('confirmed-row');
    tr.innerHTML = `
      <td>${entry._type==='worker'? entry.worker_name : entry.equipment_name}</td>
      <td data-hours="${entry.hours}">${entry.hours}</td>
      <td data-activity-id="${entry.activity_id}">
        ${entry.activity_code}${entry.activity_description ? ' – '+entry.activity_description : ''}
      </td>
      <td data-payment-id="${entry.payment_item_id||''}">
        ${entry.payment_item_code||''}
      </td>
      <td data-cwp="${entry.cwp||''}">${entry.cwp||''}</td>
      <td class="actions">
        <button class="edit-btn"   data-id="${entry.id}" data-type="${entry._type}">✏️</button>
        <button class="delete-btn" data-id="${entry.id}" data-type="${entry._type}">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('.edit-btn') .forEach(b => b.addEventListener('click', handleEdit));
  tbody.querySelectorAll('.delete-btn').forEach(b => b.addEventListener('click', handleDelete));
}

/**
 * 9) Inline edit: swap to inputs/selects
 */
function handleEdit(evt) {
  evt.preventDefault();

  const btn        = evt.currentTarget;
  const tr         = btn.closest('tr');
  const entryId    = btn.dataset.id;
  const entryType  = btn.dataset.type;

  const [ , hrsCell, actCell, payCell, cwpCell, actions ] = tr.children;

  // hours → input
  const curHrs = hrsCell.dataset.hours;
  hrsCell.innerHTML = `<input type="number" step="0.1" class="edit-hours" value="${curHrs}">`;

  // activity code → select
  const actSelect = document.createElement('select');
  actSelect.appendChild(new Option('-- Sélectionner --',''));
  (window.activityCodesList||[]).forEach(ac => {
    const opt = new Option(`${ac.code} – ${ac.description}`, ac.id);
    if (`${ac.id}`===`${actCell.dataset.activityId}`) opt.selected = true;
    actSelect.appendChild(opt);
  });
  actCell.innerHTML = ''; actCell.appendChild(actSelect);

  // payment item → select
  const paySelect = document.createElement('select');
  paySelect.appendChild(new Option('-- Aucun --',''));
  (window.paymentItemsList||[]).forEach(pi => {
    const opt = new Option(`${pi.payment_code} – ${pi.item_name}`, pi.id);
    if (`${pi.id}`===`${payCell.dataset.paymentId}`) opt.selected = true;
    paySelect.appendChild(opt);
  });
  payCell.innerHTML = ''; payCell.appendChild(paySelect);

  // CWP → select
  const cwpSelect = document.createElement('select');
  cwpSelect.appendChild(new Option('-- Aucun --',''));
  (window.cwpList||[]).forEach(c => {
    const opt = new Option(`${c.code} – ${c.name}`, c.code);
    if (c.code===cwpCell.dataset.cwp) opt.selected = true;
    cwpSelect.appendChild(opt);
  });
  cwpCell.innerHTML = ''; cwpCell.appendChild(cwpSelect);

  // swap buttons
  actions.innerHTML = `
    <button class="save-btn"   data-id="${entryId}" data-type="${entryType}">💾</button>
    <button class="cancel-btn">❌</button>
  `;
  actions.querySelector('.save-btn').addEventListener('click', saveEdit);
  actions.querySelector('.cancel-btn').addEventListener('click', () => {
    const proj = document.getElementById('projectNumber').value;
    const date = document.getElementById('dateSelector').value;
    loadPendingEntries(proj, date);
  });
}

/**
 * 10) Save inline edit via PUT
 */
async function saveEdit(evt) {
  evt.preventDefault();
  if (!updateLaborEquipmentEntry) throw new Error('Missing API.updateLaborEquipmentEntry');

  const btn        = evt.currentTarget;
  const entryId    = btn.dataset.id;
  const entryType  = btn.dataset.type;
  const tr         = btn.closest('tr');

  const newHrs = tr.children[1].querySelector('input').value.trim();
  const newAct = tr.children[2].querySelector('select').value;
  const newPay = tr.children[3].querySelector('select').value || null;
  const newCwp = tr.children[4].querySelector('select').value || null;

  if (!newHrs || !newAct) {
    return alert('Veuillez fournir heures et code d’activité.');
  }

  try {
    const url = `${updateLaborEquipmentEntry}/${entryType}/${entryId}`;
    const resp = await fetch(url, {
      method:  'PUT',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({
        hours:             Number(newHrs),
        activity_code_id:  Number(newAct),
        payment_item_id:   newPay,
        cwp:               newCwp
      })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error||'Erreur mise à jour');

    const proj = document.getElementById('projectNumber').value;
    const date = document.getElementById('dateSelector').value;
    await loadPendingEntries(proj, date);
    alert('Entrée mise à jour.');
  } catch (err) {
    console.error('saveEdit()', err);
    alert('Erreur : ' + err.message);
  }
}

/**
 * 11) Delete via DELETE
 */
async function handleDelete(evt) {
  if (!deleteLaborEquipmentEntry) throw new Error('Missing API.deleteLaborEquipmentEntry');
  if (!confirm("Supprimer cette entrée ?")) return;

  const btn   = evt.currentTarget;
  const id    = btn.dataset.id;
  const type  = btn.dataset.type;
  const url   = `${deleteLaborEquipmentEntry}/${type}/${id}`;

  try {
    const resp = await fetch(url, { method:'DELETE' });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error||'Erreur delete');

    alert("Entrée supprimée.");
    const proj = document.getElementById('projectNumber').value;
    const date = document.getElementById('dateSelector').value;
    await loadPendingEntries(proj, date);
  } catch(err) {
    console.error("handleDelete()", err);
    alert("Erreur : " + err.message);
  }
}
