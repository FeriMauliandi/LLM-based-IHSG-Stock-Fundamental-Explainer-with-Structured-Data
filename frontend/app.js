/**
 * AI IHSG Stock Screener & Fundamental Analyzer - Frontend Application
 */

// Auto-detect API Base URL:
// Only use origin if we are explicitly on port 8000 (FastAPI server).
// Otherwise (e.g. VS Code Live Server port 5500, file://, etc.), default to http://localhost:8000.
const API_BASE =
  window.location.port === "8000"
    ? window.location.origin
    : "http://localhost:8000";

// Format Helpers
function formatRupiah(value) {
  if (value === null || value === undefined) return "N/A";
  return (
    "Rp " + Number(value).toLocaleString("id-ID", { maximumFractionDigits: 0 })
  );
}

function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined) return "N/A";
  return Number(value).toLocaleString("id-ID", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined) return "N/A";
  return formatNumber(value, decimals) + "%";
}

// Global state for clipboard copy
let lastAiExplanation = "";
let lastCompareAi = "";

// ==========================================
// 1. INITIALIZATION & TAB SWITCHER
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  initTabs();
  initScreenerEvents();
  initAnalysisEvents();
  initComparisonEvents();
  initCopyButtons();
});

function initCopyButtons() {
  const btnCopyAi = document.getElementById("btn-copy-ai");
  const btnCopyAiText = document.getElementById("btn-copy-ai-text");

  btnCopyAi?.addEventListener("click", () => {
    if (!lastAiExplanation) return;
    navigator.clipboard.writeText(lastAiExplanation).then(() => {
      btnCopyAiText.textContent = "Tersalin!";
      setTimeout(() => {
        btnCopyAiText.textContent = "Salin Laporan";
      }, 2000);
    });
  });

  const btnCopyCompare = document.getElementById("btn-copy-compare-ai");
  const btnCopyCompareText = document.getElementById(
    "btn-copy-compare-ai-text",
  );

  btnCopyCompare?.addEventListener("click", () => {
    if (!lastCompareAi) return;
    navigator.clipboard.writeText(lastCompareAi).then(() => {
      btnCopyCompareText.textContent = "Tersalin!";
      setTimeout(() => {
        btnCopyCompareText.textContent = "Salin Putusan";
      }, 2000);
    });
  });
}

function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");
      switchTab(targetId);
    });
  });
}

function switchTab(tabId) {
  // Update Tab buttons
  document.querySelectorAll(".nav-tab").forEach((btn) => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
      btn.classList.remove("border-transparent");
    } else {
      btn.classList.remove("active");
      btn.classList.add("border-transparent");
    }
  });

  // Show target Pane
  document.querySelectorAll(".tab-pane").forEach((pane) => {
    if (pane.id === tabId) {
      pane.classList.remove("hidden");
    } else {
      pane.classList.add("hidden");
    }
  });

  if (window.lucide) {
    lucide.createIcons();
  }
}

// ==========================================
// 2. BACKEND HEALTH CHECK
// ==========================================
async function checkBackendHealth(showNotice = false) {
  const statusEl = document.getElementById("backend-status");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Backend offline");
    const data = await res.json();

    if (statusEl) {
      statusEl.className =
        "flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#0a1a02]/80 border border-[#4bfa14]/20 text-xs text-[#4bfa14]";
      statusEl.innerHTML = `
        <span class="w-2.5 h-2.5 rounded-full bg-[#4bfa14] pulse-green"></span>
        <span>API Online (Port 8000)</span>
        ${data.groq_configured ? '<span class="text-[10px] bg-[#4bfa14]/12 text-[#4bfa14] px-1.5 py-0.5 rounded font-mono border border-[#4bfa14]/22">Groq AI Active</span>' : ""}
      `;
    }
    if (showNotice) alert("Berhasil terhubung ke Backend FastAPI!");
  } catch (err) {
    if (statusEl) {
      statusEl.className =
        "flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-500/30 text-xs text-rose-300";
      statusEl.innerHTML = `
        <span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span>
        <span>API Offline (Jalankan python backend/main.py)</span>
      `;
    }
    if (showNotice) {
      alert(
        "Gagal menghubungi backend di http://localhost:8000. Pastikan server sudah jalan:\npython backend/main.py",
      );
    }
  }
}

// ==========================================
// 3. TAB 1: SCREENER (COMPACT 8-COLUMN TABLE)
// ==========================================
function initScreenerEvents() {
  const scoreSlider = document.getElementById("filter-score");
  const scoreLabel = document.getElementById("label-score");

  scoreSlider?.addEventListener("input", (e) => {
    scoreLabel.textContent = `${e.target.value} pt`;
  });

  // Presets
  document.querySelectorAll(".preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const preset = btn.getAttribute("data-preset");
      applyScreenerPreset(preset);
    });
  });

  // Run Screener
  document.getElementById("btn-run-screener")?.addEventListener("click", () => {
    runScreener();
  });
}

function applyScreenerPreset(preset) {
  const scoreSlider = document.getElementById("filter-score");
  const scoreLabel = document.getElementById("label-score");
  const peInput = document.getElementById("filter-pe");
  const roeInput = document.getElementById("filter-roe");
  const derInput = document.getElementById("filter-der");

  if (preset === "undervalued") {
    scoreSlider.value = 60;
    scoreLabel.textContent = "60 pt";
    peInput.value = 15.0;
    roeInput.value = 10.0;
    derInput.value = 1.2;
  } else if (preset === "dividen") {
    scoreSlider.value = 50;
    scoreLabel.textContent = "50 pt";
    peInput.value = 25.0;
    roeInput.value = 8.0;
    derInput.value = 2.0;
  } else if (preset === "bluechip") {
    scoreSlider.value = 65;
    scoreLabel.textContent = "65 pt";
    peInput.value = 30.0;
    roeInput.value = 12.0;
    derInput.value = 1.5;
  }

  runScreener();
}

