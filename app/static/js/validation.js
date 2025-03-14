// utils/validation.js

// Function to clear error styles
export function clearErrorStyles(element) {
    if (element) {
        element.classList.remove('error');
        const errorElement = element.nextElementSibling;
        if (errorElement && errorElement.classList.contains('error-message')) {
            errorElement.remove();
        }
    }
}

// Display error message and apply error styling to the input element
export function showError(element, errorMessage) {
    if (element) {
        element.classList.add('error');
        let errorElement = element.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('error-message')) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            element.parentNode.insertBefore(errorElement, element.nextSibling);
        }
        errorElement.textContent = errorMessage;
    }
}


// Event handler for date change
export function onDateChange(dateValue) {
    
    // Add future data-fetching logic or visual updates here
}

// Example input validation (Frontend logic for immediate feedback)
export function validateWorkerInput(workerName, laborHours, activityCode) {
    const errors = {};

    if (!workerName || workerName === '-- Select Worker --') {
        errors.workerName = 'Please select a valid worker.';
    }

    if (!laborHours || isNaN(laborHours) || laborHours <= 0) {
        errors.laborHours = 'Please enter a valid number of labor hours.';
    }

    if (!activityCode || activityCode === '-- Select Activity Code --') {
        errors.activityCode = 'Please select a valid activity code.';
    }

    return errors;
}

// Function to handle validation on form submission
export async function validateFormSubmission(workerName, laborHours, activityCode) {
    const errors = validateWorkerInput(workerName, laborHours, activityCode);

    if (Object.keys(errors).length > 0) {
        console.error('Validation errors:', errors);
        return errors;
    }

    // Optional: Send to backend for additional validation (if implemented)
    try {
        const response = await fetch('/validation/validate_worker', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ workerName, laborHours, activityCode }),
        });

        if (!response.ok) {
            throw new Error('Failed to validate worker input on server.');
        }

        const result = await response.json();
        if (result.errors) {
            console.error('Server-side validation errors:', result.errors);
            return result.errors;
        }
    } catch (error) {
        console.error('Error during server-side validation:', error);
    }

    return {}; // Return an empty object if no errors
}
