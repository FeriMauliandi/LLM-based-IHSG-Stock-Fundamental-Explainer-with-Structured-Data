/**
 * AI IHSG Stock Screener & Fundamental Analyzer - Frontend Application
 */

// Auto-detect API Base URL:
// Only use origin if we are explicitly on port 8000 (FastAPI server).
// Otherwise (e.g. VS Code Live Server port 5500, file://, etc.), default to http://localhost:8000.
const API_BASE = (window.location.port === "8000")
  ? window.location.origin
  : "http://localhost:8000";

// Format Helpers
function formatRupiah(value) {
  if (value === null || value === undefined) return "N/A";
  return "Rp " + Number(value).toLocaleString("id-ID", { maximumFractionDigits: 0 });
}

function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined) return "N/A";
  return Number(value).toLocaleString("id-ID", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
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
  checkBackendHealth();
  initScreenerEvents();
  initAnalysisEvents();
  initComparisonEvents();
  initValuationEvents();
  initCopyButtons();

  // Status refresh button
  document.getElementById("btn-refresh-status")?.addEventListener("click", () => {
    checkBackendHealth(true);
  });
});

function initCopyButtons() {
  const btnCopyAi = document.getElementById("btn-copy-ai");
  const btnCopyAiText = document.getElementById("btn-copy-ai-text");
  btnCopyAi?.addEventListener("click", () => {
    if (!lastAiExplanation) return;
    navigator.clipboard.writeText(lastAiExplanation).then(() => {
      btnCopyAiText.textContent = "Tersalin!";
      setTimeout(() => {
        btnCopyAiText.textContent = "Salin Analisis";
      }, 2000);
    });
  });

  const btnCopyCompare = document.getElementById("btn-copy-compare-ai");
  const btnCopyCompareText = document.getElementById("btn-copy-compare-ai-text");
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
      btn.classList.add("active", "border-blue-500", "text-blue-400");
      btn.classList.remove("border-transparent", "text-slate-400");
    } else {
      btn.classList.remove("active", "border-blue-500", "text-blue-400");
      btn.classList.add("border-transparent", "text-slate-400");
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
  const textEl = document.getElementById("status-text");

  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Backend offline");
    const data = await res.json();

    statusEl.className = "flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/30 text-xs text-emerald-300";
    statusEl.innerHTML = `
      <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 pulse-green"></span>
      <span>API Online (Port 8000)</span>
      ${data.groq_configured ? '<span class="text-[10px] bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded font-mono">Groq AI Active</span>' : ''}
    `;

    if (showNotice) alert("Berhasil terhubung ke Backend FastAPI!");
  } catch (err) {
    statusEl.className = "flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-500/30 text-xs text-rose-300";
    statusEl.innerHTML = `
      <span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span>
      <span>API Offline (Jalankan python backend/main.py)</span>
    `;

    if (showNotice) {
      alert("Gagal menghubungi backend di http://localhost:8000. Pastikan server sudah jalan:\npython backend/main.py");
    }
  }
}