async function runScreener() {
  const loading = document.getElementById("screener-loading");
  const container = document.getElementById("screener-results-container");
  const badgeCount = document.getElementById("screener-badge-count");

  const min_score = parseInt(document.getElementById("filter-score").value);
  const max_pe = parseFloat(document.getElementById("filter-pe").value);
  const min_roe = parseFloat(document.getElementById("filter-roe").value);
  const max_der = parseFloat(document.getElementById("filter-der").value);

  loading.classList.remove("hidden");
  container.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/api/screener/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ min_score, max_pe, min_roe, max_der }),
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `Server error (Status ${res.status})`);
    }

    const data = await res.json();
    renderScreenerTable(data.results);
    badgeCount.textContent = `${data.total_matched} dari ${data.total_screened} Saham`;
    container.classList.remove("hidden");
  } catch (err) {
    console.error("Screener Error:", err);
    alert(
      `Gagal menjalankan screener:\n${err.message}\n\nPastikan backend FastAPI sudah berjalan di:\n${API_BASE}`,
    );
  } finally {
    loading.classList.add("hidden");
  }
}

function renderScreenerTable(stocks) {
  const tbody = document.getElementById("screener-table-body");
  tbody.innerHTML = "";

  if (!stocks || stocks.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="px-6 py-10 text-center text-[#8ea7a1] font-mono text-xs">
          Tidak ada saham yang lolos kriteria. Coba longgarkan filter batas skor, PER, atau ROE.
        </td>
      </tr>
    `;
    return;
  }

  stocks.forEach((s) => {
    const tr = document.createElement("tr");
    tr.className =
      "hover:bg-[#4bfa14]/05 transition even:bg-[#111620]/50 odd:bg-[#0d1117]/30 group";

    // Score color badge
    let scoreColor = "text-emerald-400";
    if (s.score < 50) scoreColor = "text-rose-400";
    else if (s.score < 65) scoreColor = "text-amber-400";

    // Status valuation badge
    const valStatus = (s.valuation_status || s.valuation || "N/A").toString();
    let valBadge = "bg-[#131b2b] text-[#8ea7a1] border border-white/5";
    if (valStatus.includes("Undervalued")) {
      valBadge =
        "bg-[#4bfa14]/10 text-[#4bfa14] border border-[#4bfa14]/25 font-semibold";
    } else if (valStatus.includes("Overvalued")) {
      valBadge =
        "bg-rose-500/15 text-rose-400 border border-rose-500/30 font-semibold";
    } else {
      valBadge =
        "bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold";
    }

    const mosColor =
      s.mos !== null && s.mos >= 0 ? "text-emerald-400" : "text-rose-400";
    const mosText =
      s.mos !== null
        ? `(${(s.mos > 0 ? "+" : "") + formatPercent(s.mos)})`
        : "N/A";

    tr.innerHTML = `
      <td class="px-3.5 py-3 whitespace-nowrap border-b border-[#4bfa14]/08 border-r border-[#4bfa14]/05">
        <div class="flex items-center space-x-2.5">
          <span class="text-base">${s.badge || "🟢"}</span>
          <div>
            <div class="flex items-center gap-1.5">
              <span class="font-bold text-white font-mono tracking-wide text-sm">${s.ticker}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#8ea7a1]">${s.sector || "IDX"}</span>
            </div>
            <div class="text-[11px] text-[#8ea7a1] max-w-[165px] truncate" title="${s.company_name}">${s.company_name}</div>
          </div>
        </div>
      </td>
      <td class="px-3 py-3 text-right font-mono font-bold text-white whitespace-nowrap border-b border-[#4bfa14]/08 border-r border-[#4bfa14]/05">${formatRupiah(s.price)}</td>
      <td class="px-3 py-3 whitespace-nowrap border-b border-[#4bfa14]/08 border-r border-[#4bfa14]/05">
        <div class="flex items-center space-x-2">
          <div class="w-12 bg-slate-900 h-2 rounded-full overflow-hidden border border-white/10">
            <div class="h-2 rounded-full" style="background:#4bfa14;box-shadow:0 0 8px rgba(75,250,20,0.5);width:${s.score}%;"></div>
          </div>
          <span class="font-mono font-bold ${scoreColor}">${s.score} pt</span>
        </div>
        <div class="text-[10px] text-[#4d6963]">${s.category || ""}</div>
      </td>
      <td class="px-3 py-3 text-right font-mono text-xs whitespace-nowrap border-b border-[#4bfa14]/08 border-r border-[#4bfa14]/05">
        <span class="text-white font-semibold">${formatNumber(s.pe, 1)}x</span> / <span class="text-[#8ea7a1]">${formatNumber(s.pbv, 2)}x</span>
      </td>
      <td class="px-3 py-3 text-right font-mono text-xs whitespace-nowrap border-b border-[#4bfa14]/08 border-r border-[#4bfa14]/05">
        <div class="text-emerald-400 font-bold">${formatPercent(s.roe)}</div>
        <div class="text-[10px] text-amber-300 font-semibold">Div: ${formatPercent(s.dividend_yield)}</div>
      </td>
      <td class="px-3 py-3 text-right font-mono text-xs whitespace-nowrap border-b border-[#4bfa14]/10 border-r border-[#4bfa14]/06">
        <div class="font-bold text-[#4bfa14]">${formatRupiah(s.fair_value)}</div>
        <div class="text-[11px] font-bold ${mosColor}">${mosText}</div>
      </td>
      <td class="px-3 py-3 text-center whitespace-nowrap border-b border-[#4bfa14]/08 border-r border-[#4bfa14]/05">
        <span class="px-2.5 py-1 rounded-md text-[11px] ${valBadge}">
          ${valStatus}
        </span>
      </td>
      <td class="px-3.5 py-3 text-center whitespace-nowrap border-b border-[#4bfa14]/08">
        <button class="btn-analyze-row px-3 py-1.5 rounded-lg bg-[#4bfa14]/08 hover:bg-[#4bfa14] text-[#4bfa14] hover:text-black border border-[#4bfa14]/30 text-xs font-semibold transition shadow-sm" data-ticker="${s.ticker}">
          Analisis AI
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Attach click listener on row action buttons
  document.querySelectorAll(".btn-analyze-row").forEach((btn) => {
    btn.addEventListener("click", () => {
      const ticker = btn.getAttribute("data-ticker");
      document.getElementById("input-ticker").value = ticker;
      switchTab("tab-analysis");
      analyzeSingleStock(ticker);
    });
  });
}

// ==========================================
// 4. TAB 2: DETAIL ANALYSIS & AI (100% REPO ASLI)
// ==========================================
function initAnalysisEvents() {
  document
    .getElementById("btn-analyze-stock")
    ?.addEventListener("click", () => {
      const ticker = document.getElementById("input-ticker").value.trim();
      if (ticker) analyzeSingleStock(ticker);
    });

  document.querySelectorAll(".quick-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const ticker = chip.getAttribute("data-ticker");
      document.getElementById("input-ticker").value = ticker;
      analyzeSingleStock(ticker);
    });
  });
}

