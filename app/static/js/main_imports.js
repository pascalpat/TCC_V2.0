
import { clearErrorStyles, showError } from './validation.js';
import { openTab } from './openTab.js';
import { fetchProjectNumbers } from './projects.js';
// import { addWorker, fetchAndRenderWorkers } from './workers.js';
import { initLaborEquipmentTab } from '/static/js/LaborEquipment.js';
import { fetchAndRenderMaterials, addMaterial } from './materials.js';
// import { fetchAndRenderEquipment, addEquipment } from './equipment.js';
import { fetchAndRenderDailyNotes } from './notes.js';
import { fetchAndRenderWorkOrders } from './workorders.js';
import { fetchAndRenderPictures } from './pictures.js';
import { fetchAndRenderMedia } from './media.js';
import { getCurrentDate, highlightDates, confirmDateSelection, getTemperature, markTabComplete, restoreProgress } from './date_temp_loader.js';
import { populateDropdown, populateDropdowns } from './populate_drop_downs.js';
import { confirmWorkers } from './workers.js';	


// Date / temp / progress logic
import { 
    getCurrentDate, 
    highlightDates, 
    confirmDateSelection, 
    getTemperature, 
    markTabComplete, 
    restoreProgress 
  } from './date_temp_loader.js';

// Dropdown population
import { populateDropdown, populateDropdowns } from './populate_drop_downs.js';

// If still using any worker logic:
import { confirmWorkers /*, addWorker, etc... */ } from './workers.js';


// ------------------------------
// 2. ATTACH TO GLOBAL WINDOW (IF NEEDED)
// ------------------------------
if (typeof window !== 'undefined') {
    // Example: Make certain functions globally accessible
    window.openTab = openTab;
    window.populateDropdowns = populateDropdowns;

  
// Export functions globally if needed
//console.log('Environment check:', typeof window !== 'undefined' ? 'Browser' : 'Non-browser');

//window.openTab = openTab;
//window.populateDropdowns = populateDropdowns;
//window.addWorker = addWorker;
window.confirmWorkers = confirmWorkers;
//console.log('addWorker attached to window: main_imports line 23', window.addWorker);
}

// ------------------------------
// 3. OPTIONAL: PAGE-LOAD INITIALIZATION
// ------------------------------
document.addEventListener('DOMContentLoaded', async () => {
    console.log('main_imports.js: DOMContentLoaded fired.');
  
    // Example: Initialize your new combined "labor & equipment" tab:
    // (Only if you want it to run automatically on page load)
    try {
      await initLaborEquipmentTab();
      console.log("Initialized labor & equipment tab from main_imports.js");
    } catch (err) {
      console.error("Error initializing laborEquipmentTab:", err);
    }
    populateWorkers();
        try {
          await fetchAndRenderMedia();
        } catch (err) {
          console.error('Error loading media:', err);
        }

    // Any other startup logic goes here...
    
    // For example, load project numbers (if needed)
    // await fetchProjectNumbers();
  
    // Possibly call other setups, like restoring progress bar, 
    // or populating certain dropdowns:
    // await populateDropdowns();
  
    // ...
  });
