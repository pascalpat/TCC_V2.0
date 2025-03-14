export async function fetchAndRenderWorkOrders() {
    const response = await fetch('/work-orders/list');
    const data = await response.json();

    const workOrdersContainer = document.getElementById('workOrdersContainer');
    workOrdersContainer.innerHTML = data.work_orders.map(order => `
        <div class="work-order">
            <p>Order #: ${order.order_number}</p>
            <p>Description: ${order.description}</p>
            <p>Hours: ${order.hours}</p>
        </div>
    `).join('');
}
