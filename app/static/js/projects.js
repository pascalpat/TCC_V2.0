// Function to fetch project numbers from the backend and populate the dropdown
export async function fetchProjectNumbers() {
    try {
        // Fetch project numbers from the backend
        const response = await fetch('/projects/list');
        if (!response.ok) {
            throw new Error(`Failed to fetch project numbers: ${response.statusText}`);
        }
        
        const data = await response.json();
        

        // Get the projectNumber dropdown
        const projectDropdown = document.getElementById("projectNumber");
        if (!projectDropdown) {
            throw new Error("Project dropdown element with ID 'projectNumber' not found in the DOM.");
        }

        
        // Clear existing options
        projectDropdown.innerHTML = "<option value='' disabled selected>-- Choisir Projet --</option>";

        // Populate with project numbers from data
        if (data.project_numbers && data.project_numbers.length > 0) {
            data.project_numbers.forEach(projectNumber => {
                const option = document.createElement("option");
                option.value = projectNumber;
                option.textContent = projectNumber;
                projectDropdown.appendChild(option);
            });
        } else {
            const option = document.createElement("option");
            option.value = "";
            option.disabled = true;
            option.textContent = "No Projects Available";
            projectDropdown.appendChild(option);
        }
    }catch (error) {
        console.error("Error fetching project numbers:", error);

        // Handle UI feedback in case of failure
        const projectDropdown = document.getElementById("projectNumber");
        if (projectDropdown) {
            projectDropdown.innerHTML = "<option value='' disabled>No Projects Available</option>";
        }

    }
}