async function analyzeSingleStock(ticker) {
  const loading = document.getElementById("analysis-loading");
  const results = document.getElementById("analysis-results");
  const includeAi = document.getElementById("check-include-ai").checked;

  loading.classList.remove("hidden");
  results.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/api/stocks/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: ticker, include_ai: includeAi }),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Gagal menganalisis saham.");
    }

    const data = await res.json();
    renderStockDetail(data);
    results.classList.remove("hidden");
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    loading.classList.add("hidden");
  }
}

function renderStockDetail(data) {
  const m = data.metrics;
  const s = data.score_info;
  const v = data.valuation_info;

  // Header
  document.getElementById("stock-badge").textContent = s.badge || "🟢";
  document.getElementById("stock-company-name").textContent =
    data.company_name || data.ticker;
  document.getElementById("stock-ticker").textContent =
    data.symbol || data.ticker;
  document.getElementById("stock-sector").textContent =
    `Sektor: ${m.sector || "N/A"}`;
  document.getElementById("stock-industry").textContent =
    `Industri: ${m.industry || "N/A"}`;
  document.getElementById("stock-timestamp").textContent =
    `Dianalisis: ${data.timestamp}`;

  // 5 Key Cards
  document.getElementById("card-price").textContent = formatRupiah(m.price);
  document.getElementById("card-score").textContent = `${s.total_score} / 100`;
  document.getElementById("card-category").textContent = s.category;
  document.getElementById("card-fair-value").textContent = formatRupiah(
    v.fair_value,
  );
  document.getElementById("card-valuation-status").textContent =
    v.status || "N/A";

  const mosVal = v.margin_of_safety;
  const mosCard = document.getElementById("card-mos");
  if (mosVal !== null && mosVal !== undefined) {
    mosCard.textContent = (mosVal > 0 ? "+" : "") + formatPercent(mosVal);
    mosCard.className = `text-xl font-bold mt-1 font-mono ${mosVal >= 0 ? "text-emerald-400" : "text-rose-400"}`;
  } else {
    mosCard.textContent = "N/A";
  }

  document.getElementById("card-per-pbv").textContent =
    `${formatNumber(m.pe, 1)}x / ${formatNumber(m.pb, 2)}x`;

  // 4 Pillars Breakdown
  const pillars = s.pillars;
  const pProf = pillars["Profitabilitas"] || 0;
  const pVal = pillars["Valuasi"] || 0;
  const pSolv = pillars["Solvabilitas & Kas"] || 0;
  const pGrow = pillars["Pertumbuhan & Dividen"] || 0;

  document.getElementById("pillar-prof-val").textContent = `${pProf} / 25`;
  document.getElementById("pillar-prof-bar").style.width =
    `${(pProf / 25) * 100}%`;

  document.getElementById("pillar-val-val").textContent = `${pVal} / 25`;
  document.getElementById("pillar-val-bar").style.width =
    `${(pVal / 25) * 100}%`;

  document.getElementById("pillar-solv-val").textContent = `${pSolv} / 25`;
  document.getElementById("pillar-solv-bar").style.width =
    `${(pSolv / 25) * 100}%`;

  document.getElementById("pillar-grow-val").textContent = `${pGrow} / 25`;
  document.getElementById("pillar-grow-bar").style.width =
    `${(pGrow / 25) * 100}%`;

  // Reward/Penalty Details
  const detailsList = document.getElementById("score-details-list");
  detailsList.innerHTML = "";
  s.details.forEach((det) => {
    const li = document.createElement("li");
    li.textContent = det;
    detailsList.appendChild(li);
  });

  // AI Explanation Executive Report (Full Width & Modular Design)
  const aiCard = document.getElementById("ai-explanation-card");
  const traceAccordion = document.getElementById("agent-trace-accordion");
  const traceSteps = document.getElementById("agent-trace-steps");

  if (data.ai_explanation) {
    lastAiExplanation = data.ai_explanation;
    renderAiExecutiveReport(data);
    aiCard.classList.remove("hidden");

    // Populate Multi-Agent Trace if available
    if (
      data.agent_trace &&
      data.agent_trace.length > 0 &&
      traceAccordion &&
      traceSteps
    ) {
      traceSteps.innerHTML = "";
      data.agent_trace.forEach((step, idx) => {
        const stepDiv = document.createElement("div");
        stepDiv.className =
          "p-3.5 rounded-xl bg-[#090d14] border border-white/5 text-[#8ea7a1] space-y-1.5 transition hover:border-[#4bfa14]/20";
        stepDiv.innerHTML = `
          <div class="flex items-center justify-between text-xs font-semibold text-[#4bfa14] font-mono">
            <span class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-md bg-[#4bfa14]/15 text-[#4bfa14] border border-[#4bfa14]/30 flex items-center justify-center text-[10px] font-bold">${idx + 1}</span>
              <span>${step.agent || "Agent"}</span>
            </span>
            <span class="text-[10px] text-[#4d6963]">${step.timestamp || ""}</span>
          </div>
          <div class="text-[11px] text-[#8ea7a1] flex items-center gap-1.5">
            <span class="text-[#4d6963]">Action:</span>
            <span class="text-white font-medium">${step.action || "-"}</span>
          </div>
          <div class="text-xs text-white/90 bg-[#0e1420] p-3 rounded-lg border border-white/5 leading-relaxed font-mono whitespace-pre-wrap">${step.summary || ""}</div>
        `;
        traceSteps.appendChild(stepDiv);
      });
      traceAccordion.classList.remove("hidden");
    } else if (traceAccordion) {
      traceAccordion.classList.add("hidden");
    }
  } else {
    lastAiExplanation = "";
    aiCard.classList.add("hidden");
    if (traceAccordion) traceAccordion.classList.add("hidden");
  }

  // Signals Badges
  const sigList = document.getElementById("signals-list");
  sigList.innerHTML = "";
  data.signals.forEach((sig) => {
    const div = document.createElement("div");
    div.className =
      "px-3 py-2 rounded-xl bg-[#111620] border border-[#4bfa14]/10 text-[#8ba8a5] flex items-start space-x-2";
    div.innerHTML = `<span>${sig}</span>`;
    sigList.appendChild(div);
  });

  if (window.lucide) lucide.createIcons();
}

