let stagedMedia = [];

export async function fetchAndRenderMedia() {
    const resp = await fetch('/media/list');
    const data = await resp.json();
    renderCommittedTable(data.media || []);
    renderPreviewTable();
}

export function stageMedia(fileInfo) {
    stagedMedia.push(fileInfo);
    renderPreviewTable();
}

export async function confirmMedia() {
    if (!stagedMedia.length) return;
    const resp = await fetch('/media/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ media: stagedMedia })
    });
    const data = await resp.json();
    if (resp.ok) {
        stagedMedia = [];
        await fetchAndRenderMedia();
        alert(`${data.records.length} fichiers enregistrés.`);
    } else {
        alert(data.error || 'Erreur lors de la sauvegarde');
    }
}

function renderCommittedTable(media) {
    const container = document.getElementById('mediaCommitted');
    if (!container) return;
    container.innerHTML = '';
    media.forEach(m => {
        const div = document.createElement('div');
        div.classList.add('media-item');
        if (m.type === 'picture') {
            div.innerHTML = `<img src="${m.url}" alt="${m.filename}" class="thumb">`;
        } else {
            div.innerHTML = `<a href="${m.url}" target="_blank">📄 ${m.filename}</a>`;
        }
        container.appendChild(div);
    });
}

function renderPreviewTable() {
    const container = document.getElementById('mediaPending');
    if (!container) return;
    container.innerHTML = '';
    stagedMedia.forEach((m, idx) => {
        const div = document.createElement('div');
        div.classList.add('media-item');
        if (m.type === 'picture') {
            div.innerHTML = `<img src="${m.url}" alt="${m.filename}" class="thumb">`;
        } else {
            div.innerHTML = `<span>📄 ${m.filename}</span>`;
        }
        container.appendChild(div);
    });
}