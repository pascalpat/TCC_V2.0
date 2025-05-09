// static/js/utils/validation.js

// ────────────────────────────────────────────────────
// Grab our validation endpoint from window.API
// ────────────────────────────────────────────────────
const {
  validateWorker: validateWorkerEndpoint = ''
} = window.API || {};

/**
 * 1) Clear any existing error styles & messages
 */
export function clearErrorStyles(element) {
  if (!element) return;
  element.classList.remove('error');
  const next = element.nextElementSibling;
  if (next?.classList.contains('error-message')) {
    next.remove();
  }
}

/**
 * 2) Show an inline error message on a field
 */
export function showError(element, errorMessage) {
  if (!element) return;
  element.classList.add('error');

  let msgEl = element.nextElementSibling;
  if (!msgEl || !msgEl.classList.contains('error-message')) {
    msgEl = document.createElement('div');
    msgEl.className = 'error-message';
    element.parentNode.insertBefore(msgEl, element.nextSibling);
  }
  msgEl.textContent = errorMessage;
}

/**
 * 3) Stub hook for when the date picker changes
 */
export function onDateChange(dateValue) {
  // future: call server or re-paint parts of the page
  console.log('[validation] date changed to', dateValue);
}

/**
 * 4) Pure-client validation of a worker entry
 */
export function validateWorkerInput(workerName, laborHours, activityCode) {
  const errors = {};

  if (!workerName || workerName === '-- Sélectionner Employé ou Équipement --') {
    errors.workerName = 'Veuillez sélectionner un travailleur ou un équipement.';
  }
  if (!laborHours || isNaN(laborHours) || Number(laborHours) <= 0) {
    errors.laborHours = 'Veuillez fournir un nombre d’heures valide.';
  }
  if (!activityCode || activityCode === '-- Sélectionner Code d’Activité --') {
    errors.activityCode = 'Veuillez sélectionner un code d’activité.';
  }

  return errors;
}

/**
 * 5) Combined client + optional server validation before submit
 */
export async function validateFormSubmission(workerName, laborHours, activityCode) {
  // 1) client‐side checks
  const errors = validateWorkerInput(workerName, laborHours, activityCode);
  if (Object.keys(errors).length) {
    console.error('[validation] client errors:', errors);
    return errors;
  }

  // 2) if no server endpoint configured, skip server‐side
  if (!validateWorkerEndpoint) {
    console.warn('[validation] validateWorker endpoint not set, skipping server validation');
    return {};
  }

  // 3) server‐side validation
  try {
    const resp = await fetch(validateWorkerEndpoint, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ workerName, laborHours, activityCode })
    });

    if (!resp.ok) {
      throw new Error(`Server returned ${resp.status}`);
    }

    const payload = await resp.json();
    if (payload.errors) {
      console.error('[validation] server errors:', payload.errors);
      return payload.errors;
    }
  } catch (err) {
    console.error('[validation] error during server validation:', err);
    // you might choose to show a generic error here
  }

  // 4) no errors
  return {};
}
