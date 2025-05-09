// static/js/notes.js

// Pull the “list notes” URL from window.API
const { getDailyNotes } = window.API || {};

export async function fetchAndRenderDailyNotes() {
  if (!getDailyNotes) {
    console.error('API.getDailyNotes endpoint not defined');
    return;
  }

  try {
    const resp = await fetch(getDailyNotes);
    if (!resp.ok) throw new Error(`Fetch failed: ${resp.status}`);

    const { notes = [] } = await resp.json();
    const container = document.getElementById('dailyNotesContainer');
    if (!container) {
      console.error('Element #dailyNotesContainer not found');
      return;
    }

    container.innerHTML = notes.map(note => `
      <div class="note">
        <p>${note.note_content}</p>
        <p>Date: ${note.date}</p>
      </div>
    `).join('');
  } catch (err) {
    console.error('fetchAndRenderDailyNotes() error:', err);
  }
}
