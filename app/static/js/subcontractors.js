// static/js/subcontractors.js

// ────────────────────────────────────────────────────
// Pull in our “save subcontractors draft” endpoint
// ────────────────────────────────────────────────────
const { saveSubcontractorsDraft = '' } = window.API || {};

document.addEventListener('DOMContentLoaded', () => {
  const addBtn     = document.getElementById('addSubcontractorBtn');
  const confirmBtn = document.getElementById('confirmSubcontractorsBtn');

  // 1) Add one row to the table
  if (addBtn) {
    addBtn.addEventListener('click', e => {
      e.preventDefault();
      const nameInput    = document.getElementById('subcontractorName');
      const empInput     = document.getElementById('numEmployees');
      const hoursInput   = document.getElementById('totalHours');
      const activitySelect = document.getElementById('subcontractorActivityCode');

      const name    = nameInput?.value.trim();
      const numEmp  = empInput?.value.trim();
      const hours   = hoursInput?.value.trim();
      const actText = activitySelect?.options[activitySelect.selectedIndex]?.text || '';
      const actVal  = activitySelect?.value;

      if (!name || !numEmp || !hours || !actVal) {
        alert("Veuillez remplir tous les champs (y compris le code d’activité).");
        return;
      }

      const tbody = document.querySelector('#subcontractorsTable tbody');
      if (!tbody) {
        console.error("[subcontractors] table body not found.");
        return;
      }

      const row = tbody.insertRow();
      row.innerHTML = `
        <td>${name}</td>
        <td>${numEmp}</td>
        <td>${hours}</td>
        <td>${actText}</td>
      `;
      console.log("[subcontractors] row added:", { name, numEmp, hours, activity: actText });

      // clear inputs
      nameInput.value = '';
      empInput.value  = '';
      hoursInput.value= '';
      activitySelect.selectedIndex = 0;
    });
  }

  // 2) Collect all rows and POST to server
  if (confirmBtn) {
    confirmBtn.addEventListener('click', async e => {
      e.preventDefault();

      if (!saveSubcontractorsDraft) {
        console.warn("[subcontractors] saveSubcontractorsDraft endpoint not configured, skipping.");
        alert("Impossible de sauvegarder : endpoint introuvable.");
        return;
      }

      const tbody = document.querySelector('#subcontractorsTable tbody');
      if (!tbody) {
        console.error("[subcontractors] table body not found.");
        return;
      }

      // gather entries
      const entries = Array.from(tbody.rows).map(row => ({
        companyName:  row.cells[0]?.innerText || '',
        numEmployees: row.cells[1]?.innerText || '',
        totalHours:   row.cells[2]?.innerText || '',
        activityCode: row.cells[3]?.innerText || ''
      }));

      try {
        const resp = await fetch(saveSubcontractorsDraft, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ entries, tab: 'subcontractors' })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'Save failed');

        console.log("[subcontractors] draft saved:", data);
        alert("Les sous-traitants ont été sauvegardés en tant que brouillon.");
      } catch (err) {
        console.error("[subcontractors] error saving draft:", err);
        alert("Erreur lors de la sauvegarde des sous-traitants.");
      }
    });
  }
});
