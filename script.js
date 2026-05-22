/**
 * FuelGuard AI — Frontend Logic
 * Handles API communication, UI updates, charts, filtering, and notifications.
 */

// ── Configuration ──────────────────────────────────────────────
// Use relative paths so API calls work on both Vercel and local dev.
// Locally with uvicorn: override this to "http://localhost:8000" if serving
// the HTML file directly from the filesystem.
const API_BASE = "";

// ── State ──────────────────────────────────────────────────────
let allTransactions = [];
let currentFilter = "all";
let fraudChartInstance = null;
let shortageChartInstance = null;

// ── Initialization ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  checkBackendStatus();
  initCharts();

  // Enter key triggers simulation
  document.getElementById("fuelInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") simulateTransaction();
  });

  // Smooth-scroll for nav links
  document.querySelectorAll(".header-nav a").forEach((link) => {
    link.addEventListener("click", function () {
      document
        .querySelectorAll(".header-nav a")
        .forEach((l) => l.classList.remove("active"));
      this.classList.add("active");
    });
  });
});

// ── Backend Health Check ───────────────────────────────────────
async function checkBackendStatus() {
  const dot = document.getElementById("statusDot");
  const text = document.getElementById("statusText");
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    const data = await res.json();
    dot.classList.remove("offline");
    text.textContent = data.status;
  } catch {
    dot.classList.add("offline");
    text.textContent = "Backend offline — start the server to begin";
  }
}

// ── Toast Notifications ────────────────────────────────────────
function showToast(message, type = "") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = "toast visible " + type;
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove("visible");
  }, 3500);
}

// ── Button Loading States ──────────────────────────────────────
function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (loading) {
    btn.classList.add("loading");
    btn.disabled = true;
  } else {
    btn.classList.remove("loading");
    btn.disabled = false;
  }
}

