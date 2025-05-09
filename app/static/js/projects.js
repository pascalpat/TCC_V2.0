// static/js/projects.js

// Pull in our projects-list endpoint from window.API (fallback to empty string)
const { listProjects = '' } = window.API || {};

/**
 *  Fetch project numbers from the backend and populate the #projectNumber dropdown.
 */
export async function fetchProjectNumbers() {
  console.log("[fetchProjectNumbers] fetching project numbers…");

  // If the endpoint isn’t configured, bail
  if (!listProjects) {
    console.warn("[fetchProjectNumbers] listProjects endpoint not defined, skipping.");
    return;
  }

  try {
    const response = await fetch(listProjects);
    if (!response.ok) {
      throw new Error(`Failed to fetch project numbers: ${response.statusText}`);
    }
    const data = await response.json();

    // Target the dropdown (or input) with ID 'projectNumber'
    const projectDropdown = document.getElementById("projectNumber");
    if (!projectDropdown) {
      console.error("[fetchProjectNumbers] #projectNumber not found in DOM.");
      return;
    }

    // Clear existing options (if it's a <select>) or value (if it's an <input>)
    if (projectDropdown.tagName === "SELECT") {
      projectDropdown.innerHTML = "<option value='' disabled selected>-- Choisir Projet --</option>";
    } else {
      projectDropdown.value = "";
    }

    // Populate with data.project_numbers
    if (Array.isArray(data.project_numbers) && data.project_numbers.length > 0) {
      data.project_numbers.forEach(proj => {
        if (projectDropdown.tagName === "SELECT") {
          const option = document.createElement("option");
          option.value = proj;
          option.textContent = proj;
          projectDropdown.appendChild(option);
        } else {
          // if it's an <input>, just set its value to the first project
          projectDropdown.value = data.project_numbers[0];
        }
      });
    } else {
      // no projects returned
      if (projectDropdown.tagName === "SELECT") {
        const option = document.createElement("option");
        option.value = "";
        option.disabled = true;
        option.textContent = "No Projects Available";
        projectDropdown.appendChild(option);
      } else {
        projectDropdown.placeholder = "No Projects Available";
      }
    }

    console.log("[fetchProjectNumbers] done.");
  }
  catch (error) {
    console.error("[fetchProjectNumbers] error:", error);

    // On error, show “No Projects Available”
    const projectDropdown = document.getElementById("projectNumber");
    if (projectDropdown) {
      if (projectDropdown.tagName === "SELECT") {
        projectDropdown.innerHTML = "<option value='' disabled>No Projects Available</option>";
      } else {
        projectDropdown.placeholder = "No Projects Available";
      }
    }
  }
}
