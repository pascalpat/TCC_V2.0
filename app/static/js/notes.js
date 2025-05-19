let editingNoteId = null;
let stagedNotes   = [];

export async function fetchAndRenderDailyNotes() {
    const tbody = document.querySelector('#dailyNotesTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    try {
        const resp = await fetch('/dailynotes_routes/list');
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'fetch failed');

        const notes = data.daily_notes || data.dailynotes || [];
        notes.forEach(note => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${(note.content || '').substring(0,25)}</td>
                <td>${note.category || ''}</td>
                <td>${Array.isArray(note.tags) ? note.tags.join(', ') : ''}</td>
                <td>${note.activity_code_id || ''}</td>
                <td>${note.payment_item_id || ''}</td>
                <td>${note.cwp || ''}</td>
                <td class="actions">
                    <button class="edit-note-btn" data-id="${note.id}">✏️</button>
                    <button class="delete-note-btn" data-id="${note.id}">🗑️</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll('.edit-note-btn').forEach(b => b.addEventListener('click', editNote));
        tbody.querySelectorAll('.delete-note-btn').forEach(b => b.addEventListener('click', deleteNote));

        renderPreviewTable();


    } catch (err) {
        console.error('fetchAndRenderDailyNotes', err);
        tbody.innerHTML = '<tr><td colspan="7" class="error-msg">Impossible de charger les notes.</td></tr>';
    }
}

export async function addDailyNote() {
    const activityCode = document.getElementById('noteActivityCode')?.value || '';
    const paymentItem  = document.getElementById('notePaymentItem')?.value  || '';
    const cwp          = document.getElementById('noteCwp')?.value          || '';
    const workOrder    = document.getElementById('noteWorkOrderNumber')?.value || '';

    const tagsInput = document.getElementById('noteTags').value || '';
    const tags = tagsInput
        .split(',')
        .map(t => t.trim())
        .filter(t => t);

    [activityCode, paymentItem, cwp].forEach(val => {
        if (val) tags.push(val);
    });


    const payload = {
        project_id: document.getElementById('projectNumber').value,
        note_datetime: document.getElementById('noteDatetime').value,
        author:    document.getElementById('noteAuthor').value,
        category:  document.getElementById('noteCategory').value,
        tags,
        content:   document.getElementById('noteContent').value,
        payment_item_id: document.getElementById('notePaymentItem').value,
        work_order_number: workOrder,
        cwp: document.getElementById('noteCwp').value,
        activity_code_id: activityCode
    };

    try {
        if (editingNoteId) {
            const resp = await fetch(`/dailynotes/${editingNoteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error || 'save failed');
            await fetchAndRenderDailyNotes();
        } else {
            stagedNotes.push({
                ...payload,
                _display: {
                    activityText: document.getElementById('noteActivityCode').selectedOptions[0]?.text || '',
                    paymentText:  document.getElementById('notePaymentItem').selectedOptions[0]?.text || '',
                    cwpText:      document.getElementById('noteCwp').selectedOptions[0]?.text || ''
                }
            });
            renderPreviewTable();
        }

        editingNoteId = null;  // reset after save
        resetNoteForm();

    } catch (err) {
        console.error('addDailyNote', err);
        alert('Erreur sauvegarde: ' + err.message);
    }
}

async function editNote(evt) {
    evt.preventDefault();
    const id = evt.currentTarget.dataset.id;
    try {
        const resp = await fetch(`/dailynotes/${id}`);
        const note = await resp.json();
        if (!resp.ok) throw new Error(note.error || 'fetch failed');

        editingNoteId = id;
        document.getElementById('noteDatetime').value = (note.note_datetime || '').slice(0,16);
        document.getElementById('noteAuthor').value = note.author || '';
        document.getElementById('noteCategory').value = note.category || '';
        document.getElementById('noteTags').value = Array.isArray(note.tags) ? note.tags.join(', ') : '';
        document.getElementById('noteActivityCode').value = note.activity_code_id || '';
        document.getElementById('notePaymentItem').value = note.payment_item_id || '';
        document.getElementById('noteWorkOrderNumber').value = note.work_order_number || '';
        document.getElementById('noteCwp').value = note.cwp || '';
        document.getElementById('noteContent').value = note.content || '';
    } catch (err) {
        console.error('editNote', err);
        alert('Erreur chargement note: ' + err.message);
    }
}

async function deleteNote(evt) {
    if (!confirm('Supprimer cette note ?')) return;
    const id = evt.currentTarget.dataset.id;
    try {
        const resp = await fetch(`/dailynotes/${id}`, { method: 'DELETE' });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'delete failed');
        await fetchAndRenderDailyNotes();
    } catch (err) {
        console.error('deleteNote', err);
        alert('Erreur suppression: ' + err.message);
    }
}

function resetNoteForm() {
    document.getElementById('noteDatetime').value = '';
    document.getElementById('noteAuthor').value = '';
    document.getElementById('noteCategory').selectedIndex = 0;
    document.getElementById('noteTags').value = '';
    document.getElementById('noteActivityCode').selectedIndex = 0;
    document.getElementById('notePaymentItem').selectedIndex = 0;
    const wo = document.getElementById('noteWorkOrderNumber');
    if (wo) wo.value = '';
    document.getElementById('noteCwp').selectedIndex = 0;
    const txt = document.getElementById('noteContent');
    if (txt) txt.value = '';
}
// ────────────────────────────────────────────────────
// Render staged preview rows
// ────────────────────────────────────────────────────
function renderPreviewTable() {
    const tbody = document.querySelector('#dailyNotesTable tbody');
    if (!tbody) return;
    // remove existing preview rows
    tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

    stagedNotes.forEach(n => {
        const tr = document.createElement('tr');
        tr.classList.add('preview-row');
        tr.innerHTML = `
            <td>${(n.content || '').substring(0,25)}</td>
            <td>${n.category || ''}</td>
            <td>${Array.isArray(n.tags) ? n.tags.join(', ') : ''}</td>
            <td>${n._display.activityText || ''}</td>
            <td>${n._display.paymentText || ''}</td>
            <td>${n._display.cwpText || ''}</td>
            <td></td>
        `;
        tbody.appendChild(tr);
    });
}

// ────────────────────────────────────────────────────
// Confirm staged notes to server
// ────────────────────────────────────────────────────
export async function confirmDailyNotes() {
    if (stagedNotes.length === 0) {
        return alert('Aucune note à confirmer.');
    }

    try {
        const resp = await fetch('/dailynotes/confirm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: stagedNotes })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'Erreur serveur');

        alert(`Notes confirmées (${data.records.length}).`);
        stagedNotes = [];
        renderPreviewTable();
        await fetchAndRenderDailyNotes();

    } catch (err) {
        console.error('confirmDailyNotes', err);
        alert('Erreur : ' + err.message);
    }
}