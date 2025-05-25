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
    const respData = await resp.json();
    renderDocumentsTable(respData.documents || []);
  } catch (err) {
    console.error('loadDocuments', err);
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td colspan="3" class="error-msg">Aucun documents.</td>
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
  const note = document.getElementById('docNote').value || '';
  const detailed = document.getElementById('docNotes').value || '';
  const tags = document.getElementById('docTags').value || '';
  formData.append('project_id', projectId);
  formData.append('work_date', reportDate);
  formData.append('short_note', note);
  formData.append('doc_notes', detailed);
  formData.append('tags', tags);


  try {
    const resp = await fetch('/documents/upload', {
      method: 'POST',
      body: formData
    });

    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || 'Erreur upload');   
    }

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
    const fileUrl = `/documents/files/${encodeURIComponent(doc.file_name)}`;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><a href="${fileUrl}" target="_blank">${doc.file_name}</a></td>
      <td>${doc.document_type}</td>
      <td>${doc.status}</td>
    `;

  const link = tr.querySelector('a');
  link.addEventListener('mouseover', e => showPreview(fileUrl, e.target));
    link.addEventListener('mouseout', hidePreview);
    tbody.appendChild(tr);
  });
}

export function showPreview(url, anchor) {
  const ext = url.split('.').pop().toLowerCase();
  const allowed = ['jpg', 'jpeg', 'png', 'gif'];
  if (!allowed.includes(ext)) return;
  const img = document.getElementById('docPreviewImg');
  const box = document.getElementById('docPreview');
  img.src = url;
  const rect = anchor.getBoundingClientRect();
  box.style.top = `${rect.bottom + window.scrollY}px`;
  box.style.left = `${rect.left + window.scrollX}px`;
  box.classList.remove('hidden');

}
export function hidePreview() {
  const box = document.getElementById('docPreview');
  box.classList.add('hidden');
  document.getElementById('docPreviewImg').src = '';
}
