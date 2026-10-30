import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Path as FastPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# 1. Pastikan root direktori proyek ada di sys.path agar modul data, reason, chains terbaca
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Muat file .env dari root direktori
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

# Import fungsi-fungsi inti dari proyek
from data.data_fetcher import fetch_fundamental_data
from data.screener import run_stock_screener, POPULAR_IHSG_STOCKS
from reason.scoring import calculate_fundamental_score
from reason.signals import generate_fundamental_signals
from reason.valuation import calculate_fair_value
from chains.analysis_chain import build_analysis_chain, build_comparison_chain

# ==========================================
# INISIALISASI FASTAPI & CORS
# ==========================================
app = FastAPI(
    title="AI IHSG Stock Screener & Fundamental Analyzer API",
    description="Backend REST API untuk analisis fundamental saham IHSG, kalkulator harga wajar, screener, dan rekomendasi AI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend web app if folder exists
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# Cache LLM Chains agar tidak dibuat berulang kali di memori
analysis_chain = None
comparison_chain = None


def get_analysis_chain():
    global analysis_chain
    if analysis_chain is None:
        analysis_chain = build_analysis_chain()
    return analysis_chain


def get_comparison_chain():
    global comparison_chain
    if comparison_chain is None:
        comparison_chain = build_comparison_chain()
    return comparison_chain


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()
    if not ticker.endswith(".JK"):
        ticker = f"{ticker}.JK"
    return ticker


def clean_ticker(ticker: str) -> str:
    return ticker.upper().strip().replace(".JK", "")


def format_rupiah(value: Optional[float], decimals: int = 0) -> str:
    if value is None:
        return "N/A"
    return f"Rp {value:,.{decimals}f}"


def safe_round(value, decimals=2):
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return None


def safe_pct(value, decimals=2):
    if value is None:
        return None
    try:
        return round(float(value) * 100, decimals)
    except (TypeError, ValueError):
        return None


def build_metrics_summary(data: Dict[str, Any]) -> str:
    roe = (data.get("roe") or 0) * 100
    roa = (data.get("roa") or 0) * 100
    margin = (data.get("profit_margin") or 0) * 100
    div = (data.get("dividend_yield") or 0) * 100
    rev_g = (data.get("revenue_growth") or 0) * 100
    earn_g = (data.get("earnings_growth") or 0) * 100

    return f"""
    - Nama Perusahaan: {data.get('company_name')}
    - Sektor / Industri: {data.get('sector')} / {data.get('industry')}
    - Harga Terkini: Rp {data.get('price')}
    - Market Cap: {format_rupiah(data.get('market_cap'))}
    - PER (Trailing): {data.get('pe')}x
    - PER (Forward): {data.get('forward_pe')}x
    - PBV (Price to Book): {data.get('pb')}x
    - ROE (Return on Equity): {roe:.1f}%
    - ROA (Return on Assets): {roa:.1f}%
    - Net Margin: {margin:.1f}%
    - DER (Debt to Equity): {data.get('debt_to_equity')}x
    - Current Ratio: {data.get('current_ratio')}x
    - Dividend Yield: {div:.1f}%
    - Revenue Growth: {rev_g:.1f}%
    - Earnings Growth: {earn_g:.1f}%
    - Free Cash Flow: {data.get('free_cashflow')}
    - Operating Cash Flow: {data.get('operating_cashflow')}
    - EPS: {data.get('eps')}
    - Book Value per Share: {data.get('book_value')}
    """


# ==========================================
# PYDANTIC SCHEMAS (REQUEST & RESPONSE)
# ==========================================
class StockAnalysisRequest(BaseModel):
    ticker: str = Field(..., examples=["BBCA"], description="Kode ticker saham IHSG")
    include_ai: bool = Field(False, description="Set True jika ingin menyertakan narasi analisis AI")


class ScreenerRequest(BaseModel):
    min_score: int = Field(50, ge=0, le=100, description="Minimal skor fundamental (0-100)")
    max_pe: float = Field(25.0, description="Maksimal PER")
    min_roe: float = Field(8.0, description="Minimal ROE (%)")
    max_der: float = Field(2.0, description="Maksimal DER")
    preset: Optional[str] = Field(None, examples=["undervalued"], description="Preset: undervalued, dividen, atau bluechip")
    tickers: Optional[List[str]] = Field(None, description="Daftar ticker khusus yang ingin disaring (opsional)")


class ComparisonRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=8, examples=[["BBCA", "BBRI", "BMRI"]], description="Daftar ticker saham (minimal 2)")
    include_ai: bool = Field(True, description="Apakah menyertakan perbandingan dan rekomendasi dari AI")