// ==========================================
// 4B. AI EXECUTIVE REPORT RENDERING ENGINE (FULL WIDTH & MODULAR)
// ==========================================

function safeParseMarkdown(text) {
  if (!text) return "";
  try {
    return window.marked ? marked.parse(text) : text;
  } catch (e) {
    return text;
  }
}

function getConvictionDetails(score) {
  const num = Number(score);
  if (isNaN(num)) {
    return {
      text: "Netral / Watchlist",
      colorClass: "text-[#4bfa14]",
      borderClass: "border-[#4bfa14]/30",
      bgClass: "bg-[#4bfa14]/10",
      percent: 65,
    };
  }
  if (num >= 8.0) {
    return {
      text: "High Conviction (Sangat Kuat)",
      colorClass: "text-emerald-400",
      borderClass: "border-emerald-500/30",
      bgClass: "bg-emerald-500/10",
      percent: Math.min(num * 10, 100),
    };
  } else if (num >= 6.5) {
    return {
      text: "Moderate-High (Menarik)",
      colorClass: "text-[#4bfa14]",
      borderClass: "border-[#4bfa14]/30",
      bgClass: "bg-[#4bfa14]/10",
      percent: num * 10,
    };
  } else if (num >= 5.0) {
    return {
      text: "Fair / Neutral (Konservatif)",
      colorClass: "text-amber-400",
      borderClass: "border-amber-500/30",
      bgClass: "bg-amber-500/10",
      percent: num * 10,
    };
  } else {
    return {
      text: "Speculative / Underweight (Waspada)",
      colorClass: "text-rose-400",
      borderClass: "border-rose-500/30",
      bgClass: "bg-rose-500/10",
      percent: Math.max(num * 10, 20),
    };
  }
}

