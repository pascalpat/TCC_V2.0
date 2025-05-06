// static/js/populate_drop_downs.js

/**
 * 1) Populate Workers & Equipment dropdown
 */
export async function populateWorkersAndEquipmentDropdown() {
  console.log("[populateWorkersAndEquipmentDropdown] fetching workers & equipment...");
  try {
    const [wkResp, eqResp] = await Promise.all([
      fetch("/workers/list"),
      fetch("/equipment/list")
    ]);
    if (!wkResp.ok || !eqResp.ok) throw new Error("Fetch failed");

    const { workers }   = await wkResp.json();
    const { equipment } = await eqResp.json();
    const dd = document.getElementById("workerName");
    if (!dd) return;

    // reset options
    dd.innerHTML = `<option value="" disabled selected>-- Sélectionner Employé ou Équipement --</option>`;

    const wgroup = document.createElement("optgroup");
    wgroup.label = "👤 Employés";
    workers.forEach(w => {
      wgroup.appendChild(new Option(`👤 ${w.name}`, `worker|${w.id}`));
    });
    dd.appendChild(wgroup);

    const egroup = document.createElement("optgroup");
    egroup.label = "🛠️ Équipements";
    equipment.forEach(e => {
      egroup.appendChild(new Option(`🛠️ ${e.name}`, `equipment|${e.id}`));
    });
    dd.appendChild(egroup);

    console.log("[populateWorkersAndEquipmentDropdown] done.");
  } catch (err) {
    console.error("[populateWorkersAndEquipmentDropdown] error:", err);
  }
}

/**
 * 2) Populate Activity Codes dropdown for all tabs
 */
export async function populateActivityDropdown() {
  console.log("[populateActivityDropdown] fetching codes...");
  try {
    const resp = await fetch("/activity-codes/get_activity_codes");
    if (!resp.ok) throw new Error("Fetch failed");

    const { activity_codes } = await resp.json();
    // store for later use in confirm
    window.activityCodesList = activity_codes;

    const ids = [
      "activityCode",
      "materialActivityCode",
      "subcontractorActivityCode"
    ];
    ids.forEach(id => {
      const dd = document.getElementById(id);
      if (!dd) return;
      // reset options
      dd.innerHTML = `<option value="" disabled selected>-- Sélectionner Code d’Activité --</option>`;
      activity_codes.forEach(ac => {
        if (!ac.code.trim()) return;
        dd.appendChild(new Option(
          `${ac.code} – ${ac.description}`,
          ac.id
        ));
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
export async function populatePaymentItemDropdown() {
  console.log("[populatePaymentItemDropdown] fetching payment items...");
  try {
    const resp = await fetch("/data-entry/payment-items/list");
    if (!resp.ok) throw new Error(`Status ${resp.status}`);
    const { payment_items: items } = await resp.json();
    const dd = document.getElementById("payment_item_id");
    if (!dd) return;

    // reset options
    dd.innerHTML = `<option value="" disabled selected>-- Aucun --</option>`;
    items.forEach(pi => {
      const text = pi.payment_code
        ? `${pi.payment_code} – ${pi.item_name}`
        : pi.item_name;
      dd.appendChild(new Option(text, pi.id));
    });

    console.log("[populatePaymentItemDropdown] done.");
  } catch (err) {
    console.error("[populatePaymentItemDropdown] failed to fetch:", err);
  }
}

/**
 * 4) Populate CWP dropdown
 */
export async function populateCwpDropdown() {
  console.log("[populateCwpDropdown] fetching CWPs...");
  try {
    const resp = await fetch("/data_entry/cw-packages/list");
    if (!resp.ok) throw new Error(`Status ${resp.status}`);
    const { cwps } = await resp.json();

    const dd = document.getElementById("cwp_code");
    if (!dd) {
      console.warn("populateCwpDropdown(): #cwp_code not found");
      return;
    }

    // reset to a clean default
    dd.innerHTML = `<option value="" disabled selected>-- Aucun --</option>`;

    cwps.forEach(c => {
      dd.add(new Option(`${c.code} – ${c.name}`, c.code));
    });
    console.log("[populateCwpDropdown] done.");
  } catch (err) {
    console.error("[populateCwpDropdown] failed to fetch:", err);
  }
}

/**
 * 5) Master helper: wire up all dropdowns
 */
export async function populateDropdowns() {
  console.log("[populateDropdowns] start");
  await populateWorkersAndEquipmentDropdown();
  await populateActivityDropdown();
  await populatePaymentItemDropdown();
  await populateCwpDropdown();
  console.log("[populateDropdowns] all dropdowns populated");
}
