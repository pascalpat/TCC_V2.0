// static/js/subcontractors.js
import { populateDropdowns } from './populate_drop_downs.js';

let stagedSubs = [];

// Fetch subcontractor names for datalist
export async function loadSubcontractorList() {
    try {
        const resp = await fetch('/subcontractors/list');
        if (!resp.ok) throw new Error(await resp.text());
        const { subcontractors } = await resp.json();

        let datalist = document.getElementById('subcontractorNames');
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = 'subcontractorNames';
            document.body.appendChild(datalist);
        }

        datalist.innerHTML = '';
        (subcontractors || []).forEach(sub => {
            const opt = document.createElement('option');
            opt.value = sub.name;
            datalist.appendChild(opt);
        });

        const input = document.getElementById('subcontractorName');
        if (input) input.setAttribute('list', 'subcontractorNames');
    } catch (err) {
        console.error('Error loading subcontractor list:', err);
    }
}


export async function initSubcontractorsTab() {
    await populateDropdowns();                   // fill activity-code dropdown
    loadSubcontractorList();                     // fetch /subcontractors/list

    const addBtn = document.getElementById('addSubcontractorBtn');
    const confirmBtn = document.getElementById('confirmSubcontractorsBtn');
    if (addBtn) {
        addBtn.removeEventListener('click', addSubLine);
        addBtn.addEventListener('click', addSubLine);
    }
    if (confirmBtn) {
        confirmBtn.removeEventListener('click', confirmSubLines);
        confirmBtn.addEventListener('click', confirmSubLines);
    }
    const projectId  = document.getElementById('projectNumber').value;
    const reportDate = document.getElementById('dateSelector').value;
    if (projectId && reportDate) {
        loadPendingSubs(projectId, reportDate);  // GET /subcontractors/by-project-date
    }
}

function addSubLine(e) {
    e.preventDefault();
    
    const nameInput   = document.getElementById('subcontractorName');
    const empInput    = document.getElementById('numEmployees');
    const hrsInput    = document.getElementById('totalHours');
    const actSelect   = document.getElementById('subcontractorActivityCode');

    const name   = nameInput.value.trim();
    const empTxt = empInput.value.trim();
    const hrsTxt = hrsInput.value.trim();
    const actId  = actSelect.value;

    if (!name || !empTxt || !hrsTxt || !actId) {
        return alert("Veuillez remplir tous les champs (y compris le code activité).");
    }

    stagedSubs.push({
        companyName:      name,
        numEmployees:     parseInt(empTxt, 10),
        totalHours:       parseFloat(hrsTxt),
        activity_code_id: parseInt(actId, 10),
        _display: {
            name,
            emp: empTxt,
            hrs: hrsTxt,
            activityText: actSelect.options[actSelect.selectedIndex]?.text || ''
        }
    });

    renderPreviewTable();
    resetSubForm();
}

function resetSubForm() {
    document.getElementById('subcontractorName').value = '';
    document.getElementById('numEmployees').value = '';
    document.getElementById('totalHours').value = '';
    const act = document.getElementById('subcontractorActivityCode');
    if (act) act.selectedIndex = 0;
}

function renderPreviewTable() {
    const tbody = document.querySelector('#subcontractorsTable tbody');
    if (!tbody) return;
    tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

    stagedSubs.forEach(entry => {
        const tr = document.createElement('tr');
        tr.classList.add('preview-row');
        tr.innerHTML = `
            <td>${entry._display.name}</td>
            <td>${entry._display.emp}</td>
            <td>${entry._display.hrs}</td>
            <td>${entry._display.activityText}</td>
            <td></td>
        `;
        tbody.appendChild(tr);
    });
}

async function confirmSubLines(e) {
    e.preventDefault();

    if (stagedSubs.length === 0) {
        return alert('Aucun sous-traitant à confirmer.');
    }

    const projectId  = document.getElementById('projectNumber').value;
    const reportDate = document.getElementById('dateSelector').value;

    const usage = stagedSubs.map(entry => ({
        companyName:      entry.companyName,
        numEmployees:     entry.numEmployees,
        totalHours:       entry.totalHours,
        activity_code_id: entry.activity_code_id
    }));

    try {
        const resp = await fetch('/subcontractors/confirm-entries', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: projectId,
                date: reportDate,
                usage
            })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'Erreur serveur');

        alert(`Sous-traitants confirmés (${data.records.length} lignes).`);
        stagedSubs = [];
        renderPreviewTable();
        await loadPendingSubs(projectId, reportDate);
    } catch (err) {
        console.error('Erreur confirmation sous-traitants:', err);
        alert('Erreur : ' + err.message);
    }
}

async function loadPendingSubs(projectId, reportDate) {
    try {
        const resp = await fetch(
            `/subcontractors/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`
        );
        if (!resp.ok) throw new Error(await resp.text());
        const { entries } = await resp.json();
        renderConfirmedTable(entries);
    } catch (err) {
        console.error('Error loading pending subcontractors:', err);
    }
}

function renderConfirmedTable(entries = []) {
    const tbody = document.querySelector('#subcontractorsTable tbody');
    if (!tbody) return;
    tbody.querySelectorAll('tr.confirmed-row').forEach(r => r.remove());

    entries.forEach(e => {
        const tr = document.createElement('tr');
        tr.classList.add('confirmed-row');
        tr.innerHTML = `
            <td data-entry-id="${e.id}" data-subcontractor-id="${e.subcontractor_id}">${e.subcontractor_id}</td>
            <td>${e.num_employees || ''}</td>
            <td>${e.labor_hours || ''}</td>
            <td data-activity-id="${e.activity_code_id || ''}">${e.activity_code_id || ''}</td>
            <td class="actions"></td>
        `;
        tbody.appendChild(tr);
    });
}