function buildHeroBannerHtml(conviction, classification, ticker, companyName) {
  const convDetails =
    conviction !== null && conviction !== undefined
      ? getConvictionDetails(conviction)
      : null;

  return `
    <div class="ai-hero-card p-5 sm:p-6 mb-6">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        
        <!-- Left: Badges & Scores -->
        <div class="flex flex-wrap items-center gap-3.5">
          ${
            convDetails
              ? `
            <div class="conviction-meter-container">
              <div class="w-10 h-10 rounded-xl ${convDetails.bgClass} border ${convDetails.borderClass} flex items-center justify-center">
                <span class="conviction-score-badge ${convDetails.colorClass}">
                  ${Number(conviction).toFixed(1)}
                </span>
              </div>
              <div>
                <div class="text-[10px] text-[#4d6963] uppercase tracking-wider font-mono font-bold">Conviction Score</div>
                <div class="text-xs font-bold ${convDetails.colorClass} flex items-center gap-1.5">
                  <span>${convDetails.text}</span>
                  <span class="text-[10px] text-[#4d6963] font-mono">/ 10.0</span>
                </div>
              </div>
            </div>
          `
              : ""
          }

          ${
            classification
              ? `
            <div class="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-[#0e1420]/90 border border-[#4bfa14]/20 shadow-sm">
              <i data-lucide="award" class="w-4 h-4 text-[#4bfa14] shrink-0"></i>
              <div>
                <div class="text-[10px] text-[#4d6963] uppercase tracking-wider font-mono font-bold">Klasifikasi Strategis</div>
                <div class="text-xs font-bold text-white tracking-wide">
                  ${classification}
                </div>
              </div>
            </div>
          `
              : ""
          }
        </div>

        <!-- Right: Telemetry & StateGraph Consensus Status -->
        <div class="flex flex-wrap items-center gap-3 text-xs text-[#8ea7a1] font-mono pt-1 lg:pt-0">
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e1420] border border-white/5">
            <i data-lucide="network" class="w-3.5 h-3.5 text-[#4bfa14]"></i>
            <span class="text-white font-semibold">4 Agent StateGraph</span>
          </div>
          <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e1420] border border-white/5 text-[#8ea7a1]">
            <i data-lucide="clock" class="w-3.5 h-3.5 text-[#4bfa14]"></i>
            <span>~2-3 Menit Baca</span>
          </div>
        </div>

      </div>
    </div>
  `;
}

function buildSectionCardHtml(num, iconName, title, contentMarkdown) {
  const parsedContent = safeParseMarkdown(contentMarkdown || "");
  return `
    <div class="ai-section-card">
      <div class="ai-section-header">
        <div class="ai-section-title">
          <span class="ai-section-number">${num}</span>
          <i data-lucide="${iconName}" class="w-4 h-4 text-[#4bfa14]"></i>
          <span>${title}</span>
        </div>
      </div>
      <div class="ai-section-body">
        ${parsedContent}
      </div>
    </div>
  `;
}

function buildBullishBearishArenaHtml(bullishPoints, bearishPoints) {
  const bullItems = (bullishPoints || [])
    .map((p) => {
      const cleanText = p.replace(/^[-*•\s]+/, "").trim();
      return `
      <li class="ai-bullish-item">
        <i data-lucide="check-circle-2" class="w-4 h-4 text-[#4bfa14] shrink-0 mt-0.5"></i>
        <span>${cleanText}</span>
      </li>
    `;
    })
    .join("");

  const bearItems = (bearishPoints || [])
    .map((p) => {
      const cleanText = p.replace(/^[-*•\s]+/, "").trim();
      return `
      <li class="ai-bearish-item">
        <i data-lucide="alert-triangle" class="w-4 h-4 text-rose-400 shrink-0 mt-0.5"></i>
        <span>${cleanText}</span>
      </li>
    `;
    })
    .join("");

  return `
    <div class="my-6">
      <div class="flex items-center gap-2 mb-3.5">
        <span class="ai-section-number">06</span>
        <h4 class="font-extrabold text-white text-sm uppercase tracking-wider font-mono flex items-center gap-2">
          <i data-lucide="scale" class="w-4 h-4 text-[#4bfa14]"></i>
          <span>Keunggulan Utama vs Risiko Kunci (Risk-Reward Matrix)</span>
        </h4>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Bullish Column -->
        <div class="ai-bullish-card">
          <div class="flex items-center justify-between pb-2.5 mb-3.5 border-b border-[#4bfa14]/20">
            <div class="flex items-center gap-2 text-[#4bfa14] font-extrabold text-xs uppercase font-mono tracking-wider">
              <i data-lucide="trending-up" class="w-4 h-4"></i>
              <span>Faktor Pendorong (Bullish Drivers)</span>
            </div>
            <span class="px-2 py-0.5 rounded bg-[#4bfa14]/15 text-[#4bfa14] text-[10px] font-mono font-bold">Katalis Positif</span>
          </div>
          <ul class="space-y-2.5">
            ${
              bullItems ||
              "<li class='text-xs text-[#8ea7a1] italic'>Tidak ada katalis bullish terdaftar.</li>"
            }
          </ul>
        </div>

        <!-- Bearish Column -->
        <div class="ai-bearish-card">
          <div class="flex items-center justify-between pb-2.5 mb-3.5 border-b border-rose-500/20">
            <div class="flex items-center gap-2 text-rose-400 font-extrabold text-xs uppercase font-mono tracking-wider">
              <i data-lucide="shield-alert" class="w-4 h-4"></i>
              <span>Faktor Risiko (Bearish Risks)</span>
            </div>
            <span class="px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 text-[10px] font-mono font-bold">Perlu Dimonitor</span>
          </div>
          <ul class="space-y-2.5">
            ${
              bearItems ||
              "<li class='text-xs text-[#8ea7a1] italic'>Tidak ada risiko kunci terdaftar.</li>"
            }
          </ul>
        </div>
      </div>
    </div>
  `;
}

