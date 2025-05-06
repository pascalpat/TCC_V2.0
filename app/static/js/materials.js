// static/js/Materials.js

import { populateDropdowns } from './populate_drop_downs.js';

let confirmedMaterialsData = [];

// ----------------------
// 1. Main Initialization
// ----------------------
export function initMaterialsTab() {
  console.log("Initializing Materials Tab...");

  populateDropdowns().then(() => {
    document.getElementById('addMaterialBtn')
      .addEventListener('click', addMaterialLine);
    document.getElementById('confirmMaterialsBtn')
      .addEventListener('click', confirmMaterialLines);

    // Load pending entries from server
    const projectId  = document.getElementById('projectNumber')?.value;
    const reportDate = document.getElementById('dateSelector')?.value;
    if (projectId && reportDate) {
      loadPendingMaterials(projectId, reportDate);
    }

    resetMaterialsForm();
  });
}

// ----------------------
// 2. Reset Form Fields
// ----------------------
function resetMaterialsForm() {
  document.getElementById('materialName').value            = '';
  document.getElementById('materialQuantity').value        = '';
  document.getElementById('materialActivityCode').selectedIndex = 0;
  document.getElementById('materialPaymentItem').selectedIndex  = 0;
  document.getElementById('materialCwp').selectedIndex          = 0;
}

// ----------------------
// 3. Add Preview Line
// ----------------------
function addMaterialLine(event) {
  event.preventDefault();

  const nameInput  = document.getElementById('materialName');
  const qtyInput   = document.getElementById('materialQuantity');
  const actSelect  = document.getElementById('materialActivityCode');
  const paySelect  = document.getElementById('materialPaymentItem');
  const cwpSelect  = document.getElementById('materialCwp');

  const materialName = nameInput.value.trim();
  const quantity     = qtyInput.value.trim();
  const activityCode = actSelect.value;
  const activityText = actSelect.options[actSelect.selectedIndex]?.text || '';
  const paymentItem  = paySelect.value;
  const paymentText  = paySelect.options[paySelect.selectedIndex]?.text || '';
  const cwpCode      = cwpSelect.value;
  const cwpText      = cwpSelect.options[cwpSelect.selectedIndex]?.text || '';

  if (!materialName || !quantity || isNaN(quantity) || Number(quantity) <= 0 || !activityCode) {
    return alert("Veuillez remplir tous les champs correctement.");
  }

  confirmedMaterialsData.push({
    // for manual adds we never have a real catalog id
    material_id:   null,
    manual_name:   materialName,
    quantity:      parseFloat(quantity),
    activity_code_id: activityCode,
    payment_item_id:  paymentItem || null,
    cwp:              cwpCode    || null,
    _display: {      // these just drive the UI
      materialName, activityText, paymentText, cwpText
    }
  });

  renderPreviewTable();
  resetMaterialsForm();
}

// ----------------------
// 4. Render Preview Table
// ----------------------
function renderPreviewTable() {
  const tbody = document.querySelector('#materialsTable tbody');
  tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

  confirmedMaterialsData.forEach(entry => {
    const row = document.createElement('tr');
    row.classList.add('preview-row');
    row.innerHTML = `
      <td>${entry._display.materialName}</td>
      <td>${entry.quantity}</td>
      <td>${entry._display.activityText}</td>
      <td>${entry._display.paymentText}</td>
      <td>${entry._display.cwpText}</td>
      <td></td>
    `;
    tbody.appendChild(row);
  });
}

// ----------------------
// 5. Confirm & POST
// ----------------------
async function confirmMaterialLines(event) {
  event.preventDefault();

  // only un‐confirmed preview rows
  const rows = Array.from(
    document.querySelectorAll('#materialsTable tbody tr.preview-row')
  );
  if (!rows.length) {
    return alert('Aucun matériel à confirmer.');
  }

  // build payload exactly matching the Flask route
  const usage = confirmedMaterialsData.map(entry => ({
    material_id:       entry.material_id,
    manual_name:       entry.manual_name,
    quantity:          entry.quantity,
    activity_code_id:  entry.activity_code_id,
    payment_item_id:   entry.payment_item_id,
    cwp:               entry.cwp
  }));

  const projectId  = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;

  try {
    const resp = await fetch('/materials/confirm-materials', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ usage, project_id: projectId, date_of_report: reportDate })
    });
    const result = await resp.json();
    if (!resp.ok) throw new Error(result.error || 'Erreur serveur');

    alert(`Matériaux confirmés (${result.records_saved} lignes).`);
    // clear the staged array & reload from server
    confirmedMaterialsData = [];
    await loadPendingMaterials(projectId, reportDate);

  } catch (err) {
    console.error('Erreur confirmation matériaux:', err);
    alert('Erreur: ' + err.message);
  }
}

