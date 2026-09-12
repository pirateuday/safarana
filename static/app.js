// Safarana Client-Side Application

let currentPlan = null;
let activeVariantKey = "balanced";
let activeDayFilter = "all";
let leafletMap = null;
let routeLayerGroup = null;
let pendingBooking = null;
let mapPickingTarget = null;
let tempPickerMarker = null;
let currentLegModes = {};
let currentReturnMode = null;
let currentSelectedTrains = {};
let currentReturnTrain = null;
let currentSelectedFlights = {};
let currentReturnFlight = null;
let userSelectedSpotsByCity = {};
let userSelectedHotelsByCity = {};
let userSelectedHotelObjsByCity = {};
let userSelectedDiningByCity = {};
let userSelectedDiningObjsByCity = {};
let userSelectedDiningSlotsByCity = {};
let userSelectedDiningDaysByCity = {};
let predefinedSelectionSnapshot = null;
let selectionReplanTimer = null;
let citySpotsCache = {};
let cityHotelsCache = {};
let cityDiningCache = {};
let cityActiveGenre = {};
let cityActiveStayTier = {};
let cityActiveCuisine = {};

// ---- Inline SVG symbol set (replaces emoji across the UI) ----
const ic = (paths) =>
  `<svg class="s-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;

const I = {
  car: ic('<path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11"/><path d="M4 11h16a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1h-1"/><path d="M3 17h18"/><circle cx="7.5" cy="17.5" r="1.7"/><circle cx="16.5" cy="17.5" r="1.7"/><path d="M12 5v6"/>'),
  train: ic('<path d="M8 3.1V7a4 4 0 0 0 8 0V3.1"/><path d="m9 15-1-1"/><path d="m15 15 1-1"/><path d="M9 19c-2.8 0-5-2.2-5-5v-4a8 8 0 0 1 16 0v4c0 2.8-2.2 5-5 5Z"/><path d="m8 19-2 3"/><path d="m16 19 2 3"/>'),
  station: ic('<path d="M3 16s8-3.2 18-3.2"/><path d="M3 16a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2"/><path d="M3 16v-5a9 9 0 0 1 18 0v5"/><path d="M9 10h6"/>'),
  flight: ic('<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>'),
  bus: ic('<path d="M4 17 6 5.5A2 2 0 0 1 8 4h8a2 2 0 0 1 2 1.5L20 17"/><path d="M20 17v2a1 1 0 0 1-1 1h-2"/><path d="M4 17v2a1 1 0 0 0 1 1h2"/><path d="M4 12h16"/><circle cx="7.5" cy="17.5" r="1.6"/><circle cx="16.5" cy="17.5" r="1.6"/><path d="M9 7h6"/>'),
  cab: ic('<path d="M6 9h12"/><path d="M6 9 7 4.5A2 2 0 0 1 9 3h6a2 2 0 0 1 2 1.5L18 9"/><path d="M5 9h14a1 1 0 0 1 1 1v5h-1"/><path d="M3 15v3h2"/><path d="M21 15v3h-2"/><circle cx="7" cy="15" r="1.6"/><circle cx="17" cy="15" r="1.6"/><path d="M7 18h10"/>'),
  local: ic('<path d="M20 10c0 4.9-5.5 10.2-7.4 11.8a1 1 0 0 1-1.2 0C9.5 20.2 4 14.9 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>'),
  seat: ic('<rect x="3" y="15" width="18" height="6" rx="1"/><path d="M6 15v-4a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v4"/><path d="M6 9V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v3"/>'),
  ticket: ic('<path d="M2 7a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-3a2 2 0 0 0 0-4Z"/><path d="M15 5v14"/>'),
  clock: ic('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
  timer: ic('<path d="M5 22h14M5 2h14M17 22v-4.2a2 2 0 0 0-.6-1.4L12 12l-4.4 4.4a2 2 0 0 0-.6 1.4V22M17 2v4.2a2 2 0 0 1-.6 1.4L12 12 7.6 7.6a2 2 0 0 1-.6-1.4V2"/>'),
  calendar: ic('<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>'),
  pin: ic('<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>'),
  landmark: ic('<line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="12"/><line x1="10" x2="10" y1="18" y2="12"/><line x1="14" x2="14" y1="18" y2="12"/><line x1="18" x2="18" y1="18" y2="12"/><polygon points="12 2 20 7 4 7"/>'),
  hotel: ic('<path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8"/><path d="M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><path d="M12 4v6"/><path d="M2 18h20"/>'),
  dining: ic('<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>'),
  luggage: ic('<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>'),
  clipboard: ic('<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/>'),
  globe: ic('<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>'),
  lightbulb: ic('<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.4 1 2.3h6c0-.9.4-1.8 1-2.3A7 7 0 0 0 12 2Z"/>'),
  info: ic('<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>'),
  check: ic('<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 6-6"/>'),
  alert: ic('<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
  shield: ic('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>'),
  swap: ic('<path d="M7 16V4m0 0L3 8m4-4 4 4"/><path d="M17 8v12m0 0 4-4"/><path d="m17 20-4-4"/>'),
  fuel: ic('<line x1="3" x2="15" y1="22" y2="22"/><line x1="4" x2="14" y1="9" y2="9"/><path d="M14 22V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v18"/><path d="M14 13h2a2 2 0 0 1 2 2v2a2 2 0 0 0 4 0V9.83a2 2 0 0 0-.59-1.42L18 5"/>'),
  route: ic('<path d="M5 22v-3c0-1 .5-2 1.5-2h11c1 0 1.5 1 1.5 2v3"/><path d="M3 16l3-5h12l3 5"/>'),
  sun: ic('<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>'),
  moon: ic('<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'),
  cloud: ic('<path d="M17.5 19a4.5 4.5 0 0 0 .4-9A6 6 0 0 0 6.3 8.2 4.5 4.5 0 0 0 7 17h10.5Z"/>'),
  rain: ic('<path d="M17.5 19a4.5 4.5 0 0 0 .4-9A6 6 0 0 0 6.3 8.2 4.5 4.5 0 0 0 7 17h10.5Z"/><path d="M7 19l-1.5 3"/><path d="M12 19l-1.5 3"/><path d="M17 19l-1.5 3"/>'),
  snow: ic('<path d="M17.5 19a4.5 4.5 0 0 0 .4-9A6 6 0 0 0 6.3 8.2 4.5 4.5 0 0 0 7 17h10.5Z"/><path d="M8 16h8"/><path d="M12 13v6"/>'),
  fog: ic('<path d="M3 7h11M3 11h17M3 15h14"/><path d="M3 19h8"/>'),
  hot: ic('<path d="M14 4a2 2 0 0 0-4 0v9.2a4 4 0 1 0 4 0Z"/><path d="M12 9v7"/>'),
};

const dotOn = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#16a34a;margin-right:4px;vertical-align:middle;"></span>';
const dotAlarm = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#dc2626;margin-right:4px;vertical-align:middle;"></span>';
const dotWarn = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#d97706;margin-right:4px;vertical-align:middle;"></span>';

function weatherIcon(ic) {
  const s = (ic || "");
  const t = s.toLowerCase();
  if (s.includes("\u2744") || t.includes("frosty") || t.includes("snow")) return I.snow;
  if (s.includes("\uD83C\uDF27") || t.includes("rain") || t.includes("monsoon") || t.includes("shower")) return I.rain;
  if (s.includes("\uD83C\uDF2B") || t.includes("fog") || t.includes("mist")) return I.fog;
  if (s.includes("\uD83D\uDD25") || t.includes("hot") || t.includes("heat") || t.includes("humid")) return I.hot;
  if (s.includes("\u26C5") || t.includes("cloud") || t.includes("breeze") || t.includes("crisp") || t.includes("overcast")) return I.cloud;
  return I.sun;
}

function applyTheme(theme) {
  const root = document.documentElement;
  root.setAttribute("data-theme", theme);
  const iconLight = document.getElementById("themeIconLight");
  const iconDark = document.getElementById("themeIconDark");
  if (iconLight) iconLight.style.display = theme === "dark" ? "block" : "none";
  if (iconDark) iconDark.style.display = theme === "dark" ? "none" : "block";
}

function initTheme() {
  const saved = localStorage.getItem("safarana-theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (prefersDark ? "dark" : "light");
  applyTheme(theme);
  const toggleBtn = document.getElementById("themeToggleBtn");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem("safarana-theme", next);
    });
  }
}

// Initialize upon DOM load
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initMap();
  initEventListeners();
  initLocationControls();
  initSpotPickers();
  initStayAndDiningPickers();
  loadCities();
  loadBookingsCount();
  // Initial plan load
  triggerPlanning();
});

function initMap() {
  const mapElement = document.getElementById("leafletMap");
  if (!mapElement) return;

  leafletMap = L.map("leafletMap").setView([27.5, 76.5], 7);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
  }).addTo(leafletMap);

  routeLayerGroup = L.layerGroup().addTo(leafletMap);

  // Map click listener for interactive location picking
  leafletMap.on("click", (e) => {
    if (!mapPickingTarget) return;

    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    const nearest = findNearestCity(lat, lon);
    const chosenName = nearest ? nearest.name : `${lat.toFixed(3)}, ${lon.toFixed(3)}`;

    if (mapPickingTarget === "origin") {
      document.getElementById("originInput").value = chosenName;
    } else if (mapPickingTarget === "destination") {
      document.getElementById("destinationInput").value = chosenName;
    }

    if (tempPickerMarker) {
      leafletMap.removeLayer(tempPickerMarker);
    }

    const markerColor = mapPickingTarget === "origin" ? "#22c55e" : "#ef4444";
    tempPickerMarker = L.circleMarker([lat, lon], {
      radius: 9,
      color: markerColor,
      fillColor: markerColor,
      fillOpacity: 0.9,
      weight: 2
    }).addTo(leafletMap).bindPopup(`<strong>${mapPickingTarget.toUpperCase()}:</strong> ${chosenName}`).openPopup();

    stopMapPicking();
    triggerPlanning();
  });
}

function initEventListeners() {
  // Trip form submission
  document.getElementById("tripForm").addEventListener("submit", (e) => {
    e.preventDefault();
    triggerPlanning();
  });

  // Tabs navigation
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const targetPanel = document.getElementById(btn.dataset.tab);
      if (targetPanel) {
        targetPanel.classList.add("active");
        if (btn.dataset.tab === "tab-map" && leafletMap) {
          setTimeout(() => leafletMap.invalidateSize(), 200);
        }
      }
    });
  });

  // Modal actions
  document.getElementById("closeModalBtn").addEventListener("click", closeModal);
  document.getElementById("cancelBookingBtn").addEventListener("click", closeModal);
  document.getElementById("confirmBookingBtn").addEventListener("click", confirmPendingBooking);
  document.getElementById("openBookingsBtn").addEventListener("click", openMyBookingsModal);
  document.getElementById("closeBookingsModalBtn").addEventListener("click", closeMyBookingsModal);

  // Calendar Export & Print
  const exportIcsBtn = document.getElementById("exportIcsBtn");
  if (exportIcsBtn) {
    exportIcsBtn.addEventListener("click", downloadCalendarIcs);
  }
  const printTripBtn = document.getElementById("printTripBtn");
  if (printTripBtn) {
    printTripBtn.addEventListener("click", () => window.print());
  }
}

function initLocationControls() {
  // Swap button (Reverse route)
  const swapBtn = document.getElementById("swapLocationsBtn");
  if (swapBtn) {
    swapBtn.addEventListener("click", () => {
      const origInput = document.getElementById("originInput");
      const destInput = document.getElementById("destinationInput");
      const temp = origInput.value;
      origInput.value = destInput.value;
      destInput.value = temp;
      updateCorridorSuggestions();
      updateDestSpotPicker(false);
      triggerPlanning();
    });
  }

  // Quick-tag city chips
  document.querySelectorAll(".city-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const target = chip.dataset.target;
      const city = chip.dataset.city;
      if (target === "origin") {
        document.getElementById("originInput").value = city;
      } else if (target === "destination") {
        document.getElementById("destinationInput").value = city;
        updateDestSpotPicker(false);
      }
      updateCorridorSuggestions();
      triggerPlanning();
    });
  });

  // Reset button in navbar
  const newTripBtn = document.getElementById("newTripBtn");
  if (newTripBtn) {
    newTripBtn.addEventListener("click", () => {
      document.getElementById("originInput").value = "Delhi";
      document.getElementById("destinationInput").value = "Jaipur";
      currentLegModes = {};
      userSelectedSpotsByCity = {};
      const container = document.getElementById("stopoversContainer");
      if (container) container.innerHTML = "";
      document.getElementById("originInput").focus();
      updateCorridorSuggestions();
      updateDestSpotPicker(false);
      triggerPlanning();
    });
  }

  // Map Picking Buttons
  const pickOriginBtn = document.getElementById("pickOriginMapBtn");
  if (pickOriginBtn) {
    pickOriginBtn.addEventListener("click", () => startMapPicking("origin"));
  }
  const pickDestBtn = document.getElementById("pickDestMapBtn");
  if (pickDestBtn) {
    pickDestBtn.addEventListener("click", () => startMapPicking("destination"));
  }
  const cancelPickerBtn = document.getElementById("cancelMapPickerBtn");
  if (cancelPickerBtn) {
    cancelPickerBtn.addEventListener("click", stopMapPicking);
  }

  // Date change listeners for deadline calculation
  const startDateInput = document.getElementById("startDateInput");
  const endDateInput = document.getElementById("endDateInput");
  if (startDateInput && endDateInput) {
    startDateInput.addEventListener("change", updateDeadlineDisplay);
    endDateInput.addEventListener("change", updateDeadlineDisplay);
  }

  // Origin & Destination input change for corridor suggestions & spot picker
  const origInput = document.getElementById("originInput");
  const destInput = document.getElementById("destinationInput");
  if (origInput && destInput) {
    origInput.addEventListener("change", updateCorridorSuggestions);
    destInput.addEventListener("change", () => {
      updateCorridorSuggestions();
      updateDestSpotPicker(false);
    });
  }

  // Add In-Between Stop button
  const addStopoverBtn = document.getElementById("addStopoverBtn");
  if (addStopoverBtn) {
    addStopoverBtn.addEventListener("click", () => addStopoverRow());
  }

  // Initial updates
  updateDeadlineDisplay();
  updateCorridorSuggestions();
}

function initSpotPickers() {
  const toggleBtn = document.getElementById("destSpotPickerToggle");
  const body = document.getElementById("destSpotPickerBody");
  const container = document.getElementById("destSpotPicker");
  const refreshBtn = document.getElementById("destRefreshSpotsBtn");
  const destInput = document.getElementById("destinationInput");

  if (toggleBtn && body && container) {
    toggleBtn.addEventListener("click", () => {
      const isOpen = container.classList.toggle("open");
      body.style.display = isOpen ? "block" : "none";
      if (isOpen) {
        updateDestSpotPicker(false);
      }
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const dest = destInput ? destInput.value.trim() : "Jaipur";
      if (dest) {
        updateDestSpotPicker(true);
      }
    });
  }

  if (destInput) {
    destInput.addEventListener("change", () => {
      const dest = destInput.value.trim();
      const nameElem = document.getElementById("destSpotPickerCityName");
      if (nameElem) nameElem.textContent = dest || "Destination";
      updateDestSpotPicker(false);
    });
  }
}

async function fetchCitySpots(cityName, forceRefresh = false) {
  const normCity = (cityName || "").trim();
  if (!normCity) return [];
  if (!forceRefresh && citySpotsCache[normCity]) {
    return citySpotsCache[normCity];
  }
  try {
    const res = await fetch(`/api/spots?city=${encodeURIComponent(normCity)}`);
    if (!res.ok) throw new Error("Failed to fetch spots");
    const data = await res.json();
    citySpotsCache[normCity] = data.spots || [];
    return citySpotsCache[normCity];
  } catch (err) {
    console.error(`Error fetching spots for ${normCity}:`, err);
    return [];
  }
}

async function updateDestSpotPicker(forceRefresh = false) {
  const destInput = document.getElementById("destinationInput");
  const dest = destInput ? destInput.value.trim() : "Jaipur";
  const nameElem = document.getElementById("destSpotPickerCityName");
  if (nameElem) nameElem.textContent = dest || "Destination";
  if (!dest) return;

  const listElem = document.getElementById("destSpotsList");
  const genresElem = document.getElementById("destGenreFilters");
  const badgeElem = document.getElementById("destSpotSelectedBadge");

  await renderCitySpotPicker(dest, listElem, genresElem, badgeElem, false, forceRefresh);
}

async function renderCitySpotPicker(cityName, listElem, genresElem, badgeElem, isStopover = false, forceRefresh = false) {
  if (!listElem) return;
  listElem.innerHTML = `<div class="spots-loading-hint">Fetching attractions in ${cityName} from OpenStreetMap & OpenTripMap...</div>`;

  const spots = await fetchCitySpots(cityName, forceRefresh);
  if (!spots || spots.length === 0) {
    listElem.innerHTML = `<div class="spots-loading-hint">No attractions found for "${cityName}". Spots will be discovered automatically during planning.</div>`;
    return;
  }

  // Determine genres present
  const genres = ["All"];
  spots.forEach(s => {
    if (s.genre && !genres.includes(s.genre)) {
      genres.push(s.genre);
    }
  });

  const activeGenre = cityActiveGenre[cityName] || "All";

  // Render genre filter chips
  if (genresElem) {
    genresElem.innerHTML = genres.map(g => `
      <button type="button" class="genre-filter-chip ${g === activeGenre ? 'active' : ''}" data-genre="${g}">
        ${g}
      </button>
    `).join("");

    genresElem.querySelectorAll(".genre-filter-chip").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        cityActiveGenre[cityName] = btn.dataset.genre;
        renderCitySpotPicker(cityName, listElem, genresElem, badgeElem, isStopover, false);
      });
    });
  }

  // Filter spots by genre
  const filteredSpots = activeGenre === "All"
    ? spots
    : spots.filter(s => s.genre === activeGenre);

  // Initialize selected set for city if not existing
  if (!userSelectedSpotsByCity[cityName]) {
    userSelectedSpotsByCity[cityName] = new Set();
  }
  const selectedSet = userSelectedSpotsByCity[cityName];

  // Update badge count
  const count = selectedSet.size;
  if (badgeElem) {
    badgeElem.textContent = `${count} Selected`;
    badgeElem.classList.toggle("has-selected", count > 0);
  }

  listElem.innerHTML = "";
  filteredSpots.forEach(spot => {
    const isSelected = selectedSet.has(spot.name);
    const item = document.createElement("div");
    item.className = `spot-selection-item ${isSelected ? 'selected' : ''}`;
    
    const feeText = spot.entry_fee_per_person > 0 ? `${I.ticket} ₹${spot.entry_fee_per_person}` : "${I.ticket} Free";
    const hoursText = `${I.clock} ${spot.opening_time} - ${spot.closing_time}`;
    const genreBadge = spot.genre ? `<span class="badge-genre">${spot.genre}</span>` : "";
    const sourceBadge = spot.source ? `<span class="badge-source">${spot.source.toUpperCase()}</span>` : "";

    item.innerHTML = `
      <input type="checkbox" class="spot-checkbox" ${isSelected ? 'checked' : ''} />
      <div class="spot-item-details">
        <div class="spot-item-header">
          <span class="spot-item-name" title="${spot.name}">${spot.name}</span>
          <span class="spot-item-rating">★ ${spot.rating}</span>
        </div>
        <div class="spot-item-badges">
          ${genreBadge}
          <span class="badge-timing">${hoursText}</span>
          <span class="badge-fee">${feeText}</span>
          ${sourceBadge}
        </div>
      </div>
    `;

    const checkbox = item.querySelector(".spot-checkbox");

    item.addEventListener("click", (e) => {
      if (e.target !== checkbox) {
        checkbox.checked = !checkbox.checked;
      }
      if (checkbox.checked) {
        selectedSet.add(spot.name);
        item.classList.add("selected");
      } else {
        selectedSet.delete(spot.name);
        item.classList.remove("selected");
      }

      const updatedCount = selectedSet.size;
      if (badgeElem) {
        badgeElem.textContent = `${updatedCount} Selected`;
        badgeElem.classList.toggle("has-selected", updatedCount > 0);
      }

      triggerPlanning();
    });

    listElem.appendChild(item);
  });
}

function initStayAndDiningPickers() {
  // Stay Picker Setup
  const stayToggle = document.getElementById("destStayPickerToggle");
  const stayBody = document.getElementById("destStayPickerBody");
  const stayContainer = document.getElementById("destStayPicker");
  const stayRefresh = document.getElementById("destRefreshStayBtn");
  const destInput = document.getElementById("destinationInput");

  if (stayToggle && stayBody && stayContainer) {
    stayToggle.addEventListener("click", () => {
      const isOpen = stayContainer.classList.toggle("open");
      stayBody.style.display = isOpen ? "block" : "none";
      if (isOpen) {
        updateDestStayPicker(false);
      }
    });
  }

  if (stayRefresh) {
    stayRefresh.addEventListener("click", (e) => {
      e.stopPropagation();
      updateDestStayPicker(true);
    });
  }

  // Dining Picker Setup
  const diningToggle = document.getElementById("destDiningPickerToggle");
  const diningBody = document.getElementById("destDiningPickerBody");
  const diningContainer = document.getElementById("destDiningPicker");
  const diningRefresh = document.getElementById("destRefreshDiningBtn");

  if (diningToggle && diningBody && diningContainer) {
    diningToggle.addEventListener("click", () => {
      const isOpen = diningContainer.classList.toggle("open");
      diningBody.style.display = isOpen ? "block" : "none";
      if (isOpen) {
        updateDestDiningPicker(false);
      }
    });
  }

  if (diningRefresh) {
    diningRefresh.addEventListener("click", (e) => {
      e.stopPropagation();
      updateDestDiningPicker(true);
    });
  }

  if (destInput) {
    destInput.addEventListener("change", () => {
      const dest = destInput.value.trim() || "Destination";
      const sName = document.getElementById("destStayPickerCityName");
      if (sName) sName.textContent = dest;
      const dName = document.getElementById("destDiningPickerCityName");
      if (dName) dName.textContent = dest;
      if (stayBody && stayBody.style.display === "block") updateDestStayPicker(false);
      if (diningBody && diningBody.style.display === "block") updateDestDiningPicker(false);
    });
  }
}

async function fetchCityHotels(cityName, stayTier = null, forceRefresh = false) {
  const normCity = (cityName || "").trim();
  if (!normCity) return [];
  const cacheKey = `${normCity}_${stayTier || 'all'}`;
  if (!forceRefresh && cityHotelsCache[cacheKey]) {
    return cityHotelsCache[cacheKey];
  }
  try {
    const tierParam = stayTier && stayTier !== "all" ? `&tier=${encodeURIComponent(stayTier)}` : "";
    const res = await fetch(`/api/hotels?city=${encodeURIComponent(normCity)}${tierParam}`);
    if (!res.ok) throw new Error("Failed to fetch hotels");
    const data = await res.json();
    cityHotelsCache[cacheKey] = data.hotels || [];
    return cityHotelsCache[cacheKey];
  } catch (err) {
    console.error(`Error fetching hotels for ${normCity}:`, err);
    return [];
  }
}

async function fetchCityDining(cityName, cuisine = null, forceRefresh = false) {
  const normCity = (cityName || "").trim();
  if (!normCity) return [];
  const cacheKey = `${normCity}_${cuisine || 'all'}`;
  if (!forceRefresh && cityDiningCache[cacheKey]) {
    return cityDiningCache[cacheKey];
  }
  try {
    const cuisParam = cuisine && cuisine !== "all" ? `&cuisine=${encodeURIComponent(cuisine)}` : "";
    const res = await fetch(`/api/restaurants?city=${encodeURIComponent(normCity)}${cuisParam}`);
    if (!res.ok) throw new Error("Failed to fetch restaurants");
    const data = await res.json();
    cityDiningCache[cacheKey] = data.restaurants || [];
    return cityDiningCache[cacheKey];
  } catch (err) {
    console.error(`Error fetching dining for ${normCity}:`, err);
    return [];
  }
}

async function updateDestStayPicker(forceRefresh = false) {
  const dest = document.getElementById("destinationInput")?.value.trim() || "Jaipur";
  const nameElem = document.getElementById("destStayPickerCityName");
  if (nameElem) nameElem.textContent = dest;
  const listElem = document.getElementById("destStaysList");
  const filtersElem = document.getElementById("destStayFilters");
  const badgeElem = document.getElementById("destStaySelectedBadge");
  await renderCityHotelPicker(dest, listElem, filtersElem, badgeElem, false, forceRefresh);
}

async function updateDestDiningPicker(forceRefresh = false) {
  const dest = document.getElementById("destinationInput")?.value.trim() || "Jaipur";
  const nameElem = document.getElementById("destDiningPickerCityName");
  if (nameElem) nameElem.textContent = dest;
  const listElem = document.getElementById("destDiningList");
  const filtersElem = document.getElementById("destDiningFilters");
  const badgeElem = document.getElementById("destDiningSelectedBadge");
  await renderCityDiningPicker(dest, listElem, filtersElem, badgeElem, false, forceRefresh);
}

async function renderCityHotelPicker(cityName, listElem, filtersElem, badgeElem, isStopover = false, forceRefresh = false) {
  if (!listElem) return;
  listElem.innerHTML = `<div class="spots-loading-hint">Fetching stays in ${cityName} from StayingAPI, Google Places & OSM...</div>`;

  const activeTier = cityActiveStayTier[cityName] || "all";
  const hotels = await fetchCityHotels(cityName, activeTier, forceRefresh);

  if (filtersElem) {
    filtersElem.querySelectorAll("[data-stay-tier]").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.stayTier === activeTier);
      btn.onclick = (e) => {
        e.stopPropagation();
        cityActiveStayTier[cityName] = btn.dataset.stayTier;
        renderCityHotelPicker(cityName, listElem, filtersElem, badgeElem, isStopover, false);
      };
    });
  }

  if (!hotels || hotels.length === 0) {
    listElem.innerHTML = `<div class="spots-loading-hint">No accommodations found for "${cityName}". AI will automatically allocate verified stays.</div>`;
    return;
  }

  const selectedHotelId = userSelectedHotelsByCity[cityName];
  if (badgeElem) {
    badgeElem.textContent = selectedHotelId ? "1 Stay Selected" : "Auto-picked";
    badgeElem.classList.toggle("has-selected", !!selectedHotelId);
  }

  listElem.innerHTML = "";
  hotels.forEach(h => {
    const isSelected = selectedHotelId && (selectedHotelId === h.id || selectedHotelId === h.name);
    const card = document.createElement("div");
    card.className = `hospitality-item-card ${isSelected ? 'selected' : ''}`;
    const src = h.source || "curated";
    const srcBadgeClass = src === "staying_api" ? "source-staying" : src === "google_places" ? "source-google" : src === "osm" ? "source-osm" : "source-curated";
    const srcText = src === "staying_api" ? "StayingAPI" : src === "google_places" ? "Google Places" : src === "osm" ? "OSM" : "Curated";
    const amenitiesText = (h.amenities && h.amenities.length > 0) ? h.amenities.slice(0, 3).join(", ") : "Comfort stay";

    card.innerHTML = `
      <div class="hosp-info">
        <div class="hosp-name">${h.name}</div>
        <div class="hosp-sub">
          <span class="hosp-source-badge ${srcBadgeClass}">${srcText}</span>
          <span>★ ${h.rating || 4.3}</span>
          <span>• ${amenitiesText}</span>
        </div>
      </div>
      <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
        <span class="hosp-price">₹${(h.price_per_night || 2500).toLocaleString()}/n</span>
        <button type="button" class="hosp-select-btn">
          ${isSelected ? '✓ Picked' : 'Select'}
        </button>
      </div>
    `;

    card.addEventListener("click", () => {
      if (isSelected) {
        delete userSelectedHotelsByCity[cityName];
        if (userSelectedHotelObjsByCity) delete userSelectedHotelObjsByCity[cityName];
      } else {
        userSelectedHotelsByCity[cityName] = h.id;
        if (!userSelectedHotelObjsByCity) userSelectedHotelObjsByCity = {};
        userSelectedHotelObjsByCity[cityName] = h;
      }
      renderCityHotelPicker(cityName, listElem, filtersElem, badgeElem, isStopover, false);
      applySelectionOverridesLive();
      scheduleSelectionReplan();
    });

    listElem.appendChild(card);
  });
}

async function renderCityDiningPicker(cityName, listElem, filtersElem, badgeElem, isStopover = false, forceRefresh = false) {
  if (!listElem) return;
  listElem.innerHTML = `<div class="spots-loading-hint">Fetching dining & dhabas in ${cityName} from Google Places & OSM...</div>`;

  const activeCuisine = cityActiveCuisine[cityName] || "all";
  const restaurants = await fetchCityDining(cityName, activeCuisine, forceRefresh);

  if (filtersElem) {
    filtersElem.querySelectorAll("[data-cuisine]").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.cuisine === activeCuisine);
      btn.onclick = (e) => {
        e.stopPropagation();
        cityActiveCuisine[cityName] = btn.dataset.cuisine;
        renderCityDiningPicker(cityName, listElem, filtersElem, badgeElem, isStopover, false);
      };
    });
  }

  if (!restaurants || restaurants.length === 0) {
    listElem.innerHTML = `<div class="spots-loading-hint">No food spots found for "${cityName}". AI will automatically allocate authentic regional dhabas.</div>`;
    return;
  }

  if (!userSelectedDiningByCity[cityName]) {
    userSelectedDiningByCity[cityName] = new Set();
  }
  const selectedSet = userSelectedDiningByCity[cityName];
  if (badgeElem) {
    const count = selectedSet.size;
    badgeElem.textContent = `${count} Selected`;
    badgeElem.classList.toggle("has-selected", count > 0);
  }

  listElem.innerHTML = "";
  restaurants.forEach(r => {
    const isSelected = selectedSet.has(r.id) || selectedSet.has(r.name);
    const card = document.createElement("div");
    card.className = `hospitality-item-card dining-card ${isSelected ? 'selected' : ''}`;
    const src = r.source || "curated";
    const srcBadgeClass = src === "google_places" ? "source-google" : src === "osm" ? "source-osm" : "source-curated";
    const srcText = src === "google_places" ? "Google Places" : src === "osm" ? "OSM" : "Dhaba Curated";
    const dish = r.specialty ? `• ${r.specialty}` : `• ${(r.cuisine_type || 'local').replace('_', ' ')}`;

    let slotsRow = "";
    if (isSelected) {
      const slots = getDiningSlotsFor(cityName, r.id);
      slotsRow = `
        <div class="slot-toggle-row">
          <span class="slot-toggle-label">Applies to:</span>
          <button type="button" class="slot-toggle-btn ${slots.has('lunch') ? 'on' : ''}" data-slot="lunch">Lunch</button>
          <button type="button" class="slot-toggle-btn ${slots.has('dinner') ? 'on' : ''}" data-slot="dinner">Dinner</button>
        </div>
      `;
    }

    const cityDates = cityPlanDays(cityName);
    let daysRow = "";
    if (isSelected && cityDates.length > 0) {
      const pinMap = diningPinMapForRest(cityName, r.id);
      const dayChips = cityDates.map((d) => {
        const on = pinMap && pinMap.has(d.date) ? " on" : "";
        return `<button type="button" class="day-toggle-btn${on}" data-date="${d.date}" title="Day ${d.day_number} — ${d.date}">D${d.day_number}<span class="day-toggle-d">${formatDateShort(d.date)}</span></button>`;
      }).join("");
      daysRow = `
        <div class="day-toggle-row">
          <span class="day-toggle-label">On days:</span>
          <span class="day-toggle-hint">pick exact dates for this place</span>
          ${dayChips}
        </div>
      `;
    }

    card.innerHTML = `
      <div class="hosp-row">
        <div class="hosp-info">
          <div class="hosp-name">${r.name}</div>
          <div class="hosp-sub">
            <span class="hosp-source-badge ${srcBadgeClass}">${srcText}</span>
            <span>★ ${r.rating || 4.4}</span>
            <span style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${dish}</span>
          </div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
          <span class="hosp-price">~₹${(r.avg_cost_per_person || 250).toLocaleString()}/p</span>
          <button type="button" class="hosp-select-btn">
            ${isSelected ? '✓ Picked' : 'Select'}
          </button>
        </div>
      </div>
      ${slotsRow}
      ${daysRow}
    `;

    card.addEventListener("click", (e) => {
      if (e.target.closest(".slot-toggle-btn")) return;
      if (e.target.closest(".day-toggle-btn")) return;
      if (isSelected) {
        selectedSet.delete(r.id);
        selectedSet.delete(r.name);
        if (userSelectedDiningObjsByCity[cityName]) {
          userSelectedDiningObjsByCity[cityName].delete(r.id);
        }
        if (userSelectedDiningSlotsByCity[cityName]) {
          userSelectedDiningSlotsByCity[cityName].delete(r.id);
        }
        if (userSelectedDiningDaysByCity[cityName]) {
          userSelectedDiningDaysByCity[cityName].delete(r.id);
        }
      } else {
        selectedSet.add(r.id);
        if (!userSelectedDiningObjsByCity[cityName]) userSelectedDiningObjsByCity[cityName] = new Map();
        userSelectedDiningObjsByCity[cityName].set(r.id, r);
        if (!userSelectedDiningSlotsByCity[cityName]) userSelectedDiningSlotsByCity[cityName] = new Map();
        userSelectedDiningSlotsByCity[cityName].set(r.id, new Set(["lunch", "dinner"]));
      }
      renderCityDiningPicker(cityName, listElem, filtersElem, badgeElem, isStopover, false);
      applySelectionOverridesLive();
      scheduleSelectionReplan();
    });

    card.querySelectorAll(".slot-toggle-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const slot = btn.dataset.slot;
        const slots = getDiningSlotsFor(cityName, r.id);
        if (slots.has(slot)) slots.delete(slot); else slots.add(slot);
        renderCityDiningPicker(cityName, listElem, filtersElem, badgeElem, isStopover, false);
        applySelectionOverridesLive();
        scheduleSelectionReplan();
      });
    });

    card.querySelectorAll(".day-toggle-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const date = btn.dataset.date;
        if (!userSelectedDiningDaysByCity[cityName]) userSelectedDiningDaysByCity[cityName] = new Map();
        let dateMap = userSelectedDiningDaysByCity[cityName].get(r.id);
        if (!dateMap) {
          dateMap = new Map();
          userSelectedDiningDaysByCity[cityName].set(r.id, dateMap);
        }
        if (dateMap.has(date)) {
          dateMap.delete(date);
          if (dateMap.size === 0) userSelectedDiningDaysByCity[cityName].delete(r.id);
        } else {
          dateMap.set(date, new Set(getDiningSlotsFor(cityName, r.id)));
        }
        renderCityDiningPicker(cityName, listElem, filtersElem, badgeElem, isStopover, false);
        applySelectionOverridesLive();
        scheduleSelectionReplan();
      });
    });

    listElem.appendChild(card);
  });
}

function cloneJson(obj) {
  return obj ? JSON.parse(JSON.stringify(obj)) : obj;
}

function getDiningSlotsFor(city, restId) {
  if (!userSelectedDiningSlotsByCity[city]) userSelectedDiningSlotsByCity[city] = new Map();
  if (!userSelectedDiningSlotsByCity[city].has(restId)) {
    userSelectedDiningSlotsByCity[city].set(restId, new Set(["lunch", "dinner"]));
  }
  return userSelectedDiningSlotsByCity[city].get(restId);
}

function pickedDiningForCity(city) {
  const objs = userSelectedDiningObjsByCity[city];
  if (!objs || objs.size === 0) return [];
  const sel = userSelectedDiningByCity[city];
  const out = [];
  objs.forEach((r, id) => {
    if (sel && (sel.has(id) || sel.has(r && r.name))) out.push(r);
  });
  return out;
}

function diningOverridesForCity(city) {
  const ov = { lunch: [], dinner: [] };
  pickedDiningForCity(city).forEach((r) => {
    if (!r) return;
    const slots = userSelectedDiningSlotsByCity[city] && userSelectedDiningSlotsByCity[city].get(r.id)
      ? userSelectedDiningSlotsByCity[city].get(r.id)
      : new Set(["lunch", "dinner"]);
    if (slots.has("lunch")) ov.lunch.push(r);
    if (slots.has("dinner")) ov.dinner.push(r);
  });
  return ov;
}

function cityPlanDays(city) {
  const firstKey = currentPlan && currentPlan.options ? Object.keys(currentPlan.options)[0] : null;
  const v = firstKey ? currentPlan.options[firstKey] : null;
  if (!v) return [];
  return (v.days || []).filter((d) => (d.active_city || "").toLowerCase() === String(city).toLowerCase())
    .map((d) => ({ day_number: d.day_number, date: d.date }))
    .filter((d) => d.date);
}

function formatDateShort(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function diningPinMapForRest(city, restId) {
  if (!userSelectedDiningDaysByCity[city]) return null;
  if (!userSelectedDiningDaysByCity[city].has(restId)) return null;
  return userSelectedDiningDaysByCity[city].get(restId);
}

function diningPinsForDate(city, date) {
  const pins = { lunch: [], dinner: [] };
  const cityMap = userSelectedDiningDaysByCity[city];
  if (!cityMap || !date) return pins;
  const objs = userSelectedDiningObjsByCity[city];
  cityMap.forEach((dateMap, rid) => {
    const slotSet = dateMap.get(date);
    if (!slotSet || slotSet.size === 0) return;
    const rest = objs && objs.get(rid);
    if (!rest) return;
    if (slotSet.has("lunch")) pins.lunch.push(rest);
    if (slotSet.has("dinner")) pins.dinner.push(rest);
  });
  return pins;
}

function planStructureSignature() {
  const p = currentPlan.input_params || {};
  const firstKey = currentPlan.options ? Object.keys(currentPlan.options)[0] : null;
  const v0 = firstKey ? currentPlan.options[firstKey] : null;
  return JSON.stringify({
    o: p.origin,
    d: p.destination,
    dates: [p.start_date, p.end_date],
    stops: (p.stopovers || []).map(s => `${s.location}:${s.stay_days || ''}`).join('|'),
    days: v0 ? v0.days.map(x => x.active_city || '').join('|') : '',
    mode: p.travel_mode
  });
}

function snapshotPlanMeals() {
  if (!currentPlan) return;
  const sig = planStructureSignature();
  const hasDiningSelections = Object.keys(userSelectedDiningByCity || {}).some(
    (c) => userSelectedDiningByCity[c] && userSelectedDiningByCity[c].size > 0
  );
  const hasHotelSelections = Object.keys(userSelectedHotelsByCity || {}).length > 0;
  if ((hasDiningSelections || hasHotelSelections)
      && predefinedSelectionSnapshot && predefinedSelectionSnapshot.signature === sig) {
    return;
  }
  const fallbackCity = (currentPlan.input_params && currentPlan.input_params.destination) || "";
  const variants = {};
  for (const [key, v] of Object.entries(currentPlan.options || {})) {
    const days = (v.days || []).map((day) => {
      const stay = day.overnight_stay || null;
      return {
        date: day.date || "",
        active_city: day.active_city
          || (stay && stay.hotel && stay.hotel.location)
          || fallbackCity,
        foodCost: (day.day_cost_breakdown && day.day_cost_breakdown.food) || 0,
        stayCost: (day.day_cost_breakdown && day.day_cost_breakdown.stay) || 0,
        totalCost: day.total_day_cost || 0,
        meals: (day.meals || []).map((m) => ({
          meal_type: m.meal_type,
          estimated_cost: m.estimated_cost || 0,
          time_slot: m.time_slot || "",
          booked: m.booked || false,
          booking_id: m.booking_id || null,
          restaurant: cloneJson(m.restaurant)
        })),
        stayInfo: stay ? {
          hotel: cloneJson(stay.hotel),
          check_in_date: stay.check_in_date || "",
          nights: stay.nights || 1,
          booked: stay.booked || false,
          booking_id: stay.booking_id || null,
          totalCost: stay.total_cost || 0
        } : null
      };
    });
    variants[key] = {
      foodTotal: (v.cost_summary && v.cost_summary.food) || 0,
      stayTotal: (v.cost_summary && v.cost_summary.stays) || 0,
      totalCost: v.total_cost || 0,
      days
    };
  }
  predefinedSelectionSnapshot = { signature: sig, variants };
}

function applySelectionOverridesLive() {
  if (!currentPlan || !predefinedSelectionSnapshot) return;
  const partySize = (currentPlan.input_params && currentPlan.input_params.party_size) || 2;
  const counters = {};

  Object.keys(currentPlan.options || {}).forEach((key) => {
    const v = currentPlan.options[key];
    const snapV = predefinedSelectionSnapshot.variants[key];
    if (!v || !snapV) return;
    const daySnaps = snapV.days || [];

    const rot = (city, slot) => {
      if (!counters[city]) counters[city] = {};
      if (!counters[city][slot]) counters[city][slot] = 0;
      return counters[city][slot]++;
    };

    (v.days || []).forEach((day, idx) => {
      const snapDay = daySnaps[idx];
      if (!snapDay) return;
      const city = day.active_city || snapDay.active_city || "";
      const ov = city ? diningOverridesForCity(city) : { lunch: [], dinner: [] };
      const dayPins = city ? diningPinsForDate(city, day.date || snapDay.date) : { lunch: [], dinner: [] };

      (day.meals || []).forEach((meal) => {
        const snapMeal = (snapDay.meals || []).find((m) => m.meal_type === meal.meal_type) || snapDay.meals[0];
        if (!snapMeal) return;
        const isOverridable = meal.meal_type === "lunch" || meal.meal_type === "dinner";
        const pinnedList = dayPins[meal.meal_type] || [];
        const cwList = ov[meal.meal_type] || [];
        if (isOverridable && (pinnedList.length > 0 || cwList.length > 0)) {
          const rest = pinnedList.length > 0 ? pinnedList[0] : cwList[rot(city, meal.meal_type) % cwList.length];
          meal.restaurant = Object.assign(cloneJson(rest), { user_selected: true });
          meal.estimated_cost = Math.round((rest.avg_cost_per_person || 0) * partySize);
          meal.time_slot = snapMeal.time_slot || meal.time_slot;
        } else {
          meal.restaurant = cloneJson(snapMeal.restaurant);
          meal.estimated_cost = snapMeal.estimated_cost;
          meal.time_slot = snapMeal.time_slot;
        }
      });

      // Live stay override: user-selected hotel replaces the AI-picked hotel for this city
      if (day.overnight_stay) {
        const pickedHotel = userSelectedHotelObjsByCity && userSelectedHotelObjsByCity[city];
        if (pickedHotel) {
          const nights = day.overnight_stay.nights || 1;
          day.overnight_stay.hotel = Object.assign(cloneJson(pickedHotel), { user_selected: true });
          day.overnight_stay.total_cost = Math.round((pickedHotel.price_per_night || 0) * nights);
        } else if (snapDay.stayInfo) {
          const st = snapDay.stayInfo;
          day.overnight_stay.hotel = cloneJson(st.hotel);
          day.overnight_stay.check_in_date = st.check_in_date || day.overnight_stay.check_in_date;
          day.overnight_stay.nights = st.nights;
          day.overnight_stay.booked = st.booked;
          day.overnight_stay.booking_id = st.booking_id || null;
          day.overnight_stay.total_cost = st.totalCost;
        }
      }

      const dayFood = (day.meals || []).reduce((sum, m) => sum + (m.estimated_cost || 0), 0);
      const dayStay = (day.overnight_stay ? (day.overnight_stay.total_cost || 0) : 0);
      if (day.day_cost_breakdown) {
        day.day_cost_breakdown.food = Math.round(dayFood);
        day.day_cost_breakdown.stay = Math.round(dayStay);
      }
      day.total_day_cost = Math.round(
        snapDay.totalCost - (snapDay.foodCost || 0) - (snapDay.stayCost || 0) + dayFood + dayStay
      );
    });

    const newFoodTotal = (v.days || []).reduce(
      (sum, d) => sum + (d.meals || []).reduce((s, m) => s + (m.estimated_cost || 0), 0), 0
    );
    const newStayTotal = (v.days || []).reduce(
      (sum, d) => sum + (d.overnight_stay ? (d.overnight_stay.total_cost || 0) : 0), 0
    );
    if (v.cost_summary) {
      v.cost_summary.food = Math.round(newFoodTotal);
      v.cost_summary.stays = Math.round(newStayTotal);
    }
    v.total_cost = Math.round(
      snapV.totalCost - (snapV.foodTotal || 0) - (snapV.stayTotal || 0) + newFoodTotal + newStayTotal
    );
  });

  renderParetoCards();
  const variant = currentPlan.options[activeVariantKey];
  if (variant) {
    renderTimeline(variant);
    renderBudgetAudit(variant);
  }
}

function scheduleSelectionReplan() {
  clearTimeout(selectionReplanTimer);
  selectionReplanTimer = setTimeout(() => {
    triggerPlanning();
  }, 500);
}

function updateDeadlineDisplay() {
  const startVal = document.getElementById("startDateInput")?.value;
  const endVal = document.getElementById("endDateInput")?.value;
  if (!startVal || !endVal) return;

  const d1 = new Date(startVal);
  const d2 = new Date(endVal);
  const diffDays = Math.max(1, Math.round((d2 - d1) / (1000 * 60 * 60 * 24)) + 1);

  const badge = document.getElementById("deadlineDaysVal");
  if (badge) {
    badge.textContent = `${diffDays} Day${diffDays > 1 ? 's' : ''}`;
  }
}

function updateCorridorSuggestions() {
  const orig = (document.getElementById("originInput")?.value || "").trim().toLowerCase();
  const dest = (document.getElementById("destinationInput")?.value || "").trim().toLowerCase();
  const container = document.getElementById("suggestionChips");
  if (!container) return;

  const corridorMap = {
    "delhi-jaipur": ["Neemrana", "Behror", "Alwar", "Shahpura"],
    "jaipur-delhi": ["Shahpura", "Behror", "Neemrana", "Alwar"],
    "delhi-agra": ["Mathura", "Vrindavan", "Fatehpur Sikri"],
    "agra-delhi": ["Vrindavan", "Mathura", "Faridabad"],
    "mumbai-goa": ["Pune", "Lonavala", "Satara", "Kolhapur"],
    "goa-mumbai": ["Kolhapur", "Satara", "Lonavala", "Pune"],
    "bangalore-coorg": ["Mysore", "Mandya", "Hunsur", "Kushalnagar"],
    "coorg-bangalore": ["Kushalnagar", "Hunsur", "Mysore", "Mandya"],
    "chandigarh-manali": ["Bilaspur", "Mandi", "Kullu"],
    "delhi-rishikesh": ["Haridwar", "Roorkee"],
    "jaipur-udaipur": ["Ajmer", "Chittorgarh"],
    "pune-mahabaleshwar": ["Lonavala", "Wai", "Panchgani"]
  };

  const key = `${orig}-${dest}`;
  let suggestions = corridorMap[key];
  if (!suggestions) {
    suggestions = ["Neemrana", "Agra", "Mathura", "Pune", "Mysore", "Lonavala"]
      .filter(c => c.toLowerCase() !== orig && c.toLowerCase() !== dest)
      .slice(0, 4);
  }

  container.innerHTML = suggestions
    .map(city => `<button type="button" class="chip-suggestion" data-city="${city}">+ ${city}</button>`)
    .join("");

  container.querySelectorAll(".chip-suggestion").forEach(btn => {
    btn.addEventListener("click", () => {
      addStopoverRow(btn.dataset.city, "");
      triggerPlanning();
    });
  });
}

function addStopoverRow(city = "", stayDays = "") {
  const container = document.getElementById("stopoversContainer");
  if (!container) return;

  const stopoverUid = "st_" + Math.random().toString(36).substring(2, 8);
  const row = document.createElement("div");
  row.className = "stopover-node";
  row.innerHTML = `
    <div class="node-marker stopover-marker" title="Intermediate stopover">
      <span class="marker-dot"></span>
    </div>
    <div class="node-content">
      <div class="node-header">
        <label>In-Between Stop</label>
        <button type="button" class="btn-remove-stopover" title="Remove this stopover">&times;</button>
      </div>
      <div class="stopover-input-row">
        <input type="text" class="stopover-loc-input" list="citiesList" value="${city}" placeholder="In-between city or place..." required autocomplete="off" />
        <select class="stopover-select">
          <option value="" ${stayDays === "" ? "selected" : ""}>Not Sure (AI Best)</option>
          <option value="1" ${stayDays === "1" ? "selected" : ""}>Stay 1 Day</option>
          <option value="2" ${stayDays === "2" ? "selected" : ""}>Stay 2 Days</option>
          <option value="3" ${stayDays === "3" ? "selected" : ""}>Stay 3 Days</option>
          <option value="4" ${stayDays === "4" ? "selected" : ""}>Stay 4 Days</option>
          <option value="0" ${stayDays === "0" ? "selected" : ""}>En-Route (0 Days)</option>
        </select>
      </div>

      <!-- Nested Spot Picker for Stopover -->
      <div class="stopover-spot-picker">
        <button type="button" class="btn-toggle-stopover-spots" id="toggle_${stopoverUid}">
          <span>${I.landmark} Places in <strong class="stopover-city-label">${city || 'this Stop'}</strong></span>
          <span class="spot-picker-count-badge" id="badge_${stopoverUid}">0 Selected</span>
          <svg class="spot-picker-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="spot-picker-body" id="body_${stopoverUid}" style="display:none; margin-top:6px;">
          <div class="genre-filter-bar" id="genres_${stopoverUid}"></div>
          <div class="spot-selection-list" id="list_${stopoverUid}">
            <div class="spots-loading-hint">${city ? 'Click to load places...' : 'Enter a city name above'}</div>
          </div>
        </div>
      </div>

      <!-- Nested Stay Picker for Stopover -->
      <div class="stopover-spot-picker" style="margin-top:6px;">
        <button type="button" class="btn-toggle-stopover-spots" id="toggle_stay_${stopoverUid}">
          <span>${I.hotel} Stay in <strong class="stopover-city-label-stay">${city || 'this Stop'}</strong></span>
          <span class="spot-picker-count-badge" id="badge_stay_${stopoverUid}">Auto-picked</span>
          <svg class="spot-picker-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="spot-picker-body" id="body_stay_${stopoverUid}" style="display:none; margin-top:6px;">
          <div class="genre-filter-bar" id="filters_stay_${stopoverUid}">
            <button type="button" class="genre-filter-chip active" data-stay-tier="all">All Tiers</button>
            <button type="button" class="genre-filter-chip" data-stay-tier="standard_hotel">Standard</button>
            <button type="button" class="genre-filter-chip" data-stay-tier="budget_hostel">Hostel</button>
            <button type="button" class="genre-filter-chip" data-stay-tier="boutique_resort">Resort</button>
          </div>
          <div class="stay-selection-list" id="list_stay_${stopoverUid}">
            <div class="spots-loading-hint">${city ? 'Click to load stays...' : 'Enter a city name above'}</div>
          </div>
        </div>
      </div>

      <!-- Nested Dining Picker for Stopover -->
      <div class="stopover-spot-picker" style="margin-top:6px;">
        <button type="button" class="btn-toggle-stopover-spots" id="toggle_dining_${stopoverUid}">
          <span>${I.dining} Food & Dhabas in <strong class="stopover-city-label-dining">${city || 'this Stop'}</strong></span>
          <span class="spot-picker-count-badge" id="badge_dining_${stopoverUid}">0 Selected</span>
          <svg class="spot-picker-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="spot-picker-body" id="body_dining_${stopoverUid}" style="display:none; margin-top:6px;">
          <div class="genre-filter-bar" id="filters_dining_${stopoverUid}">
            <button type="button" class="genre-filter-chip active" data-cuisine="all">All Food</button>
            <button type="button" class="genre-filter-chip" data-cuisine="roadside_dhaba">Dhabas</button>
            <button type="button" class="genre-filter-chip" data-cuisine="local_cuisine">Local</button>
            <button type="button" class="genre-filter-chip" data-cuisine="vegetarian">Veg</button>
          </div>
          <div class="dining-selection-list" id="list_dining_${stopoverUid}">
            <div class="spots-loading-hint">${city ? 'Click to load food places...' : 'Enter a city name above'}</div>
          </div>
        </div>
      </div>
    </div>
  `;

  const input = row.querySelector(".stopover-loc-input");
  const toggleBtn = row.querySelector(`#toggle_${stopoverUid}`);
  const bodyElem = row.querySelector(`#body_${stopoverUid}`);
  const listElem = row.querySelector(`#list_${stopoverUid}`);
  const genresElem = row.querySelector(`#genres_${stopoverUid}`);
  const badgeElem = row.querySelector(`#badge_${stopoverUid}`);
  const cityLabel = row.querySelector(".stopover-city-label");

  // Stay Picker Elements
  const toggleStayBtn = row.querySelector(`#toggle_stay_${stopoverUid}`);
  const bodyStayElem = row.querySelector(`#body_stay_${stopoverUid}`);
  const listStayElem = row.querySelector(`#list_stay_${stopoverUid}`);
  const filtersStayElem = row.querySelector(`#filters_stay_${stopoverUid}`);
  const badgeStayElem = row.querySelector(`#badge_stay_${stopoverUid}`);
  const cityLabelStay = row.querySelector(".stopover-city-label-stay");

  // Dining Picker Elements
  const toggleDiningBtn = row.querySelector(`#toggle_dining_${stopoverUid}`);
  const bodyDiningElem = row.querySelector(`#body_dining_${stopoverUid}`);
  const listDiningElem = row.querySelector(`#list_dining_${stopoverUid}`);
  const filtersDiningElem = row.querySelector(`#filters_dining_${stopoverUid}`);
  const badgeDiningElem = row.querySelector(`#badge_dining_${stopoverUid}`);
  const cityLabelDining = row.querySelector(".stopover-city-label-dining");

  toggleBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isVisible = bodyElem.style.display === "block";
    bodyElem.style.display = isVisible ? "none" : "block";
    toggleBtn.classList.toggle("open", !isVisible);
    if (!isVisible) {
      const curCity = input.value.trim();
      if (curCity) {
        renderCitySpotPicker(curCity, listElem, genresElem, badgeElem, true, false);
      }
    }
  });

  toggleStayBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isVisible = bodyStayElem.style.display === "block";
    bodyStayElem.style.display = isVisible ? "none" : "block";
    toggleStayBtn.classList.toggle("open", !isVisible);
    if (!isVisible) {
      const curCity = input.value.trim();
      if (curCity) {
        renderCityHotelPicker(curCity, listStayElem, filtersStayElem, badgeStayElem, true, false);
      }
    }
  });

  toggleDiningBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isVisible = bodyDiningElem.style.display === "block";
    bodyDiningElem.style.display = isVisible ? "none" : "block";
    toggleDiningBtn.classList.toggle("open", !isVisible);
    if (!isVisible) {
      const curCity = input.value.trim();
      if (curCity) {
        renderCityDiningPicker(curCity, listDiningElem, filtersDiningElem, badgeDiningElem, true, false);
      }
    }
  });

  input.addEventListener("change", () => {
    const curCity = input.value.trim();
    if (cityLabel) cityLabel.textContent = curCity || 'this Stop';
    if (cityLabelStay) cityLabelStay.textContent = curCity || 'this Stop';
    if (cityLabelDining) cityLabelDining.textContent = curCity || 'this Stop';
    if (bodyElem.style.display === "block" && curCity) {
      renderCitySpotPicker(curCity, listElem, genresElem, badgeElem, true, false);
    }
    if (bodyStayElem.style.display === "block" && curCity) {
      renderCityHotelPicker(curCity, listStayElem, filtersStayElem, badgeStayElem, true, false);
    }
    if (bodyDiningElem.style.display === "block" && curCity) {
      renderCityDiningPicker(curCity, listDiningElem, filtersDiningElem, badgeDiningElem, true, false);
    }
    triggerPlanning();
  });

  row.querySelector(".btn-remove-stopover").addEventListener("click", () => {
    const curCity = input.value.trim();
    if (curCity) {
      if (userSelectedSpotsByCity[curCity]) delete userSelectedSpotsByCity[curCity];
      if (userSelectedHotelsByCity[curCity]) delete userSelectedHotelsByCity[curCity];
      if (userSelectedDiningByCity[curCity]) delete userSelectedDiningByCity[curCity];
    }
    row.remove();
    triggerPlanning();
  });

  row.querySelector(".stopover-select").addEventListener("change", () => {
    triggerPlanning();
  });

  container.appendChild(row);
  if (!city) input.focus();
}