function buildVerdictBoxHtml(verdictText, conviction, classification) {
  const convDetails =
    conviction !== null && conviction !== undefined
      ? getConvictionDetails(conviction)
      : null;

  const parsedVerdict = safeParseMarkdown(verdictText || "");

  return `
    <div class="ai-verdict-box">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3.5 mb-4 border-b border-[#4bfa14]/20">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-[#35c40a] via-[#4bfa14] to-[#7dfc55] flex items-center justify-center text-black font-extrabold shadow-md shadow-[#4bfa14]/20">
            <i data-lucide="target" class="w-5 h-5 stroke-[2.5]"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="ai-section-number">07</span>
              <h4 class="font-black text-white text-base tracking-tight">Kesimpulan Objektif &amp; Profil Alokasi Investor</h4>
            </div>
            <p class="text-[11px] text-[#4bfa14]/90 font-mono">Chief Investment Officer (Lead Synthesis) Autonomous Verdict</p>
          </div>
        </div>

        ${
          convDetails
            ? `
          <div class="flex items-center gap-2">
            <span class="px-3.5 py-1.5 rounded-full ${convDetails.bgClass} border ${convDetails.borderClass} ${convDetails.colorClass} font-mono font-bold text-xs tracking-wide">
              Keyakinan: ${Number(conviction).toFixed(1)} / 10.0
            </span>
          </div>
        `
            : ""
        }
      </div>

      <div class="ai-section-body text-[#e6f5f0] text-sm sm:text-base leading-relaxed font-normal">
        ${parsedVerdict}
      </div>

      ${
        classification
          ? `
        <div class="mt-4 pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-[#8ea7a1]">
          <span>Rekomendasi Profil: <strong class="text-white">${classification}</strong></span>
          <span class="text-[#4d6963]">Review berkala setiap rilis laporan keuangan kuartalan.</span>
        </div>
      `
          : ""
      }
    </div>
  `;
}

function enhanceTablesWithBadges(container) {
  if (!container) return;
  const tables = container.querySelectorAll("table");
  tables.forEach((table) => {
    if (!table.parentElement.classList.contains("ai-table-wrapper")) {
      const wrapper = document.createElement("div");
      wrapper.className = "ai-table-wrapper";
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }

    table.querySelectorAll("td").forEach((td) => {
      const text = td.textContent.trim();
      const lower = text.toLowerCase();
      if (
        lower.includes("undervalued") ||
        lower.includes("diskon") ||
        lower.includes("sehat") ||
        lower.includes("tinggi") ||
        lower.includes("atas benchmark") ||
        lower.includes("prima") ||
        lower.includes("kuat")
      ) {
        td.innerHTML = `<span class="cell-badge-green"><i data-lucide="check" class="w-3 h-3"></i> ${text}</span>`;
      } else if (
        lower.includes("overvalued") ||
        lower.includes("mahal") ||
        lower.includes("waspada") ||
        lower.includes("rendah") ||
        lower.includes("bawah benchmark") ||
        lower.includes("lemah")
      ) {
        td.innerHTML = `<span class="cell-badge-red"><i data-lucide="alert-triangle" class="w-3 h-3"></i> ${text}</span>`;
      } else if (
        lower.includes("fair") ||
        lower.includes("wajar") ||
        lower.includes("moderat") ||
        lower.includes("sejajar")
      ) {
        td.innerHTML = `<span class="cell-badge-amber"><i data-lucide="minus" class="w-3 h-3"></i> ${text}</span>`;
      }
    });
  });
}

