export async function fetchAndRenderMaterials() {
    const response = await fetch('/materials/list');
    const data = await response.json();

    const materialsContainer = document.getElementById('materialsContainer');
    materialsContainer.innerHTML = data.materials.map(material => `
        <div class="material">
            <p>Name: ${material.material_name}</p>
            <p>Quantity: ${material.quantity}</p>
            <p>Unit: ${material.unit}</p>
        </div>
    `).join('');
}

export async function addMaterial(material) {
    try {
        const response = await fetch('/materials/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(material)
        });

        if (!response.ok) throw new Error('Failed to add material');
        const data = await response.json();
           await fetchAndRenderMaterials(); // Refresh the list
    } catch (error) {
        console.error('Error adding material:', error);
    }
}
