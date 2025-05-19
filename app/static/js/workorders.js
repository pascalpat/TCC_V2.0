export async function fetchAndRenderWorkOrders() {
    const response = await fetch('/work-orders/list');
    const data = await response.json();

    const container = document.getElementById('workOrdersContainer');
    if (!container) return;

    container.innerHTML = (data.work_orders || []).map(order => `
        <div class="work-order">
            <p>Number: ${order.sequential_number}</p>
            <p>Description: ${order.description}</p>
            <p>Status: ${order.status}</p>
        </div>
    `).join('');
}
