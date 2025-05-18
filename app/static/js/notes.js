export async function fetchAndRenderDailyNotes() {
   const container = document.getElementById('dailyNotesContainer');
    if (!container) return;

    try {
        const resp = await fetch('/dailynotes/list');
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.message || 'fetch failed');

        const notes = data.data || [];
        container.innerHTML = notes.map(note => `
            <div class="note">
                <p>${note.content}</p>
                <p>Date: ${note.date}</p>
            </div>
        `).join('');
    } catch (err) {
        console.error('fetchAndRenderDailyNotes', err);
        container.innerHTML = '<p class="error">Impossible de charger les notes.</p>';
    }
}

export async function saveDailyNote() {
    const payload = {
        date:      document.getElementById('noteDatetime').value,
        author:    document.getElementById('noteAuthor').value,
        category:  document.getElementById('noteCategory').value,
        tags:      document.getElementById('noteTags').value,
        content:   document.getElementById('noteContent').value
    };

    try {
        const resp = await fetch('/dailynotes/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.message || 'save failed');

        await fetchAndRenderDailyNotes();
    } catch (err) {
        console.error('saveDailyNote', err);
        alert('Erreur sauvegarde: ' + err.message);
    }
}