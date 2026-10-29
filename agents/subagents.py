"""
Sub-agents and LLM node implementations for the Stock AI Multi-Agent System.
Contains:
1. Tool Execution Engine (Dynamic Quantitative Diagnostics)
2. Valuation & Capital Efficiency Agent (Structured Output: ValuationAnalysisSchema)
3. Solvency & Downside Risk Officer (Structured Output: RiskAnalysisSchema)
4. Chief Investment Officer (CIO) / Lead Synthesis Agent (Structured Output: CIOInvestmentReport)
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Type

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agents.state import StockAgentState
from agents.schemas import (
    ValuationAnalysisSchema,
    RiskAnalysisSchema,
    CIOInvestmentReport
)
from agents.tools import (
    peer_benchmark_tool,
    financial_distress_tool,
    dividend_sustainability_tool
)

load_dotenv()

# Synchronize LangSmith / LangChain Tracing V2 environment variables
if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
if os.getenv("LANGSMITH_TRACING_V2") and not os.getenv("LANGCHAIN_TRACING_V2"):
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGSMITH_TRACING_V2")
if os.getenv("LANGSMITH_PROJECT") and not os.getenv("LANGCHAIN_PROJECT"):
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT").strip('"')
if os.getenv("LANGSMITH_ENDPOINT") and not os.getenv("LANGCHAIN_ENDPOINT"):
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")

GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]


def call_groq_structured(prompt_text: str, schema_class: Type, temperature: float = 0.2) -> Optional[Any]:
    """
    Memanggil Groq LLM dengan Type-Safe Structured Output (Pydantic Schema).
    Menjamin response valid, konsisten, dan dapat diparsing oleh mesin.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "dummy" or "your_groq_api_key" in api_key.lower():
        return None

    last_err = None
    for model_name in GROQ_MODELS:
        try:
            llm = ChatGroq(
                model_name=model_name,
                temperature=temperature,
                groq_api_key=api_key,
                max_retries=2
            )
            structured_llm = llm.with_structured_output(schema_class)
            resp = structured_llm.invoke(prompt_text)
            if isinstance(resp, schema_class):
                return resp
            if isinstance(resp, dict):
                return schema_class.model_validate(resp)
            return resp
        except Exception as e:
            last_err = e
            continue

    return None


def call_groq_llm(prompt_text: str, temperature: float = 0.3) -> str:
    """Helper resilient LLM caller fallback jika structured output tidak tersedia."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "dummy" or "your_groq_api_key" in api_key.lower():
        return "⚠️ API Key Groq belum dikonfigurasi."

    last_err = None
    for model_name in GROQ_MODELS:
        try:
            llm = ChatGroq(
                model_name=model_name,
                temperature=temperature,
                groq_api_key=api_key,
                max_retries=2
            )
            resp = llm.invoke(prompt_text)
            if hasattr(resp, "content"):
                return resp.content.strip()
            return str(resp).strip()
        except Exception as e:
            last_err = e
            continue

    return f"Gagal memanggil model LLM Groq. Detail: {last_err}"


def tool_execution_node(state: StockAgentState) -> Dict[str, Any]:
    """
    Eksekusi dinamis tools kuantitatif independen:
    - peer_benchmark_tool
    - financial_distress_tool
    - dividend_sustainability_tool
    """
    raw = state.get("raw_data") or {}
    ticker = state.get("ticker", "UNKNOWN")
    sector = raw.get("sector")
    industry = raw.get("industry")
    pe = raw.get("pe")
    pb = raw.get("pb")
    roe = raw.get("roe")
    roa = raw.get("roa")
    der = raw.get("debt_to_equity")
    cr = raw.get("current_ratio")
    npm = raw.get("profit_margin")
    div_yield = raw.get("dividend_yield")
    fcf = raw.get("free_cashflow")

    # Jalankan tools
    peer_res = peer_benchmark_tool(
        ticker=ticker,
        sector=sector,
        industry=industry,
        pe=pe,
        pbv=pb,
        roe=roe
    )

    distress_res = financial_distress_tool(
        ticker=ticker,
        sector=sector,
        industry=industry,
        roa=roa,
        roe=roe,
        current_ratio=cr,
        debt_to_equity=der,
        profit_margin=npm
    )

    div_res = dividend_sustainability_tool(
        ticker=ticker,
        dividend_yield=div_yield,
        free_cashflow=fcf,
        profit_margin=npm
    )

    tool_results = {
        "peer_benchmark": peer_res,
        "financial_distress": distress_res,
        "dividend_sustainability": div_res
    }

    now_str = datetime.now().strftime("%H:%M:%S")
    trace_item = {
        "agent": "🛠️ Tool Engine",
        "action": "Dynamic Quantitative Diagnostics Executed",
        "summary": (
            f"1. Peer Benchmark ({peer_res.get('sector_name')}): {peer_res.get('summary')} | "
            f"2. Distress Check: {distress_res.get('status')} ({distress_res.get('risk_level')} Risk) | "
            f"3. Dividend: {div_res.get('status')}"
        ),
        "timestamp": now_str
    }

    return {
        "tool_results": tool_results,
        "agent_trace": [trace_item]
    }


def valuation_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """
    Sub-Agent 1: Valuation & Capital Efficiency Analyst
    Menghasilkan Pydantic Schema 'ValuationAnalysisSchema' secara terstruktur.
    """
    ticker = state.get("ticker", "")
    company_name = state.get("company_name", "")
    price = state.get("price", "N/A")
    fair_value = state.get("fair_value", "N/A")
    mos = state.get("mos", "N/A")
    metrics = state.get("metrics", "")
    peer_res = (state.get("tool_results") or {}).get("peer_benchmark", {})

    prompt = f"""
