// static/js/notes.js

import { startDictation } from './speech_recognition.js';

////////////////////////////////////////////////////////////////////////////////
// 0) API Endpoints (injected via base.html / notes.html):
//    window.API.listNotes       → GET list of drafts
//    window.API.addNote         → POST new note
//    window.API.commitNotes     → POST commit all drafts
//    window.API.deleteNoteBase  → URL with placeholder '/dailynotes/0'
//    
//    We replace the trailing "0" with the real note ID below.
////////////////////////////////////////////////////////////////////////////////
const API = {
  listNotes:   window.API.listNotes,
  addNote:     window.API.addNote,
  commitNotes: window.API.commitNotes,
  deleteNote:  id => window.API.deleteNoteBase.replace(/0$/, id)
};

export async function initDailyNotes() {
  const form       = document.getElementById('NotesForm');
  const tableBody  = document.querySelector('#notesTable tbody');
  const confirmBtn = document.getElementById('confirmNotesBtn');
  const dictateBtn = document.getElementById('dictateBtn');

  // 0) Hook up the microphone button
  dictateBtn.onclick = () => startDictation('noteText');

  // 1) Load existing drafts
  try {
    const resp = await fetch(API.listNotes);
    const { notes } = await resp.json();
    notes.forEach(renderRow);
  } catch (err) {
    console.error('Failed to load notes:', err);
  }

  // 2) Add a new draft
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const text = document.getElementById('noteText').value.trim();
    if (!text) return;

    const data = new FormData(form);
    // FormData already includes content/category/priority/etc.
    try {
      const resp = await fetch(API.addNote, {
        method: 'POST',
        body: data
      });
      const note = await resp.json();
      renderRow(note);
      form.reset();
      confirmBtn.disabled = false;
    } catch (err) {
      console.error('Failed to add note:', err);
    }
  });

  // 3) Commit all drafts
  confirmBtn.addEventListener('click', async () => {
    try {
      await fetch(API.commitNotes, { method: 'POST' });
      setTabComplete('NotesTab');
      confirmBtn.disabled = true;
    } catch (err) {
      console.error('Failed to commit notes:', err);
    }
  });

  // Helper to add a row to the table
  function renderRow(n) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${new Date(n.created_at).toLocaleTimeString()}</td>
      <td>${n.content}</td>
      <td>${n.category}</td>
      <td>${n.priority}</td>
      <td>${n.activity_code || ''}</td>
      <td>${n.work_order_id ? `WO ${n.work_order_id}` : ''}</td>
      <td>${n.attachment_url
           ? `<a href="${n.attachment_url}" target="_blank">📎</a>`
           : ''
         }</td>
      <td>
        <button data-id="${n.id}" class="delete-note">🗑️</button>
      </td>
    `;

    // Delete button
    tr.querySelector('.delete-note').onclick = async () => {
      try {
        await fetch(API.deleteNote(n.id), { method: 'DELETE' });
        tr.remove();
        confirmBtn.disabled = false;
      } catch (err) {
        console.error(`Failed to delete note ${n.id}:`, err);
      }
    };

    tableBody.appendChild(tr);
  }
}