// ----------------------
// 6. Render Confirmed Rows
// ----------------------
function renderConfirmedTableFromServer(materials = []) {
  const tbody = document.querySelector('#materialsTable tbody');
  tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

  materials.forEach(entry => {
    const row = document.createElement('tr');
    row.classList.add('confirmed-row');
    row.innerHTML = `
      <td data-material-id="${entry.material_id}">${entry.material_name}</td>
      <td>${entry.quantity}</td>
      <td data-actid="${entry.activity_code_id}">
        ${entry.activity_code} – ${entry.activity_description || ''}
      </td>
      <td>${ entry.payment_item_code
            ? entry.payment_item_code+' – '+entry.payment_item_name
            : '' }</td>
      <td>${entry.cwp || ''}</td>
      <td class="actions">
        <button class="edit-btn"   data-entry-id="${entry.id}">✏️</button>
        <button class="delete-btn" data-entry-id="${entry.id}">🗑️</button>
      </td>
    `;
    tbody.appendChild(row);
  });

  // wire up all edit/delete buttons
  tbody.querySelectorAll('.edit-btn')
    .forEach(b => b.addEventListener('click', handleEditConfirmedRow));
  tbody.querySelectorAll('.delete-btn')
    .forEach(b => b.addEventListener('click', handleDeleteConfirmedRow));
}

// ----------------------
// 7. Load Pending from Server
// ----------------------
async function loadPendingMaterials(projectId, reportDate) {
  try {
    const resp = await fetch(
      `/materials/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`
    );
    if (!resp.ok) throw new Error(await resp.text());
    const { materials } = await resp.json();
    renderConfirmedTableFromServer(materials);
  } catch (err) {
    console.error('Error loading pending materials:', err);
  }
}

// ----------------------
// 8. Inline Edit Handler
// ----------------------
function handleEditConfirmedRow(event) {
  const btn     = event.currentTarget;
  const tr      = btn.closest('tr');
  const entryId = btn.dataset.entryId;

  // grab all cells
  const nameCell = tr.children[0];
  const qtyCell  = tr.children[1];
  const actCell  = tr.children[2];
  const payCell  = tr.children[3];
  const cwpCell  = tr.children[4];
  const actions  = tr.children[5];

  // 1) quantity → input
  const curQty = qtyCell.textContent.trim();
  qtyCell.innerHTML = `<input type="number" min="0" step="0.01" value="${curQty}"/>`;

  // 2) activity dropdown
  const actSelect = document.createElement('select');
  window.activityCodesList.forEach(ac => {
    const opt = new Option(`${ac.code} – ${ac.description}`, ac.id);
    if (ac.id === parseInt(actCell.dataset.actid,10)) opt.selected = true;
    actSelect.appendChild(opt);
  });
  actCell.innerHTML = '';
  actCell.appendChild(actSelect);

  // 3) payment dropdown
  const paySelect = document.createElement('select');
  paySelect.appendChild(new Option('-- Aucun --',''));
  window.paymentItemsList.forEach(pi => {
    const opt = new Option(pi.payment_code+' – '+pi.item_name, pi.id);
    if (pi.id === parseInt(payCell.textContent.split(' – ')[0],10)) opt.selected = true;
    paySelect.appendChild(opt);
  });
  payCell.innerHTML = '';
  payCell.appendChild(paySelect);

  // 4) cwp dropdown
  const cwpSelect = document.createElement('select');
  cwpSelect.appendChild(new Option('-- Aucun --',''));
  window.cwpList.forEach(c => {
    const opt = new Option(c.code+' – '+c.name, c.code);
    if (c.code === cwpCell.textContent) opt.selected = true;
    cwpSelect.appendChild(opt);
  });
  cwpCell.innerHTML = '';
  cwpCell.appendChild(cwpSelect);

  // 5) swap buttons
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

// ----------------------
// 9. Save‐edit Handler
// ----------------------
async function handleSaveEditConfirmedRow(event) {
  const btn     = event.currentTarget;
  const entryId = btn.dataset.entryId;
  const tr      = btn.closest('tr');

  const newQty = tr.children[1].querySelector('input').value;
  const newAct = tr.children[2].querySelector('select').value;
  const newPay = tr.children[3].querySelector('select').value || null;
  const newCwp = tr.children[4].querySelector('select').value || null;

  try {
    const resp = await fetch(`/materials/update-entry/${entryId}`, {
      method: 'PUT',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        quantity:         newQty,
        activity_code_id: newAct,
        payment_item_id:  newPay,
        cwp:              newCwp
      })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur mise à jour');

    alert("Entrée mise à jour.");
    const pid = document.getElementById('projectNumber').value;
    const dt  = document.getElementById('dateSelector').value;
    loadPendingMaterials(pid, dt);
  } catch (err) {
    console.error('Erreur mise à jour matériaux:', err);
    alert('Erreur : '+err.message);
  }
}

// ----------------------
// 10. Delete‐button Handler
// ----------------------
async function handleDeleteConfirmedRow(event) {
  if (!confirm('Supprimer cette entrée ?')) return;
  const entryId = event.currentTarget.dataset.entryId;

  try {
    const resp = await fetch(`/materials/delete-entry/${entryId}`, { method: 'DELETE' });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Erreur suppression');

    alert("Entrée supprimée.");
    const pid = document.getElementById('projectNumber').value;
    const dt  = document.getElementById('dateSelector').value;
    loadPendingMaterials(pid, dt);
  } catch (err) {
    console.error('Erreur suppression matériaux:', err);
    alert('Erreur : '+err.message);
  }
}
