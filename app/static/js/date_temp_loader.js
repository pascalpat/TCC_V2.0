// File: static/js/date_temp_loader.js

// ────────────────────────────────────────────────────
// 1) Show “today” in a dedicated span (#todayDate)
// ────────────────────────────────────────────────────
export function showToday() {
  const todaySpan = document.getElementById('todayDate');
  if (!todaySpan) return;
  const today = new Date();
  todaySpan.textContent = today.toLocaleDateString(undefined, {
    weekday: 'long',
    year:    'numeric',
    month:   'long',
    day:     'numeric'
  });
}

// ────────────────────────────────────────────────────
// 2) Highlight completed/in-progress days
// ────────────────────────────────────────────────────
export async function highlightDates() {
  try {
    const resp = await fetch(window.API.daysStatus);
    if (!resp.ok) throw new Error(`Fetch failed: ${resp.status}`);
    const { completedDays = [], incompleteDays = [] } = await resp.json();

    const dateEl = document.getElementById('dateSelector');
    if (!dateEl || dateEl.tagName !== 'SELECT') return;

    Array.from(dateEl.options).forEach(opt => {
      opt.style.backgroundColor = '';
      if (completedDays.includes(opt.value)) {
        opt.style.backgroundColor = 'green';
      } else if (incompleteDays.includes(opt.value)) {
        opt.style.backgroundColor = 'orange';
      }
    });

    console.log('[highlightDates] applied status colors');
  } catch (err) {
    console.error('[highlightDates] error:', err);
  }
}

// ────────────────────────────────────────────────────
// 3) Initialize reporting‐date in session
// ────────────────────────────────────────────────────
export async function confirmDateSelection(selectedDate) {
  try {
    const resp = await fetch(window.API.initializeDay, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ dateStamp: selectedDate })
    });
    if (!resp.ok) throw new Error(`Init‐day failed: ${resp.statusText}`);
    return await resp.json();
  } catch (err) {
    console.error('[confirmDateSelection] error:', err);
  }
}

// ────────────────────────────────────────────────────
// 4) Weather widget
// ────────────────────────────────────────────────────
export async function getTemperature() {
  console.log('[Weather] getTemperature() → running');
  const tempEl = document.getElementById('currentTemperature');
  const img    = document.getElementById('weatherIcon');

  try {
    const resp = await fetch(window.API.weather);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const { temperature, icon } = await resp.json();

    if (tempEl) {
      tempEl.textContent = (typeof temperature === 'number')
        ? `${Math.round(temperature)}°C`
        : '--°C';
    }

    if (img) {
      if (icon) {
        img.src         = `https://openweathermap.org/img/wn/${icon}@2x.png`;
        img.alt         = `Weather icon ${icon}`;
        img.style.display = '';
      } else {
        img.removeAttribute('src');
        img.alt = 'No weather data';
        img.style.display = 'none';
      }
    }

    console.log('[Weather] updated temperature & icon');
  } catch (error) {
    console.error('[Weather] failed:', error);
    if (tempEl) tempEl.textContent = '--°C';
    if (img) {
      img.removeAttribute('src');
      img.alt = 'No weather data';
      img.style.display = 'none';
    }
  }
}

// ────────────────────────────────────────────────────
// 5) (optional) Progress‐bar helpers stubs
// ────────────────────────────────────────────────────
export async function markTabComplete(tabName) { /* … */ }
export async function restoreProgress()    { /* … */ }

// ────────────────────────────────────────────────────
// Run on page load
// ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  showToday();
  highlightDates();
  getTemperature();
  restoreProgress();
});