Anda adalah Senior Quantitative Valuation Analyst di institutional hedge fund.
Fokus Anda HANYA pada valuasi intrinsik, efisiensi modal (ROE/ROIC), dan margin diskonto harga.

Target Emiten: {ticker} ({company_name})
Harga Terkini: Rp {price}
Estimasi Fair Value Konsensus: Rp {fair_value} (Margin of Safety: {mos}%)

Metrik Finansial:
{metrics}

Data Diagnostik Peer Benchmark (Hasil Eksekusi Tool):
- Sektor Teridentifikasi: {peer_res.get('sector_name')}
- Median PER Sektor: {peer_res.get('peer_median_pe')}x
- Median PBV Sektor: {peer_res.get('peer_median_pbv')}x
- Median ROE Sektor: {peer_res.get('peer_median_roe')}%
- Selisih Diskon PER terhadap Median Sektor: {peer_res.get('pe_discount_pct')}%
- Ringkasan Tool: {peer_res.get('summary')}

Tugas:
Lakukan analisis valuasi komprehensif dan kembalikan output terstruktur sesuai schema:
- valuation_status: UNDERVALUED, FAIRLY_VALUED, atau OVERVALUED
- is_value_trap: True jika harga murah karena prospek bisnis rusak/merugi
- mos_credibility_score: 1.0 - 10.0
- upside_downside_pct: estimasi % potensi apresiasi/penurunan
- valuation_memo: narasi evaluasi 2-3 paragraf padat berbasis data
"""
    structured_res = call_groq_structured(prompt, ValuationAnalysisSchema, temperature=0.2)
    now_str = datetime.now().strftime("%H:%M:%S")

    if structured_res:
        memo = structured_res.valuation_memo
        val_dump = structured_res.model_dump()
        summary_trace = (
            f"Valuasi Terstruktur: Status={structured_res.valuation_status}, "
            f"Value Trap={structured_res.is_value_trap}, "
            f"MoS Credibility={structured_res.mos_credibility_score}/10, "
            f"Upside/Downside={structured_res.upside_downside_pct:+0.1f}%."
        )
    else:
        memo = call_groq_llm(prompt, temperature=0.3)
        val_dump = None
        summary_trace = f"Evaluasi valuasi selesai untuk Fair Value Rp {fair_value} (MoS: {mos}%)."

    trace_item = {
        "agent": "📊 Valuation & Efficiency Analyst",
        "action": "Structured Intrinsic & Relative Valuation Evaluation",
        "summary": summary_trace,
        "timestamp": now_str
    }

    return {
        "valuation_analysis": memo,
        "structured_valuation": val_dump,
        "agent_trace": [trace_item]
    }


def risk_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """
    Sub-Agent 2: Solvency & Downside Risk Officer
    Menghasilkan Pydantic Schema 'RiskAnalysisSchema' secara terstruktur.
    """
    ticker = state.get("ticker", "")
    company_name = state.get("company_name", "")
    metrics = state.get("metrics", "")
    tool_results = state.get("tool_results") or {}
    distress = tool_results.get("financial_distress", {})
    div = tool_results.get("dividend_sustainability", {})

    prompt = f"""
