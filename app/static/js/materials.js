// static/js/Materials.js

import { populateDropdowns } from './populate_drop_downs.js';

const {
  confirmMaterials:     // e.g. '/materials/confirm-materials'
    window.API?.confirmMaterials,
  getPendingMaterials:  // e.g. '/materials/by-project-date'
    window.API?.getPendingMaterials,
  updateMaterialEntry:  // e.g. '/materials/update-entry'
    window.API?.updateMaterialEntry,
  deleteMaterialEntry   // e.g. '/materials/delete-entry'
    window.API?.deleteMaterialEntry
} = window.API || {};

// In-memory staging of manual material entries
let stagedMaterials = [];

// ────────────────────────────────────────────────────
// 1) Initialize Materials Tab
// ────────────────────────────────────────────────────
export async function initMaterialsTab() {
  console.log("Initializing Materials Tab...");

  // populate all dropdowns (activity, payment, CWP)
  await populateDropdowns();

  // mirror payment-items into materialPaymentItem
  const srcPay = document.getElementById('payment_item_id');
  const dstPay = document.getElementById('materialPaymentItem');
  if (srcPay && dstPay) dstPay.innerHTML = srcPay.innerHTML;

  // wire Add & Confirm
  document.getElementById('addMaterialBtn')
    .addEventListener('click', addMaterialLine);
  document.getElementById('confirmMaterialsBtn')
    .addEventListener('click', confirmMaterialLines);

  // fetch & render pending
  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;
  if (projectId && reportDate) {
    await loadPendingMaterials(projectId, reportDate);
  }

  resetMaterialsForm();
}

// ────────────────────────────────────────────────────
// 2) Clear the form inputs
// ────────────────────────────────────────────────────
function resetMaterialsForm() {
  document.getElementById('materialName').value               = '';
  document.getElementById('materialQuantity').value           = '';
  document.getElementById('materialActivityCode').selectedIndex = 0;
  document.getElementById('materialPaymentItem').selectedIndex  = 0;
  document.getElementById('materialCwp').selectedIndex          = 0;
}

// ────────────────────────────────────────────────────
// 3) Stage a new “preview” row
// ────────────────────────────────────────────────────
function addMaterialLine(e) {
  e.preventDefault();

  const nameInput = document.getElementById('materialName');
  const qtyInput  = document.getElementById('materialQuantity');
  const actSelect = document.getElementById('materialActivityCode');
  const paySelect = document.getElementById('materialPaymentItem');
  const cwpSelect = document.getElementById('materialCwp');

  const manualName  = nameInput.value.trim();
  const quantityTxt = qtyInput.value.trim();
  const actId       = actSelect.value;
  const payId       = paySelect.value;
  const cwpCode     = cwpSelect.value;

  if (!manualName || !actId || isNaN(quantityTxt) || Number(quantityTxt) <= 0) {
    return alert("Veuillez remplir tous les champs correctement.");
  }

  stagedMaterials.push({
    material_id:        null,
    manual_name:        manualName,
    quantity:           Number(quantityTxt),
    activity_code_id:   Number(actId),
    payment_item_id:    payId || null,
    cwp:                cwpCode || null,
    _display: {
      materialName: manualName,
      activityText: actSelect.selectedOptions[0].text,
      paymentText:  paySelect.selectedOptions[0]?.text || '',
      cwpText:      cwpSelect.selectedOptions[0]?.text || ''
    }
  });

  renderPreviewTable();
  resetMaterialsForm();
}

// ────────────────────────────────────────────────────
// 4) Render all staged (preview) rows
// ────────────────────────────────────────────────────
function renderPreviewTable() {
  const tbody = document.querySelector('#materialsTable tbody');
  tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

  stagedMaterials.forEach(entry => {
    const tr = document.createElement('tr');
    tr.classList.add('preview-row');
    tr.innerHTML = `
      <td>${entry._display.materialName}</td>
      <td>${entry.quantity}</td>
      <td>${entry._display.activityText}</td>
      <td>${entry._display.paymentText}</td>
      <td>${entry._display.cwpText}</td>
      <td></td>
    `;
    tbody.appendChild(tr);
  });
}

