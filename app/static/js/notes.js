// app/static/js/notes.js

let editingNoteId = null;
let stagedNotes   = [];

/**
 * Wire up buttons, dropdowns, then load existing notes.
 */
export async function initNotesTab() {
    const addBtn     = document.getElementById('addNoteBtn');
    const confirmBtn = document.getElementById('confirmNotesBtn');
    if (addBtn)     addBtn.addEventListener('click', addDailyNote);
    if (confirmBtn) confirmBtn.addEventListener('click', confirmDailyNotes);

    const cat = document.getElementById('noteCategory');
    if (cat) cat.addEventListener('change', toggleWorkOrderInput);
    toggleWorkOrderInput();

    // initial fetch & render of existing notes
    await fetchAndRenderDailyNotes();
}

/** Show/hide the Work-Order field based on category selection */
function toggleWorkOrderInput() {
    const cat   = document.getElementById('noteCategory');
    const group = document.getElementById('noteWorkOrderGroup');
    if (!cat || !group) return;
    group.classList.toggle('hidden', cat.value !== 'Work-order');
}

/**
 * Fetch saved notes from the server and render into the table.
 */
export async function fetchAndRenderDailyNotes() {
    // 1) Find the table body
  const tbody = document.querySelector('#entriesDailyNotesTable tbody');
  if (!tbody) return;

  // 2) Wipe out any existing rows
  tbody.innerHTML = '';

  try {
    // 3) Fetch from the new endpoint
    const resp = await fetch('/entries_daily_notes/list');
    const data = await resp.json();

    // 4) If the status is not OK, throw to be caught below
    if (!resp.ok) throw new Error(data.error || 'Fetch failed');

    // 5) Pull the list from data.entries (empty array fallback)
    const notes = Array.isArray(data.entries) ? data.entries : [];

    // 6) Render each note
    notes.forEach(note => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${(note.content || '').substring(0, 25)}</td>
        <td>${note.category || ''}</td>
        <td>${Array.isArray(note.tags) ? note.tags.join(', ') : ''}</td>
        <td>${note.activity_code_id || ''}</td>
        <td>${note.payment_item_id || ''}</td>
        <td>${note.cwp || ''}</td>
        <td class="actions">
          <button class="edit-note-btn"   data-id="${note.id}">✏️</button>
          <button class="delete-note-btn" data-id="${note.id}">🗑️</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // 7) Wire up the buttons
    tbody.querySelectorAll('.edit-note-btn')
         .forEach(btn => btn.addEventListener('click', editNote));
    tbody.querySelectorAll('.delete-note-btn')
         .forEach(btn => btn.addEventListener('click', deleteNote));

    // 8) Finally, render any staged notes preview
    renderPreviewTable();

  } catch (err) {
    console.error('fetchAndRenderDailyNotes Error:', err);

    // 9) Show a single error row
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td colspan="7" class="error-msg">
        Impossible de charger les notes.
      </td>
    `;
    tbody.appendChild(tr);
  }
}

/**
 * Add a new note to the staging area or send an edit to the server.
 */
export async function addDailyNote() {
    const activityCode = document.getElementById('noteActivityCode')?.value || '';
    const paymentItem  = document.getElementById('notePaymentItem')?.value  || '';
    const cwp          = document.getElementById('noteCwp')?.value          || '';
    const workOrder    = document.getElementById('noteWorkOrderId')?.value || '';
    // build tags array
    const tagsInput = document.getElementById('noteTags').value || '';
    const tags = tagsInput
        .split(',')
        .map(t => t.trim())
        .filter(t => t);
    [activityCode, paymentItem, cwp].forEach(val => { if (val) tags.push(val); });

    const payload = {
        project_id:         document.getElementById('projectNumber').value,
        note_datetime: document.getElementById('dateSelector').value + 'T00:00',
        author:             document.getElementById('noteAuthor').value,
        category:           document.getElementById('noteCategory').value,
        tags,
        content:            document.getElementById('noteContent').value,
        payment_item_id:    document.getElementById('notePaymentItem').value,
        work_order_id:      workOrder,
        cwp:                document.getElementById('noteCwp').value,
        activity_code_id:   activityCode
    };

    try {
        if (editingNoteId) {
            // Update existing note
            const resp = await fetch(`/entries_daily_notes/${editingNoteId}`, {
                method:  'PUT',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify(payload)
            });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error || 'save failed');
            await fetchAndRenderDailyNotes();
        } else {
            // Stage new note for batch confirm
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

        editingNoteId = null;
        resetNoteForm();

    } catch (err) {
        console.error('addDailyNote', err);
        alert('Erreur sauvegarde: ' + err.message);
    }
}

/**
 * Switch a row into inline-edit mode.
 */
async function handleInLineEdit(event) {
    event.preventDefault();
    const btn = event.currentTarget;
    const tr  = btn.closest('tr');
    const id  = btn.dataset.id;

    let note;
    try {
        const resp = await fetch(`/entries_daily_notes/${id}`);
        note = await resp.json();
        if (!resp.ok) throw new Error(note.error || 'fetch failed');
    } catch (err) {
        console.error('handleInLineEdit', err);
        alert('Erreur chargement note: ' + err.message);
        return;
    }

    // Replace cells with inputs/selects
    tr.children[0].innerHTML = `<textarea class="edit-content">${note.content || ''}</textarea>`;

    const catSelect = document.createElement('select');
    ['Progress','Safety','General'].forEach(c => {
        catSelect.appendChild(new Option(c, c, false, c === note.category));
    });
    catSelect.classList.add('edit-category');
    tr.children[1].innerHTML = '';
    tr.children[1].appendChild(catSelect);

    tr.children[2].innerHTML = `<input type="text" class="edit-tags"
                                     value="${Array.isArray(note.tags)?note.tags.join(', '):''}">`;

    const actSel = document.createElement('select');
    actSel.appendChild(new Option('-- Sélectionner Code d’Activité --',''));
    (window.activityCodesList||[]).forEach(ac => {
        const o = new Option(`${ac.code} – ${ac.description}`, ac.id);
        if (String(ac.id)===String(note.activity_code_id)) o.selected = true;
        actSel.appendChild(o);
    });
    actSel.classList.add('edit-activity');
    tr.children[3].innerHTML = '';
    tr.children[3].appendChild(actSel);

    const paySel = document.createElement('select');
    paySel.appendChild(new Option('-- Aucun --',''));
    (window.paymentItemsList||[]).forEach(pi => {
        const o = new Option(`${pi.payment_code} – ${pi.item_name}`, pi.id);
        if (String(pi.id)===String(note.payment_item_id)) o.selected = true;
        paySel.appendChild(o);
    });
    paySel.classList.add('edit-payment');
    tr.children[4].innerHTML = '';
    tr.children[4].appendChild(paySel);

    const cwpSel = document.createElement('select');
    cwpSel.appendChild(new Option('-- Aucun --',''));
    (window.cwpList||[]).forEach(cwpItem => {
        const o = new Option(`${cwpItem.code} – ${cwpItem.name}`, cwpItem.code);
        if (cwpItem.code===note.cwp) o.selected = true;
        cwpSel.appendChild(o);
    });
    cwpSel.classList.add('edit-cwp');
    tr.children[5].innerHTML = '';
    tr.children[5].appendChild(cwpSel);

    tr.children[6].innerHTML =
      `<button class="save-note-edit-btn"  data-id="${id}">💾</button>
       <button class="cancel-note-edit-btn">❌</button>`;

    tr.querySelector('.save-note-edit-btn')
      .addEventListener('click', saveInlineEdit);
    tr.querySelector('.cancel-note-edit-btn')
      .addEventListener('click', fetchAndRenderDailyNotes);
}

/**
 * Save an inline edit back to the server.
 */
async function saveInlineEdit(event) {
    event.preventDefault();
    const btn = event.currentTarget;
    const id  = btn.dataset.id;
    const tr  = btn.closest('tr');

    const content  = tr.querySelector('.edit-content').value.trim();
    const category = tr.querySelector('.edit-category').value;
    const tags     = tr.querySelector('.edit-tags').value
                          .split(',').map(t=>t.trim()).filter(Boolean);
    const actId    = tr.querySelector('.edit-activity').value || null;
    const payId    = tr.querySelector('.edit-payment').value  || null;
    const cwp      = tr.querySelector('.edit-cwp').value      || null;

    if (!content) return alert('Veuillez saisir une note.');

    try {
        const resp = await fetch(`/entries_daily_notes/${id}`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                content,
                category,
                tags,
                activity_code_id: actId ? Number(actId) : null,
                payment_item_id:  payId || null,
                cwp
            })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'save failed');
        await fetchAndRenderDailyNotes();
    } catch (err) {
        console.error('saveInlineEdit', err);
        alert('Erreur sauvegarde: ' + err.message);
    }
}

/**
 * Populate the form for editing a saved note.
 */
async function editNote(evt) {
    evt.preventDefault();
    const id = evt.currentTarget.dataset.id;

    try {
        const resp = await fetch(`/entries_daily_notes/${id}`);
        const note = await resp.json();
        if (!resp.ok) throw new Error(note.error || 'fetch failed');

        editingNoteId = id;
        document.getElementById('noteDatetime').value        = (note.note_datetime||'').slice(0,16);
        document.getElementById('noteAuthor').value          = note.author   || '';
        document.getElementById('noteCategory').value        = note.category || '';
        document.getElementById('noteTags').value            = Array.isArray(note.tags)?note.tags.join(', '):'';
        document.getElementById('noteActivityCode').value    = note.activity_code_id || '';
        document.getElementById('notePaymentItem').value     = note.payment_item_id  || '';
        document.getElementById('noteWorkOrderId').value = note.work_order_id || '';
        document.getElementById('noteCwp').value             = note.cwp      || '';
        document.getElementById('noteContent').value         = note.content  || '';

    } catch (err) {
        console.error('editNote', err);
        alert('Erreur chargement note: ' + err.message);
    }
}

/**
 * Delete a saved note.
 */
async function deleteNote(evt) {
    if (!confirm('Supprimer cette note ?')) return;
    const id = evt.currentTarget.dataset.id;

    try {
        const resp = await fetch(`/entries_daily_notes/${id}`, { method: 'DELETE' });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || 'delete failed');
        await fetchAndRenderDailyNotes();
    } catch (err) {
        console.error('deleteNote', err);
        alert('Erreur suppression: ' + err.message);
    }
}

/** Reset the note form fields. */
function resetNoteForm() {
    // Helper: lookup by id, only run fn if the element exists
    const safe = (id, fn) => {
    const el = document.getElementById(id);
    if (el) fn(el);
    };

    // 1) Simple inputs
    safe('noteDatetime',       el => el.value = '');
    safe('noteAuthor',         el => el.value = '');
    safe('noteTags',           el => el.value = '');
    safe('noteWorkOrderId',    el => el.value = '');
    safe('noteContent',        el => el.value = '');

    // 2) <select> elements — reset to first option
    safe('noteCategory',       el => { if ('selectedIndex' in el) el.selectedIndex = 0; });
    safe('noteActivityCode',   el => { if ('selectedIndex' in el) el.selectedIndex = 0; });
    safe('notePaymentItem',    el => { if ('selectedIndex' in el) el.selectedIndex = 0; });
    safe('noteCwp',            el => { if ('selectedIndex' in el) el.selectedIndex = 0; });

    // 3) Any extra container you need to hide
    safe('noteWorkOrderGroup', el => el.classList.add('hidden'));
}

/** Render any locally staged notes above the saved ones. */
function renderPreviewTable() {
    const tbody = document.querySelector('#entriesDailyNotesTable tbody');
    if (!tbody) return;
    tbody.querySelectorAll('tr.preview-row').forEach(r => r.remove());

    stagedNotes.forEach(n => {
        const tr = document.createElement('tr');
        tr.classList.add('preview-row');
        tr.innerHTML = `
            <td>${(n.content || '').substring(0,25)}</td>
            <td>${n.category || ''}</td>
            <td>${Array.isArray(n.tags) ? n.tags.join(', ') : ''}</td>
            <td>${n._display.activityText || ''}</td>
            <td>${n._display.paymentText  || ''}</td>
            <td>${n._display.cwpText      || ''}</td>
            <td></td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Send all staged notes up in one batch to /entries_daily_notes/confirm.
 */
export async function confirmDailyNotes() {
    if (stagedNotes.length === 0) {
        return alert('Aucune note à confirmer.');
    }

    try {
        const resp = await fetch('/entries_daily_notes/confirm', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ notes: stagedNotes })
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