function startMapPicking(target) {
  mapPickingTarget = target;

  // Switch to map tab
  const mapTabBtn = document.querySelector('.tab-btn[data-tab="tab-map"]');
  if (mapTabBtn) mapTabBtn.click();

  const banner = document.getElementById("mapPickerBanner");
  const targetLabel = document.getElementById("mapPickerTargetLabel");
  if (banner && targetLabel) {
    targetLabel.textContent = target === "origin" ? "Origin" : "Destination";
    banner.style.display = "flex";
  }

  const mapContainer = document.getElementById("leafletMap");
  if (mapContainer) mapContainer.classList.add("map-picking-active");

  const origBtn = document.getElementById("pickOriginMapBtn");
  const destBtn = document.getElementById("pickDestMapBtn");
  if (origBtn) origBtn.classList.toggle("active", target === "origin");
  if (destBtn) destBtn.classList.toggle("active", target === "destination");
}

function stopMapPicking() {
  mapPickingTarget = null;
  const banner = document.getElementById("mapPickerBanner");
  if (banner) banner.style.display = "none";

  const mapContainer = document.getElementById("leafletMap");
  if (mapContainer) mapContainer.classList.remove("map-picking-active");

  const origBtn = document.getElementById("pickOriginMapBtn");
  const destBtn = document.getElementById("pickDestMapBtn");
  if (origBtn) origBtn.classList.remove("active");
  if (destBtn) destBtn.classList.remove("active");
}