// ── Simulate Transaction ───────────────────────────────────────
async function simulateTransaction() {
  const input = document.getElementById("fuelInput");
  const value = parseFloat(input.value);

  // Validation
  if (!input.value || isNaN(value)) {
    showToast("Please enter a valid fuel amount.", "error");
    input.focus();
    return;
  }
  if (value <= 0) {
    showToast("Fuel amount must be greater than zero.", "error");
    input.focus();
    return;
  }
  if (value > 500) {
    showToast("Fuel amount seems unrealistic (max 500 L).", "error");
    input.focus();
    return;
  }

  setLoading("btnSimulate", true);
  try {
    const res = await fetch(`${API_BASE}/api/simulate-transaction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requested_fuel: value }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Simulation failed");
    }

    const data = await res.json();
    displayResult(data);
    await refreshAnalytics();
    await refreshTransactions();
    showToast("Transaction simulated successfully", "success");
  } catch (err) {
    showToast(err.message || "Could not reach backend", "error");
  } finally {
    setLoading("btnSimulate", false);
  }
}

// ── Display Result ─────────────────────────────────────────────
function displayResult(data) {
  const panel = document.getElementById("resultPanel");
  const grid = document.getElementById("resultGrid");

  const fraudClass = data.fraud_detected ? "fraud" : "safe";
  const riskClass =
    data.risk_level === "High"
      ? "fraud"
      : data.risk_level === "Medium"
      ? "medium"
      : "safe";

  grid.innerHTML = `
    <div class="result-item">
      <div class="label">Transaction ID</div>
      <div class="value">#${data.transaction_id}</div>
    </div>
    <div class="result-item">
      <div class="label">Requested Fuel</div>
      <div class="value">${data.requested_fuel} L</div>
    </div>
    <div class="result-item">
      <div class="label">Delivered Fuel</div>
      <div class="value">${data.delivered_fuel} L</div>
    </div>
    <div class="result-item">
      <div class="label">Difference</div>
      <div class="value">${data.difference} L</div>
    </div>
    <div class="result-item">
      <div class="label">Shortage</div>
      <div class="value">${data.shortage_percentage}%</div>
    </div>
    <div class="result-item">
      <div class="label">Fraud Status</div>
      <div class="value ${fraudClass}">${data.fraud_detected ? "FRAUD DETECTED" : "SAFE"}</div>
    </div>
    <div class="result-item">
      <div class="label">Risk Level</div>
      <div class="value ${riskClass}">${data.risk_level}</div>
    </div>
    <div class="result-item">
      <div class="label">Risk Score</div>
      <div class="value">${data.risk_score}/100</div>
    </div>
  `;

  panel.classList.add("visible");
}

// ── Refresh Analytics ──────────────────────────────────────────
async function refreshAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    const data = await res.json();

    document.getElementById("statTotal").textContent = data.total_transactions;
    document.getElementById("statFraud").textContent = data.fraud_transactions;
    document.getElementById("statSafe").textContent = data.safe_transactions;
    document.getElementById("statFraudPct").textContent =
      data.fraud_percentage + "%";
    document.getElementById("statAvgShortage").textContent =
      data.average_shortage + "%";
    document.getElementById("statHighShortage").textContent =
      data.highest_shortage + "%";

    updateCharts(data);
  } catch {
    // Silently fail — analytics not critical
  }
}

// ── Refresh Transactions ───────────────────────────────────────
async function refreshTransactions() {
  try {
    const res = await fetch(`${API_BASE}/api/transactions`);
    allTransactions = await res.json();
    filterTable();
  } catch {
    // Silently fail
  }
}

// ── Render Transaction Table ───────────────────────────────────
function renderTable(transactions) {
  const tbody = document.getElementById("txTableBody");

  if (transactions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8">
          <div class="empty-state">
            <div class="empty-icon">📋</div>
            No transactions match your criteria.
          </div>
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = transactions
    .map((t) => {
      const fraudBadge = t.fraud_detected
        ? '<span class="badge fraud">Fraud</span>'
        : '<span class="badge safe">Safe</span>';

      const riskClass =
        t.risk_level === "High"
          ? "high"
          : t.risk_level === "Medium"
          ? "medium"
          : "low";

      return `
      <tr>
        <td><strong>#${t.transaction_id}</strong></td>
        <td>${t.requested_fuel} L</td>
        <td>${t.delivered_fuel} L</td>
        <td>${t.difference} L</td>
        <td>${t.shortage_percentage}%</td>
        <td>${fraudBadge}</td>
        <td><span class="badge ${riskClass}">${t.risk_level}</span></td>
        <td>${t.timestamp}</td>
      </tr>`;
    })
    .join("");
}

// ── Filter & Search ────────────────────────────────────────────
function setFilter(filter, btn) {
  currentFilter = filter;
  document
    .querySelectorAll(".filter-btn")
    .forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  filterTable();
}

function filterTable() {
  const searchId = document.getElementById("searchInput").value.trim();
  let filtered = allTransactions;

  // Apply fraud/safe filter
  if (currentFilter === "fraud") {
    filtered = filtered.filter((t) => t.fraud_detected);
  } else if (currentFilter === "safe") {
    filtered = filtered.filter((t) => !t.fraud_detected);
  }

  // Apply ID search
  if (searchId) {
    filtered = filtered.filter((t) =>
      String(t.transaction_id).includes(searchId)
    );
  }

  renderTable(filtered);
}

// ── Charts ─────────────────────────────────────────────────────
function initCharts() {
  const commonFont = {
    family: "'Inter', sans-serif",
    size: 12,
    weight: "500",
  };

  Chart.defaults.font = commonFont;
  Chart.defaults.color = "#5f6368";

  // Fraud vs Safe — Doughnut
  const fraudCtx = document.getElementById("fraudChart").getContext("2d");
  fraudChartInstance = new Chart(fraudCtx, {
    type: "doughnut",
    data: {
      labels: ["Fraud", "Safe"],
      datasets: [
        {
          data: [0, 0],
          backgroundColor: ["#dc2626", "#16a34a"],
          borderWidth: 0,
          spacing: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "65%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { padding: 16, usePointStyle: true, pointStyleWidth: 10 },
        },
      },
    },
  });

  // Shortage Trends — Line
  const shortageCtx = document
    .getElementById("shortageChart")
    .getContext("2d");
  shortageChartInstance = new Chart(shortageCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Shortage %",
          data: [],
          borderColor: "#2563eb",
          backgroundColor: "rgba(37,99,235,0.08)",
          fill: true,
          tension: 0.35,
          pointRadius: 3,
          pointBackgroundColor: "#2563eb",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        x: {
          grid: { display: false },
          title: { display: true, text: "Transaction ID" },
        },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(0,0,0,0.04)" },
          title: { display: true, text: "Shortage %" },
        },
      },
    },
  });
}

function updateCharts(analytics) {
  // Doughnut
  fraudChartInstance.data.datasets[0].data = [
    analytics.fraud_transactions,
    analytics.safe_transactions,
  ];
  fraudChartInstance.update();

  // Line — derive from allTransactions (oldest → newest)
  const sorted = [...allTransactions].reverse();
  shortageChartInstance.data.labels = sorted.map((t) => `#${t.transaction_id}`);
  shortageChartInstance.data.datasets[0].data = sorted.map(
    (t) => t.shortage_percentage
  );
  shortageChartInstance.update();
}

// ── Generate Report ────────────────────────────────────────────
async function generateReport() {
  setLoading("btnReport", true);
  try {
    const res = await fetch(`${API_BASE}/api/generate-report`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Report generation failed");
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "FuelGuard_Report.pdf";
    a.click();
    URL.revokeObjectURL(url);
    showToast("Report downloaded successfully", "success");
  } catch (err) {
    showToast(err.message || "Could not generate report", "error");
  } finally {
    setLoading("btnReport", false);
  }
}

// ── Export JSON ────────────────────────────────────────────────
async function exportJSON() {
  setLoading("btnExport", true);
  try {
    const res = await fetch(`${API_BASE}/api/export-json`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Export failed");
    }

    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fuelguard_transactions.json";
    a.click();
    URL.revokeObjectURL(url);
    showToast("JSON exported successfully", "success");
  } catch (err) {
    showToast(err.message || "Could not export JSON", "error");
  } finally {
    setLoading("btnExport", false);
  }
}
