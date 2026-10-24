/**
 * ParkSmart: Smart Parking Management System — Vanilla Frontend Engine
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Element References
  const clockEl = document.getElementById("facilityClock");
  const totalSpacesEl = document.getElementById("metricTotalSpaces");
  const availableSpacesEl = document.getElementById("metricAvailableSpaces");
  const occupiedSpacesEl = document.getElementById("metricOccupiedSpaces");
  const occupancyPercentageEl = document.getElementById("metricOccupancyPercentage");
  const occupancyProgressBar = document.getElementById("occupancyProgressBar");
  const activeSessionsCountEl = document.getElementById("metricActiveSessions");

  const parkingGridSectionA = document.getElementById("parkingGridSectionA");
  const parkingGridSectionB = document.getElementById("parkingGridSectionB");
  const activeSessionsTbody = document.getElementById("activeSessionsTbody");
  const historyTbody = document.getElementById("historyTbody");

  // Filters & Controls
  const slotSearchInput = document.getElementById("slotSearchInput");
  const statusFilterSelect = document.getElementById("statusFilterSelect");
  const typeFilterSelect = document.getElementById("typeFilterSelect");
  const sortSelect = document.getElementById("sortSelect");

  // History Filters
  const historySearchInput = document.getElementById("historySearchInput");
  const historyStartTime = document.getElementById("historyStartTime");
  const historyEndTime = document.getElementById("historyEndTime");
  const btnFilterHistory = document.getElementById("btnFilterHistory");
  const btnResetHistory = document.getElementById("btnResetHistory");

  // Modals & Forms
  const entryModal = document.getElementById("entryModal");
  const exitModal = document.getElementById("exitModal");
  const slotDetailModal = document.getElementById("slotDetailModal");
  const vehicleEntryForm = document.getElementById("vehicleEntryForm");
  const vehicleExitForm = document.getElementById("vehicleExitForm");

  // Quick Action Buttons
  const btnOpenEntry = document.getElementById("btnOpenEntry");
  const btnOpenExit = document.getElementById("btnOpenExit");
  const btnResetDb = document.getElementById("btnResetDb");

  // Tab Switching
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      const tabId = btn.getAttribute("data-tab");
      const targetContent = document.getElementById(tabId);
      if (targetContent) targetContent.classList.add("active");

      if (tabId === "historyTab") {
        loadHistory();
      } else if (tabId === "activeSessionsTab") {
        loadActiveSessions();
      } else {
        loadSlots();
      }
    });
  });

  // Clock Update
  function updateClock() {
    const now = new Date();
    if (clockEl) {
      clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
  }
  setInterval(updateClock, 1000);
  updateClock();

  // Toast Notification System
  function showToast(title, message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    let iconSvg = "";
    if (type === "success") {
      iconSvg = `<svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (type === "error") {
      iconSvg = `<svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`;
    } else {
      iconSvg = `<svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    }

    toast.innerHTML = `
      ${iconSvg}
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-msg">${message}</div>
      </div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 250);
    }, 4000);
  }

  // Load Occupancy Stats
  async function loadStats() {
    try {
      const res = await fetch("/api/stats");
      if (!res.ok) throw new Error("Failed to load statistics");
      const stats = await res.json();

      if (totalSpacesEl) totalSpacesEl.textContent = stats.total_spaces;
      if (availableSpacesEl) availableSpacesEl.textContent = stats.available_spaces;
      if (occupiedSpacesEl) occupiedSpacesEl.textContent = stats.occupied_spaces;
      if (occupancyPercentageEl) occupancyPercentageEl.textContent = `${stats.occupancy_percentage}%`;
      if (occupancyProgressBar) occupancyProgressBar.style.width = `${stats.occupancy_percentage}%`;
      if (activeSessionsCountEl) activeSessionsCountEl.textContent = stats.active_sessions;
    } catch (err) {
      console.error("Error loading stats:", err);
    }
  }

  // Get vehicle / slot icon SVG
  function getSlotIcon(type, isOccupied) {
    if (isOccupied) {
      return `<svg class="slot-icon-svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.85 7h10.29l1.04 3H5.81l1.04-3zM19 17H5v-4.66l.12-.34h13.77l.11.34V17z"/>
        <circle cx="7.5" cy="14.5" r="1.5"/><circle cx="16.5" cy="14.5" r="1.5"/>
      </svg>`;
    }
    if (type === "ev") {
      return `<svg class="slot-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>`;
    }
    return `<svg class="slot-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="3" width="18" height="18" rx="3"/>
      <path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>
    </svg>`;
  }

  // Render Slot Card Tile
  function createSlotTile(slot) {
    const isOccupied = slot.is_occupied === 1;
    const tile = document.createElement("div");
    tile.className = `slot-tile ${isOccupied ? "occupied" : "available"}`;
    tile.setAttribute("data-slot-number", slot.slot_number);

    const activeSession = slot.active_session;
    const plateText = activeSession ? activeSession.plate_number : "";

    tile.innerHTML = `
      <div class="slot-top">
        <span class="slot-number">${slot.slot_number}</span>
        <span class="slot-badge ${slot.slot_type}">${slot.slot_type}</span>
      </div>
      <div class="slot-center">
        ${getSlotIcon(slot.slot_type, isOccupied)}
      </div>
      <div class="slot-bottom">
        <span class="status-tag">
          ${isOccupied ? "OCCUPIED" : "AVAILABLE"}
        </span>
        ${isOccupied && plateText ? `<span class="plate-badge">${plateText}</span>` : ""}
      </div>
    `;

    tile.addEventListener("click", () => {
      openSlotModal(slot.slot_number);
    });

    return tile;
  }

  // Load Parking Map Slots
  async function loadSlots() {
    try {
      const search = slotSearchInput ? slotSearchInput.value.trim() : "";
      const status = statusFilterSelect ? statusFilterSelect.value : "all";
      const slotType = typeFilterSelect ? typeFilterSelect.value : "all";
      const sortVal = sortSelect ? sortSelect.value : "slot_number_asc";

      let sortBy = "slot_number";
      let order = "asc";
      if (sortVal === "slot_number_desc") {
        sortBy = "slot_number";
        order = "desc";
      } else if (sortVal === "slot_type") {
        sortBy = "slot_type";
        order = "asc";
      } else if (sortVal === "status") {
        sortBy = "status";
        order = "desc";
      }

      const params = new URLSearchParams({
        search,
        status,
        slot_type: slotType,
        sort_by: sortBy,
        order
      });

      const res = await fetch(`/api/slots?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to load parking slots");
      const slots = await res.json();

      if (parkingGridSectionA) parkingGridSectionA.innerHTML = "";
      if (parkingGridSectionB) parkingGridSectionB.innerHTML = "";

      let countA = 0;
      let countB = 0;

      slots.forEach(slot => {
        const tile = createSlotTile(slot);
        if (slot.slot_number.startsWith("A-")) {
          if (parkingGridSectionA) parkingGridSectionA.appendChild(tile);
          countA++;
        } else {
          if (parkingGridSectionB) parkingGridSectionB.appendChild(tile);
          countB++;
        }
      });

      const statsA = document.getElementById("statsSectionA");
      const statsB = document.getElementById("statsSectionB");
      if (statsA) statsA.textContent = `${countA} slots`;
      if (statsB) statsB.textContent = `${countB} slots`;
    } catch (err) {
      console.error("Error loading slots:", err);
      showToast("Error", "Could not fetch parking slots", "error");
    }
  }

  // Load Active Sessions Table
  async function loadActiveSessions() {
    try {
      const res = await fetch("/api/sessions/active");
      if (!res.ok) throw new Error("Failed to load active sessions");
      const sessions = await res.json();

      if (!activeSessionsTbody) return;
      activeSessionsTbody.innerHTML = "";

      if (sessions.length === 0) {
        activeSessionsTbody.innerHTML = `
          <tr>
            <td colspan="6" class="empty-state">
              <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>
              </svg>
              <div>No vehicles currently parked in facility</div>
            </td>
          </tr>
        `;
        return;
      }

      sessions.forEach(sess => {
        const tr = document.createElement("tr");
        const entryTime = new Date(sess.entry_time);
        const elapsedMinutes = Math.max(1, Math.round((new Date() - entryTime) / 60000));

        tr.innerHTML = `
          <td><strong>${sess.session_id}</strong></td>
          <td><span class="slot-badge standard">${sess.slot_number}</span></td>
          <td><span class="plate-pill">${sess.plate_number}</span></td>
          <td><span class="slot-badge ${sess.vehicle_type}">${sess.vehicle_type}</span></td>
          <td>${entryTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} (${elapsedMinutes}m ago)</td>
          <td>
            <button class="btn btn-secondary btn-quick-exit" data-slot="${sess.slot_number}" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;">
              Release / Exit
            </button>
          </td>
        `;

        const btnExit = tr.querySelector(".btn-quick-exit");
        if (btnExit) {
          btnExit.addEventListener("click", () => {
            openExitModal(sess.slot_number, sess.plate_number);
          });
        }

        activeSessionsTbody.appendChild(tr);
      });
    } catch (err) {
      console.error("Error loading active sessions:", err);
    }
  }

  // Load Parking History
  async function loadHistory() {
    try {
      const search = historySearchInput ? historySearchInput.value.trim() : "";
      const startTime = historyStartTime ? historyStartTime.value : "";
      const endTime = historyEndTime ? historyEndTime.value : "";

      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (startTime) params.append("start_time", startTime);
      if (endTime) params.append("end_time", endTime);

      const res = await fetch(`/api/sessions/history?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to load parking history");
      const history = await res.json();

      if (!historyTbody) return;
      historyTbody.innerHTML = "";

      if (history.length === 0) {
        historyTbody.innerHTML = `
          <tr>
            <td colspan="7" class="empty-state">
              <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              <div>No parking records found matching criteria</div>
            </td>
          </tr>
        `;
        return;
      }

      history.forEach(h => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${h.session_id}</td>
          <td><strong>${h.slot_number}</strong></td>
          <td><span class="plate-pill">${h.plate_number}</span></td>
          <td><span class="slot-badge ${h.vehicle_type}">${h.vehicle_type}</span></td>
          <td>${h.entry_time.replace("T", " ")}</td>
          <td>${h.exit_time ? h.exit_time.replace("T", " ") : "—"}</td>
          <td><strong style="color: var(--accent-primary);">$${h.fee ? Number(h.fee).toFixed(2) : '0.00'}</strong></td>
        `;
        historyTbody.appendChild(tr);
      });
    } catch (err) {
      console.error("Error loading history:", err);
      showToast("Error", "Could not fetch parking history", "error");
    }
  }

  // Modal Handlers
  function openModal(modal) {
    if (modal) modal.classList.add("active");
  }
  function closeModal(modal) {
    if (modal) modal.classList.remove("active");
  }

  document.querySelectorAll(".close-btn, .btn-modal-cancel").forEach(btn => {
    btn.addEventListener("click", () => {
      closeModal(entryModal);
      closeModal(exitModal);
      closeModal(slotDetailModal);
    });
  });

  // Open Vehicle Entry Modal
  if (btnOpenEntry) {
    btnOpenEntry.addEventListener("click", () => {
      if (vehicleEntryForm) vehicleEntryForm.reset();
      openModal(entryModal);
    });
  }

  // Open Vehicle Exit Modal
  function openExitModal(slotNumber = "", plateNumber = "") {
    if (vehicleExitForm) {
      vehicleExitForm.reset();
      const input = document.getElementById("exitIdentifierInput");
      if (input) input.value = slotNumber || plateNumber || "";
    }
    openModal(exitModal);
  }

  if (btnOpenExit) {
    btnOpenExit.addEventListener("click", () => {
      openExitModal();
    });
  }

  // Open Slot Details Modal
  async function openSlotModal(slotNumber) {
    try {
      const res = await fetch(`/api/slots/${slotNumber}`);
      if (!res.ok) throw new Error("Failed to load slot details");
      const slot = await res.json();

      document.getElementById("detailSlotNumber").textContent = slot.slot_number;
      document.getElementById("detailSection").textContent = slot.section;
      document.getElementById("detailType").textContent = slot.slot_type.toUpperCase();

      const statusEl = document.getElementById("detailStatus");
      const isOcc = slot.is_occupied === 1;
      statusEl.textContent = isOcc ? "OCCUPIED" : "AVAILABLE";
      statusEl.style.color = isOcc ? "var(--accent-red)" : "var(--accent-primary)";

      const vehicleInfoSection = document.getElementById("detailVehicleSection");
      const parkActionBtn = document.getElementById("btnDetailPark");
      const exitActionBtn = document.getElementById("btnDetailExit");

      if (isOcc && slot.active_session) {
        vehicleInfoSection.style.display = "block";
        document.getElementById("detailPlate").textContent = slot.active_session.plate_number;
        document.getElementById("detailVehicleType").textContent = slot.active_session.vehicle_type;
        document.getElementById("detailEntryTime").textContent = slot.active_session.entry_time.replace("T", " ");

        if (parkActionBtn) parkActionBtn.style.display = "none";
        if (exitActionBtn) {
          exitActionBtn.style.display = "inline-flex";
          exitActionBtn.onclick = () => {
            closeModal(slotDetailModal);
            openExitModal(slot.slot_number);
          };
        }
      } else {
        vehicleInfoSection.style.display = "none";
        if (exitActionBtn) exitActionBtn.style.display = "none";
        if (parkActionBtn) {
          parkActionBtn.style.display = "inline-flex";
          parkActionBtn.onclick = () => {
            closeModal(slotDetailModal);
            openModal(entryModal);
          };
        }
      }

      openModal(slotDetailModal);
    } catch (err) {
      console.error(err);
      showToast("Error", "Could not load slot details", "error");
    }
  }

  // Vehicle Entry Submission
  if (vehicleEntryForm) {
    vehicleEntryForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const plate = document.getElementById("entryPlateInput").value.trim().toUpperCase();
      const vType = document.getElementById("entryTypeSelect").value;
      const color = document.getElementById("entryColorInput").value.trim();
      const desc = document.getElementById("entryDescInput").value.trim();

      if (!plate) {
        showToast("Validation Error", "License plate is required", "error");
        return;
      }

      try {
        const res = await fetch("/api/vehicles/entry", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            plate_number: plate,
            vehicle_type: vType,
            color,
            description: desc
          })
        });

        const data = await res.json();
        if (!res.ok) {
          showToast("Entry Failed", data.error || "Allocation failed", "error");
          return;
        }

        showToast("Slot Allocated!", `Vehicle ${plate} assigned to slot ${data.slot.slot_number}`, "success");
        closeModal(entryModal);
        loadStats();
        loadSlots();
        loadActiveSessions();
      } catch (err) {
        console.error(err);
        showToast("Error", "Network or server failure", "error");
      }
    });
  }

  // Vehicle Exit Submission
  if (vehicleExitForm) {
    vehicleExitForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const identifier = document.getElementById("exitIdentifierInput").value.trim();

      if (!identifier) {
        showToast("Validation Error", "Slot number, license plate, or session ID required", "error");
        return;
      }

      try {
        const res = await fetch("/api/vehicles/exit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier })
        });

        const data = await res.json();
        if (!res.ok) {
          showToast("Exit Failed", data.error || "Exit processing failed", "error");
          return;
        }

        showToast("Vehicle Exited", `${data.message} • Fee: $${Number(data.session.fee).toFixed(2)}`, "success");
        closeModal(exitModal);
        loadStats();
        loadSlots();
        loadActiveSessions();
        loadHistory();
      } catch (err) {
        console.error(err);
        showToast("Error", "Network or server failure", "error");
      }
    });
  }

  // Reset Facility Data
  if (btnResetDb) {
    btnResetDb.addEventListener("click", async () => {
      if (!confirm("Are you sure you want to reset all parking bays to their initial state?")) return;
      try {
        const res = await fetch("/api/reset", { method: "POST" });
        if (!res.ok) throw new Error("Reset failed");
        showToast("System Reset", "Parking facility restored to initial seed", "warning");
        loadStats();
        loadSlots();
        loadActiveSessions();
        loadHistory();
      } catch (err) {
        showToast("Error", "Failed to reset facility", "error");
      }
    });
  }

  // Event Listeners for Filters
  if (slotSearchInput) slotSearchInput.addEventListener("input", () => loadSlots());
  if (statusFilterSelect) statusFilterSelect.addEventListener("change", () => loadSlots());
  if (typeFilterSelect) typeFilterSelect.addEventListener("change", () => loadSlots());
  if (sortSelect) sortSelect.addEventListener("change", () => loadSlots());

  if (btnFilterHistory) btnFilterHistory.addEventListener("click", () => loadHistory());
  if (btnResetHistory) {
    btnResetHistory.addEventListener("click", () => {
      if (historySearchInput) historySearchInput.value = "";
      if (historyStartTime) historyStartTime.value = "";
      if (historyEndTime) historyEndTime.value = "";
      loadHistory();
    });
  }

  // Initial Data Load
  loadStats();
  loadSlots();
  loadActiveSessions();
  loadHistory();
});