// ────────────────────────────────────────────────────
// 5) Send staged rows to server & reload
// ────────────────────────────────────────────────────
async function confirmMaterialLines(e) {
  e.preventDefault();
  if (!confirmMaterials) throw new Error('Missing API.confirmMaterials');

  if (stagedMaterials.length === 0) {
    return alert('Aucun matériel à confirmer.');
  }

  const usage = stagedMaterials.map(entry => ({
    entityId:         entry.material_id,
    manual_name:      entry.manual_name,
    is_manual:        true,
    quantity:         entry.quantity,
    activity_code_id: entry.activity_code_id,
    payment_item_id:  entry.payment_item_id,
    cwp:              entry.cwp
  }));

  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;

  try {
    const resp = await fetch(confirmMaterials, {
      method:  'POST',
      headers: { 'Content-Type':'application/json' },
      body:    JSON.stringify({ usage, project_id:projectId, date_of_report:reportDate })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur serveur');

    alert(`Matériaux confirmés (${data.records.length} lignes).`);
    stagedMaterials = [];
    renderPreviewTable();
    await loadPendingMaterials(projectId, reportDate);
  } catch (err) {
    console.error('Erreur confirmation matériaux:', err);
    alert('Erreur : ' + err.message);
  }
}

// ────────────────────────────────────────────────────
// 6) Fetch & render “pending” rows from server
// ────────────────────────────────────────────────────
async function loadPendingMaterials(projectId, reportDate) {
  if (!getPendingMaterials) throw new Error('Missing API.getPendingMaterials');

  try {
    const url = `${getPendingMaterials}?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(await resp.text());
    const { materials } = await resp.json();
    renderConfirmedTable(materials);
  } catch (err) {
    console.error('Error loading pending materials:', err);
  }
}

// ────────────────────────────────────────────────────
// 7) Render confirmed rows + wire up edit/delete
// ────────────────────────────────────────────────────
function renderConfirmedTable(materials = []) {
  const tbody = document.querySelector('#materialsTable tbody');
  tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

  materials.forEach(m => {
    const tr = document.createElement('tr');
    tr.classList.add('confirmed-row');
    tr.innerHTML = `
      <td data-material-id="${m.material_id}" data-manual-name="${m.material_name}">
        ${m.material_name}
      </td>
      <td>${m.quantity}</td>
      <td data-activity-id="${m.activity_id}">
        ${m.activity_code}${m.activity_description ? ' – ' + m.activity_description : ''}
      </td>
      <td data-payment-id="${m.payment_item_id||''}">
        ${m.payment_item_id ? `${m.payment_item_code} – ${m.payment_item_name}` : ''}
      </td>
      <td data-cwp="${m.cwp||''}">${m.cwp||''}</td>
      <td class="actions">
        <button class="edit-btn"   data-entry-id="${m.id}">✏️</button>
        <button class="delete-btn" data-entry-id="${m.id}">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('.edit-btn')
       .forEach(btn => btn.addEventListener('click', handleEditConfirmedRow));
  tbody.querySelectorAll('.delete-btn')
       .forEach(btn => btn.addEventListener('click', handleDeleteConfirmedRow));
}

// ────────────────────────────────────────────────────
// 8) Inline edit a confirmed row
// ────────────────────────────────────────────────────
function handleEditConfirmedRow(event) {
  event.preventDefault();
  const btn     = event.currentTarget;
  const tr      = btn.closest('tr');
  const entryId = btn.dataset.entryId;

  const [ , qtyCell, actCell, payCell, cwpCell, actions ] = tr.children;

  // quantity → input
  const curQty = qtyCell.textContent.trim();
  qtyCell.innerHTML = `<input type="number" step="0.01" class="edit-qty" value="${curQty}">`;

  // activity → select
  const actSelect = document.createElement('select');
  actSelect.appendChild(new Option('-- Sélectionner --',''));
  (window.activityCodesList||[]).forEach(ac => {
    const opt = new Option(`${ac.code} – ${ac.description}`, ac.id);
    if (`${ac.id}` === actCell.dataset.activityId) opt.selected = true;
    actSelect.appendChild(opt);
  });
  actCell.innerHTML = '';
  actCell.appendChild(actSelect);

  // payment → select
  const paySelect = document.createElement('select');
  paySelect.appendChild(new Option('-- Aucun --',''));
  (window.paymentItemsList||[]).forEach(pi => {
    const opt = new Option(`${pi.payment_code} – ${pi.item_name}`, pi.id);
    if (`${pi.id}` === payCell.dataset.paymentId) opt.selected = true;
    paySelect.appendChild(opt);
  });
  payCell.innerHTML = '';
  payCell.appendChild(paySelect);

  // cwp → select
  const cwpSelect = document.createElement('select');
  cwpSelect.appendChild(new Option('-- Aucun --',''));
  (window.cwpList||[]).forEach(c => {
    const opt = new Option(`${c.code} – ${c.name}`, c.code);
    if (c.code === cwpCell.dataset.cwp) opt.selected = true;
    cwpSelect.appendChild(opt);
  });
  cwpCell.innerHTML = '';
  cwpCell.appendChild(cwpSelect);

  // swap Edit → Save/Cancel
  actions.innerHTML = `
    <button class="save-edit-btn"   data-entry-id="${entryId}">💾</button>
    <button class="cancel-edit-btn">❌</button>
  `;
  actions.querySelector('.save-edit-btn')
         .addEventListener('click', handleSaveEditConfirmedRow);
  actions.querySelector('.cancel-edit-btn')
         .addEventListener('click', () => {
           const pid = document.getElementById('projectNumber').value;
           const dt  = document.getElementById('dateSelector').value;
           loadPendingMaterials(pid, dt);
         });
}

// ────────────────────────────────────────────────────
// 9) Save an edited row back to server
// ────────────────────────────────────────────────────
async function handleSaveEditConfirmedRow(event) {
  event.preventDefault();
  if (!updateMaterialEntry) throw new Error('Missing API.updateMaterialEntry');

  const btn     = event.currentTarget;
  const entryId = btn.dataset.entryId;
  const tr      = btn.closest('tr');

  const newQty = tr.children[1].querySelector('input').value.trim();
  const newAct = tr.children[2].querySelector('select').value;
  const newPay = tr.children[3].querySelector('select').value || null;
  const newCwp = tr.children[4].querySelector('select').value || null;

  if (!newQty || !newAct) {
    return alert('Veuillez fournir quantité et code d’activité.');
  }

  try {
    const resp = await fetch(`${updateMaterialEntry}/${entryId}`, {
      method:  'PUT',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({
        quantity:          Number(newQty),
        activity_code_id:  Number(newAct),
        payment_item_id:   newPay !== '' ? Number(newPay) : null,
        cwp:               newCwp || null
      })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur mise à jour');

    const pid = document.getElementById('projectNumber').value;
    const dt  = document.getElementById('dateSelector').value;
    await loadPendingMaterials(pid, dt);
    alert('Entrée mise à jour.');
  }
  catch (err) {
    console.error('Erreur mise à jour matériaux:', err);
    alert('Erreur : ' + err.message);
  }
}

// ────────────────────────────────────────────────────
// 10) Delete a confirmed row
// ────────────────────────────────────────────────────
async function handleDeleteConfirmedRow(event) {
  if (!deleteMaterialEntry) throw new Error('Missing API.deleteMaterialEntry');
  if (!confirm('Supprimer cette entrée ?')) return;

  const entryId = event.currentTarget.dataset.entryId;
  const resp = await fetch(`${deleteMaterialEntry}/${entryId}`, { method:'DELETE' });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || 'Erreur suppression');

  alert('Entrée supprimée.');
  const pid = document.getElementById('projectNumber').value;
  const dt  = document.getElementById('dateSelector').value;
  loadPendingMaterials(pid, dt);
}