function findNearestCity(lat, lon) {
  if (!window.cityCatalog || window.cityCatalog.length === 0) return null;
  let nearest = null;
  let minD = Infinity;
  for (const c of window.cityCatalog) {
    const d = Math.hypot(c.lat - lat, c.lon - lon);
    if (d < minD) {
      minD = d;
      nearest = c;
    }
  }
  if (minD < 1.6 && nearest) return nearest;
  return null;
}

function downloadCalendarIcs() {
  if (!currentPlan) {
    alert("Please generate an itinerary first!");
    return;
  }
  const url = `/api/plan/${currentPlan.plan_id}/export/ics?variant=${activeVariantKey}`;
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `safarana_${currentPlan.plan_id.toLowerCase()}_${activeVariantKey}.ics`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function loadCities() {
  try {
    const res = await fetch("/api/cities");
    const data = await res.json();
    window.cityCatalog = data.cities || [];

    // Dynamically populate the datalist for both Origin and Destination
    const datalist = document.getElementById("citiesList");
    if (datalist) {
      datalist.innerHTML = "";
      window.cityCatalog.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.name;
        opt.label = `${c.state} • ${c.category}`;
        datalist.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Failed to load cities catalog:", err);
  }
}

async function triggerPlanning() {
  const origin = document.getElementById("originInput").value.trim();
  const destination = document.getElementById("destinationInput").value.trim();

  if (!origin || !destination) {
    alert("Please enter or select both an Origin and Destination city.");
    return;
  }

  if (origin.toLowerCase() === destination.toLowerCase()) {
    alert("Origin and Destination must be different cities! Please choose two distinct locations.");
    return;
  }

  const submitBtn = document.getElementById("planSubmitBtn");
  submitBtn.disabled = true;
  submitBtn.querySelector(".btn-text").textContent = "Planning your journey...";

  const selectedInterests = Array.from(
    document.querySelectorAll("input[name='interests']:checked")
  ).map((cb) => cb.value);

  // Extract all user-selected in-between stopovers
  const stopovers = [];
  document.querySelectorAll(".stopover-node").forEach((node) => {
    const locInput = node.querySelector(".stopover-loc-input");
    const durSelect = node.querySelector(".stopover-select");
    const loc = locInput ? locInput.value.trim() : "";
    if (loc) {
      const durVal = durSelect ? durSelect.value : "";
      const selectedForStop = userSelectedSpotsByCity[loc] ? Array.from(userSelectedSpotsByCity[loc]) : [];
      const selectedDiningForStop = userSelectedDiningByCity[loc] ? Array.from(userSelectedDiningByCity[loc]) : [];
      stopovers.push({
        location: loc,
        stay_days: durVal === "" ? null : parseInt(durVal, 10),
        selected_places: selectedForStop,
        selected_hotel_id: userSelectedHotelsByCity[loc] || null,
        selected_restaurant_ids: selectedDiningForStop
      });
    }
  });

  const selectedForDest = userSelectedSpotsByCity[destination] ? Array.from(userSelectedSpotsByCity[destination]) : [];
  const serializedPlacesByCity = {};
  for (const [c, setVal] of Object.entries(userSelectedSpotsByCity)) {
    if (setVal && setVal.size > 0) {
      serializedPlacesByCity[c] = Array.from(setVal);
    }
  }

  const serializedDiningByCity = {};
  const serializedDiningSlotsByCity = {};
  const serializedDiningDaysByCity = {};
  for (const [c, setVal] of Object.entries(userSelectedDiningByCity)) {
    if (setVal && setVal.size > 0) {
      serializedDiningByCity[c] = Array.from(setVal);
      const slotMap = {};
      setVal.forEach((id) => {
        const slots = userSelectedDiningSlotsByCity[c] && userSelectedDiningSlotsByCity[c].get(id);
        slotMap[id] = slots ? Array.from(slots) : ["lunch", "dinner"];
      });
      serializedDiningSlotsByCity[c] = slotMap;
    }
    const cityDaysMap = userSelectedDiningDaysByCity[c];
    if (cityDaysMap && cityDaysMap.size > 0) {
      const byRest = {};
      cityDaysMap.forEach((dateMap, rid) => {
        if (!dateMap || dateMap.size === 0) return;
        const byDate = {};
        dateMap.forEach((slotSet, date) => {
          byDate[date] = Array.from(slotSet);
        });
        byRest[rid] = byDate;
      });
      if (Object.keys(byRest).length > 0) serializedDiningDaysByCity[c] = byRest;
    }
  }

  const payload = {
    origin: origin,
    destination: destination,
    stopovers: stopovers,
    selected_places: selectedForDest,
    places_by_city: serializedPlacesByCity,
    budget: parseFloat(document.getElementById("budgetInput").value) || 15000,
    start_date: document.getElementById("startDateInput").value,
    end_date: document.getElementById("endDateInput").value,
    travel_mode: document.getElementById("travelModeInput").value,
    leg_modes: currentLegModes,
    return_travel_mode: currentReturnMode || document.getElementById("travelModeInput").value,
    selected_trains: currentSelectedTrains,
    return_train_number: currentReturnTrain,
    selected_flights: currentSelectedFlights,
    return_flight_number: currentReturnFlight,
    selected_hotel_id: userSelectedHotelsByCity[destination] || null,
    selected_hotels_by_city: userSelectedHotelsByCity,
    selected_restaurant_ids: Array.from(userSelectedDiningByCity[destination] || []),
    selected_dining_by_city: serializedDiningByCity,
    selected_dining_slots_by_city: serializedDiningSlotsByCity,
    selected_dining_days_by_city: serializedDiningDaysByCity,
    interests: selectedInterests.length > 0 ? selectedInterests : ["heritage", "food"],
    food_preference: document.getElementById("foodPrefInput").value,
    stay_preference: document.getElementById("stayPrefInput").value,
    party_size: parseInt(document.getElementById("partySizeInput").value, 10) || 2,
    start_time_of_day: document.getElementById("startTimeInput").value || "07:30",
  };

  try {
    const res = await fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error("Planning failed");
    currentPlan = await res.json();
    renderAllViews();
  } catch (err) {
    alert("Error generating trip plan: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector(".btn-text").textContent = "Generate Optimized Itineraries";
  }
}

function renderAllViews() {
  if (!currentPlan) return;
  renderParetoCards();
  renderLegModeSelectors();
  renderActiveVariant();
  renderAgentTrace();
  snapshotPlanMeals();
}

function renderLegModeSelectors() {
  const container = document.getElementById("legSelectorsList");
  const returnContainer = document.getElementById("returnLegContainer");
  if (!container) return;
  container.innerHTML = "";
  if (returnContainer) returnContainer.innerHTML = "";

  const legs = (currentPlan && currentPlan.route && currentPlan.route.legs) ? currentPlan.route.legs : [];
  const parentContainer = document.getElementById("legModesContainer");

  if (legs.length === 0) {
    if (parentContainer) parentContainer.style.display = "none";
    return;
  }

  if (parentContainer) parentContainer.style.display = "flex";

  const partySize = (currentPlan && currentPlan.input_params && currentPlan.input_params.party_size) || 1;

  legs.forEach((leg, legIdx) => {
    const card = document.createElement("div");
    card.className = "leg-mode-card";
    card.dataset.legIndex = legIdx;

    const selectedMode = currentLegModes[String(legIdx)] || leg.selected_mode || "driving";
    currentLegModes[String(legIdx)] = selectedMode;

    const availableModes = leg.available_modes || [];

    const modeLabels = {
      driving: { icon: I.car, name: "Car", tip: "Self-Drive / Car" },
      train: { icon: I.train, name: "Train", tip: "Express Rail" },
      flight: { icon: I.flight, name: "Flight", tip: "Domestic Flight" },
      bus: { icon: I.bus, name: "Bus", tip: "Highway Bus" },
      shared_cab: { icon: I.cab, name: "Shared Cab", tip: "Shared Cab" },
    };

    let modeButtonsHtml = "";
    if (availableModes.length > 0) {
      modeButtonsHtml = availableModes.map(opt => {
        const info = modeLabels[opt.mode] || { icon: I.car, name: opt.mode, tip: opt.mode };
        const isActive = opt.mode === selectedMode;
        return `
          <button type="button" class="mode-choice-btn ${isActive ? 'active' : ''}" data-leg="${legIdx}" data-mode="${opt.mode}" title="${opt.description}">
            <div class="mode-choice-top">
              <span class="name">${info.icon} ${info.name}</span>
              <span class="mode-choice-cost">₹${opt.total_cost.toLocaleString()}</span>
            </div>
            <div class="mode-choice-meta">
              <span>~${opt.buffered_duration_hours}h</span>
              <span>${partySize > 1 && opt.ticket_cost_per_person > 0 ? `₹${opt.ticket_cost_per_person}/p` : ''}</span>
            </div>
          </button>
        `;
      }).join("");
    } else {
      ["driving", "train", "flight", "bus", "shared_cab"].forEach(m => {
        const info = modeLabels[m];
        const isActive = m === selectedMode;
        modeButtonsHtml += `
          <button type="button" class="mode-choice-btn ${isActive ? 'active' : ''}" data-leg="${legIdx}" data-mode="${m}">
            <div class="mode-choice-top">
              <span class="name">${info.icon} ${info.name}</span>
            </div>
          </button>
        `;
      });
    }

    const selectedOpt = availableModes.find(o => o.mode === selectedMode);
    let metaDetailsHtml = "";
    if (selectedOpt && selectedMode === "flight") {
      const activeFlightNum = currentSelectedFlights[String(legIdx)] || leg.flight_number || selectedOpt.flight_number;
      const availFlights = leg.available_flights || selectedOpt.available_flights || [];
      const curFlight = availFlights.find(f => String(f.flight_number) === String(activeFlightNum)) || {
        flight_number: activeFlightNum || leg.flight_number || "6E-2381",
        airline: leg.airline || selectedOpt.airline || "IndiGo",
        airline_code: leg.airline_code || selectedOpt.airline_code || "6E",
        departure: leg.departure_time || selectedOpt.departure_time || "09:30",
        arrival: leg.arrival_time || selectedOpt.arrival_time || "10:45",
        duration: `${leg.buffered_duration_hours || 3.2} hrs`,
        cabin_class: leg.cabin_class || "Economy",
        baggage_allowance: leg.baggage_allowance || "15kg check-in + 7kg cabin",
        fare: selectedOpt.ticket_cost_per_person || leg.ticket_cost || 3450
      };

      let flightSelectorHtml = "";
      if (availFlights.length > 0) {
        flightSelectorHtml = `
          <div class="flight-selector-section">
            <div class="flight-selector-header">
              <span>${I.flight} <strong>Select Flight (${availFlights.length} commercial flights available):</strong></span>
              <span class="badge-live-flight">● Live Domestic Schedules</span>
            </div>
            <div class="flight-pills-scroll">
              ${availFlights.map(f => {
                const isCur = String(f.flight_number) === String(curFlight.flight_number);
                const seatsCount = f.seats_available || 18;
                const seatClass = seatsCount < 8 ? 'low' : '';
                return `
                  <button type="button" class="flight-pill-btn ${isCur ? 'active' : ''}" data-leg="${legIdx}" data-flight="${f.flight_number}">
                    <div class="flight-pill-top">
                      <span class="flight-num">${f.flight_number}</span>
                      <span class="flight-times">${f.departure} ➔ ${f.arrival}</span>
                    </div>
                    <div class="flight-pill-airline">
                      <span>${f.airline}</span>
                      <span class="flight-fare">₹${(f.fare || 3200).toLocaleString()}</span>
                    </div>
                    <div class="flight-pill-meta">
                      <span>${I.timer} ${f.duration || '1h 15m'}</span>
                      <span class="flight-seats-badge ${seatClass}">${dotOn} ${seatsCount} Seats</span>
                    </div>
                  </button>
                `;
              }).join("")}
            </div>
          </div>
        `;
      }

      metaDetailsHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.flight}</span>
            <span><strong>Flight:</strong> ${curFlight.airline} (${curFlight.flight_number}) &bull; Dep: <strong>${curFlight.departure}</strong>, Arr: <strong>${curFlight.arrival}</strong></span>
            <span class="badge-tag badge-open" style="background:#dcfce7; color:#166534; font-weight:700;">${dotOn} On Time & Verified</span>
            <span class="badge-tag" style="background:#fef3c7; color:#92400e; font-weight:600;">${I.seat} ${curFlight.cabin_class || 'Economy'} Class</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.flight}</span>
            <span><strong>Route:</strong> ${leg.departure_hub || selectedOpt.departure_hub || (leg.from_place ? leg.from_place + ' Airport' : 'Departure')} ${curFlight.flight_number} ➔ ${leg.arrival_hub || selectedOpt.arrival_hub || (leg.to_place ? leg.to_place + ' Airport' : 'Arrival')} ${curFlight.flight_number}</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.cab}</span>
            <span><strong>Feeder & Buffers:</strong> 1h 45m Terminal Security + Baggage Deboarding + Cab Feeder Included</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.luggage}</span>
            <span style="font-size:0.75rem; color:#475569;"><strong>Baggage:</strong> ${curFlight.baggage_allowance || '15kg Check-in + 7kg Cabin Baggage'}</span>
          </div>
        </div>
        ${flightSelectorHtml}
      `;
    } else if (selectedOpt && selectedMode === "train") {
      const activeTrainNum = currentSelectedTrains[String(legIdx)] || leg.train_number || selectedOpt.train_number;
      const availTrains = leg.available_trains || selectedOpt.available_trains || [];
      const curTrain = availTrains.find(t => String(t.number) === String(activeTrainNum)) || {
        number: activeTrainNum || leg.train_number || "",
        name: leg.train_name || selectedOpt.train_name || "Express Train",
        departure: leg.departure_time || selectedOpt.departure_time || "--:--",
        arrival: leg.arrival_time || selectedOpt.arrival_time || "--:--",
        duration: `${leg.buffered_duration_hours || 4} hrs`
      };

      let trainSelectorHtml = "";
      if (availTrains.length > 0) {
        trainSelectorHtml = `
          <div class="train-selector-section">
            <div class="train-selector-header">
              <span>${I.train} <strong>Select Train (${availTrains.length} direct trains via RailRadar):</strong></span>
              <span class="badge-live-rail">● Live IRCTC API</span>
            </div>
            <div class="train-pills-scroll">
              ${availTrains.map(t => {
                const isCur = String(t.number) === String(curTrain.number);
                const seatsSnippet = (t.seat_status && t.seat_status.length > 0)
                  ? `<div class="train-pill-seats">${t.seat_status.slice(0, 3).map(s => `<span class="seat-badge-mini ${s.badge}">${s.class_code}: ${s.status_code}</span>`).join('')}</div>`
                  : '';
                return `
                  <button type="button" class="train-pill-btn ${isCur ? 'active' : ''}" data-leg="${legIdx}" data-train="${t.number}">
                    <div class="train-pill-top">
                      <span class="train-num">#${t.number}</span>
                      <span class="train-times">${t.departure} ➔ ${t.arrival}</span>
                    </div>
                    <div class="train-pill-name" title="${t.name}">${t.name}</div>
                    <div class="train-pill-meta">
                      <span>${I.timer} ${t.duration || ''}</span>
                      <span>${t.type || 'Express'}</span>
                    </div>
                    ${seatsSnippet}
                  </button>
                `;
              }).join("")}
            </div>
          </div>
        `;
      }

      const liveInfo = curTrain.live_status || {};
      const liveDelay = liveInfo.delay_minutes || 0;
      const liveBadge = liveDelay > 0
        ? `<span class="badge-tag badge-delay" style="background:#fee2e2; color:#991b1b; font-weight:700;">${dotAlarm} Delayed ${liveDelay}m</span>`
        : `<span class="badge-tag badge-open" style="background:#dcfce7; color:#166534; font-weight:700;">${dotOn} On Time</span>`;
      const curStation = liveInfo.current_station ? ` &bull; At: <strong>${liveInfo.current_station}</strong>` : '';

      const fareSrc = selectedOpt.fare_source;
      const fareBadge = (fareSrc === 'google_maps')
        ? `<span class="badge-tag gmaps-fare-badge">${I.globe} Google Maps Transit Fare</span>`
        : `<span class="badge-tag fare-calc-badge">${I.lightbulb} Calibrated Fare</span>`;

      const seats = curTrain.seat_status || [];
      const seatBadgesHtml = (seats && seats.length > 0)
        ? `
          <div class="meta-row seat-status-row">
            <span class="icon">${I.seat}</span>
            <div class="seat-badges-container">
              <span class="seat-row-label"><strong>Seat Status:</strong></span>
              ${seats.map(s => `
                <span class="seat-badge ${s.badge}" title="${s.class_name} — ₹${s.fare} (${s.confirmation_chance || 'GN Quota'})">
                  <strong>${s.class_code}</strong>: ${s.status_code} <span class="seat-fare">₹${s.fare}</span>
                </span>
              `).join("")}
            </div>
          </div>
        ` : '';

      const coachPosHtml = curTrain.coach_position
        ? `
          <div class="meta-row">
            <span class="icon">${I.train}</span>
            <span style="font-size:0.75rem; color:#475569;"><strong>Coach Composition:</strong> <code class="coach-pos-code">${curTrain.coach_position}</code></span>
          </div>
        ` : '';

      const haltsCount = curTrain.route_stops ? curTrain.route_stops.filter(s => s.is_halt).length : (curTrain.halts || 5);
      const timetableBtnHtml = `
        <div class="meta-row timetable-btn-row">
          <button type="button" class="btn-sm-action view-timetable-btn" data-train="${curTrain.number || curTrain.train_number}" data-name="${curTrain.name || curTrain.train_name}">
            ${I.clipboard} View Actual Route & Timetable (${haltsCount} Halts)
          </button>
        </div>
      `;

      metaDetailsHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.train}</span>
            <span><strong>Train:</strong> #${curTrain.number} ${curTrain.name} &bull; Dep: <strong>${curTrain.departure}</strong>, Arr: <strong>${curTrain.arrival}</strong></span>
            ${liveBadge}
            ${fareBadge}
          </div>
          <div class="meta-row">
            <span class="icon">${I.station}</span>
            <span><strong>Stations:</strong> ${selectedOpt.departure_hub} ➔ ${selectedOpt.arrival_hub}${curStation}</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.cab}</span>
            <span><strong>Feeder:</strong> ${selectedOpt.local_vehicle_type} (₹${selectedOpt.local_shared_transit_cost || 0} included)</span>
          </div>
          ${seatBadgesHtml}
          ${coachPosHtml}
          ${timetableBtnHtml}
        </div>
        ${trainSelectorHtml}
      `;
    } else if (selectedOpt && (selectedMode === "bus" || selectedMode === "shared_cab")) {
      const fareSrc = selectedOpt.fare_source;
      const fareBadge = (fareSrc === 'google_maps')
        ? `<span class="badge-tag gmaps-fare-badge">${I.globe} Google Maps Transit</span>`
        : `<span class="badge-tag fare-calc-badge">${I.lightbulb} Calibrated Fare</span>`;
      const breakdownText = selectedOpt.fare_breakdown ? (selectedOpt.fare_breakdown.description || '') : '';
      metaDetailsHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.station}</span>
            <span><strong>Hubs:</strong> ${selectedOpt.departure_hub} ➔ ${selectedOpt.arrival_hub}</span>
            ${fareBadge}
          </div>
          <div class="meta-row">
            <span class="icon">${I.cab}</span>
            <span><strong>Feeder:</strong> ${selectedOpt.local_vehicle_type} (₹${selectedOpt.local_shared_transit_cost || 0} included)</span>
          </div>
          ${breakdownText ? `<div class="meta-row"><span class="icon">${I.info}</span><span style="font-size:0.75rem; color:#64748b;">${breakdownText}</span></div>` : ''}
        </div>
      `;
    } else if (selectedOpt && selectedMode === "driving") {
      const fareSrc = selectedOpt.fare_source;
      const fareBadge = (fareSrc === 'google_maps')
        ? `<span class="badge-tag gmaps-fare-badge">${I.globe} Google Maps Routing</span>`
        : `<span class="badge-tag fare-calc-badge">${I.lightbulb} Fuel & Tolls</span>`;
      const breakdownText = selectedOpt.fare_breakdown ? (selectedOpt.fare_breakdown.description || '') : '';
      metaDetailsHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.route}</span>
            <span><strong>Route:</strong> Direct Door-to-Door via NH &bull; +18% Traffic Buffer</span>
            ${fareBadge}
          </div>
          ${breakdownText ? `<div class="meta-row"><span class="icon">${I.fuel}</span><span style="font-size:0.75rem; color:#475569;">${breakdownText}</span></div>` : ''}
        </div>
      `;
    }

    card.innerHTML = `
      <div class="leg-mode-card-header">
        <span class="leg-route-pill">
          <span>Leg ${legIdx + 1}:</span>
          <strong>${leg.from_place} ➔ ${leg.to_place}</strong>
        </span>
        <span class="leg-dist-badge">${leg.distance_km} km</span>
      </div>
      <div class="leg-mode-options-grid">
        ${modeButtonsHtml}
      </div>
      ${metaDetailsHtml}
    `;

    card.querySelectorAll(".mode-choice-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const leg = btn.dataset.leg;
        const mode = btn.dataset.mode;
        currentLegModes[String(leg)] = mode;
        triggerPlanning();
      });
    });

    card.querySelectorAll(".train-pill-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const leg = btn.dataset.leg;
        const trainNum = btn.dataset.train;
        currentSelectedTrains[String(leg)] = trainNum;
        triggerPlanning();
      });
    });

    card.querySelectorAll(".flight-pill-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const leg = btn.dataset.leg;
        const flightNum = btn.dataset.flight;
        currentSelectedFlights[String(leg)] = flightNum;
        triggerPlanning();
      });
    });

    container.appendChild(card);
  });

  // Dedicated Return Leg Card
  if (returnContainer && currentPlan.input_params) {
    const originCity = currentPlan.input_params.origin;
    const destCity = currentPlan.input_params.destination;
    const activeVariant = currentPlan.options[activeVariantKey] || currentPlan.options.balanced;
    const days = activeVariant ? activeVariant.days : [];
    const returnDay = (days.length > 1) ? days[days.length - 1] : null;
    const returnTransit = returnDay ? returnDay.transit_details : null;

    const returnSelectedMode = currentReturnMode || (returnTransit ? returnTransit.mode : (currentPlan.input_params.return_travel_mode || currentPlan.input_params.travel_mode || "driving"));
    currentReturnMode = returnSelectedMode;

    const returnCard = document.createElement("div");
    returnCard.className = "return-leg-card";

    const modeLabels = {
      driving: { icon: I.car, name: "Car", tip: "Self-Drive / Car via NH" },
      train: { icon: I.train, name: "Train", tip: "Return Express Rail" },
      flight: { icon: I.flight, name: "Flight", tip: "Return Domestic Flight" },
      bus: { icon: I.bus, name: "Bus", tip: "Return Highway Bus" },
      shared_cab: { icon: I.cab, name: "Shared Cab", tip: "Return Shared Cab / Shuttle" },
    };

    const modes = ["driving", "train", "flight", "bus", "shared_cab"];
    const modeButtonsHtml = modes.map(m => {
      const info = modeLabels[m];
      const isActive = m === returnSelectedMode;
      return `
        <button type="button" class="mode-choice-btn ${isActive ? 'active' : ''}" data-return-mode="${m}" title="${info.tip}">
          <div class="mode-choice-top">
            <span class="name">${info.icon} ${info.name}</span>
          </div>
        </button>
      `;
    }).join("");

    let metaHtml = "";
    if (returnTransit && returnSelectedMode === "flight") {
      const activeRetFlight = currentReturnFlight || returnTransit.flight_number;
      const retAvailFlights = returnTransit.available_flights || [];
      const curRetFlight = retAvailFlights.find(f => String(f.flight_number) === String(activeRetFlight)) || {
        flight_number: activeRetFlight || returnTransit.flight_number || "AI-492",
        airline: returnTransit.airline || "Air India",
        airline_code: returnTransit.airline_code || "AI",
        departure: returnTransit.departure_time || "17:30",
        arrival: returnTransit.arrival_time || "18:50",
        duration: `${returnTransit.duration_hours || 3.1} hrs`,
        cabin_class: returnTransit.cabin_class || "Economy",
        baggage_allowance: returnTransit.baggage_allowance || "15kg Check-in + 7kg Cabin",
        fare: returnTransit.ticket_cost || 3600
      };

      let retFlightSelectorHtml = "";
      if (retAvailFlights.length > 0) {
        retFlightSelectorHtml = `
          <div class="flight-selector-section">
            <div class="flight-selector-header">
              <span>${I.flight} <strong>Select Return Flight (${retAvailFlights.length} flights available):</strong></span>
              <span class="badge-live-flight">● Live Schedules</span>
            </div>
            <div class="flight-pills-scroll">
              ${retAvailFlights.map(f => {
                const isCur = String(f.flight_number) === String(curRetFlight.flight_number);
                const seatsCount = f.seats_available || 16;
                const seatClass = seatsCount < 8 ? 'low' : '';
                return `
                  <button type="button" class="flight-pill-btn ${isCur ? 'active' : ''}" data-return-flight="${f.flight_number}">
                    <div class="flight-pill-top">
                      <span class="flight-num">${f.flight_number}</span>
                      <span class="flight-times">${f.departure} ➔ ${f.arrival}</span>
                    </div>
                    <div class="flight-pill-airline">
                      <span>${f.airline}</span>
                      <span class="flight-fare">₹${(f.fare || 3200).toLocaleString()}</span>
                    </div>
                    <div class="flight-pill-meta">
                      <span>${I.timer} ${f.duration || '1h 20m'}</span>
                      <span class="flight-seats-badge ${seatClass}">${dotOn} ${seatsCount} Seats</span>
                    </div>
                  </button>
                `;
              }).join("")}
            </div>
          </div>
        `;
      }

      metaHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.flight}</span>
            <span><strong>Return Flight:</strong> ${curRetFlight.airline} (${curRetFlight.flight_number}) &bull; Dep: <strong>${curRetFlight.departure}</strong>, Arr: <strong>${curRetFlight.arrival}</strong></span>
            <span class="badge-tag badge-open" style="background:#dcfce7; color:#166534; font-weight:700;">${dotOn} Confirmed Airway</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.flight}</span>
            <span><strong>Route:</strong> ${returnTransit.departure_hub || destCity + ' Airport'} ${curRetFlight.flight_number} ➔ ${returnTransit.arrival_hub || originCity + ' Airport'} ${curRetFlight.flight_number}</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.cab}</span>
            <span><strong>Feeder & Buffers:</strong> Feeder Cab Drop + Security Buffers factored in schedule</span>
          </div>
        </div>
        ${retFlightSelectorHtml}
      `;
    } else if (returnTransit && returnSelectedMode === "train") {
      const activeRetNum = currentReturnTrain || returnTransit.train_number;
      const retAvail = returnTransit.available_trains || [];
      const curRetTrain = retAvail.find(t => String(t.number) === String(activeRetNum)) || {
        number: activeRetNum || returnTransit.train_number || "",
        name: returnTransit.train_name || "Return Express Train",
        departure: returnTransit.departure_time || "--:--",
        arrival: returnTransit.arrival_time || "--:--",
        duration: `${returnTransit.duration_hours || 4} hrs`
      };

      let retTrainSelectorHtml = "";
      if (retAvail.length > 0) {
        retTrainSelectorHtml = `
          <div class="train-selector-section">
            <div class="train-selector-header">
              <span>${I.train} <strong>Select Return Train (${retAvail.length} direct trains via RailRadar):</strong></span>
              <span class="badge-live-rail">● Live IRCTC API</span>
            </div>
            <div class="train-pills-scroll">
              ${retAvail.map(t => {
                const isCur = String(t.number) === String(curRetTrain.number);
                const seatsSnippet = (t.seat_status && t.seat_status.length > 0)
                  ? `<div class="train-pill-seats">${t.seat_status.slice(0, 3).map(s => `<span class="seat-badge-mini ${s.badge}">${s.class_code}: ${s.status_code}</span>`).join('')}</div>`
                  : '';
                return `
                  <button type="button" class="train-pill-btn ${isCur ? 'active' : ''}" data-return-train="${t.number}">
                    <div class="train-pill-top">
                      <span class="train-num">#${t.number}</span>
                      <span class="train-times">${t.departure} ➔ ${t.arrival}</span>
                    </div>
                    <div class="train-pill-name" title="${t.name}">${t.name}</div>
                    <div class="train-pill-meta">
                      <span>${I.timer} ${t.duration || ''}</span>
                      <span>${t.type || 'Express'}</span>
                    </div>
                    ${seatsSnippet}
                  </button>
                `;
              }).join("")}
            </div>
          </div>
        `;
      }

      const retLive = curRetTrain.live_status || {};
      const retDelay = retLive.delay_minutes || 0;
      const retLiveBadge = retDelay > 0
        ? `<span class="badge-tag badge-delay" style="background:#fee2e2; color:#991b1b; font-weight:700;">${dotAlarm} Delayed ${retDelay}m</span>`
        : `<span class="badge-tag badge-open" style="background:#dcfce7; color:#166534; font-weight:700;">${dotOn} On Time</span>`;

      const retFareSrc = returnTransit.fare_source;
      const retFareBadge = (retFareSrc === 'google_maps')
        ? `<span class="badge-tag gmaps-fare-badge">${I.globe} Google Maps Fare</span>`
        : `<span class="badge-tag fare-calc-badge">${I.lightbulb} Calibrated Fare</span>`;

      const retSeats = curRetTrain.seat_status || [];
      const retSeatBadgesHtml = (retSeats && retSeats.length > 0)
        ? `
          <div class="meta-row seat-status-row">
            <span class="icon">${I.seat}</span>
            <div class="seat-badges-container">
              <span class="seat-row-label"><strong>Seat Status:</strong></span>
              ${retSeats.map(s => `
                <span class="seat-badge ${s.badge}" title="${s.class_name} — ₹${s.fare} (${s.confirmation_chance || 'GN Quota'})">
                  <strong>${s.class_code}</strong>: ${s.status_code} <span class="seat-fare">₹${s.fare}</span>
                </span>
              `).join("")}
            </div>
          </div>
        ` : '';

      const retHaltsCount = curRetTrain.route_stops ? curRetTrain.route_stops.filter(s => s.is_halt).length : (curRetTrain.halts || 5);
      const retTimetableBtn = `
        <div class="meta-row timetable-btn-row">
          <button type="button" class="btn-sm-action view-timetable-btn" data-train="${curRetTrain.number}" data-name="${curRetTrain.name}">
            ${I.clipboard} View Actual Route & Timetable (${retHaltsCount} Halts)
          </button>
        </div>
      `;

      metaHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.train}</span>
            <span><strong>Return Train:</strong> #${curRetTrain.number} ${curRetTrain.name} &bull; Dep: <strong>${curRetTrain.departure}</strong>, Arr: <strong>${curRetTrain.arrival}</strong></span>
            ${retLiveBadge}
            ${retFareBadge}
          </div>
          <div class="meta-row">
            <span class="icon">${I.station}</span>
            <span><strong>Stations:</strong> ${returnTransit.departure_hub || destCity + ' Station'} ➔ ${returnTransit.arrival_hub || originCity + ' Station'}</span>
          </div>
          <div class="meta-row">
            <span class="icon">${I.cab}</span>
            <span><strong>Feeder:</strong> ${returnTransit.local_vehicle_type || 'Shared Auto'} (₹${returnTransit.local_transit_cost || 0} feeder included)</span>
          </div>
          ${retSeatBadgesHtml}
          ${retTimetableBtn}
        </div>
        ${retTrainSelectorHtml}
      `;
    } else if (returnTransit && (returnSelectedMode === "bus" || returnSelectedMode === "shared_cab")) {
      const retFareSrc = returnTransit.fare_source;
      const retFareBadge = (retFareSrc === 'google_maps')
        ? `<span class="badge-tag gmaps-fare-badge">${I.globe} Google Maps Fare</span>`
        : `<span class="badge-tag fare-calc-badge">${I.lightbulb} Calibrated Fare</span>`;
      metaHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.station}</span>
            <span><strong>Hubs:</strong> ${returnTransit.departure_hub || destCity + ' Station'} ➔ ${returnTransit.arrival_hub || originCity + ' Station'}</span>
            ${retFareBadge}
          </div>
          <div class="meta-row">
            <span class="icon">${I.cab}</span>
            <span><strong>Feeder:</strong> ${returnTransit.local_vehicle_type || 'Shared Auto'} (₹${returnTransit.local_transit_cost || 0} feeder included)</span>
          </div>
        </div>
      `;
    } else {
      metaHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">${I.route}</span>
            <span><strong>Route:</strong> Return via National Highway &bull; Door-to-Door</span>
          </div>
        </div>
      `;
    }

    const retDist = returnTransit ? returnTransit.distance_km : (currentPlan.route ? currentPlan.route.total_distance_km : 260);

    returnCard.innerHTML = `
      <div class="leg-mode-card-header">
        <span class="return-leg-title">
          <span>${I.swap} Return Leg:</span>
          <strong>${destCity} ➔ ${originCity}</strong>
        </span>
        <span class="leg-dist-badge">${retDist} km</span>
      </div>
      <div class="leg-mode-options-grid">
        ${modeButtonsHtml}
      </div>
      ${metaHtml}
    `;

    returnCard.querySelectorAll(".mode-choice-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const m = btn.dataset.returnMode;
        currentReturnMode = m;
        triggerPlanning();
      });
    });

    returnCard.querySelectorAll(".train-pill-btn").forEach(tBtn => {
      tBtn.addEventListener("click", () => {
        const trainNum = tBtn.dataset.returnTrain;
        currentReturnTrain = trainNum;
        triggerPlanning();
      });
    });

    returnCard.querySelectorAll(".flight-pill-btn").forEach(fBtn => {
      fBtn.addEventListener("click", () => {
        const flightNum = fBtn.dataset.returnFlight;
        currentReturnFlight = flightNum;
        triggerPlanning();
      });
    });

    returnContainer.appendChild(returnCard);
  }
}