function formatMarkdownAiReport(rawMarkdown, conviction, classification) {
  if (!rawMarkdown)
    return "<p class='text-[#8ea7a1] italic'>Tidak ada laporan analisis AI yang tersedia.</p>";

  const cleanMd = rawMarkdown.replace(/\r\n/g, "\n");
  const hasNumberedSections = /###\s*(?:1[\.\s]|🏢)/i.test(cleanMd);

  if (!hasNumberedSections) {
    return `<div class="prose-ai space-y-4">${safeParseMarkdown(cleanMd)}</div>`;
  }

  const chunks = cleanMd.split(/(?=^###\s+)/m);
  let resultHtml = "";

  chunks.forEach((chunk) => {
    const trimmed = chunk.trim();
    if (!trimmed) return;

    const firstLine = trimmed.split("\n")[0];
    const content = trimmed.substring(firstLine.length).trim();

    if (/###.*(?:Rangkuman Metrik|Benchmark|📊)/i.test(firstLine)) {
      resultHtml += `
        <div class="my-4">
          <div class="flex items-center gap-2 mb-2.5">
            <i data-lucide="table" class="w-4 h-4 text-[#4bfa14]"></i>
            <span class="font-extrabold text-white text-xs uppercase tracking-wider font-mono">Rangkuman Metrik Kuantitatif &amp; Benchmark Sektor</span>
          </div>
          <div class="ai-table-wrapper">
            ${safeParseMarkdown(content.replace(/^---\s*/m, ""))}
          </div>
        </div>
      `;
    } else if (/###\s*1[\.\s]|🏢|Gambaran Umum/i.test(firstLine)) {
      resultHtml += buildSectionCardHtml(
        "01",
        "building-2",
        "Gambaran Umum &amp; Kesehatan Keuangan",
        content,
      );
    } else if (/###\s*2[\.\s]|💡|Profitabilitas/i.test(firstLine)) {
      resultHtml += buildSectionCardHtml(
        "02",
        "trending-up",
        "Profitabilitas &amp; Efisiensi Operasional",
        content,
      );
    } else if (/###\s*3[\.\s]|🏷️|Valuasi/i.test(firstLine)) {
      resultHtml += buildSectionCardHtml(
        "03",
        "tag",
        "Valuasi &amp; Potensi Diskonto",
        content,
      );
    } else if (/###\s*4[\.\s]|🛡️|Neraca|Arus Kas/i.test(firstLine)) {
      resultHtml += buildSectionCardHtml(
        "04",
        "shield-check",
        "Kekuatan Neraca &amp; Arus Kas",
        content,
      );
    } else if (/###\s*5[\.\s]|📈|Pertumbuhan/i.test(firstLine)) {
      resultHtml += buildSectionCardHtml(
        "05",
        "line-chart",
        "Pertumbuhan &amp; Prospek",
        content,
      );
    } else if (/###\s*6[\.\s]|⚖️|Keunggulan|Risiko/i.test(firstLine)) {
      const bullMatch = content.match(
        /\*\*Keunggulan[^\*]*\*\*[:\s]*([\s\S]*?)(?=\*\*Risiko|\n\s*###|$)/i,
      );
      const bearMatch = content.match(
        /\*\*Risiko[^\*]*\*\*[:\s]*([\s\S]*?)(?=\n\s*###|$)/i,
      );

      const bullPoints = bullMatch
        ? bullMatch[1]
            .split("\n")
            .map((l) => l.trim())
            .filter((l) => l.startsWith("-") || l.startsWith("*"))
        : [];
      const bearPoints = bearMatch
        ? bearMatch[1]
            .split("\n")
            .map((l) => l.trim())
            .filter((l) => l.startsWith("-") || l.startsWith("*"))
        : [];

      if (bullPoints.length > 0 || bearPoints.length > 0) {
        resultHtml += buildBullishBearishArenaHtml(bullPoints, bearPoints);
      } else {
        resultHtml += buildSectionCardHtml(
          "06",
          "scale",
          "Keunggulan Utama vs Risiko Kunci",
          content,
        );
      }
    } else if (
      /###\s*7[\.\s]|🎯|Kesimpulan|Profil Investor|Verdict/i.test(firstLine)
    ) {
      const cleanContent = content
        .replace(/-?\s*\*\*Tingkat Keyakinan[^\n]*\n?/gi, "")
        .replace(/-?\s*\*\*Klasifikasi Saham[^\n]*\n?/gi, "")
        .trim();
      resultHtml += buildVerdictBoxHtml(
        cleanContent,
        conviction,
        classification,
      );
    } else {
      const titleClean = firstLine.replace(/^###\s*/, "");
      resultHtml += `
        <div class="ai-section-card">
          <div class="ai-section-header">
            <div class="ai-section-title">
              <i data-lucide="file-text" class="w-4 h-4 text-[#4bfa14]"></i>
              <span>${titleClean}</span>
            </div>
          </div>
          <div class="ai-section-body">
            ${safeParseMarkdown(content)}
          </div>
        </div>
      `;
    }
  });

  return resultHtml;
}

function renderAiExecutiveReport(data) {
  const aiContent = document.getElementById("ai-explanation-content");
  if (!aiContent) return;

  const rawMarkdown = data.ai_explanation || "";
  const structured = data.structured_analysis || null;
  const conviction =
    data.conviction_score !== null && data.conviction_score !== undefined
      ? Number(data.conviction_score)
      : structured?.conviction_score
      ? Number(structured.conviction_score)
      : null;
  const classification =
    data.investment_classification ||
    structured?.investment_classification ||
    "";

  let html = "";

  // 1. Hero Banner at Top
  html += buildHeroBannerHtml(
    conviction,
    classification,
    data.ticker || data.symbol,
    data.company_name,
  );

  // Check if structured analysis is available directly
  if (structured && structured.company_overview) {
    // 2. Scorecard Table
    if (structured.quantitative_scorecard_table) {
      html += `
        <div class="my-4">
          <div class="flex items-center gap-2 mb-2.5">
            <i data-lucide="table" class="w-4 h-4 text-[#4bfa14]"></i>
            <span class="font-extrabold text-white text-xs uppercase tracking-wider font-mono">Rangkuman Metrik Kuantitatif &amp; Benchmark Sektor</span>
          </div>
          <div class="ai-table-wrapper">
            ${safeParseMarkdown(structured.quantitative_scorecard_table)}
          </div>
        </div>
      `;
    }

    // 3. Sections 1 to 5
    html += buildSectionCardHtml(
      "01",
      "building-2",
      "Gambaran Umum &amp; Kesehatan Keuangan",
      structured.company_overview,
    );
    html += buildSectionCardHtml(
      "02",
      "trending-up",
      "Profitabilitas &amp; Efisiensi Operasional",
      structured.profitability_efficiency,
    );
    html += buildSectionCardHtml(
      "03",
      "tag",
      "Valuasi &amp; Potensi Diskonto",
      structured.valuation_discount,
    );
    html += buildSectionCardHtml(
      "04",
      "shield-check",
      "Kekuatan Neraca &amp; Arus Kas",
      structured.balance_sheet_cashflow,
    );
    html += buildSectionCardHtml(
      "05",
      "line-chart",
      "Pertumbuhan &amp; Prospek",
      structured.growth_prospects,
    );

    // 4. Section 6: Bullish vs Bearish Arena
    html += buildBullishBearishArenaHtml(
      structured.bullish_points,
      structured.bearish_points,
    );

    // 5. Section 7: Executive Verdict Box
    html += buildVerdictBoxHtml(
      structured.executive_verdict,
      conviction,
      classification,
    );
  } else {
    // Process markdown string smartly
    html += formatMarkdownAiReport(rawMarkdown, conviction, classification);
  }

  aiContent.innerHTML = html;

  // Enhance tables with status badges
  enhanceTablesWithBadges(aiContent);

  // Re-run Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }
}

// ==========================================
// 5. TAB 3: COMPARISON
// ==========================================
function initComparisonEvents() {
  document.getElementById("btn-run-compare")?.addEventListener("click", () => {
    runComparison();
  });

  document.querySelectorAll(".compare-preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("input-compare-tickers").value =
        btn.getAttribute("data-tickers");
      runComparison();
    });
  });
}

async function runComparison() {
  const input = document.getElementById("input-compare-tickers").value;
  const includeAi = document.getElementById("check-compare-ai").checked;
  const loading = document.getElementById("compare-loading");
  const results = document.getElementById("compare-results");

  const tickers = input.split(/[\s,]+/).filter(Boolean);
  if (tickers.length < 2) {
    alert("Masukkan minimal 2 kode saham untuk dibandingkan.");
    return;
  }

  loading.classList.remove("hidden");
  results.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/api/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tickers: tickers, include_ai: includeAi }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Gagal komparasi.");
    }

    const data = await res.json();
    renderComparisonTable(data.stocks);

    const aiCard = document.getElementById("compare-ai-verdict-card");
    const aiContent = document.getElementById("compare-ai-content");
    if (data.ai_comparison) {
      lastCompareAi = data.ai_comparison;
      aiContent.innerHTML = safeParseMarkdown(data.ai_comparison);
      enhanceTablesWithBadges(aiContent);
      if (window.lucide) lucide.createIcons();
      aiCard.classList.remove("hidden");
    } else {
      lastCompareAi = "";
      aiCard.classList.add("hidden");
    }

    results.classList.remove("hidden");
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    loading.classList.add("hidden");
  }
}

