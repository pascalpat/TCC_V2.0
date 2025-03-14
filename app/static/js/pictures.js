export async function fetchAndRenderPictures() {
    const response = await fetch('/pictures/list');
    const data = await response.json();

    const picturesContainer = document.getElementById('picturesContainer');
    picturesContainer.innerHTML = data.pictures.map(picture => `
        <div class="picture">
            <p>File: ${picture.filename}</p>
            <p>Description: ${picture.description}</p>
        </div>
    `).join('');
}
