export async function fetchAndRenderDailyNotes() {
    const response = await fetch('/notes/list');
    const data = await response.json();

    const dailynotesContainer = document.getElementById('dailyNotesContainer');
    dailyNotesContainer.innerHTML = data.notes.map(note => `
        <div class="note">
            <p>${note.note_content}</p>
            <p>Date: ${note.date}</p>
        </div>
    `).join('');
}
