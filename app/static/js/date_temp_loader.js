// static/js/date_temp_loader.js

// ─────────────────────────────────────────────────────────────
// 1) Show “today” in a dedicated span (#todayDate)
// ─────────────────────────────────────────────────────────────
export function showToday() {
  const todaySpan = document.getElementById('todayDate');
  if (!todaySpan) return;
  const today = new Date();
  todaySpan.textContent = today.toLocaleDateString(undefined, {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
}

// ─────────────────────────────────────────────────────────────
// 2) Highlight completed/in-progress days (if #dateSelector is <select>)
// ─────────────────────────────────────────────────────────────
export async function highlightDates() {
  try {
    const resp = await fetch(window.API.getDayStatus);
    if (!resp.ok) throw new Error(`Fetch failed: ${resp.status}`);
    const { completedDays = [], incompleteDays = [] } = await resp.json();
    const dateEl = document.getElementById('dateSelector');
    if (!dateEl || dateEl.tagName !== 'SELECT') return;

    Array.from(dateEl.options).forEach(opt => {
      opt.style.backgroundColor = '';
      if (completedDays.includes(opt.value))       opt.style.backgroundColor = 'green';
      else if (incompleteDays.includes(opt.value)) opt.style.backgroundColor = 'orange';
    });
  } catch (err) {
    console.error('highlightDates()', err);
  }
}

// ─────────────────────────────────────────────────────────────
// 3) Initialize the reporting-date in session
// ─────────────────────────────────────────────────────────────
export async function confirmDateSelection(selectedDate) {
  try {
    const resp = await fetch(window.API.initializeDay, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ dateStamp: selectedDate })
    });
    if (!resp.ok) throw new Error(`Init-day failed: ${resp.statusText}`);
    return resp.json();
  } catch (err) {
    console.error('confirmDateSelection()', err);
  }
}

// ─────────────────────────────────────────────────────────────
// 4) Weather widget
// ─────────────────────────────────────────────────────────────
export async function getTemperature() {
  console.log('[Weather] getTemperature() → running');
  const tempEl = document.getElementById('currentTemperature');
  const img    = document.getElementById('weatherIcon');

  try {
    const resp = await fetch(window.API.getWeather);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const { temperature, icon } = await resp.json();

    // —— Temperature display —— 
    if (tempEl) {
      tempEl.textContent = 
        typeof temperature === 'number'
          ? `${Math.round(temperature)}°C`
          : '--°C';
    }

    // —— Icon display —— 
    if (img) {
      if (icon) {
        img.src           = `https://openweathermap.org/img/wn/${icon}@2x.png`;
        img.alt           = `Weather icon ${icon}`;
        img.style.display = '';
      } else {
        img.removeAttribute('src');
        img.alt           = 'No weather data';
        img.style.display = 'none';
      }
    }
  } catch (error) {
    console.error('[Weather] failed:', error);
    if (tempEl) tempEl.textContent = '--°C';
    if (img) {
      img.removeAttribute('src');
      img.alt           = 'No weather data';
      img.style.display = 'none';
    }
  }
}

// ─────────────────────────────────────────────────────────────
// 5) Progress‐bar helpers
// ─────────────────────────────────────────────────────────────
export async function markTabComplete(tabName) {
  try {
    await fetch(window.API.updateProgress, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tab: tabName })
    });
  } catch (err) {
    console.error('markTabComplete()', err);
  }
}

export async function restoreProgress() {
  try {
    const resp = await fetch(window.API.getProgress);
    if (!resp.ok) throw new Error(`Fetch failed: ${resp.status}`);
    const { completedTabs = [] } = await resp.json();
    completedTabs.forEach(tabId => {
      const el = document.getElementById(tabId);
      if (el) el.classList.add('tab-complete');
    });
  } catch (err) {
    console.error('restoreProgress()', err);
  }
}

// ─────────────────────────────────────────────────────────────
// 6) Run on page load
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  showToday();
  highlightDates();
  getTemperature();
  restoreProgress();
});
