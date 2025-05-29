// static/js/subcontractors.js
import { populateDropdowns } from './populate_drop_downs.js';

let stagedSubs = [];

export async function initSubcontractorsTab() {
    await populateDropdowns();                   // fill activity-code dropdown
    loadSubcontractorList();                     // fetch /subcontractors/list
    document.getElementById('addSubBtn')
        .addEventListener('click', addSubLine);
    document.getElementById('confirmSubBtn')
        .addEventListener('click', confirmSubLines);

    const projectId  = document.getElementById('projectNumber').value;
    const reportDate = document.getElementById('dateSelector').value;
    if (projectId && reportDate) {
        loadPendingSubs(projectId, reportDate);  // GET /subcontractors/by-project-date
    }
}

function addSubLine(e) {
    e.preventDefault();
    // push form values to stagedSubs and renderPreviewTable()
}

async function confirmSubLines(e) {
    e.preventDefault();

    if (stagedSubs.length === 0) {
        return alert('Aucun sous-traitant à confirmer.');
    }

    const projectId  = document.getElementById('projectNumber').value;
    const reportDate = document.getElementById('dateSelector').value;

    try {
        const resp = await fetch('/subcontractors/confirm-entries', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: projectId,
                date: reportDate,
                usage: stagedSubs
            })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'Erreur serveur');

        alert(`Sous-traitants confirmés (${data.records.length} lignes).`);
        stagedSubs = [];
        await loadPendingSubs(projectId, reportDate);
    } catch (err) {
        console.error('Erreur confirmation sous-traitants:', err);
        alert('Erreur : ' + err.message);
    }
}

async function loadPendingSubs(projectId, reportDate) {
    const resp = await fetch(
        `/subcontractors/by-project-date?project_id=${encodeURIComponent(projectId)}&date=${encodeURIComponent(reportDate)}`
    );
    const { entries } = await resp.json();
    // renderConfirmedTable(entries)
}


document.addEventListener('DOMContentLoaded', function () {
    const addSubcontractorBtn = document.getElementById('addSubcontractorBtn');
    const confirmSubcontractorsBtn = document.getElementById('confirmSubcontractorsBtn');

    if (addSubcontractorBtn) {
        addSubcontractorBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const name = document.getElementById('subcontractorName').value.trim();
            const numEmployees = document.getElementById('numEmployees').value.trim();
            const totalHours = document.getElementById('totalHours').value.trim();
            const activitySelect = document.getElementById('subcontractorActivityCode');

            if (!activitySelect) {
                console.error("Subcontractor activity code dropdown not found.");
                return;
            }

            const activityText = activitySelect.options[activitySelect.selectedIndex]?.text || "";

            if (!name || !numEmployees || !totalHours || !activitySelect.value) {
                alert("Veuillez remplir tous les champs (y compris le code activité).");
                return;
            }

            const tableBody = document.getElementById('subcontractorsTable').querySelector("tbody");
            if (!tableBody) {
                console.error("Subcontractors table tbody not found.");
                return;
            }

            let row = tableBody.insertRow();
            row.innerHTML = `
                <td>${name}</td>
                <td>${numEmployees}</td>
                <td>${totalHours}</td>
                <td>${activityText}</td>
            `;

            console.log("Subcontractor row added:", { name, numEmployees, totalHours, activityCode: activityText });

            // Clear inputs after adding
            document.getElementById('subcontractorName').value = "";
            document.getElementById('numEmployees').value = "";
            document.getElementById('totalHours').value = "";
            activitySelect.selectedIndex = 0;
        });
    }

    if (confirmSubcontractorsBtn) {
        confirmSubcontractorsBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const tbody = document.getElementById('subcontractorsTable').querySelector('tbody');
            let subcontractorEntries = [];
            for (let row of tbody.rows) {
                let subName = row.cells[0].innerText;
                let subEmployees = row.cells[1].innerText;
                let subHours = row.cells[2].innerText;
                let subActivity = row.cells[3]?.innerText || "";
                subcontractorEntries.push({
                    companyName: subName,
                    numEmployees: subEmployees,
                    totalHours: subHours,
                    activityCode: subActivity
                });
            }
            fetch("/data-entry/save_draft", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ entries: subcontractorEntries, tab: "subcontractors" })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Subcontractors draft saved successfully:", data);
                alert("Les sous-traitants ont été sauvegardés en tant que brouillon.");
            })
            .catch(error => {
                console.error("Error saving subcontractors draft:", error);
                alert("Erreur lors de la sauvegarde des brouillons des sous-traitants.");
            });
        });
    }
});

