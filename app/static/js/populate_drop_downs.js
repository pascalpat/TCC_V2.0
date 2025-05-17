// File: static/js/populate_drop_downs.js

/**
 * 0) Master helper: wire up all dropdowns
 */
export async function populateDropdowns(API) {
  console.log("[populateDropdowns] start");
  await populateWorkersAndEquipmentDropdown(API);
  await populateActivityDropdown(API);
  await populatePaymentItemDropdown(API);
  await populateCwpDropdown(API);
  console.log("[populateDropdowns] all dropdowns populated");
}


/**
 * 1) Populate Workers & Equipment dropdown
 */
export async function populateWorkersAndEquipmentDropdown(API) {
  console.log("[populateWorkersAndEquipmentDropdown] fetching workers & equipment...");
  // ensure the two endpoints exist
  if (!API.listWorkers || !API.listEquipment) {
    console.warn("[populateWorkersAndEquipmentDropdown] missing API endpoints");
    return;
  }

  try {
    // fetch workers and equipment in parallel
    const [wkResp, eqResp] = await Promise.all([
      fetch(`${window.API_BASE}${API.listWorkers}`),
      fetch(`${window.API_BASE}${API.listEquipment}`)
    ]);
    if (!wkResp.ok || !eqResp.ok) {
      throw new Error(`Fetch failed: workers ${wkResp.status}, equipment ${eqResp.status}`);
    }

    const { workers = [] }   = await wkResp.json();
    const { equipment = [] } = await eqResp.json();

    // pick the correct <select> by ID
    const dd = document.getElementById("workerName") 
            || document.getElementById("workerEquipmentSelector");
    if (!dd) {
      console.warn("[populateWorkersAndEquipmentDropdown] no dropdown element found");
      return;
    }

    // reset to default option
    dd.innerHTML = `<option value="" disabled selected>-- Sélectionner Employé ou Équipement --</option>`;

    // ── Employees group ──
    if (workers.length) {
      const wgroup = document.createElement("optgroup");
      wgroup.label = "👤 Employés";
      workers.forEach(w => {
        wgroup.appendChild(new Option(`👤 ${w.name}`, `worker|${w.id}`));
      });
      dd.appendChild(wgroup);
    }

    // ── Equipment group ──
    if (equipment.length) {
      const egroup = document.createElement("optgroup");
      egroup.label = "🛠️ Équipements";
      equipment.forEach(e => {
        egroup.appendChild(new Option(`🛠️ ${e.name}`, `equipment|${e.id}`));
      });
      dd.appendChild(egroup);
    }

    console.log("[populateWorkersAndEquipmentDropdown] done.");
  } catch (err) {
    console.error("[populateWorkersAndEquipmentDropdown] error:", err);
  }
}


/**
 * 2) Populate Activity Codes dropdown
 */
export async function populateActivityDropdown(API) {
  console.log("[populateActivityDropdown] fetching codes...");
  if (!API.listActivityCodes) {
    console.warn("[populateActivityDropdown] missing API endpoint");
    return;
  }

  try {
    const resp = await fetch(`${window.API_BASE}${API.listActivityCodes}`);
    if (!resp.ok) throw new Error(`Status ${resp.status}`);

    const { activity_codes = [] } = await resp.json();
    window.activityCodesList = activity_codes;

    ["activityCode", "materialActivityCode", "subcontractorActivityCode"]
      .forEach(id => {
        const dd = document.getElementById(id);
        if (!dd) return;
        dd.innerHTML = `<option value="" disabled selected>-- Sélectionner Code d’Activité --</option>`;
        activity_codes.forEach(ac => {
          if (!ac.code.trim()) return;
          dd.appendChild(new Option(`${ac.code} – ${ac.description}`, ac.id));
        });
      });

    console.log("[populateActivityDropdown] done.");
  } catch (err) {
    console.error("[populateActivityDropdown] error:", err);
  }
}


/**
 * 3) Populate Payment Items dropdown
 */
export async function populatePaymentItemDropdown(API) {
  console.log("[populatePaymentItemDropdown] fetching payment items...");
  if (!API.listPaymentItems) {
    console.warn("[populatePaymentItemDropdown] missing API endpoint");
    return;
  }

  try {
    const resp = await fetch(`${window.API_BASE}${API.listPaymentItems}`);
    if (!resp.ok) throw new Error(`Status ${resp.status}`);

    const { payment_items: items = [] } = await resp.json();
    window.paymentItemsList = items;

    const dd = document.getElementById("payment_item_id");
    if (!dd) return;
    dd.innerHTML = `<option value="" disabled selected>-- Aucun --</option>`;
    items.forEach(pi => {
      const label = pi.payment_code
        ? `${pi.payment_code} – ${pi.item_name}`
        : pi.item_name;
      dd.appendChild(new Option(label, pi.id));
    });

    console.log("[populatePaymentItemDropdown] done.");
  } catch (err) {
    console.error("[populatePaymentItemDropdown] error:", err);
  }
}


/**
 * 4) Populate CWP dropdown
 */
export async function populateCwpDropdown(API) {
  console.log("[populateCwpDropdown] fetching CWPs...");
  if (!API.listCwps) {
    console.warn("[populateCwpDropdown] missing API endpoint");
    return;
  }

  try {
    const resp = await fetch(`${window.API_BASE}${API.listCwps}`);
    if (!resp.ok) throw new Error(`Status ${resp.status}`);
    const { cwps = [] } = await resp.json();
    window.cwpList = cwps;

    ["cwp_code", "materialCwp"].forEach(selectId => {
      const dd = document.getElementById(selectId);
      if (!dd) return;
      dd.innerHTML = `<option value="" disabled selected>-- Aucun --</option>`;
      cwps.forEach(c => {
        dd.appendChild(new Option(`${c.code} – ${c.name}`, c.code));
      });
    });

    console.log("[populateCwpDropdown] done.");
  } catch (err) {
    console.error("[populateCwpDropdown] error:", err);
  }
}