class ValuationRequest(BaseModel):
    price: float = Field(..., gt=0, examples=[5000.0], description="Harga pasar terkini (Rp)")
    eps: float = Field(..., gt=0, examples=[400.0], description="Laba per saham / EPS (Rp)")
    book_value: float = Field(..., gt=0, examples=[3000.0], description="Nilai buku per saham / BVPS (Rp)")
    target_pe: Optional[float] = Field(15.0, gt=0, description="Target acuan PER (x)")
    target_pbv: Optional[float] = Field(1.8, gt=0, description="Target acuan PBV (x)")
    profit_margin: Optional[float] = Field(15.0, description="Net Profit Margin (%)")


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/", tags=["Info"])
def root():
    """Endpoint root - Info API dan daftar endpoint."""
    return {
        "status": "online",
        "name": "AI IHSG Stock Screener & Analyzer API",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "web_ui": "/app/",
        "landing_page": "/app/landing.html",
        "endpoints": {
            "popular_stocks": "GET /api/stocks/popular",
            "stock_detail": "GET /api/stocks/{ticker}?include_ai=false",
            "stock_analyze_post": "POST /api/stocks/analyze",
            "screener_presets": "GET /api/screener/presets",
            "screener_run": "POST /api/screener/run",
            "stock_comparison": "POST /api/compare",
            "valuation_calculator": "POST /api/valuation/calculate",
        }
    }


@app.get("/health", tags=["Info"])
def health():
    """Cek status kesehatan API dan konfigurasi Groq."""
    groq_key = os.getenv("GROQ_API_KEY", "")
    has_groq = bool(groq_key and "your_groq_api_key" not in groq_key.lower())
    return {
        "status": "healthy",
        "groq_configured": has_groq,
        "timestamp": datetime.now().isoformat(),
    }


# ------------------------------------------
# 1. STOCKS & DETAIL ANALYSIS
# ------------------------------------------

@app.get("/api/stocks/popular", tags=["Stocks"])
def get_popular_stocks():
    """Mengembalikan daftar saham IHSG populer terkurasi."""
    return [
        {"ticker": t, "symbol": clean_ticker(t)}
        for t in POPULAR_IHSG_STOCKS
    ]