function renderComparisonTable(stocks) {
  const thead = document.getElementById("compare-table-head");
  const tbody = document.getElementById("compare-table-body");

  // Build Head
  thead.innerHTML = `<th class="px-4 py-3.5 sticky left-0 bg-[#0e1420] border-r border-[#4bfa14]/20 border-b border-[#4bfa14]/20 z-10 text-[#4bfa14] font-bold uppercase tracking-wider text-xs">Metrik Fundamental</th>`;
  stocks.forEach((s) => {
    thead.innerHTML += `
      <th class="px-4 py-3.5 text-right border-b border-[#4bfa14]/20 border-r border-white/5 last:border-r-0">
        <div class="font-bold text-white text-sm font-mono tracking-wide">${s.symbol}</div>
        <div class="text-[11px] text-[#8ea7a1] font-normal truncate max-w-[140px]" title="${s.company_name}">${s.company_name}</div>
      </th>
    `;
  });

  // Calculate highest score for badge highlight
  const maxScore = Math.max(...stocks.map((s) => s.score || 0));

  // Metric Rows definitions
  const rows = [
    {
      label: "Skor Fundamental (0-100)",
      key: "score",
      format: (v) => {
        const isLeader = v === maxScore;
        return isLeader
          ? `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">👑 ${v} pt</span>`
          : `<span class="font-bold">${v} pt</span>`;
      },
    },
    {
      label: "Kategori Kesehatan",
      key: "category",
      format: (v) => `<span class="text-xs text-slate-300">${v}</span>`,
    },
    { label: "Harga Terkini", key: "price", format: (v) => formatRupiah(v) },
    {
      label: "Fair Value Konsensus",
      key: "fair_value",
      format: (v) =>
        `<span class="text-[#4bfa14] font-semibold">${formatRupiah(v)}</span>`,
    },
    {
      label: "Margin of Safety (MoS %)",
      key: "mos",
      format: (v) => {
        if (v === null || v === undefined) return "N/A";
        const color = v >= 0 ? "text-emerald-400" : "text-rose-400";
        return `<span class="${color} font-bold">${v > 0 ? "+" : ""}${formatPercent(v)}</span>`;
      },
    },
    {
      label: "PER (Price to Earnings)",
      key: "pe",
      format: (v) => `${formatNumber(v, 1)}x`,
    },
    {
      label: "PBV (Price to Book)",
      key: "pbv",
      format: (v) => `${formatNumber(v, 2)}x`,
    },
    {
      label: "ROE (Return on Equity)",
      key: "roe",
      format: (v) =>
        `<span class="text-emerald-400 font-semibold">${formatPercent(v)}</span>`,
    },
    {
      label: "Net Profit Margin",
      key: "net_margin",
      format: (v) => formatPercent(v),
    },
    {
      label: "DER (Rasio Utang)",
      key: "der",
      format: (v) => `${formatNumber(v, 2)}x`,
    },
    {
      label: "Dividend Yield",
      key: "dividend_yield",
      format: (v) => `<span class="text-amber-300">${formatPercent(v)}</span>`,
    },
    {
      label: "Revenue Growth",
      key: "revenue_growth",
      format: (v) => formatPercent(v),
    },
    { label: "Market Cap", key: "market_cap", format: (v) => formatRupiah(v) },
  ];

  tbody.innerHTML = "";
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.className =
      "hover:bg-[#4bfa14]/04 transition even:bg-[#111620]/50 odd:bg-[#0d1117]/30";

    // Sticky first column
    tr.innerHTML = `
      <td class="px-4 py-3 font-semibold text-[#8ea7a1] text-xs sticky left-0 bg-[#090d14]/95 border-r border-[#4bfa14]/15 border-b border-white/5 z-10 whitespace-nowrap shadow-sm">
        ${r.label}
      </td>
    `;

    // Data columns
    stocks.forEach((s) => {
      const val = s[r.key];
      const displayVal = r.format(val, s);
      tr.innerHTML += `
        <td class="px-4 py-3 text-right font-mono text-xs text-white border-b border-white/5 border-r border-white/5 last:border-r-0 whitespace-nowrap">
          ${displayVal}
        </td>
      `;
    });

    tbody.appendChild(tr);
  });
}
