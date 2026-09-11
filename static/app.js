// SmartRoute Client-Side Application

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

// Initialize upon DOM load
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initEventListeners();
  initLocationControls();
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
      const container = document.getElementById("stopoversContainer");
      if (container) container.innerHTML = "";
      document.getElementById("originInput").focus();
      updateCorridorSuggestions();
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

  // Origin & Destination input change for corridor suggestions
  const origInput = document.getElementById("originInput");
  const destInput = document.getElementById("destinationInput");
  if (origInput && destInput) {
    origInput.addEventListener("change", updateCorridorSuggestions);
    destInput.addEventListener("change", updateCorridorSuggestions);
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
    </div>
  `;

  row.querySelector(".btn-remove-stopover").addEventListener("click", () => {
    row.remove();
    triggerPlanning();
  });

  row.querySelector(".stopover-select").addEventListener("change", () => {
    triggerPlanning();
  });

  row.querySelector(".stopover-loc-input").addEventListener("change", () => {
    triggerPlanning();
  });

  container.appendChild(row);
  const input = row.querySelector(".stopover-loc-input");
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
  link.setAttribute("download", `smartroute_${currentPlan.plan_id.toLowerCase()}_${activeVariantKey}.ics`);
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
  submitBtn.querySelector(".btn-text").textContent = "Agents Solving Constraints...";

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
      stopovers.push({
        location: loc,
        stay_days: durVal === "" ? null : parseInt(durVal, 10),
      });
    }
  });

  const payload = {
    origin: origin,
    destination: destination,
    stopovers: stopovers,
    budget: parseFloat(document.getElementById("budgetInput").value) || 15000,
    start_date: document.getElementById("startDateInput").value,
    end_date: document.getElementById("endDateInput").value,
    travel_mode: document.getElementById("travelModeInput").value,
    leg_modes: currentLegModes,
    return_travel_mode: currentReturnMode || document.getElementById("travelModeInput").value,
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
      driving: { icon: "🚗", name: "Car", tip: "Self-Drive / Car" },
      train: { icon: "🚆", name: "Train", tip: "Express Rail" },
      bus: { icon: "🚌", name: "Bus", tip: "Highway Bus" },
      shared_cab: { icon: "🛺", name: "Shared Cab", tip: "Shared Cab" },
    };

    let modeButtonsHtml = "";
    if (availableModes.length > 0) {
      modeButtonsHtml = availableModes.map(opt => {
        const info = modeLabels[opt.mode] || { icon: "🚘", name: opt.mode, tip: opt.mode };
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
      ["driving", "train", "bus", "shared_cab"].forEach(m => {
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
    if (selectedOpt && (selectedMode === "train" || selectedMode === "bus" || selectedMode === "shared_cab")) {
      metaDetailsHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">🚉</span>
            <span><strong>Hubs:</strong> ${selectedOpt.departure_hub} ➔ ${selectedOpt.arrival_hub}</span>
          </div>
          <div class="meta-row">
            <span class="icon">🛺</span>
            <span><strong>Feeder:</strong> ${selectedOpt.local_vehicle_type} (₹${selectedOpt.local_shared_transit_cost || 0} included)</span>
          </div>
        </div>
      `;
    } else if (selectedOpt && selectedMode === "driving") {
      metaDetailsHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">🛣️</span>
            <span><strong>Route:</strong> Direct Door-to-Door via NH &bull; +18% Traffic Buffer</span>
          </div>
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
      driving: { icon: "🚗", name: "Car", tip: "Self-Drive / Car via NH" },
      train: { icon: "🚆", name: "Train", tip: "Return Express Rail" },
      bus: { icon: "🚌", name: "Bus", tip: "Return Highway Bus" },
      shared_cab: { icon: "🛺", name: "Shared Cab", tip: "Return Shared Cab / Shuttle" },
    };

    const modes = ["driving", "train", "bus", "shared_cab"];
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
    if (returnTransit && (returnSelectedMode === "train" || returnSelectedMode === "bus" || returnSelectedMode === "shared_cab")) {
      metaHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">🚉</span>
            <span><strong>Hubs:</strong> ${returnTransit.departure_hub || destCity + ' Station'} ➔ ${returnTransit.arrival_hub || originCity + ' Station'}</span>
          </div>
          <div class="meta-row">
            <span class="icon">🛺</span>
            <span><strong>Feeder:</strong> ${returnTransit.local_vehicle_type || 'Shared Auto'} (₹${returnTransit.local_transit_cost || 0} feeder included)</span>
          </div>
        </div>
      `;
    } else {
      metaHtml = `
        <div class="leg-transit-meta">
          <div class="meta-row">
            <span class="icon">🛣️</span>
            <span><strong>Route:</strong> Return via National Highway &bull; Door-to-Door</span>
          </div>
        </div>
      `;
    }

    const retDist = returnTransit ? returnTransit.distance_km : (currentPlan.route ? currentPlan.route.total_distance_km : 260);

    returnCard.innerHTML = `
      <div class="leg-mode-card-header">
        <span class="return-leg-title">
          <span>🔄 Return Leg:</span>
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
    dayHeader.innerHTML = `📅 ${day.title} <span style="font-size:0.75rem; color:#64748b; font-weight:500;">(${day.date})</span>`;
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
              <span>${day.weather.icon || "☀️"}</span>
              <span>${day.weather.temperature_celsius}°C</span>
            </div>
            <div class="weather-desc">${day.weather.condition}</div>
          </div>
          ${day.weather.risk_alert ? `<div class="weather-alert-badge">⚠️ ${day.weather.risk_alert}</div>` : ""}
        </div>
        ${packingChipsHtml ? `
          <div class="weather-packing">
            <span class="packing-title">🧳 Packing Advisory:</span>
            ${packingChipsHtml}
          </div>
        ` : ""}
      `;
      timelineContainer.appendChild(weatherBanner);
    }

    // Day transit notice
    if (day.transit_time_hours > 0 || day.transit_details) {
      const transitStep = document.createElement("div");
      transitStep.className = "timeline-step step-transit";

      const tDet = day.transit_details || {};
      const tMode = day.transit_mode || tDet.mode || "driving";
      const modeIcons = { train: "🚆", bus: "🚌", shared_cab: "🛺", driving: "🚗", local: "🛺" };
      const modeNames = { train: "Intercity Express Train", bus: "Highway Express Bus", shared_cab: "Shared Outstation Cab", driving: "Highway Drive / Car", local: "Local City Transit" };
      const icon = modeIcons[tMode] || "🚗";
      const modeTitle = tDet.mode_title || modeNames[tMode] || `${tMode.toUpperCase()} Transit`;

      let substepsHtml = "";
      if (tDet.steps && tDet.steps.length > 0) {
        substepsHtml = `
          <div class="transit-steps-box">
            <div style="font-size:0.75rem; font-weight:700; color:#475569; margin-bottom:2px;">Transit Steps & Local Shared Transfers:</div>
            ${tDet.steps.map((st) => `
              <div class="transit-step-row">
                <div class="transit-step-left">
                  <span>${st.vehicle === 'Shared Auto' ? '🛺' : (st.vehicle === 'Express Train' ? '🚆' : (st.vehicle === 'Express Bus' ? '🚌' : '🚗'))}</span>
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
            <button type="button" class="switcher-btn ${tMode === 'driving' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="driving">🚗 Car</button>
            <button type="button" class="switcher-btn ${tMode === 'train' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="train">🚆 Train</button>
            <button type="button" class="switcher-btn ${tMode === 'bus' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="bus">🚌 Bus</button>
            <button type="button" class="switcher-btn ${tMode === 'shared_cab' ? 'active' : ''}" data-is-return="${isReturnDay}" data-leg="${legIndexForDay}" data-mode="shared_cab">🛺 Shared Cab</button>
          </div>
        `;
      }

      const delayText = tMode === "train" 
        ? "⏱️ +12% Rail Signal Delay & 40m Station Buffer" 
        : (tMode === "bus" 
          ? "⏱️ +22% Traffic Delay & 25m Terminal Buffer" 
          : (tMode === "shared_cab" 
            ? "⏱️ +15% Traffic & Pickup Buffer" 
            : "⏱️ +18% Traffic Delay Buffer Included"));

      const hubsText = (tDet.departure_hub && tDet.arrival_hub) 
        ? `<span class="badge-tag badge-buffer">🚉 ${tDet.departure_hub} ➔ ${tDet.arrival_hub}</span>` 
        : "";

      const localAutoBadge = (tDet.local_transit_cost && tDet.local_transit_cost > 0)
        ? `<span class="badge-tag badge-delay">🛺 Includes Shared Autos (₹${tDet.local_transit_cost})</span>`
        : "";

      const ticketBadge = (tDet.ticket_cost && tDet.ticket_cost > 0)
        ? `<span class="badge-tag badge-open">🎟️ Tickets: ₹${tDet.ticket_cost}</span>`
        : "";

      transitStep.innerHTML = `
        <div class="step-header">
          <div class="step-time">${icon} ${modeTitle} &bull; ~${day.transit_time_hours} hrs</div>
          <span class="badge-tag badge-cost">Transport: ₹${day.day_cost_breakdown.transport || 0}</span>
        </div>
        <div class="step-title">${tDet.from_place ? `${tDet.from_place} ➔ ${tDet.to_place}` : 'City Transit'}: ${day.transit_distance_km} km</div>
        <div class="step-badges">
          <span class="badge-tag badge-open">${delayText}</span>
          ${hubsText}
          ${localAutoBadge}
          ${ticketBadge}
        </div>
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

      timelineContainer.appendChild(transitStep);
    }

    // Activities & Meals
    day.activities.forEach((act) => {
      const step = document.createElement("div");
      step.className = "timeline-step";
      step.innerHTML = `
        <div class="step-header">
          <div class="step-time">⏰ ${act.start_time} - ${act.end_time} (${act.duration_mins} mins)</div>
          <span class="badge-tag badge-cost">${act.cost > 0 ? "₹" + act.cost : "Free Entry"}</span>
        </div>
        <div class="step-title">${act.place.name}</div>
        <div style="font-size:0.8rem; color:#475569;">${act.place.description || ""}</div>
        <div class="step-badges">
          <span class="badge-tag badge-open">✓ Operating Window: ${act.place.opening_time} - ${act.place.closing_time}</span>
          <span class="badge-tag badge-buffer">+${act.buffer_mins}m Transition Buffer</span>
          <span class="badge-tag badge-delay">★ ${act.place.rating} Rating</span>
        </div>
      `;
      timelineContainer.appendChild(step);
    });

    // Meals
    day.meals.forEach((meal) => {
      const step = document.createElement("div");
      step.className = "timeline-step step-dhaba";
      step.innerHTML = `
        <div class="step-header">
          <div class="step-time">🍽️ ${meal.time_slot} &bull; ${meal.meal_type.toUpperCase()}</div>
          <span class="badge-tag badge-cost">~₹${meal.estimated_cost}</span>
        </div>
        <div class="step-title">${meal.restaurant.name}</div>
        <div style="font-size:0.8rem; color:#475569;">${meal.restaurant.specialty || meal.restaurant.location}</div>
        <div class="step-badges">
          <span class="badge-tag ${meal.restaurant.is_dhaba ? 'badge-delay' : 'badge-open'}">${meal.restaurant.is_dhaba ? 'Roadside Highway Dhaba' : 'Local Dining'}</span>
          <span class="badge-tag badge-buffer">★ ${meal.restaurant.rating}</span>
        </div>
        <div class="step-actions">
          <button class="btn-book" onclick="openBookingModal('restaurant', '${meal.restaurant.id}', '${meal.restaurant.name}', '${meal.time_slot}', ${meal.estimated_cost})">
            Reserve Table / Dhaba Stop
          </button>
        </div>
      `;
      timelineContainer.appendChild(step);
    });

    // Overnight Stay
    if (day.overnight_stay) {
      const stay = day.overnight_stay;
      const step = document.createElement("div");
      step.className = "timeline-step step-hotel";
      step.innerHTML = `
        <div class="step-header">
          <div class="step-time">🏨 Overnight Stay &bull; Check-in 14:00</div>
          <span class="badge-tag badge-cost">₹${stay.total_cost}</span>
        </div>
        <div class="step-title">${stay.hotel.name}</div>
        <div style="font-size:0.8rem; color:#475569;">${stay.hotel.location} &bull; Amenities: ${stay.hotel.amenities.join(", ")}</div>
        <div class="step-badges">
          <span class="badge-tag badge-open">★ ${stay.hotel.rating} Rating</span>
          <span class="badge-tag badge-buffer">Tier: ${stay.hotel.tier}</span>
        </div>
        <div class="step-actions">
          <button class="btn-book" onclick="openBookingModal('hotel', '${stay.hotel.id}', '${stay.hotel.name}', '${day.date}', ${stay.total_cost})">
            Book Room
          </button>
        </div>
      `;
      timelineContainer.appendChild(step);
    }
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

  // 1. Plot Origin Marker (🟢)
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
        <div style="color:#10b981; font-weight:800; font-size:0.8rem; letter-spacing:0.04em;">🟢 TRIP ORIGIN (START)</div>
        <div style="font-size:1.05rem; font-weight:700; margin:4px 0 2px;">${origName}</div>
        <div style="font-size:0.8rem; color:#475569;">Start Date: <strong>${currentPlan.input_params.start_date}</strong></div>
        <div style="font-size:0.8rem; color:#475569;">Departure: <strong>${currentPlan.input_params.start_time_of_day}</strong></div>
      </div>
    `)
    .addTo(routeLayerGroup);

  // 2. Plot In-Between Stopover Markers (🟡)
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
          <div style="color:#f59e0b; font-weight:800; font-size:0.8rem; letter-spacing:0.04em;">🟡 IN-BETWEEN STOPOVER</div>
          <div style="font-size:1.05rem; font-weight:700; margin:4px 0 2px;">${stop.location}</div>
          <div style="font-size:0.8rem; color:#475569;">Allocated Time: <strong>${stayText}</strong></div>
        </div>
      `)
      .addTo(routeLayerGroup);
  });

  // 3. Plot Destination Marker (🔴)
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
        <div style="color:#ef4444; font-weight:800; font-size:0.8rem; letter-spacing:0.04em;">🔴 FINAL DESTINATION</div>
        <div style="font-size:1.05rem; font-weight:700; margin:4px 0 2px;">${destName}</div>
        <div style="font-size:0.8rem; color:#475569;">Trip Deadline: <strong>${currentPlan.input_params.end_date}</strong></div>
      </div>
    `)
    .addTo(routeLayerGroup);

  // 4. Plot Sightseeing Attractions (🔵)
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
              <div style="color:#3b82f6; font-weight:700; font-size:0.82rem;">🏛️ ${act.place.location} Attraction</div>
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
  const mapModeIcons = { train: "🚆", bus: "🚌", driving: "🚗", shared_cab: "🛺" };
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
      const icon = mapModeIcons[leg.selected_mode] || "🚗";
      const modeName = mapModeTitles[leg.selected_mode] || leg.selected_mode;

      const badgeDiv = L.divIcon({
        className: "map-transit-icon-container",
        html: `<div class="map-transit-badge mode-${leg.selected_mode}" title="${leg.from_place} to ${leg.to_place} via ${modeName}"><span class="transit-emoji">${icon}</span></div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
        popupAnchor: [0, -18]
      });

      const hubsContent = leg.departure_hub
        ? `<div class="transit-popup-hubs">🚉 <strong>Hubs:</strong> ${leg.departure_hub} ➔ ${leg.arrival_hub}</div>`
        : "";

      const ticketsContent = leg.ticket_cost > 0
        ? `<div>🎟️ <strong>Intercity Tickets:</strong> ₹${leg.ticket_cost.toLocaleString()}</div>`
        : "";

      const feederContent = leg.local_transit_cost > 0
        ? `<div>🛺 <strong>Local Feeder (${leg.local_vehicle_type || 'Shared Auto'}):</strong> ₹${leg.local_transit_cost.toLocaleString()}</div>`
        : "";

      const marker = L.marker(midCoord, { icon: badgeDiv }).bindPopup(`
        <div class="transit-popup-card">
          <div class="transit-popup-header">
            <span style="font-size:1.2rem;">${icon}</span>
            <span>Leg ${lIdx + 1}: ${leg.from_place} ➔ ${leg.to_place}</span>
          </div>
          <div class="transit-popup-meta">Mode: <strong>${modeName}</strong> &bull; ${leg.distance_km} km &bull; ~${leg.buffered_duration_hours} hrs</div>
          ${hubsContent}
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
      const retIcon = mapModeIcons[retTransit.mode] || "🚗";
      const retName = mapModeTitles[retTransit.mode] || retTransit.mode;

      const retBadgeDiv = L.divIcon({
        className: "map-transit-icon-container",
        html: `<div class="map-transit-badge mode-${retTransit.mode}" title="Return Journey to ${origName} via ${retName}"><span class="transit-emoji">${retIcon}</span></div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
        popupAnchor: [0, -18]
      });

      const retHubs = retTransit.departure_hub
        ? `<div class="transit-popup-hubs">🚉 <strong>Hubs:</strong> ${retTransit.departure_hub} ➔ ${retTransit.arrival_hub}</div>`
        : "";

      const retTickets = retTransit.ticket_cost > 0
        ? `<div>🎟️ <strong>Return Tickets:</strong> ₹${retTransit.ticket_cost.toLocaleString()}</div>`
        : "";

      const retFeeder = retTransit.local_transit_cost > 0
        ? `<div>🛺 <strong>Shared Auto Feeder:</strong> ₹${retTransit.local_transit_cost.toLocaleString()}</div>`
        : "";

      const retMarker = L.marker(returnMid, { icon: retBadgeDiv }).bindPopup(`
        <div class="transit-popup-card">
          <div class="transit-popup-header">
            <span style="font-size:1.2rem;">${retIcon}</span>
            <span>🔄 Return: ${destName} ➔ ${origName}</span>
          </div>
          <div class="transit-popup-meta">Mode: <strong>${retName}</strong> &bull; ${retTransit.distance_km} km &bull; ~${retTransit.duration_hours} hrs</div>
          ${retHubs}
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
        <span class="title">🚗 Total Transport</span>
        <span class="amount">₹${(cost.transport || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">🏨 Stays</span>
        <span class="amount">₹${(cost.stays || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">🍲 Food & Dhabas</span>
        <span class="amount">₹${(cost.food || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">🎟️ Sight Tickets</span>
        <span class="amount">₹${(cost.activities || 0).toLocaleString()}</span>
      </div>
      <div class="cost-tile">
        <span class="title">🛡️ Buffer Reserve</span>
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
          <span class="sub-icon">🎟️</span>
          <div class="sub-info">
            <span class="sub-label">Intercity Rail / Bus Tickets</span>
            <span class="sub-amount">₹${ticketCost.toLocaleString()}</span>
          </div>
        </div>
        <div class="subbreakdown-item">
          <span class="sub-icon">🛺</span>
          <div class="sub-info">
            <span class="sub-label">Local Shared Vehicles (Autos & Feeder Cabs)</span>
            <span class="sub-amount">₹${localSharedCost.toLocaleString()}</span>
          </div>
        </div>
        <div class="subbreakdown-item">
          <span class="sub-icon">⛽</span>
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
    <div style="font-size:0.78rem; color:#64748b; margin-top:8px;">Instant reservation simulated via SmartRoute Hospitality Engine.</div>
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
    alert(`🎉 Booking Confirmed!\nConfirmation Code: ${data.confirmation_code}\nItem: ${data.item_name}`);
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
