// static/js/Materials.js

import { populateDropdowns } from './populate_drop_downs.js';

//
// In-memory staging of manual material entries
//
let stagedMaterials = [];

// ────────────────────────────────────────────────────
// 1) Initialize Materials Tab
//    *    • Populate all dropdowns (activity, payment, CWP)
//    *    • Wire Add/Confirm buttons
//    *    • Fetch & render pending rows
// ────────────────────────────────────────────────────
export async function initMaterialsTab() {
  console.log("Initializing Materials Tab...");

  // 1a) Load & wire every dropdown across the page
  await populateDropdowns();                                           

  // 1b) Mirror payment-item list into materialPaymentItem select
  const srcPay = document.getElementById('payment_item_id');
  const dstPay = document.getElementById('materialPaymentItem');
  if (srcPay && dstPay) {
    dstPay.innerHTML = srcPay.innerHTML;
  }
  
  // 1c) Wire up Add & Confirm
  document.getElementById('addMaterialBtn')
    .addEventListener('click', addMaterialLine);
  document.getElementById('confirmMaterialsBtn')
    .addEventListener('click', confirmMaterialLines);


  // 1d) Fetch & render any already-pending materials
  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;
  if (projectId && reportDate) {
    loadPendingMaterials(projectId, reportDate);
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

  // basic validation
  if (!manualName || !actId || isNaN(quantityTxt) || Number(quantityTxt) <= 0) {
    return alert("Veuillez remplir tous les champs correctement.");
  }

  stagedMaterials.push({
    material_id:        null,            // always manual for now
    manual_name:        manualName,
    quantity:           Number(quantityTxt),
    activity_code_id:   Number(actId),
    payment_item_id:    payId || null,
    cwp:                cwpCode || null,
    // used purely for display
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
  // remove any old preview‐rows
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

  if (stagedMaterials.length === 0) {
    return alert('Aucun matériel à confirmer.');
  }

  // build payload matching Flask
  const usage = stagedMaterials.map(entry => ({
    entityId:         entry.material_id,        // always null here
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
    const resp = await fetch('/materials/confirm-materials', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ usage, project_id: projectId, date_of_report: reportDate })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur serveur');

    alert(`Matériaux confirmés (${data.records.length} lignes).`);

    // clear preview and reload confirmed list
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
  try {
    const resp = await fetch(
      `/materials/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`
    );
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
  // Clear out any old rows
  tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

  materials.forEach(m => {
    const tr = document.createElement('tr');
    tr.classList.add('confirmed-row');

    tr.innerHTML = `
       <td 
        data-material-id="${m.material_id}" 
        data-manual-name="${m.material_name}"
      >${m.material_name}</td>
      <td>${m.quantity}</td>
      <td data-activity-id="${m.activity_id}">
        ${m.activity_code}${m.activity_description ? ' – ' + m.activity_description : ''}
      </td>
      <td data-payment-id="${m.payment_item_id || ''}">
        ${m.payment_item_id
          ? `${m.payment_item_code} – ${m.payment_item_name}`
          : ''
        }
      </td>
      <td data-cwp="${m.cwp || ''}">${m.cwp || ''}</td>
      <td class="actions">
        <button class="edit-btn"   data-entry-id="${m.id}">✏️</button>
        <button class="delete-btn" data-entry-id="${m.id}">🗑️</button>
      </td>
    `;

    tbody.appendChild(tr);
  });

  // Re-attach handlers to the new buttons
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

  // Which button and row fired this edit?
  const btn     = event.currentTarget;
  const tr      = btn.closest('tr');
  const entryId = btn.dataset.entryId;

  // Cells: 0=name, 1=qty, 2=activity, 3=payment, 4=cwp, 5=actions
  const qtyCell = tr.children[1];
  const actCell = tr.children[2];
  const payCell = tr.children[3];
  const cwpCell = tr.children[4];
  const actions = tr.children[5];

  // 1) Quantity → <input>
  const curQty = qtyCell.textContent.trim();
  qtyCell.innerHTML = `<input
    type="number" step="0.01"
    class="edit-qty"
    value="${curQty}"
  >`;

  // 2) Activity Code → <select>
  const actSelect = document.createElement('select');
  actSelect.appendChild(new Option('-- Sélectionner Code d’Activité --',''));
  (window.activityCodesList || []).forEach(ac => {
    const opt = new Option(`${ac.code} – ${ac.description}`, ac.id);
    if (String(ac.id) === actCell.dataset.activityId) opt.selected = true;
    actSelect.appendChild(opt);
  });
  actCell.innerHTML = '';
  actCell.appendChild(actSelect);

  // 3) Payment-Item → <select>
  const paySelect = document.createElement('select');
  paySelect.appendChild(new Option('-- Aucun --',''));
  (window.paymentItemsList || []).forEach(pi => {
    const opt = new Option(`${pi.payment_code} – ${pi.item_name}`, pi.id);
    if (String(pi.id) === payCell.dataset.paymentId) opt.selected = true;
    paySelect.appendChild(opt);
  });
  payCell.innerHTML = '';
  payCell.appendChild(paySelect);

  // 4) CWP → <select>
  const cwpSelect = document.createElement('select');
  cwpSelect.appendChild(new Option('-- Aucun --',''));
  (window.cwpList || []).forEach(c => {
    const opt = new Option(`${c.code} – ${c.name}`, c.code);
    if (c.code === cwpCell.dataset.cwp) opt.selected = true;
    cwpSelect.appendChild(opt);
  });
  cwpCell.innerHTML = '';
  cwpCell.appendChild(cwpSelect);

  // 5) Swap Edit → Save & Cancel
  actions.innerHTML = `
    <button class="save-edit-btn" data-entry-id="${entryId}">💾</button>
    <button class="cancel-edit-btn">❌</button>
  `;

  // Wire Save to the handler (reads event.currentTarget)
  actions.querySelector('.save-edit-btn')
         .addEventListener('click', handleSaveEditConfirmedRow);

  // Wire Cancel to simply reload the confirmed list
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

  // 1) Identify which row/button fired this
  const btn     = event.currentTarget;
  const entryId = btn.dataset.entryId;
  const tr      = btn.closest('tr');

  // 2) Pull edited values out of that row
  const newQty = tr.children[1]
                   .querySelector('input')
                   .value
                   .trim();
  const newAct = tr.children[2]
                   .querySelector('select')
                   .value;
  const newPay = tr.children[3]
                   .querySelector('select')
                   .value || null;
  const newCwp = tr.children[4]
                   .querySelector('select')
                   .value || null;

  // 3) Validate required fields
  if (!newQty || !newAct) {
    return alert('Veuillez fournir quantité et code d’activité.');
  }

  try {
    // 4) Send update to server
    const resp = await fetch(
      `/materials/update-entry/${entryId}`,
      {
        method:  'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quantity:          Number(newQty),
          activity_code_id:  Number(newAct),
          payment_item_id:   newPay !== '' ? Number(newPay) : null,
          cwp:               newCwp || null
        })
      }
    );
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur mise à jour');

    // 5) Refresh the table so edits show up
    const proj = document.getElementById('projectNumber').value;
    const dt   = document.getElementById('dateSelector').value;
    await loadPendingMaterials(proj, dt);

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
  if (!confirm('Supprimer cette entrée ?')) return;
  const entryId = event.currentTarget.dataset.entryId;

  try {
    const resp = await fetch(`/materials/delete-entry/${entryId}`, { method: 'DELETE' });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur suppression');

    alert('Entrée supprimée.');
    const pid = document.getElementById('projectNumber').value;
    const dt  = document.getElementById('dateSelector').value;
    loadPendingMaterials(pid, dt);

  } catch (err) {
    console.error('Erreur suppression matériaux:', err);
    alert('Erreur : ' + err.message);
  }
}