Anda adalah Chief Risk Officer (CRO) dan Solvency Specialist di pasar modal.
Fokus Anda HANYA pada risiko neraca, likuiditas, solvabilitas utang, dan risiko arus kas.

Target Emiten: {ticker} ({company_name})

Metrik Finansial:
{metrics}

Hasil Diagnostik Uji Ketahanan (Tool Execution):
- Financial Distress Diagnostic: {distress.get('summary')} (Risk Level: {distress.get('risk_level', 'N/A')})
- Dividend Sustainability Diagnostic: {div.get('summary')}

Perhatian Khusus Konteks Industri:
- Jika BANK/Financials: DER tinggi adalah wajar (deposito nasabah). Fokus ke ROA buffer (>1.5% prima) dan NPM.
- Jika Non-Keuangan: Periksa Current Ratio (<1.0x berisiko), DER (>2.0x bahaya jika bunga naik), serta Free Cash Flow.

Tugas:
Lakukan stress-test neraca dan kembalikan output terstruktur sesuai schema:
- resilience_score: 1.0 - 10.0
- insolvency_risk_level: LOW, MODERATE, atau HIGH
- cash_flow_quality: STRONG_FCF, MODERATE_CASH, atau NEGATIVE_CASH_BURN
- top_risks: daftar 3-4 risiko konkret
- risk_memo: narasi evaluasi ketahanan kas dan utang yang kritis
"""
    structured_res = call_groq_structured(prompt, RiskAnalysisSchema, temperature=0.2)
    now_str = datetime.now().strftime("%H:%M:%S")

    if structured_res:
        memo = structured_res.risk_memo
        risk_dump = structured_res.model_dump()
        summary_trace = (
            f"Uji Risiko Terstruktur: Resilience Score={structured_res.resilience_score}/10, "
            f"Insolvency Risk={structured_res.insolvency_risk_level}, "
            f"Cash Quality={structured_res.cash_flow_quality}, "
            f"Risiko Kunci={len(structured_res.top_risks)} item teridentifikasi."
        )
    else:
        memo = call_groq_llm(prompt, temperature=0.3)
        risk_dump = None
        summary_trace = f"Uji solvabilitas selesai: Model={distress.get('model')}, Risk Level={distress.get('risk_level')}."

    trace_item = {
        "agent": "🛡️ Solvency & Downside Risk Officer",
        "action": "Structured Stress-Testing & Solvency Assessment",
        "summary": summary_trace,
        "timestamp": now_str
    }

    return {
        "risk_analysis": memo,
        "structured_risk": risk_dump,
        "agent_trace": [trace_item]
    }


def synthesis_agent_node(state: StockAgentState) -> Dict[str, Any]:
    """
    Sub-Agent 3: Chief Investment Officer (CIO) / Lead Synthesis Agent
    Menghasilkan Pydantic Schema 'CIOInvestmentReport' dengan jaminan Structured Output.
    """
    ticker = state.get("ticker", "")
    company_name = state.get("company_name", "")
    price = state.get("price", "N/A")
    score = state.get("score", "N/A")
    category = state.get("category", "N/A")
    fair_value = state.get("fair_value", "N/A")
    mos = state.get("mos", "N/A")
    business_summary = state.get("business_summary", "")
    signals = state.get("signals", "")
    metrics = state.get("metrics", "")

    val_memo = state.get("valuation_analysis", "")
    risk_memo = state.get("risk_analysis", "")
    tool_results = state.get("tool_results") or {}
    peer_bench = tool_results.get("peer_benchmark", {})
    distress = tool_results.get("financial_distress", {})

    prompt = f"""
Anda adalah Chief Investment Officer (CIO) institusi investasi terkemuka di Bursa Efek Indonesia (IHSG).
Sintesiskan laporan dari Senior Valuation Analyst dan Chief Risk Officer menjadi Laporan Investasi Terstruktur.