// ==========================================
// 3. TAB 1: SCREENER
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
  const tbody = document.getElementById("screener-table-body");
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
      body: JSON.stringify({ min_score, max_pe, min_roe, max_der })
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
    alert(`Gagal menjalankan screener:\n${err.message}\n\nPastikan backend FastAPI sudah berjalan di:\n${API_BASE}`);
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
        <td colspan="12" class="px-6 py-8 text-center text-slate-400">
          Tidak ada saham yang lolos kriteria. Coba longgarkan filter batas skor, PER, atau ROE.
        </td>
      </tr>
    `;
    return;
  }

  stocks.forEach((s) => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-blue-950/30 transition even:bg-slate-900/40 odd:bg-slate-950/20 group";

    // Score color badge
    let scoreColor = "text-emerald-400";
    if (s.score < 50) scoreColor = "text-rose-400";
    else if (s.score < 65) scoreColor = "text-amber-400";

    // Status valuation badge (safe check)
    const valStatus = (s.valuation_status || s.valuation || "N/A").toString();
    let valBadge = "bg-slate-800 text-slate-300 border border-slate-700";
    if (valStatus.includes("Undervalued")) {
      valBadge = "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-semibold";
    } else if (valStatus.includes("Overvalued")) {
      valBadge = "bg-rose-500/20 text-rose-400 border border-rose-500/40 font-semibold";
    } else {
      valBadge = "bg-amber-500/20 text-amber-400 border border-amber-500/40 font-semibold";
    }

    tr.innerHTML = `
      <td class="px-4 py-3.5 whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        <div class="flex items-center space-x-2.5">
          <span class="text-lg">${s.badge || '⚪'}</span>
          <div>
            <div class="font-bold text-white font-mono tracking-wide text-sm">${s.ticker}</div>
            <div class="text-[11px] text-slate-400 max-w-[150px] truncate" title="${s.company_name}">${s.company_name}</div>
          </div>
        </div>
      </td>
      <td class="px-4 py-3.5 text-xs text-slate-300 whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">${s.sector || 'N/A'}</td>
      <td class="px-4 py-3.5 text-right font-mono font-bold text-white whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">${formatRupiah(s.price)}</td>
      <td class="px-4 py-3.5 whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        <div class="flex items-center space-x-2">
          <div class="w-16 bg-slate-800 h-2 rounded-full overflow-hidden border border-slate-700">
            <div class="bg-blue-500 h-2 rounded-full" style="width: ${s.score}%"></div>
          </div>
          <span class="font-mono font-bold ${scoreColor}">${s.score} pt</span>
        </div>
        <div class="text-[10px] text-slate-400">${s.category || ''}</div>
      </td>
      <td class="px-4 py-3.5 text-right font-mono text-xs whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        <span class="text-slate-200 font-semibold">${formatNumber(s.pe, 1)}x</span> / <span class="text-slate-400">${formatNumber(s.pbv, 2)}x</span>
      </td>
      <td class="px-4 py-3.5 text-right font-mono text-xs text-emerald-400 font-bold whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        ${formatPercent(s.roe)}
      </td>
      <td class="px-4 py-3.5 text-right font-mono text-xs whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800 text-slate-200">
        ${formatPercent(s.net_margin)}
      </td>
      <td class="px-4 py-3.5 text-right font-mono text-xs text-amber-300 font-semibold whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        ${formatPercent(s.dividend_yield)}
      </td>
      <td class="px-4 py-3.5 text-right font-mono text-xs font-bold text-blue-400 whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        ${formatRupiah(s.fair_value)}
      </td>
      <td class="px-4 py-3.5 text-right font-mono text-xs font-bold ${s.mos !== null && s.mos >= 0 ? 'text-emerald-400' : 'text-rose-400'} whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        ${s.mos !== null ? (s.mos > 0 ? '+' : '') + formatPercent(s.mos) : 'N/A'}
      </td>
      <td class="px-4 py-3.5 text-center whitespace-nowrap border-b border-slate-700/70 border-r border-slate-800">
        <span class="px-2.5 py-1 rounded-md text-[11px] ${valBadge}">
          ${valStatus}
        </span>
      </td>
      <td class="px-4 py-3.5 text-center whitespace-nowrap border-b border-slate-700/70">
        <button class="btn-analyze-row px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-blue-400 hover:text-white border border-blue-500/40 text-xs font-semibold transition shadow-sm" data-ticker="${s.ticker}">
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
// 4. TAB 2: DETAIL ANALYSIS & AI
// ==========================================
function initAnalysisEvents() {
  document.getElementById("btn-analyze-stock")?.addEventListener("click", () => {
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
      body: JSON.stringify({ ticker: ticker, include_ai: includeAi })
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
  document.getElementById("stock-company-name").textContent = data.company_name || data.ticker;
  document.getElementById("stock-ticker").textContent = data.symbol || data.ticker;
  document.getElementById("stock-sector").textContent = `Sektor: ${m.sector || 'N/A'}`;
  document.getElementById("stock-industry").textContent = `Industri: ${m.industry || 'N/A'}`;
  document.getElementById("stock-timestamp").textContent = `Dianalisis: ${data.timestamp}`;

  // 5 Key Cards
  document.getElementById("card-price").textContent = formatRupiah(m.price);
  document.getElementById("card-score").textContent = `${s.total_score} / 100`;
  document.getElementById("card-category").textContent = s.category;

  document.getElementById("card-fair-value").textContent = formatRupiah(v.fair_value);
  document.getElementById("card-valuation-status").textContent = v.status || "N/A";

  const mosVal = v.margin_of_safety;
  const mosCard = document.getElementById("card-mos");
  if (mosVal !== null && mosVal !== undefined) {
    mosCard.textContent = (mosVal > 0 ? "+" : "") + formatPercent(mosVal);
    mosCard.className = `text-xl font-bold mt-1 font-mono ${mosVal >= 0 ? "text-emerald-400" : "text-rose-400"}`;
  } else {
    mosCard.textContent = "N/A";
  }

  document.getElementById("card-per-pbv").textContent = `${formatNumber(m.pe, 1)}x / ${formatNumber(m.pb, 2)}x`;

  // 4 Pillars Breakdown
  const pillars = s.pillars;
  const pProf = pillars["Profitabilitas"] || 0;
  const pVal = pillars["Valuasi"] || 0;
  const pSolv = pillars["Solvabilitas & Kas"] || 0;
  const pGrow = pillars["Pertumbuhan & Dividen"] || 0;

  document.getElementById("pillar-prof-val").textContent = `${pProf} / 25`;
  document.getElementById("pillar-prof-bar").style.width = `${(pProf / 25) * 100}%`;

  document.getElementById("pillar-val-val").textContent = `${pVal} / 25`;
  document.getElementById("pillar-val-bar").style.width = `${(pVal / 25) * 100}%`;

  document.getElementById("pillar-solv-val").textContent = `${pSolv} / 25`;
  document.getElementById("pillar-solv-bar").style.width = `${(pSolv / 25) * 100}%`;

  document.getElementById("pillar-grow-val").textContent = `${pGrow} / 25`;
  document.getElementById("pillar-grow-bar").style.width = `${(pGrow / 25) * 100}%`;

  // Reward/Penalty Details
  const detailsList = document.getElementById("score-details-list");
  detailsList.innerHTML = "";
  s.details.forEach((det) => {
    const li = document.createElement("li");
    li.textContent = det;
    detailsList.appendChild(li);
  });

  // AI Explanation Markdown
  const aiCard = document.getElementById("ai-explanation-card");
  const aiContent = document.getElementById("ai-explanation-content");
  const traceAccordion = document.getElementById("agent-trace-accordion");
  const traceSteps = document.getElementById("agent-trace-steps");

  if (data.ai_explanation) {
    lastAiExplanation = data.ai_explanation;
    aiContent.innerHTML = marked.parse(data.ai_explanation);

    // Prepend Structured Output Badges if available
    if (data.conviction_score || data.investment_classification) {
      const banner = document.createElement("div");
      banner.className = "flex flex-wrap items-center gap-2.5 p-3 rounded-xl bg-blue-950/40 border border-blue-500/30 text-xs font-semibold mb-4";
      banner.innerHTML = `
        <span class="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">
          🎯 Conviction Score: ${Number(data.conviction_score).toFixed(1)} / 10.0
        </span>
        <span class="px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-medium">
          ${data.investment_classification || ""}
        </span>
      `;
      aiContent.prepend(banner);
    }

    aiCard.classList.remove("hidden");

    // Populate Multi-Agent Trace if available
    if (data.agent_trace && data.agent_trace.length > 0 && traceAccordion && traceSteps) {
      traceSteps.innerHTML = "";
      data.agent_trace.forEach((step) => {
        const stepDiv = document.createElement("div");
        stepDiv.className = "p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 text-slate-300";
        stepDiv.innerHTML = `
          <div class="flex items-center justify-between text-xs font-semibold text-blue-300 mb-1">
            <span>${step.agent || "Agent"}</span>
            <span class="text-[10px] text-slate-400 font-mono">${step.timestamp || ""}</span>
          </div>
          <div class="text-[11px] text-slate-400 italic mb-1">Aksi: ${step.action || "-"}</div>
          <div class="text-xs text-slate-200 bg-slate-900/80 p-2 rounded border border-slate-800/80">${step.summary || ""}</div>
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
    div.className = "px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 flex items-start space-x-2";
    div.innerHTML = `<span>${sig}</span>`;
    sigList.appendChild(div);
  });

  // Multi-Model Valuation Grid
  const valGrid = document.getElementById("valuation-models-grid");
  valGrid.innerHTML = "";
  if (v.estimates) {
    for (const [modelName, modelVal] of Object.entries(v.estimates)) {
      const card = document.createElement("div");
      card.className = "glass-card p-3 rounded-xl border border-slate-800";
      card.innerHTML = `
        <span class="text-xs text-slate-400 block">${modelName}</span>
        <div class="text-base font-bold text-white mt-0.5 font-mono">${formatRupiah(modelVal)}</div>
      `;
      valGrid.appendChild(card);
    }
  }

  const caption = document.getElementById("valuation-formula-caption");
  if (v.weighted_avg && v.median) {
    caption.textContent = `Weighted Average: ${formatRupiah(v.weighted_avg)} | Median: ${formatRupiah(v.median)} | Konsensus Final (60/40 blend): ${formatRupiah(v.fair_value)}`;
  } else {
    caption.textContent = "";
  }

  if (window.lucide) lucide.createIcons();
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
      document.getElementById("input-compare-tickers").value = btn.getAttribute("data-tickers");
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
      body: JSON.stringify({ tickers: tickers, include_ai: includeAi })
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
      aiContent.innerHTML = marked.parse(data.ai_comparison);
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
  thead.innerHTML = `<th class="px-4 py-3.5 sticky left-0 bg-slate-900 border-r-2 border-slate-600 border-b-2 border-slate-600 z-10 text-slate-300 font-bold uppercase tracking-wider text-xs">Metrik Fundamental</th>`;
  stocks.forEach((s) => {
    thead.innerHTML += `
      <th class="px-4 py-3.5 text-right border-b-2 border-slate-600 border-r border-slate-700/80 last:border-r-0">
        <div class="font-bold text-white text-sm font-mono tracking-wide">${s.symbol}</div>
        <div class="text-[11px] text-slate-400 font-normal truncate max-w-[140px]" title="${s.company_name}">${s.company_name}</div>
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
      format: (v, s) => {
        const isLeader = v === maxScore;
        return isLeader
          ? `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">🏆 ${v} pt</span>`
          : `<span class="font-bold">${v} pt</span>`;
      }
    },
    { label: "Kategori Kesehatan", key: "category", format: (v) => `<span class="text-xs text-slate-300">${v}</span>` },
    { label: "Harga Terkini", key: "price", format: (v) => formatRupiah(v) },
    { label: "Fair Value Konsensus", key: "fair_value", format: (v) => `<span class="text-blue-400 font-semibold">${formatRupiah(v)}</span>` },
    {
      label: "Margin of Safety (MoS %)",
      key: "mos",
      format: (v) => {
        if (v === null || v === undefined) return "N/A";
        const color = v >= 0 ? "text-emerald-400" : "text-rose-400";
        return `<span class="${color} font-bold">${v > 0 ? "+" : ""}${formatPercent(v)}</span>`;
      }
    },
    { label: "PER (Price to Earnings)", key: "pe", format: (v) => `${formatNumber(v, 1)}x` },
    { label: "PBV (Price to Book)", key: "pbv", format: (v) => `${formatNumber(v, 2)}x` },
    { label: "ROE (Return on Equity)", key: "roe", format: (v) => `<span class="text-emerald-400 font-semibold">${formatPercent(v)}</span>` },
    { label: "Net Profit Margin", key: "net_margin", format: (v) => formatPercent(v) },
    { label: "DER (Rasio Utang)", key: "der", format: (v) => `${formatNumber(v, 2)}x` },
    { label: "Dividend Yield", key: "dividend_yield", format: (v) => `<span class="text-amber-300">${formatPercent(v)}</span>` },
    { label: "Revenue Growth", key: "revenue_growth", format: (v) => formatPercent(v) },
    { label: "Market Cap", key: "market_cap", format: (v) => formatRupiah(v) }
  ];

  tbody.innerHTML = "";
  rows.forEach((r, idx) => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-blue-950/25 transition even:bg-slate-900/40 odd:bg-slate-950/20";
    
    // Sticky first column
    tr.innerHTML = `
      <td class="px-4 py-3 font-semibold text-slate-200 text-xs sticky left-0 bg-slate-900/95 border-r-2 border-slate-600 border-b border-slate-700/70 z-10 whitespace-nowrap shadow-sm">
        ${r.label}
      </td>
    `;

    // Data columns
    stocks.forEach((s) => {
      const val = s[r.key];
      const displayVal = r.format(val, s);
      tr.innerHTML += `
        <td class="px-4 py-3 text-right font-mono text-xs text-slate-100 border-b border-slate-700/70 border-r border-slate-800 last:border-r-0 whitespace-nowrap">
          ${displayVal}
        </td>
      `;
    });

    tbody.appendChild(tr);
  });
}

// ==========================================
// 6. TAB 4: VALUATION CALCULATOR
// ==========================================
function initValuationEvents() {
  const form = document.getElementById("form-calc");
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const price = parseFloat(document.getElementById("calc-price").value);
    const eps = parseFloat(document.getElementById("calc-eps").value);
    const book_value = parseFloat(document.getElementById("calc-bvps").value);
    const target_pe = parseFloat(document.getElementById("calc-target-pe").value);
    const target_pbv = parseFloat(document.getElementById("calc-target-pbv").value);
    const profit_margin = parseFloat(document.getElementById("calc-margin").value);

    try {
      const res = await fetch(`${API_BASE}/api/valuation/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ price, eps, book_value, target_pe, target_pbv, profit_margin })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Gagal menghitung valuasi.");
      }

      const data = await res.json();
      renderValuationResults(data);
    } catch (err) {
      alert("Error: " + err.message);
    }
  });
}

function renderValuationResults(data) {
  const container = document.getElementById("calc-results");

  document.getElementById("calc-res-price").textContent = formatRupiah(data.price);
  document.getElementById("calc-res-fair-value").textContent = formatRupiah(data.fair_value);
  document.getElementById("calc-res-status").textContent = data.status || "N/A";

  const mosVal = data.margin_of_safety;
  const mosEl = document.getElementById("calc-res-mos");
  if (mosVal !== null && mosVal !== undefined) {
    mosEl.textContent = (mosVal > 0 ? "+" : "") + formatPercent(mosVal);
    mosEl.className = `text-2xl font-bold mt-1 font-mono ${mosVal >= 0 ? "text-emerald-400" : "text-rose-400"}`;
  } else {
    mosEl.textContent = "N/A";
  }

  // Model breakdown
  const grid = document.getElementById("calc-res-models-grid");
  grid.innerHTML = "";
  if (data.estimates) {
    for (const [name, val] of Object.entries(data.estimates)) {
      const card = document.createElement("div");
      card.className = "glass-card p-3 rounded-xl border border-slate-800";
      card.innerHTML = `
        <span class="text-xs text-slate-400 block">${name}</span>
        <div class="text-base font-bold text-white mt-1">${formatRupiah(val)}</div>
      `;
      grid.appendChild(card);
    }
  }

  document.getElementById("calc-res-caption").textContent = 
    `Weighted Avg: ${formatRupiah(data.weighted_avg)} | Median: ${formatRupiah(data.median)} | Konsensus Final (60/40 blend): ${formatRupiah(data.fair_value)}`;

  container.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}
