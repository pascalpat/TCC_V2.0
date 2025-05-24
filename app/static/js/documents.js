// app/static/js/documents.js

let pendingFiles = [];

export function initDocumentsTab() {
  const uploadBtn = document.getElementById('uploadDocumentsBtn');
  if (uploadBtn) uploadBtn.addEventListener('click', uploadDocuments);

  const projectId = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;
  if (projectId && reportDate) {
    loadDocuments();
  }
}

export async function loadDocuments() {
  const tbody = document.querySelector('#documentsTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  try {
    const resp = await fetch('/documents/list');
    if (!resp.ok) throw new Error('Erreur chargement');
    const data = await resp.json();
    renderDocumentsTable(data.documents || []);
  } catch (err) {
    console.error('loadDocuments', err);
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td colspan="3" class="error-msg">Impossible de charger les documents.</td>
    `;
    tbody.appendChild(tr);
  }
}

async function uploadDocuments(e) {
  e.preventDefault();
  const filesInput = document.getElementById('documentFiles');
  const typeSelect = document.getElementById('documentType');
  const files = filesInput.files;
  if (!files.length) {
    return alert('Sélectionner des fichiers.');
  }

  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  formData.append('document_type', typeSelect.value || 'general');

  const projectId = document.getElementById('projectNumber').value;
  const reportDate = document.getElementById('dateSelector').value;
  formData.append('project_id', projectId);
  formData.append('work_date', reportDate);

  try {
    const resp = await fetch('/documents/upload', {
      method: 'POST',
      body: formData
    });


    const data = await resp.json();
    let data;
    try {
      data = JSON.parse(text);
    } catch (parseErr) {
      throw new Error(text);
    }
    if (!resp.ok) throw new Error(data.error || text || 'Erreur upload');

    alert(`${data.records.length} fichier(s) téléversé(s).`);
    filesInput.value = '';
    await loadDocuments();
  } catch (err) {
    console.error('uploadDocuments', err);
    alert('Erreur : ' + err.message);
  }
}

function renderDocumentsTable(docs) {
  const tbody = document.querySelector('#documentsTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  if (!docs.length) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td colspan="3" class="error-msg">Aucun document disponible.</td>`;
    tbody.appendChild(tr);
    return;
  }

  docs.forEach(doc => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><a href="${doc.file_url}" target="_blank">${doc.file_name}</a></td>
      <td>${doc.document_type}</td>
      <td>${doc.status}</td>
    `;
    tbody.appendChild(tr);
  });
}