function renderParetoCards() {
  const container = document.getElementById("variantCards");
  container.innerHTML = "";

  const variantDefs = [
    { key: "balanced", badge: "Recommended", badgeClass: "", title: "Balanced & Curated" },
    { key: "fastest", badge: "Direct Express", badgeClass: "v-fast", title: "Fastest / Direct" },
    { key: "cheapest", badge: "Max Savings", badgeClass: "v-cheap", title: "Budget Explorer" },
    { key: "scenic", badge: "Deep Immersion", badgeClass: "v-scenic", title: "Scenic & Explorer" },
  ];

  variantDefs.forEach((def) => {
    const v = currentPlan.options[def.key];
    if (!v) return;

    const card = document.createElement("div");
    card.className = `variant-card ${def.key === activeVariantKey ? "active" : ""}`;
    card.dataset.variant = def.key;
    card.innerHTML = `
      <div class="v-badge ${def.badgeClass}">${def.badge}</div>
      <h4>${v.variant_title || def.title}</h4>
      <div class="v-price">₹${v.total_cost.toLocaleString()} <span class="v-party">/ ${currentPlan.input_params.party_size} travelers</span></div>
      <div class="v-score">★ ${v.score} Score &bull; ${v.total_spots_visited} Sights</div>
      <div class="v-desc">${v.tagline}</div>
    `;

    card.addEventListener("click", () => {
      activeVariantKey = def.key;
      document.querySelectorAll(".variant-card").forEach((c) => c.classList.remove("active"));
      card.classList.add("active");
      renderActiveVariant();
    });

    container.appendChild(card);
  });
}

