// static/js/pictures.js

// Expect a URL like "/data-entry/pictures/list" on window.API.getPictures
const { getPictures } = window.API || {};

export async function fetchAndRenderPictures() {
  if (!getPictures) {
    console.error('API.getPictures endpoint not defined');
    return;
  }

  try {
    const resp = await fetch(getPictures);
    if (!resp.ok) throw new Error(`Fetch failed: ${resp.status}`);

    const { pictures = [] } = await resp.json();
    const container = document.getElementById('picturesContainer');
    if (!container) {
      console.error('Element #picturesContainer not found');
      return;
    }

    container.innerHTML = pictures.map(picture => `
      <div class="picture">
        <p>File: ${picture.filename}</p>
        <p>Description: ${picture.description}</p>
      </div>
    `).join('');

  } catch (err) {
    console.error('fetchAndRenderPictures() error:', err);
  }
}
