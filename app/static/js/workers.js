// static/js/workers.js

// ────────────────────────────────────────────────────
// 0) Pull our three worker-related URLs from window.API
//    (with fallbacks to your current routes)
// ────────────────────────────────────────────────────
const {
  listSessionWorkers   = 'data-entry/workers/session-list',
  addWorker: addWorkerUrl   = 'data-entry/workers/add-worker',
  confirmWorkers: confirmWorkersUrl = 'data-entry/workers/confirm-workers'
} = window.API || {};

/**
 * 1) Fetch & render the “session” workers into #workersTable
 */
export async function fetchAndRenderWorkers() {
  console.log("[workers] fetching session workers…");
  try {
    const response = await fetch(listSessionWorkers);
    if (!response.ok) {
      throw new Error(`Failed to fetch workers: ${response.statusText}`);
    }
    const data = await response.json();
    console.log("[workers] session workers fetched:", data);

    // Locate the <table> (or <tbody>) and clear it
    const table = document.getElementById('workersTable');
    if (!table) {
      console.error("[workers] #workersTable not found in DOM");
      return;
    }
    // if it's a <table>, clear all rows:
    table.innerHTML = '';

    // Render each worker row
    data.workers.forEach(worker => {
      if (worker.workerName || worker.laborHours || worker.activityCode) {
        const row = table.insertRow();
        row.innerHTML = `
          <td>${worker.workerName   || 'N/A'}</td>
          <td>${worker.laborHours    || 'N/A'}</td>
          <td>${worker.activityCode  || 'N/A'}</td>
        `;
      }
    });
  } catch (error) {
    console.error("[workers] error fetching session workers:", error);
    alert("Unable to load workers. Please try again later.");
  }
}

/**
 * 2) Add one worker → POST → session, then re-fetch
 */
export async function addWorker() {
  console.log("[workers] Add Worker clicked…");
  const btn            = document.getElementById('addWorkerBtn');
  const workerDropdown = document.getElementById('workerName');
  const hoursInput     = document.getElementById('laborHours');
  const codeInput      = document.getElementById('activityCode');

  const workerName   = workerDropdown?.value;
  const laborHours   = hoursInput?.value;
  const activityCode = codeInput?.value || 'N/A';

  // Client‐side validation
  if (!workerName || !laborHours) {
    alert("Please fill in all required worker details (Name and Hours).");
    return;
  }
  if (isNaN(laborHours) || Number(laborHours) <= 0) {
    alert("Please enter a valid number for hours worked.");
    return;
  }

  // Disable & show loading
  if (btn) {
    btn.disabled    = true;
    btn.textContent = 'Adding…';
  }

  try {
    const payload = { workerName, laborHours, activityCode };
    console.log("[workers] payload:", payload);

    const response = await fetch(addWorkerUrl, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json().catch(() => null);
      throw new Error(err?.message || response.statusText);
    }

    const result = await response.json();
    console.log("[workers] added successfully:", result);
    alert('Worker added successfully!');

    // re-load the table from session
    await fetchAndRenderWorkers();

    // clear the form
    if (workerDropdown) workerDropdown.selectedIndex = 0;
    if (hoursInput)     hoursInput.value = '';
  } catch (error) {
    console.error("[workers] error adding worker:", error);
    alert(`Error adding worker: ${error.message}`);
  } finally {
    if (btn) {
      btn.disabled    = false;
      btn.textContent = 'Add Worker';
    }
  }
}

/**
 * 3) Confirm all staged workers → POST → server → update progress bar
 */
export async function confirmWorkers() {
  console.log("[workers] confirming workers…");
  try {
    // gather the table rows
    const rows = Array.from(document.querySelectorAll('#workersTable tbody tr'));
    const workers = rows.map(row => {
      const [nameCell, hoursCell, codeCell] = row.cells;
      return {
        workerName:   nameCell.textContent.trim(),
        laborHours:   hoursCell.textContent.trim(),
        activityCode: codeCell.textContent.trim()
      };
    });

    if (!workers.length) {
      alert("No workers to confirm.");
      return;
    }
    console.log("[workers] payload:", { workers });

    const response = await fetch(confirmWorkersUrl, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ workers })
    });

    if (!response.ok) {
      throw new Error(`Failed to confirm workers (${response.status})`);
    }

    const data = await response.json();
    console.log("[workers] confirmed successfully:", data);
    alert('Workers confirmed successfully!');

    // update a progress bar if your endpoint returns one
    const bar = document.getElementById('progress-bar');
    if (bar && data.progressPercentage != null) {
      bar.style.width = `${data.progressPercentage}%`;
      console.log(`[workers] progress updated to ${data.progressPercentage}%`);
    }
  } catch (error) {
    console.error("[workers] error confirming workers:", error);
    alert("Failed to confirm workers. Please try again.");
  }
}