function renderActiveVariant() {
  const variant = currentPlan.options[activeVariantKey];
  if (!variant) return;

  renderTimeline(variant);
  renderMap(variant);
  renderBudgetAudit(variant);
}

function timeToMinutes(str) {
  const m = /(\d{1,2}):(\d{2})/.exec(str || "");
  if (m) return parseInt(m[1], 10) * 60 + parseInt(m[2], 10);
  return null;
}

function transitTimeKey(tDet) {
  const candidates = [];
  if (tDet && tDet.departure_time) candidates.push(tDet.departure_time);
  if (tDet && Array.isArray(tDet.steps)) {
    for (const st of tDet.steps) candidates.push(st.time);
  }
  for (const c of candidates) {
    const m = timeToMinutes(c);
    if (m !== null) return m;
  }
  return 5 * 60;
}

function renderTimeline(variant) {
  const dayPills = document.getElementById("dayFilterContainer");
  const meta = document.getElementById("timelineMeta");
  const timelineContainer = document.getElementById("itineraryTimeline");

  // Day selection pills
  dayPills.innerHTML = `<button class="day-pill ${activeDayFilter === "all" ? "active" : ""}" data-day="all">All Days (${variant.days.length})</button>`;
  variant.days.forEach((d) => {
    dayPills.innerHTML += `<button class="day-pill ${activeDayFilter == d.day_number ? "active" : ""}" data-day="${d.day_number}">Day ${d.day_number}</button>`;
  });

  dayPills.querySelectorAll(".day-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      activeDayFilter = pill.dataset.day;
      dayPills.querySelectorAll(".day-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      renderTimeline(variant);
    });
  });

  meta.innerHTML = `<span style="font-size:0.8rem; color:#64748b;">Total Route: <strong>${variant.total_distance_km} km</strong> &bull; Total Sights: <strong>${variant.total_spots_visited}</strong></span>`;

  timelineContainer.innerHTML = "";

  const filteredDays = activeDayFilter === "all" 
    ? variant.days 
    : variant.days.filter((d) => d.day_number == activeDayFilter);

  filteredDays.forEach((day) => {
    const dayHeader = document.createElement("div");
    dayHeader.style.cssText = "margin-top:10px; margin-bottom:6px; font-weight:800; font-size:1.05rem; color:#1e293b;";
    dayHeader.innerHTML = `${I.calendar} ${day.title} <span style="font-size:0.75rem; color:#64748b; font-weight:500;">(${day.date})</span>`;
    timelineContainer.appendChild(dayHeader);

    // Day weather forecast & packing banner
    if (day.weather) {
      const weatherBanner = document.createElement("div");
      weatherBanner.className = "day-weather-banner";
      
      const packingChipsHtml = (day.weather.clothing_packing_advice || [])
        .map((chip) => `<span class="packing-chip">${chip}</span>`)
        .join("");

      weatherBanner.innerHTML = `
        <div class="weather-header">
          <div class="weather-main">
            <div class="weather-icon-temp">
              <span>${weatherIcon(day.weather.icon)}</span>
              <span>${day.weather.temperature_celsius}°C</span>
            </div>
            <div class="weather-desc">${day.weather.condition}</div>
          </div>
          ${day.weather.risk_alert ? `<div class="weather-alert-badge">${I.alert} ${day.weather.risk_alert}</div>` : ""}
        </div>
        ${packingChipsHtml ? `
          <div class="weather-packing">
            <span class="packing-title">${I.luggage} Packing Advisory:</span>
            ${packingChipsHtml}
          </div>
        ` : ""}
      `;
      timelineContainer.appendChild(weatherBanner);
    }

    const daySteps = [];
    let orderIdx = 0;

    // Day transit notice
    if (day.transit_time_hours > 0 || day.transit_details) {
      const transitStep = document.createElement("div");
      transitStep.className = "timeline-step step-transit";

      const tDet = day.transit_details || {};
      const tMode = day.transit_mode || tDet.mode || "driving";
      const modeIcons = { flight: I.flight, train: I.train, bus: I.bus, shared_cab: I.cab, driving: I.car, local: I.cab };
      const modeNames = { flight: "Commercial Domestic Flight", train: "Intercity Express Train", bus: "Highway Express Bus", shared_cab: "Shared Outstation Cab", driving: "Highway Drive / Car", local: "Local City Transit" };
      const icon = modeIcons[tMode] || I.car;
      const modeTitle = tDet.mode_title || modeNames[tMode] || `${tMode.toUpperCase()} Transit`;

      let substepsHtml = "";
      if (tDet.steps && tDet.steps.length > 0) {
        substepsHtml = `
          <div class="transit-steps-box">
            <div style="font-size:0.75rem; font-weight:700; color:#475569; margin-bottom:2px;">Transit Steps & Local Transfers:</div>
            ${tDet.steps.map((st) => `
              <div class="transit-step-row">
                <div class="transit-step-left">
                  <span>${st.vehicle && st.vehicle.includes('Flight') ? I.flight : (st.vehicle === 'Shared Auto' ? I.cab : (st.vehicle === 'Express Train' ? I.train : (st.vehicle === 'Express Bus' ? I.bus : I.car)))}</span>
                  <span>${st.title}</span>
                </div>
                <div>
                  <span class="transit-step-time">${st.time ? st.time : ''}</span>
                  ${st.cost > 0 ? `<span class="transit-step-cost">₹${st.cost.toLocaleString()}</span>` : ''}
                </div>
              </div>
            `).join("")}
          </div>
        `;
      }

      // Mode switcher buttons inside timeline card for intercity days
      const isReturnDay = (day.day_number === variant.days.length && variant.days.length > 1);
      const isInterCity = (day.day_number === 1 || isReturnDay || day.title.includes("➔") || day.title.includes("Transit") || day.title.includes("Depart") || day.title.includes("Return"));
      const legIndexForDay = Math.max(0, day.day_number - 1);
      
      let switcherHtml = "";
      if (isInterCity) {
        const switcherLabel = isReturnDay ? "Switch Return Leg Mode:" : "Switch Mode for this Leg:";
        switcherHtml = `
          <div class="transit-switcher-inline">
            <span class="switcher-label">${switcherLabel}</span>
            <button type="button" class="switcher-btn ${tMode === 'driving' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="driving">${I.car} Car</button>
            <button type="button" class="switcher-btn ${tMode === 'train' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="train">${I.train} Train</button>
            <button type="button" class="switcher-btn ${tMode === 'flight' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="flight">${I.flight} Flight</button>
            <button type="button" class="switcher-btn ${tMode === 'bus' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="bus">${I.bus} Bus</button>
            <button type="button" class="switcher-btn ${tMode === 'shared_cab' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="shared_cab">${I.cab} Shared Cab</button>
          </div>
        `;
      }

      const delayText = tMode === "flight"
        ? `${I.timer} 1h 45m Security & Check-in Buffer + Feeder Included`
        : (tMode === "train" 
          ? `${I.timer} +12% Rail Signal Delay & 40m Station Buffer` 
          : (tMode === "bus" 
            ? `${I.timer} +22% Traffic Delay & 25m Terminal Buffer` 
            : (tMode === "shared_cab" 
              ? `${I.timer} +15% Traffic & Pickup Buffer` 
              : `${I.timer} +18% Traffic Delay Buffer Included`)));

      const hubsText = (tDet.departure_hub && tDet.arrival_hub) 
        ? `<span class="badge-tag badge-buffer">${I.station} ${tDet.departure_hub} ➔ ${tDet.arrival_hub}</span>` 
        : "";

      const localAutoBadge = (tDet.local_transit_cost && tDet.local_transit_cost > 0)
        ? `<span class="badge-tag badge-delay">${I.cab} Includes Feeder / Transfers (₹${tDet.local_transit_cost})</span>`
        : "";

      const ticketBadge = (tDet.ticket_cost && tDet.ticket_cost > 0)
        ? `<span class="badge-tag badge-open">${I.ticket} Tickets: ₹${tDet.ticket_cost}</span>`
        : "";

      const flightScheduleBadge = (tMode === "flight" && tDet.departure_time && tDet.arrival_time)
        ? `<span class="badge-tag badge-open" style="background:#e0f2fe; color:#0369a1; font-weight:700;">${I.flight} Dep: ${tDet.departure_time} ➔ Arr: ${tDet.arrival_time}</span>`
        : "";

      const liveFlightBadge = (tMode === "flight" && tDet.flight_number)
        ? `<span class="badge-tag badge-open" style="background:#f0fdf4; color:#15803d; font-weight:700;">${I.flight} ${tDet.airline || 'Flight'} #${tDet.flight_number}</span>`
        : "";

      const trainScheduleBadge = (tMode === "train" && tDet.departure_time && tDet.arrival_time)
        ? `<span class="badge-tag badge-open" style="background:#dbeafe; color:#1e40af; font-weight:700;">${I.train} Dep: ${tDet.departure_time} ➔ Arr: ${tDet.arrival_time}</span>`
        : "";

      const liveTrainBadge = (tMode === "train" && tDet.train_number)
        ? `<span class="badge-tag badge-open" style="background:#dcfce7; color:#166534; font-weight:700;">${dotOn} Train #${tDet.train_number}</span>`
        : "";

      const fareSrcBadge = (tDet.fare_source === "google_maps")
        ? `<span class="badge-tag gmaps-fare-badge">${I.globe} Google Maps Fare</span>`
        : `<span class="badge-tag fare-calc-badge">${I.lightbulb} Calibrated Fare</span>`;

      const tSeats = tDet.seat_status || [];
      const daySeatsBadge = (tSeats && tSeats.length > 0)
        ? `<div class="day-seat-pills" style="margin-top:6px; display:flex; flex-wrap:wrap; gap:4px;">
            ${tSeats.slice(0, 4).map(s => `<span class="seat-badge ${s.badge}" style="font-size:0.75rem; padding:2px 8px;">${s.class_code}: <strong>${s.status_code}</strong> (₹${s.fare})</span>`).join('')}
           </div>`
        : "";

      const tHalts = (tDet.route_stops && tDet.route_stops.length > 0)
        ? tDet.route_stops.filter(s => s.is_halt).length
        : (tDet.halts || 5);
      const dayTimetableBtn = (tMode === "train" && tDet.train_number)
        ? `<button type="button" class="btn-sm-action view-timetable-btn" data-train="${tDet.train_number}" data-name="${tDet.train_name || ''}" style="margin-top:6px; font-size:0.75rem;">
            ${I.clipboard} View Route & Timetable (${tHalts} Halts)
           </button>`
        : "";

      transitStep.innerHTML = `
        <div class="step-header">
          <div class="step-time">${icon} ${modeTitle} &bull; ~${day.transit_time_hours} hrs</div>
          <span class="badge-tag badge-cost">Transport: ₹${day.day_cost_breakdown.transport || 0}</span>
        </div>
        <div class="step-title">${tDet.from_place ? `${tDet.from_place} ➔ ${tDet.to_place}` : 'City Transit'}: ${day.transit_distance_km} km</div>
        <div class="step-badges">
          ${flightScheduleBadge}
          ${liveFlightBadge}
          ${trainScheduleBadge}
          ${liveTrainBadge}
          ${fareSrcBadge}
          <span class="badge-tag badge-open">${delayText}</span>
          ${hubsText}
          ${localAutoBadge}
          ${ticketBadge}
        </div>
        ${daySeatsBadge}
        ${dayTimetableBtn}
        ${substepsHtml}
        ${switcherHtml}
      `;

      transitStep.querySelectorAll(".switcher-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const isRet = btn.dataset.isReturn === "true";
          const m = btn.dataset.mode;
          if (isRet) {
            currentReturnMode = m;
          } else {
            const lIdx = btn.dataset.leg;
            currentLegModes[String(lIdx)] = m;
          }
          triggerPlanning();
        });
      });

      daySteps.push({ key: transitTimeKey(tDet), order: orderIdx++, node: transitStep });
    }

    // Activities & Meals
    day.activities.forEach((act) => {
      const isSelected = act.place.user_selected;
      const step = document.createElement("div");
      step.className = `timeline-step ${isSelected ? "step-user-selected" : ""}`;

      const userSelectedBadge = isSelected
        ? `<span class="badge-tag badge-user-selected">⭐ Selected by You</span>`
        : "";

      const genreBadge = act.place.genre
        ? `<span class="badge-tag badge-genre" style="background:#f3e8ff; color:#7e22ce; font-weight:700;">${act.place.genre}</span>`
        : "";

      const sourceBadge = act.place.source
        ? `<span class="badge-tag badge-source" style="background:#f1f5f9; color:#475569;">${act.place.source.toUpperCase()}</span>`
        : "";

      step.innerHTML = `
        <div class="step-header">
          <div class="step-time">${I.pin} ${act.start_time} - ${act.end_time} &bull; ${act.duration_mins} mins</div>
          <span class="badge-tag badge-cost">${act.cost > 0 ? `₹${act.cost}` : 'Free'}</span>
        </div>
        <div class="step-title">${act.place.name}</div>
        <div style="font-size:0.8rem; color:#475569;">${act.place.description}</div>
        <div class="step-badges">
          ${userSelectedBadge}
          ${genreBadge}
          <span class="badge-tag badge-open">✓ Operating Window: ${act.place.opening_time} - ${act.place.closing_time}</span>
          <span class="badge-tag badge-buffer">+${act.buffer_mins}m Transition Buffer</span>
          ${sourceBadge}
        </div>
      `;
      daySteps.push({ key: timeToMinutes(act.start_time), order: orderIdx++, node: step });
    });

    // Meals
    day.meals.forEach((meal) => {
      const step = document.createElement("div");
      const isSelectedDining = meal.restaurant && (meal.restaurant.user_selected || (userSelectedDiningByCity[day.title] && userSelectedDiningByCity[day.title].has(meal.restaurant.id)));
      step.className = `timeline-step step-dhaba ${isSelectedDining ? 'step-user-selected' : ''}`;

      const selectedDiningBadge = isSelectedDining
        ? `<span class="badge-tag badge-user-selected" style="background:#fef3c7; color:#92400e; font-weight:700;">⭐ Your Selected Dining</span>`
        : "";
      const sourceBadge = meal.restaurant.source
        ? `<span class="badge-tag badge-source" style="background:#f1f5f9; color:#475569;">${meal.restaurant.source.toUpperCase()}</span>`
        : "";

      step.innerHTML = `
        <div class="step-header">
          <div class="step-time">${I.dining} ${meal.time_slot} &bull; ${meal.meal_type.toUpperCase()}</div>
          <span class="badge-tag badge-cost">~₹${meal.estimated_cost}</span>
        </div>
        <div class="step-title">${meal.restaurant.name}</div>
        <div style="font-size:0.8rem; color:#475569;">${meal.restaurant.specialty || meal.restaurant.location}</div>
        <div class="step-badges">
          ${selectedDiningBadge}
          <span class="badge-tag ${meal.restaurant.is_dhaba ? 'badge-delay' : 'badge-open'}">${meal.restaurant.is_dhaba ? 'Roadside Highway Dhaba' : 'Local Dining'}</span>
          <span class="badge-tag badge-buffer">★ ${meal.restaurant.rating}</span>
          ${sourceBadge}
        </div>
        <div class="step-actions">
          <button class="btn-book" onclick="openBookingModal('restaurant', '${meal.restaurant.id}', '${meal.restaurant.name}', '${meal.time_slot}', ${meal.estimated_cost})">
            Reserve Table / Dhaba Stop
          </button>
        </div>
      `;
      daySteps.push({ key: timeToMinutes(meal.time_slot), order: orderIdx++, node: step });
    });

    // Overnight Stay
    if (day.overnight_stay) {
      const stay = day.overnight_stay;
      const isSelectedStay = stay.hotel && stay.hotel.user_selected;
      const step = document.createElement("div");
      step.className = `timeline-step step-hotel ${isSelectedStay ? 'step-user-selected' : ''}`;

      const selectedStayBadge = isSelectedStay
        ? `<span class="badge-tag badge-user-selected" style="background:#e0e7ff; color:#3730a3; font-weight:700;">⭐ Your Selected Stay</span>`
        : "";
      const sourceBadge = stay.hotel.source
        ? `<span class="badge-tag badge-source" style="background:#f1f5f9; color:#475569;">${stay.hotel.source.toUpperCase()}</span>`
        : "";

      step.innerHTML = `
        <div class="step-header">
          <div class="step-time">${I.hotel} Overnight Stay &bull; Check-in 14:00</div>
          <span class="badge-tag badge-cost">₹${stay.total_cost}</span>
        </div>
        <div class="step-title">${stay.hotel.name}</div>
        <div style="font-size:0.8rem; color:#475569;">${stay.hotel.location} &bull; Amenities: ${(stay.hotel.amenities || []).join(", ")}</div>
        <div class="step-badges">
          ${selectedStayBadge}
          <span class="badge-tag badge-open">★ ${stay.hotel.rating} Rating</span>
          <span class="badge-tag badge-buffer">Tier: ${stay.hotel.tier}</span>
          ${sourceBadge}
        </div>
        <div class="step-actions">
          <button class="btn-book" onclick="openBookingModal('hotel', '${stay.hotel.id}', '${stay.hotel.name}', '${day.date}', ${stay.total_cost})">
            Book Room
          </button>
        </div>
      `;
      daySteps.push({ key: timeToMinutes("14:00"), order: orderIdx++, node: step });
    }

    daySteps.sort((a, b) => {
      const ka = a.key === null ? Number.MAX_SAFE_INTEGER : a.key;
      const kb = b.key === null ? Number.MAX_SAFE_INTEGER : b.key;
      if (ka !== kb) return ka - kb;
      return a.order - b.order;
    });
    daySteps.forEach((s) => timelineContainer.appendChild(s.node));
  });
}