=========================================
DATA EMITEN:
- Kode Saham: {ticker} ({company_name})
- Harga Pasar: Rp {price}
- Skor Fundamental: {score} / 100 ({category})
- Fair Value: Rp {fair_value} (MoS: {mos}%)
- Sektor: {peer_bench.get('sector_name', 'N/A')}

DESKRIPSI BISNIS:
{business_summary}

DATA METRIK:
{metrics}

SINYAL & INDIKATOR:
{signals}

HASIL DIAGNOSTIK TOOLS:
- Peer Benchmark: {peer_bench.get('summary', 'N/A')}
- Distress Check: {distress.get('summary', 'N/A')}

LAPORAN VALUATION ANALYST:
{val_memo}

LAPORAN CHIEF RISK OFFICER:
{risk_memo}

TUGAS:
Hasilkan Laporan Investasi Final yang mengedepankan DATA KUANTITATIF DALAM TABEL disusul NARASI MENDALAM sesuai schema Pydantic CIOInvestmentReport:
1. quantitative_scorecard_table: Tabel Markdown kuantitatif ringkas dan komprehensif yang membandingkan metrik fundamental emiten vs benchmark sektor.
   Format tabel:
   | Pilar Fundamental | Indikator Utama | Nilai Emiten | Benchmark Sektor | Evaluasi / Status |
   | :--- | :--- | :--- | :--- | :--- |
   (Wajib mencakup minimal 5 baris: 1. Profitabilitas [ROE & Margin], 2. Valuasi Relatif [PER & PBV], 3. Nilai Intrinsik [Fair Value & MoS], 4. Solvabilitas & Ketahanan [DER & Distress Model], 5. Kualitas Kas & Dividen [FCF & Yield]).
2. company_overview: 1. Gambaran ringkas bisnis, model monetisasi, dan interpretasi skor {score}/100
3. profitability_efficiency: 2. Evaluasi kekuatan laba (ROE, ROA, Net Margin) vs efisiensi industri
4. valuation_discount: 3. Analisis valuasi harga pasar vs Fair Value (Rp {fair_value}) dan Margin of Safety ({mos}%)
5. balance_sheet_cashflow: 4. Solvabilitas utang (DER), likuiditas kas, dan hasil uji financial distress
6. growth_prospects: 5. Tren pertumbuhan pendapatan/laba dan katalis pertumbuhan ke depan
7. bullish_points: 6. 3-4 Poin keunggulan utama berbasis angka konkret
8. bearish_points: 6. 3-4 Poin risiko utama yang harus diwaspadai investor
9. conviction_score: Skor keyakinan investasi skala 1.0 - 10.0 (misal: 8.5)
10. investment_classification: Tentukan salah satu ("💎 Value Pick", "💰 Dividend Champion", "🚀 Growth Compounder", "⚠️ High Risk / Watchlist")
11. executive_verdict: 7. Kesimpulan objektif dan rekomendasi profil alokasi investor
"""
    structured_report = call_groq_structured(prompt, CIOInvestmentReport, temperature=0.2)
    now_str = datetime.now().strftime("%H:%M:%S")

    if structured_report:
        final_markdown = structured_report.to_markdown()
        report_dump = structured_report.model_dump()
        conviction = structured_report.conviction_score
        classification = structured_report.investment_classification
        summary_trace = (
            f"Laporan CIO Terstruktur: Conviction={conviction:.1f}/10, "
            f"Klasifikasi={classification}, Bull Cases={len(structured_report.bullish_points)}, "
            f"Bear Cases={len(structured_report.bearish_points)}."
        )
    else:
        # Fallback jika panggilan structured output mengalami kendala teknis
        final_markdown = call_groq_llm(prompt, temperature=0.3)
        report_dump = None
        conviction = None
        classification = None
        summary_trace = f"Sintesis laporan CIO selesai untuk skor fundamental {score}/100."

    trace_item = {
        "agent": "🎯 Chief Investment Officer (Synthesis)",
        "action": "Structured Consolidated Investment Thesis Formulated",
        "summary": summary_trace,
        "timestamp": now_str
    }

    return {
        "final_analysis": final_markdown,
        "structured_report": report_dump,
        "conviction_score": conviction,
        "investment_classification": classification,
        "agent_trace": [trace_item]
    }
