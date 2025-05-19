export async function fetchAndRenderDailyNotes() {
   const container = document.getElementById('dailyNotesContainer');
    if (!container) return;

    try {
        const resp = await fetch('/dailynotes/list');
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.message || 'fetch failed');

        const notes = data.dailynotes || [];
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
    const activityCode = document.getElementById('noteActivityCode')?.value || '';
    const paymentItem  = document.getElementById('notePaymentItem')?.value  || '';
    const cwp          = document.getElementById('noteCwp')?.value          || '';

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
        cwp: document.getElementById('noteCwp').value,
        activity_code_id: activityCode
    };

    try {
        const resp = await fetch('/dailynotes/', {
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