@app.get("/api/stocks/{ticker}", tags=["Stocks"])
def get_stock_detail(
    ticker: str = FastPath(..., examples=["BBCA"], description="Kode ticker saham IHSG"),
    include_ai: bool = Query(False, description="Set True untuk menyertakan analisis naratif AI")
):
    """Mengambil data lengkap fundamental, skor 4 pilar, valuasi fair value, dan sinyal."""
    normalized = normalize_ticker(ticker)
    data = fetch_fundamental_data(normalized)

    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])

    score_info = calculate_fundamental_score(data)
    val_info = calculate_fair_value(data)
    signals = generate_fundamental_signals(data)

    ai_explanation = None
    agent_trace = []
    tool_diagnostics = {}
    if include_ai:
        chain = get_analysis_chain()
        try:
            agent_payload = {
                "ticker": normalized,
                "company_name": data.get("company_name"),
                "price": data.get("price"),
                "score": score_info["total_score"],
                "category": score_info["category"],
                "fair_value": val_info.get("fair_value", "N/A"),
                "mos": val_info.get("margin_of_safety", "N/A"),
                "metrics": build_metrics_summary(data),
                "signals": "\n".join(f"- {s}" for s in signals),
                "business_summary": data.get("longbussines_summary", "Deskripsi bisnis tidak tersedia."),
                "raw_data": data
            }
            structured_report = None
            conviction_score = None
            investment_classification = None
            if hasattr(chain, "invoke_full"):
                full_res = chain.invoke_full(agent_payload)
                ai_explanation = full_res.get("final_analysis")
                agent_trace = full_res.get("agent_trace", [])
                tool_diagnostics = full_res.get("tool_results", {})
                structured_report = full_res.get("structured_report")
                conviction_score = full_res.get("conviction_score")
                investment_classification = full_res.get("investment_classification")
            else:
                ai_explanation = chain.invoke(agent_payload)
        except Exception as e:
            ai_explanation = f"⚠️ Gagal mendapatkan analisis AI: {str(e)}"

    return {
        "ticker": normalized,
        "symbol": clean_ticker(normalized),
        "company_name": data.get("company_name"),
        "metrics": data,
        "score_info": score_info,
        "valuation_info": val_info,
        "signals": signals,
        "ai_explanation": ai_explanation,
        "structured_analysis": structured_report,
        "conviction_score": conviction_score,
        "investment_classification": investment_classification,
        "agent_trace": agent_trace,
        "tool_diagnostics": tool_diagnostics,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.post("/api/stocks/analyze", tags=["Stocks"])
def analyze_stock_post(req: StockAnalysisRequest):
    """Endpoint POST untuk menganalisis saham."""
    return get_stock_detail(ticker=req.ticker, include_ai=req.include_ai)


# ------------------------------------------
# 2. SCREENER
# ------------------------------------------

SCREENER_PRESETS = {
    "undervalued": {
        "name": "Saham Undervalued & Sehat (High MoS)",
        "description": "Saham bervaluasi murah dengan Margin of Safety tinggi dan rasio keuangan sehat.",
        "min_score": 60,
        "max_pe": 15.0,
        "min_roe": 10.0,
        "max_der": 1.2
    },
    "dividen": {
        "name": "Saham Dividen Royal",
        "description": "Perusahaan pembagi dividen rutin dengan profitabilitas stabil dan solvabilitas aman.",
        "min_score": 50,
        "max_pe": 25.0,
        "min_roe": 8.0,
        "max_der": 2.0
    },
    "bluechip": {
        "name": "Saham Bluechip & Giant",
        "description": "Saham berkapitalisasi pasar raksasa, market leader dengan profitabilitas tinggi.",
        "min_score": 65,
        "max_pe": 30.0,
        "min_roe": 12.0,
        "max_der": 1.5
    }
}


@app.get("/api/screener/presets", tags=["Screener"])
def get_screener_presets():
    """Melihat daftar preset strategi screener."""
    return SCREENER_PRESETS


@app.post("/api/screener/run", tags=["Screener"])
def run_screener_post(req: ScreenerRequest):
    """Menjalankan screening saham IHSG secara paralel sesuai kriteria."""
    min_score = req.min_score
    max_pe = req.max_pe
    min_roe = req.min_roe
    max_der = req.max_der
    applied_preset = None

    if req.preset and req.preset.lower() in SCREENER_PRESETS:
        p = SCREENER_PRESETS[req.preset.lower()]
        min_score = p["min_score"]
        max_pe = p["max_pe"]
        min_roe = p["min_roe"]
        max_der = p["max_der"]
        applied_preset = p["name"]

    target_tickers = [normalize_ticker(t) for t in req.tickers] if req.tickers else POPULAR_IHSG_STOCKS

    results = run_stock_screener(
        tickers=target_tickers,
        min_score=min_score,
        max_pe=max_pe,
        min_roe=min_roe,
        max_der=max_der
    )

    clean_results = []
    for r in results:
        clean_results.append({
            "ticker": r["Ticker"],
            "company_name": r.get("Nama Perusahaan"),
            "sector": r.get("Sektor"),
            "price": r.get("Harga"),
            "score": r.get("Score"),
            "category": r.get("Kategori"),
            "badge": r.get("Badge"),
            "pe": r.get("PER (x)"),
            "pbv": r.get("PBV (x)"),
            "roe": r.get("ROE (%)"),
            "net_margin": r.get("Net Margin (%)"),
            "der": r.get("DER (x)"),
            "dividend_yield": r.get("Div Yield (%)"),
            "fair_value": r.get("Fair Value"),
            "mos": r.get("MoS (%)"),
            "valuation": r.get("Valuasi", "N/A"),
            "valuation_status": r.get("Valuasi", "N/A")
        })

    return {
        "applied_preset": applied_preset,
        "filters": {
            "min_score": min_score,
            "max_pe": max_pe,
            "min_roe": min_roe,
            "max_der": max_der
        },
        "total_screened": len(target_tickers),
        "total_matched": len(clean_results),
        "results": clean_results
    }


# ------------------------------------------
# 3. KOMPARASI SAHAM HEAD-TO-HEAD
# ------------------------------------------

@app.post("/api/compare", tags=["Comparison"])
def compare_stocks(req: ComparisonRequest):
    """Membandingkan 2 hingga 8 saham sekaligus dan meminta keputusan pemenang dari AI."""
    cleaned_tickers = list(dict.fromkeys([t.strip().upper() for t in req.tickers if t.strip()]))
    if len(cleaned_tickers) < 2:
        raise HTTPException(status_code=400, detail="Minimal 2 kode saham diperlukan untuk komparasi.")

    comparison_data = []
    stocks_summary_text = ""

    for ticker_sym in cleaned_tickers:
        normalized = normalize_ticker(ticker_sym)
        data = fetch_fundamental_data(normalized)
        if "error" in data:
            continue

        score_info = calculate_fundamental_score(data)
        val_info = calculate_fair_value(data)

        comparison_data.append({
            "ticker": normalized,
            "symbol": clean_ticker(normalized),
            "company_name": data.get("company_name"),
            "sector": data.get("sector"),
            "industry": data.get("industry"),
            "score": score_info["total_score"],
            "category": score_info["category"],
            "price": data.get("price"),
            "fair_value": val_info.get("fair_value"),
            "mos": val_info.get("margin_of_safety"),
            "pe": safe_round(data.get("pe")),
            "pbv": safe_round(data.get("pb")),
            "roe": safe_pct(data.get("roe")),
            "net_margin": safe_pct(data.get("profit_margin")),
            "der": safe_round(data.get("debt_to_equity")),
            "dividend_yield": safe_pct(data.get("dividend_yield")),
            "revenue_growth": safe_pct(data.get("revenue_growth")),
            "earnings_growth": safe_pct(data.get("earnings_growth")),
            "current_ratio": safe_round(data.get("current_ratio")),
            "free_cashflow": data.get("free_cashflow"),
            "market_cap": data.get("market_cap")
        })

        stocks_summary_text += f"\n--- SAHAM: {normalized} ({data.get('company_name')}) ---\n"
        stocks_summary_text += f"- Sektor: {data.get('sector')} | Industri: {data.get('industry')}\n"
        stocks_summary_text += f"- Fundamental Score: {score_info['total_score']}/100 ({score_info['category']})\n"
        stocks_summary_text += f"- Harga Terkini: Rp {data.get('price')} | Fair Value: Rp {val_info.get('fair_value')} (MoS: {val_info.get('margin_of_safety')}%)\n"
        stocks_summary_text += f"- PER: {data.get('pe')}x | PBV: {data.get('pb')}x | ROE: {(data.get('roe') or 0)*100:.1f}%\n"
        stocks_summary_text += f"- Net Margin: {(data.get('profit_margin') or 0)*100:.1f}% | DER: {data.get('debt_to_equity')}x\n"
        stocks_summary_text += f"- Rev Growth: {(data.get('revenue_growth') or 0)*100:.1f}% | Earn Growth: {(data.get('earnings_growth') or 0)*100:.1f}%\n"
        stocks_summary_text += f"- Dividend Yield: {(data.get('dividend_yield') or 0)*100:.1f}% | Current Ratio: {data.get('current_ratio')}x\n"
        stocks_summary_text += f"- FCF: {data.get('free_cashflow')} | Market Cap: {format_rupiah(data.get('market_cap'))}\n"

    if not comparison_data:
        raise HTTPException(status_code=404, detail="Tidak ada data saham yang berhasil diambil.")

    ai_comparison = None
    if req.include_ai:
        comp_chain = get_comparison_chain()
        try:
            ai_comparison = comp_chain.invoke({"stocks_data": stocks_summary_text})
        except Exception as e:
            ai_comparison = f"⚠️ Gagal mendapatkan analisis komparasi AI: {str(e)}"

    return {
        "total_compared": len(comparison_data),
        "stocks": comparison_data,
        "ai_comparison": ai_comparison
    }


# ------------------------------------------
# 4. KALKULATOR FAIR VALUE (MANUAL INPUT)
# ------------------------------------------

@app.post("/api/valuation/calculate", tags=["Valuation"])
def calculate_manual_valuation(req: ValuationRequest):
    """Menghitung estimasi Fair Value dari metrik yang diinput secara manual."""
    roe = (req.eps / req.book_value) if req.book_value > 0 else 0.15
    profit_margin = (req.profit_margin / 100.0) if req.profit_margin is not None else 0.15

    mock_data = {
        "price": req.price,
        "eps": req.eps,
        "book_value": req.book_value,
        "roe": roe,
        "profit_margin": profit_margin,
        "target_pe": req.target_pe,
        "target_pbv": req.target_pbv,
    }

    result = calculate_fair_value(mock_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "price": req.price,
        "fair_value": result.get("fair_value"),
        "margin_of_safety": result.get("margin_of_safety"),
        "status": result.get("status"),
        "estimates": result.get("estimates", {}),
        "weights": result.get("weights", {}),
        "weighted_avg": result.get("weighted_avg"),
        "median": result.get("median")
    }


# ==========================================
# RUN ENTRYPOINT
# ==========================================
if __name__ == "__main__":
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    print(f"🚀 Memulai FastAPI Server di http://{host}:{port}")
    print(f"📖 Dokumentasi Swagger UI: http://{host}:{port}/docs")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