function getCityCoords(cityName) {
  if (!cityName) return null;
  if (window.cityCatalog && window.cityCatalog.length > 0) {
    const match = window.cityCatalog.find(
      (c) => c.name.toLowerCase() === cityName.toLowerCase()
    );
    if (match) return [match.lat, match.lon];
  }
  return null;
}

function renderMap(variant) {
  if (!leafletMap || !routeLayerGroup) return;
  routeLayerGroup.clearLayers();

  const allPlotPoints = [];

  // 1. Plot Origin Marker (${dotOn})
  const origName = currentPlan.input_params.origin;
  let originCoords = null;
  if (variant.corridor_geometry && variant.corridor_geometry.length > 0) {
    originCoords = [variant.corridor_geometry[0].lat, variant.corridor_geometry[0].lon];
  } else {
    originCoords = getCityCoords(origName) || [28.6139, 77.2090];
  }
  allPlotPoints.push(originCoords);

  L.circleMarker(originCoords, {
    radius: 11,
    fillColor: "#10b981",
    color: "#ffffff",
    weight: 3,
    opacity: 1,
    fillOpacity: 1,
  })
    .bindPopup(`
      <div style="font-family:sans-serif; min-width:160px;">
        <div style="color:#10b981; font-weight:800; font-size:0.8rem; letter-spacing:0.04em;">${dotOn} TRIP ORIGIN (START)</div>
        <div style="font-size:1.05rem; font-weight:700; margin:4px 0 2px;">${origName}</div>
        <div style="font-size:0.8rem; color:#475569;">Start Date: <strong>${currentPlan.input_params.start_date}</strong></div>
        <div style="font-size:0.8rem; color:#475569;">Departure: <strong>${currentPlan.input_params.start_time_of_day}</strong></div>
      </div>
    `)
    .addTo(routeLayerGroup);

  // 2. Plot In-Between Stopover Markers (${dotWarn})
  const stopovers = currentPlan.input_params.stopovers || [];
  stopovers.forEach((stop, idx) => {
    let stopCoords = getCityCoords(stop.location);
    if (!stopCoords) {
      for (const d of variant.days) {
        for (const act of d.activities) {
          if (act.place.location.toLowerCase().includes(stop.location.toLowerCase()) && act.place.coords) {
            stopCoords = [act.place.coords.lat, act.place.coords.lon];
            break;
          }
        }
        if (stopCoords) break;
      }
    }
    if (!stopCoords) {
      const destCoordsFallback = getCityCoords(currentPlan.input_params.destination) || [26.9124, 75.7873];
      const ratio = (idx + 1) / (stopovers.length + 1);
      stopCoords = [
        originCoords[0] + (destCoordsFallback[0] - originCoords[0]) * ratio,
        originCoords[1] + (destCoordsFallback[1] - originCoords[1]) * ratio,
      ];
    }

    allPlotPoints.push(stopCoords);

    const stayText = (stop.stay_days !== null && stop.stay_days !== undefined)
      ? (stop.stay_days === 0 ? "En-Route Transit Stop" : `Stay ${stop.stay_days} Day(s)`)
      : "AI-Optimized Duration";

    L.circleMarker(stopCoords, {
      radius: 10,
      fillColor: "#f59e0b",
      color: "#ffffff",
      weight: 3,
      opacity: 1,
      fillOpacity: 1,
    })
      .bindPopup(`
        <div style="font-family:sans-serif; min-width:160px;">
          <div style="color:#f59e0b; font-weight:800; font-size:0.8rem; letter-spacing:0.04em;">${dotWarn} IN-BETWEEN STOPOVER</div>
          <div style="font-size:1.05rem; font-weight:700; margin:4px 0 2px;">${stop.location}</div>
          <div style="font-size:0.8rem; color:#475569;">Allocated Time: <strong>${stayText}</strong></div>
        </div>
      `)
      .addTo(routeLayerGroup);
  });

  // 3. Plot Destination Marker (${dotAlarm})
  const destName = currentPlan.input_params.destination;
  let destCoords = null;
  if (variant.corridor_geometry && variant.corridor_geometry.length > 0) {
    const lastPt = variant.corridor_geometry[variant.corridor_geometry.length - 1];
    destCoords = [lastPt.lat, lastPt.lon];
  } else {
    destCoords = getCityCoords(destName) || [26.9124, 75.7873];
  }
  allPlotPoints.push(destCoords);

  L.circleMarker(destCoords, {
    radius: 11,
    fillColor: "#ef4444",
    color: "#ffffff",
    weight: 3,
    opacity: 1,
    fillOpacity: 1,
  })
    .bindPopup(`
      <div style="font-family:sans-serif; min-width:160px;">
        <div style="color:#ef4444; font-weight:800; font-size:0.8rem; letter-spacing:0.04em;">${dotAlarm} FINAL DESTINATION</div>
        <div style="font-size:1.05rem; font-weight:700; margin:4px 0 2px;">${destName}</div>
        <div style="font-size:0.8rem; color:#475569;">Trip Deadline: <strong>${currentPlan.input_params.end_date}</strong></div>
      </div>
    `)
    .addTo(routeLayerGroup);

  // 4. Plot Sightseeing Attractions
  variant.days.forEach((d) => {
    d.activities.forEach((act) => {
      if (act.place.coords) {
        const pLat = act.place.coords.lat;
        const pLon = act.place.coords.lon;
        allPlotPoints.push([pLat, pLon]);

        L.circleMarker([pLat, pLon], {
          radius: 6,
          fillColor: "#3b82f6",
          color: "#ffffff",
          weight: 1.5,
          opacity: 1,
          fillOpacity: 0.9,
        })
          .bindPopup(`
            <div style="font-family:sans-serif;">
              <div style="color:#3b82f6; font-weight:700; font-size:0.82rem;">${I.landmark} ${act.place.location} Attraction</div>
              <div style="font-size:0.95rem; font-weight:700; margin:2px 0;">${act.place.name}</div>
              <div style="font-size:0.8rem; color:#334155;">Time: <strong>${act.start_time} - ${act.end_time}</strong> (${act.duration_mins}m)</div>
              <div style="font-size:0.8rem; color:#334155;">Hours: ${act.place.opening_time} - ${act.place.closing_time}</div>
              <div style="font-size:0.8rem; color:#10b981; font-weight:600;">Ticket Fee: ₹${act.cost} &bull; ${act.opening_status_note}</div>
            </div>
          `)
          .addTo(routeLayerGroup);
      }
    });
  });

  // 5. Render Connected Road Polyline
  let polylineCoords = [];
  if (variant.corridor_geometry && variant.corridor_geometry.length > 1) {
    polylineCoords = variant.corridor_geometry.map((pt) => [pt.lat, pt.lon]);
  } else {
    polylineCoords = allPlotPoints;
  }

  if (polylineCoords.length > 1) {
    // Outer casing
    L.polyline(polylineCoords, {
      color: "#1d4ed8",
      weight: 6,
      opacity: 0.4,
    }).addTo(routeLayerGroup);

    // Core highway route
    const mainPoly = L.polyline(polylineCoords, {
      color: "#3b82f6",
      weight: 3.5,
      opacity: 0.95,
      dashArray: "8, 6",
    }).addTo(routeLayerGroup);

    leafletMap.fitBounds(mainPoly.getBounds(), { padding: [50, 50] });
  }

  // 5.5. Render Multi-Modal Interactive Transport Badges along each Leg
  const routeLegs = (currentPlan && currentPlan.route && currentPlan.route.legs) ? currentPlan.route.legs : [];
  const mapModeIcons = { train: I.train, bus: I.bus, driving: I.car, shared_cab: I.cab };
  const mapModeTitles = { train: "Express Train", bus: "Highway Bus", driving: "Self-Drive Car", shared_cab: "Shared Cab" };

  routeLegs.forEach((leg, lIdx) => {
    let midCoord = null;
    if (leg.geometry && leg.geometry.length > 2) {
      const midPt = leg.geometry[Math.floor(leg.geometry.length / 2)];
      midCoord = [midPt.lat, midPt.lon];
    } else {
      const fCoords = getCityCoords(leg.from_place);
      const tCoords = getCityCoords(leg.to_place);
      if (fCoords && tCoords) {
        midCoord = [(fCoords[0] + tCoords[0]) / 2, (fCoords[1] + tCoords[1]) / 2];
      }
    }

    if (midCoord) {
      allPlotPoints.push(midCoord);
      const icon = mapModeIcons[leg.selected_mode] || I.car;
      const modeName = mapModeTitles[leg.selected_mode] || leg.selected_mode;

      const badgeDiv = L.divIcon({
        className: "map-transit-icon-container",
        html: `<div class="map-transit-badge mode-${leg.selected_mode}" title="${leg.from_place} to ${leg.to_place} via ${modeName}"><span class="transit-emoji">${icon}</span></div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
        popupAnchor: [0, -18]
      });

      const hubsContent = leg.departure_hub
        ? `<div class="transit-popup-hubs">${I.station} <strong>Hubs:</strong> ${leg.departure_hub} ➔ ${leg.arrival_hub}</div>`
        : "";

      const ticketsContent = leg.ticket_cost > 0
        ? `<div>${I.ticket} <strong>Intercity Tickets:</strong> ₹${leg.ticket_cost.toLocaleString()}</div>`
        : "";

      const feederContent = leg.local_transit_cost > 0
        ? `<div>${I.cab} <strong>Local Feeder (${leg.local_vehicle_type || 'Shared Auto'}):</strong> ₹${leg.local_transit_cost.toLocaleString()}</div>`
        : "";

      const trainPopupContent = (leg.selected_mode === 'train' && leg.train_number)
        ? `<div style="margin-top:4px; padding:4px 8px; background:#dcfce7; border-radius:4px; color:#166534; font-size:0.75rem;">${I.train} <strong>Train #${leg.train_number}:</strong> ${leg.train_name || ''}<br/>${I.clock} Dep: <strong>${leg.departure_time || '--:--'}</strong> ➔ Arr: <strong>${leg.arrival_time || '--:--'}</strong></div>`
        : "";

      const marker = L.marker(midCoord, { icon: badgeDiv }).bindPopup(`
        <div class="transit-popup-card">
          <div class="transit-popup-header">
            <span style="font-size:1.2rem;">${icon}</span>
            <span>Leg ${lIdx + 1}: ${leg.from_place} ➔ ${leg.to_place}</span>
          </div>
          <div class="transit-popup-meta">Mode: <strong>${modeName}</strong> &bull; ${leg.distance_km} km &bull; ~${leg.buffered_duration_hours} hrs</div>
          ${hubsContent}
          ${trainPopupContent}
          <div class="transit-popup-costs">
            <div>Total Segment Transit: <strong>₹${leg.estimated_transit_cost.toLocaleString()}</strong></div>
            ${ticketsContent}
            ${feederContent}
          </div>
        </div>
      `);

      marker.addTo(routeLayerGroup);
    }
  });

  // Plot Return Leg Badge (if round trip > 1 day)
  if (variant.days.length > 1) {
    const lastDay = variant.days[variant.days.length - 1];
    const retTransit = lastDay.transit_details;
    if (retTransit && originCoords && destCoords) {
      const returnMid = [
        (destCoords[0] + originCoords[0]) / 2 - 0.05,
        (destCoords[1] + originCoords[1]) / 2 + 0.08
      ];
      allPlotPoints.push(returnMid);
      const retIcon = mapModeIcons[retTransit.mode] || I.car;
      const retName = mapModeTitles[retTransit.mode] || retTransit.mode;

      const retBadgeDiv = L.divIcon({
        className: "map-transit-icon-container",
        html: `<div class="map-transit-badge mode-${retTransit.mode}" title="Return Journey to ${origName} via ${retName}"><span class="transit-emoji">${retIcon}</span></div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
        popupAnchor: [0, -18]
      });

      const retHubs = retTransit.departure_hub
        ? `<div class="transit-popup-hubs">${I.station} <strong>Hubs:</strong> ${retTransit.departure_hub} ➔ ${retTransit.arrival_hub}</div>`
        : "";

      const retTickets = retTransit.ticket_cost > 0
        ? `<div>${I.ticket} <strong>Return Tickets:</strong> ₹${retTransit.ticket_cost.toLocaleString()}</div>`
        : "";

      const retFeeder = retTransit.local_transit_cost > 0
        ? `<div>${I.cab} <strong>Shared Auto Feeder:</strong> ₹${retTransit.local_transit_cost.toLocaleString()}</div>`
        : "";

      const retTrainPopup = (retTransit.mode === 'train' && retTransit.train_number)
        ? `<div style="margin-top:4px; padding:4px 8px; background:#dcfce7; border-radius:4px; color:#166534; font-size:0.75rem;">${I.train} <strong>Train #${retTransit.train_number}:</strong> ${retTransit.train_name || ''}<br/>${I.clock} Dep: <strong>${retTransit.departure_time || '--:--'}</strong> ➔ Arr: <strong>${retTransit.arrival_time || '--:--'}</strong></div>`
        : "";

      const retMarker = L.marker(returnMid, { icon: retBadgeDiv }).bindPopup(`
        <div class="transit-popup-card">
          <div class="transit-popup-header">
            <span style="font-size:1.2rem;">${retIcon}</span>
            <span>${I.swap} Return: ${destName} ➔ ${origName}</span>
          </div>
          <div class="transit-popup-meta">Mode: <strong>${retName}</strong> &bull; ${retTransit.distance_km} km &bull; ~${retTransit.duration_hours} hrs</div>
          ${retHubs}
          ${retTrainPopup}
          <div class="transit-popup-costs">
            <div>Return Transit Total: <strong>₹${retTransit.total_cost.toLocaleString()}</strong></div>
            ${retTickets}
            ${retFeeder}
          </div>
        </div>
      `);

      retMarker.addTo(routeLayerGroup);
    }
  }

  // 6. Update Map Overlay Header & Stats
  const stopoverNames = stopovers.map((s) => s.location).filter(Boolean);
  const fullSequence = [origName, ...stopoverNames, destName];
  document.getElementById("mapRouteTitle").textContent = fullSequence.join(" ➔ ");
  document.getElementById("mapRouteStats").innerHTML = `
    <div>Corridor: <strong>${fullSequence.join(" ➔ ")}</strong></div>
    <div>Total Distance: <strong>${variant.total_distance_km} km</strong></div>
    <div>Total Cost: <strong>₹${variant.total_cost.toLocaleString()}</strong></div>
    <div>Trip Deadline: <strong>${variant.days.length} Days</strong></div>
    <div>Pareto Score: <strong>★ ${variant.score}</strong></div>
  `;
}

function renderBudgetAudit(variant) {
  const card = document.getElementById("budgetAuditCard");
  const budgetCap = currentPlan.input_params.budget;
  const spent = variant.total_cost;
  const ratio = Math.min(100, Math.round((spent / budgetCap) * 100));
  const isOver = spent > budgetCap;

  const cost = variant.cost_summary || {};
  const ticketCost = cost.tickets || 0;
  const localSharedCost = cost.local_shared_transit || 0;
  const fuelTollCost = cost.fuel_tolls || 0;

  card.innerHTML = `
    <div>
      <h3>Budget Feasibility Gate & Cost Auditor</h3>
      <p style="font-size:0.85rem; color:#64748b;">Validating Hard Constraint: <code>Total Cost &le; ₹${budgetCap.toLocaleString()}</code></p>
    </div>

    <div class="budget-meter-container">
      <div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700;">
        <span>Spent: ₹${spent.toLocaleString()} (${ratio}%)</span>
        <span style="color:${isOver ? '#ef4444' : '#10b981'};">${isOver ? 'Deficit: -₹' + (spent - budgetCap).toLocaleString() : 'Surplus: +₹' + (budgetCap - spent).toLocaleString()}</span>
      </div>
      <div class="budget-bar-bg">
        <div class="budget-bar-fill ${isOver ? 'overbudget' : ''}" style="width: ${ratio}%;"></div>
      </div>
    </div>

    <div class="cost-breakdown-grid">
      <div class="cost-tile">
        <span class="title">${I.car} Total Transport</span>
        <span class="amount">₹${(cost.transport || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">${I.hotel} Stays</span>
        <span class="amount">₹${(cost.stays || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">${I.dining} Food & Dhabas</span>
        <span class="amount">₹${(cost.food || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">${I.ticket} Sight Tickets</span>
        <span class="amount">₹${(cost.activities || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">${I.shield} Buffer Reserve</span>
        <span class="amount">₹${(cost.buffer_reserve || 0).toLocaleString()}</span>
      </div>
    </div>

    <!-- Itemized Multi-Modal Transport Breakdown -->
    <div class="transport-subbreakdown-card">
      <div class="subbreakdown-header">
        <span class="subbreakdown-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>
          Itemized Multi-Modal Transit Breakdown
        </span>
        <span class="subbreakdown-tag">Included in ₹${(cost.transport || 0).toLocaleString()} Transport</span>
      </div>
      <div class="subbreakdown-grid">
        <div class="subbreakdown-item">
          <span class="sub-icon">${I.ticket}</span>
          <div class="sub-info">
            <span class="sub-label">Intercity Rail / Bus Tickets</span>
            <span class="sub-amount">₹${ticketCost.toLocaleString()}</span>
          </div>
        </div>
        <div class="subbreakdown-item">
          <span class="sub-icon">${I.cab}</span>
          <div class="sub-info">
            <span class="sub-label">Local Shared Vehicles (Autos & Feeder Cabs)</span>
            <span class="sub-amount">₹${localSharedCost.toLocaleString()}</span>
          </div>
        </div>
        <div class="subbreakdown-item">
          <span class="sub-icon">${I.fuel}</span>
          <div class="sub-info">
            <span class="sub-label">Highway Fuel & Tolls (Driving Legs)</span>
            <span class="sub-amount">₹${fuelTollCost.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>

    <div style="background:#f8fafc; padding:16px; border-radius:10px; border:1px solid #e2e8f0; margin-top:14px;">
      <h4 style="font-size:0.88rem; font-weight:700; color:#1e293b; margin-bottom:6px;">Feasibility Audit Log:</h4>
      <div style="font-size:0.82rem; color:${variant.feasibility.passed ? '#065f46' : '#991b1b'};">
        ${variant.feasibility.passed ? '✓ All 4 hard constraints passed (Budget, Daily Time, Operating Windows, Traffic Buffers).' : variant.feasibility.issues.join('<br>')}
      </div>
    </div>
  `;
}

function renderAgentTrace() {
  const stream = document.getElementById("traceStream");
  const badgeCount = document.getElementById("traceBadgeCount");
  const traces = currentPlan.agent_trace || [];

  badgeCount.textContent = traces.length;
  stream.innerHTML = "";

  traces.forEach((t) => {
    const item = document.createElement("div");
    item.className = "trace-item";
    item.innerHTML = `
      <div class="trace-top">
        <span class="trace-sender">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="3 11 22 2 13 21 11 13 3 11"></polygon></svg>
          ${t.sender} ➔ ${t.recipient}
        </span>
        <span class="trace-action">${t.action}</span>
      </div>
      <div class="trace-notes">${t.notes || JSON.stringify(t.payload)}</div>
    `;
    stream.appendChild(item);
  });
}

// Booking Modal Controls
function openBookingModal(itemType, itemId, itemName, dateOrTime, amount) {
  pendingBooking = {
    plan_id: currentPlan.plan_id,
    variant_type: activeVariantKey,
    item_type: itemType,
    item_id: itemId,
    date_or_time: dateOrTime,
    guests: currentPlan.input_params.party_size,
    user_name: "Uday Traveler",
    amount: amount,
    itemName: itemName,
  };

  document.getElementById("bookingModalTitle").textContent = `Book ${itemType === 'hotel' ? 'Hotel Stay' : 'Table / Dhaba Stop'}`;
  document.getElementById("bookingModalBody").innerHTML = `
    <div><strong>Item:</strong> ${itemName}</div>
    <div><strong>Date / Time Slot:</strong> ${dateOrTime}</div>
    <div><strong>Guests:</strong> ${pendingBooking.guests} person(s)</div>
    <div><strong>Estimated Payable:</strong> ₹${amount.toLocaleString()}</div>
    <div style="font-size:0.78rem; color:#64748b; margin-top:8px;">Instant reservation simulated by Safarana.</div>
  `;

  document.getElementById("bookingModal").style.display = "flex";
}

function closeModal() {
  document.getElementById("bookingModal").style.display = "none";
  pendingBooking = null;
}

async function confirmPendingBooking() {
  if (!pendingBooking) return;
  try {
    const res = await fetch("/api/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pendingBooking),
    });
    const data = await res.json();
    closeModal();
    alert(`${I.check} Booking Confirmed!\nConfirmation Code: ${data.confirmation_code}\nItem: ${data.item_name}`);
    loadBookingsCount();
  } catch (err) {
    alert("Booking failed: " + err.message);
  }
}

async function loadBookingsCount() {
  try {
    const res = await fetch("/api/bookings");
    const data = await res.json();
    document.getElementById("bookingCount").textContent = data.bookings ? data.bookings.length : 0;
  } catch (e) {}
}

async function openMyBookingsModal() {
  try {
    const res = await fetch("/api/bookings");
    const data = await res.json();
    const list = document.getElementById("myBookingsList");

    if (!data.bookings || data.bookings.length === 0) {
      list.innerHTML = `<p style="color:#64748b;">No bookings placed yet. Use the "Book Room" or "Reserve Table" buttons in your itinerary.</p>`;
    } else {
      list.innerHTML = data.bookings
        .map(
          (b) => `
        <div style="border:1px solid #e2e8f0; padding:14px; border-radius:8px; margin-bottom:10px; background:#f8fafc;">
          <div style="display:flex; justify-content:space-between; font-weight:700;">
            <span>${b.item_name} (${b.item_type})</span>
            <span style="color:#10b981;">✓ ${b.status}</span>
          </div>
          <div style="font-size:0.8rem; color:#475569; margin-top:4px;">
            Booking Ref: <strong>${b.booking_id}</strong> &bull; Code: <strong>${b.details.confirmation_code || 'CONF-OK'}</strong>
          </div>
          <div style="font-size:0.8rem; color:#64748b;">
            Date/Time: ${b.date_or_time} &bull; Guests: ${b.guests} &bull; Amount: ₹${b.amount}
          </div>
        </div>
      `
        )
        .join("");
    }

    document.getElementById("myBookingsModal").style.display = "flex";
  } catch (err) {
    alert("Failed to load bookings: " + err.message);
  }
}

function closeMyBookingsModal() {
  document.getElementById("myBookingsModal").style.display = "none";
}

// ==========================================
// Google Maps API Key & Status Management
// ==========================================
async function checkGoogleMapsStatus() {
  try {
    const res = await fetch("/api/maps/status");
    const data = await res.json();
    const dot = document.getElementById("mapsIndicatorDot");
    const label = document.getElementById("mapsStatusLabel");
    const banner = document.getElementById("mapsKeyStatusBanner");
    const help = document.getElementById("mapsKeyActivationHelp");

    if (data.active) {
      if (dot) dot.className = "gmaps-indicator-dot active";
      if (label) label.textContent = "Google Maps Live";
      if (banner) {
        banner.className = "maps-key-status-banner banner-active";
        banner.innerHTML = "${I.check} <strong>Google Maps Live:</strong> Directions & Routes API active for real-time fares and routes.";
      }
      if (help) help.style.display = "none";
    } else if (data.key_configured) {
      if (dot) dot.className = "gmaps-indicator-dot pending";
      if (label) label.textContent = "Google Maps (Key Set)";
      if (banner) {
        banner.className = "maps-key-status-banner banner-pending";
        banner.innerHTML = `${I.alert} <strong>Key Configured:</strong> Routes / Directions API needs activation in your Google Cloud Console.<br><span style="font-size:0.75rem; color:#b45309;">${data.last_error || 'Enable Routes API to activate live fares'}</span>`;
      }
      if (help) help.style.display = "block";
    } else {
      if (dot) dot.className = "gmaps-indicator-dot inactive";
      if (label) label.textContent = "Setup Google Maps";
      if (banner) {
        banner.className = "maps-key-status-banner banner-inactive";
        banner.innerHTML = "${I.info} <strong>No Key Configured:</strong> Using calibrated Indian transit fare & routing engine.";
      }
      if (help) help.style.display = "none";
    }
  } catch (e) {
    console.debug("Failed to check Google Maps status:", e);
  }
}

async function saveGoogleMapsKey() {
  const input = document.getElementById("inputGoogleMapsKey");
  const key = (input ? input.value : "").trim();
  if (!key) {
    alert("Please enter a Google Maps API Key.");
    return;
  }
  try {
    const res = await fetch("/api/maps/key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key })
    });
    const data = await res.json();
    alert(data.message || "Key saved");
    document.getElementById("mapsKeyModal").style.display = "none";
    await checkGoogleMapsStatus();
    triggerPlanning();
  } catch (err) {
    alert("Error saving key: " + err.message);
  }
}

function openMapsKeyModal() {
  document.getElementById("mapsKeyModal").style.display = "flex";
  checkGoogleMapsStatus();
}

function closeMapsKeyModal() {
  document.getElementById("mapsKeyModal").style.display = "none";
}

// ==========================================
// Train Timetable & Route Halts Modal
// ==========================================
async function openTrainTimetableModal(trainNumber, trainName) {
  const modal = document.getElementById("trainTimetableModal");
  const title = document.getElementById("timetableModalTitle");
  const body = document.getElementById("timetableModalBody");

  title.innerHTML = `${I.train} Timetable & Actual Halts: #${trainNumber} ${trainName || ''}`;
  body.innerHTML = `<div style="text-align:center; padding:30px; color:#64748b;">${I.timer} Fetching live route and halts timetable from RailRadar API...</div>`;
  modal.style.display = "flex";

  try {
    const res = await fetch(`/api/trains/${trainNumber}/details`);
    const data = await res.json();
    if (data.success && data.details) {
      const d = data.details;
      const halts = d.route_stops || [];
      const passengerHalts = halts.filter(h => h.is_halt !== false);
      const coachPos = d.coach_position || "";
      const classes = (d.classes || []).join(", ");
      const seats = d.seat_status || [];

      let seatsHtml = '';
      if (seats.length > 0) {
        seatsHtml = `
          <div class="timetable-seats-summary" style="margin-bottom:12px; background:#f1f5f9; padding:10px; border-radius:8px;">
            <div style="font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:6px;">${I.seat} Real-Time Seat Status & Confirmed Ticket Chance (RailRadar):</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${seats.map(s => `
                <span class="seat-badge ${s.badge}" style="font-size:0.8rem; padding:4px 10px;">
                  <strong>${s.class_code}</strong> (${s.class_name}): <strong>${s.status_code}</strong> &bull; ₹${s.fare} (${s.confirmation_chance})
                </span>
              `).join('')}
            </div>
          </div>
        `;
      }

      let coachHtml = coachPos ? `
        <div class="timetable-coach-summary" style="margin-bottom:12px; font-size:0.8rem; color:#475569; background:#fff; border:1px solid #e2e8f0; padding:8px 12px; border-radius:6px;">
          <strong>Coach Sequence:</strong> <code class="coach-pos-code" style="background:#f8fafc; padding:2px 6px; border-radius:4px;">${coachPos}</code>
        </div>
      ` : '';

      let tableRows = passengerHalts.map(h => `
        <tr class="${h.is_halt ? 'row-halt' : 'row-pass'}" style="border-bottom:1px solid #e2e8f0;">
          <td style="font-weight:600; text-align:center; padding:8px;">${h.sequence}</td>
          <td style="padding:8px;">
            <strong>${h.station_name}</strong>
            <span style="font-size:0.75rem; color:#64748b; margin-left:4px;">(${h.station_code})</span>
          </td>
          <td style="text-align:center; padding:8px;">${h.arrival}</td>
          <td style="text-align:center; padding:8px;">${h.departure}</td>
          <td style="text-align:center; padding:8px;">${h.halt_minutes > 0 ? `${h.halt_minutes} mins` : '--'}</td>
          <td style="text-align:center; padding:8px;">${h.distance_km} km</td>
          <td style="text-align:center; padding:8px;">Platform ${h.platform || '1'}</td>
        </tr>
      `).join('');

      body.innerHTML = `
        ${seatsHtml}
        ${coachHtml}
        <div style="font-size:0.8rem; color:#64748b; margin-bottom:8px; display:flex; justify-content:space-between;">
          <span>Showing <strong>${passengerHalts.length}</strong> scheduled passenger halts</span>
          <span>Distance: <strong>${d.distance_km} km</strong> &bull; Classes: <strong>${classes}</strong></span>
        </div>
        <div style="overflow-x:auto;">
          <table class="timetable-table" style="width:100%; border-collapse:collapse; font-size:0.85rem;">
            <thead>
              <tr style="background:#f8fafc; border-bottom:2px solid #cbd5e1; text-align:left;">
                <th style="padding:8px; text-align:center;">#</th>
                <th style="padding:8px;">Station Name</th>
                <th style="padding:8px; text-align:center;">Arrival</th>
                <th style="padding:8px; text-align:center;">Departure</th>
                <th style="padding:8px; text-align:center;">Halt</th>
                <th style="padding:8px; text-align:center;">Distance</th>
                <th style="padding:8px; text-align:center;">Platform</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows}
            </tbody>
          </table>
        </div>
      `;
    } else {
      body.innerHTML = `<div style="color:#ef4444; padding:20px;">Could not load timetable for train #${trainNumber}.</div>`;
    }
  } catch (err) {
    body.innerHTML = `<div style="color:#ef4444; padding:20px;">Failed to load timetable: ${err.message}</div>`;
  }
}

function closeTrainTimetableModal() {
  document.getElementById("trainTimetableModal").style.display = "none";
}

// Global modal & timetable click delegation
document.addEventListener("DOMContentLoaded", () => {
  checkGoogleMapsStatus();

  const mapsBtn = document.getElementById("openMapsKeyBtn");
  if (mapsBtn) mapsBtn.addEventListener("click", openMapsKeyModal);

  const saveMapsBtn = document.getElementById("saveMapsKeyBtn");
  if (saveMapsBtn) saveMapsBtn.addEventListener("click", saveGoogleMapsKey);

  const closeMapsBtn = document.getElementById("closeMapsKeyBtn");
  if (closeMapsBtn) closeMapsBtn.addEventListener("click", closeMapsKeyModal);

  const closeMapsX = document.getElementById("closeMapsKeyModalBtn");
  if (closeMapsX) closeMapsX.addEventListener("click", closeMapsKeyModal);

  const closeTimetableX = document.getElementById("closeTimetableModalBtn");
  if (closeTimetableX) closeTimetableX.addEventListener("click", closeTrainTimetableModal);

  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".view-timetable-btn");
    if (btn) {
      const tNum = btn.dataset.train;
      const tName = btn.dataset.name;
      openTrainTimetableModal(tNum, tName);
    }
  });
});

