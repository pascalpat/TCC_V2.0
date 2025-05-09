// static/js/equipment.js

// ────────────────────────────────────────────────────
// Pull the equipment‐list endpoint from window.API,
// with a fallback to the original dev route.
// ────────────────────────────────────────────────────
const {
  listEquipment = 'data-entry/equipment/list'
} = window.API || {};

/**
 * Fetches the list of equipment and renders it into
 * #equipmentContainer.
 */
export async function fetchAndRenderEquipment() {
  console.log("[equipment] fetching equipment…");
  try {
    const resp = await fetch(listEquipment);
    if (!resp.ok) {
      throw new Error(`Failed to fetch equipment: ${resp.statusText}`);
    }
    const data = await resp.json();
    console.log("[equipment] fetched:", data);

    const container = document.getElementById('equipmentContainer');
    if (!container) {
      console.error("[equipment] #equipmentContainer not found in DOM");
      return;
    }

    // Render each equipment item
    container.innerHTML = data.equipment.map(eq => `
      <div class="equipment-item">
        <p><strong>${eq.name}</strong> (ID: ${eq.id})</p>
        ${eq.description ? `<p>${eq.description}</p>` : ''}
      </div>
    `).join('');
  } catch (error) {
    console.error("[equipment] error fetching equipment:", error);
    alert("Unable to load equipment. Please try again later.");
  }
}
