import pytest
from agents.tools import (
    peer_benchmark_tool,
    financial_distress_tool,
    dividend_sustainability_tool
)
from agents.graph import create_stock_agent_graph, StockAgentRunner
from agents.schemas import (
    ValuationAnalysisSchema,
    RiskAnalysisSchema,
    CIOInvestmentReport
)


def test_peer_benchmark_tool_financial():
    res = peer_benchmark_tool(
        ticker="BBCA.JK",
        sector="Financial Services",
        industry="Banks - Diversified",
        pe=20.0,
        pbv=4.5,
        roe=0.22
    )
    assert res["tool_name"] == "peer_benchmark_tool"
    assert res["sector_key"] == "financial"
    assert res["peer_median_pe"] > 0
    assert "summary" in res


def test_financial_distress_tool_bank():
    res = financial_distress_tool(
        ticker="BBCA.JK",
        sector="Financial Services",
        roa=0.034,
        roe=0.22,
        profit_margin=0.45
    )
    assert res["risk_level"] == "LOW"
    assert "Prime" in res["status"]


def test_financial_distress_tool_corporate():
    res = financial_distress_tool(
        ticker="ASII.JK",
        sector="Industrials",
        roa=0.08,
        roe=0.15,
        current_ratio=1.5,
        debt_to_equity=0.8,
        profit_margin=0.10
    )
    assert res["tool_name"] == "financial_distress_tool"
    assert res["risk_level"] in ["LOW", "MODERATE"]


def test_dividend_sustainability_tool():
    res = dividend_sustainability_tool(
        ticker="ITMG.JK",
        dividend_yield=0.12,
        free_cashflow=5000000000000,
        profit_margin=0.25
    )
    assert res["is_sustainable"] is True
    assert "Cash-backed" in res["status"]


def test_stock_agent_graph_compilation():
    graph = create_stock_agent_graph()
    assert graph is not None


def test_valuation_analysis_schema():
    data = {
        "valuation_status": "UNDERVALUED",
        "is_value_trap": False,
        "mos_credibility_score": 8.5,
        "upside_downside_pct": 14.5,
        "valuation_memo": "Saham diperdagangkan dengan diskon 14.5% dari fair value konsensus."
    }
    schema = ValuationAnalysisSchema.model_validate(data)
    assert schema.valuation_status == "UNDERVALUED"
    assert schema.is_value_trap is False
    assert schema.mos_credibility_score == 8.5


def test_risk_analysis_schema():
    data = {
        "resilience_score": 9.0,
        "insolvency_risk_level": "LOW",
        "cash_flow_quality": "STRONG_FCF",
        "top_risks": ["Penurunan margin bunga bersih", "Kenaikan biaya kredit (CKPN)"],
        "risk_memo": "Ketahanan likuiditas sangat kuat didukung dana pihak ketiga (CASA) tinggi."
    }
    schema = RiskAnalysisSchema.model_validate(data)
    assert schema.resilience_score == 9.0
    assert schema.insolvency_risk_level == "LOW"
    assert len(schema.top_risks) == 2


def test_cio_investment_report_schema_and_markdown():
    data = {
        "quantitative_scorecard_table": (
            "| Pilar | Indikator | Nilai Emiten | Benchmark Sektor | Evaluasi |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| Profitabilitas | ROE | 22.4% | 14.5% | 🟢 Unggul |\n"
            "| Valuasi | PER | 21.5x | 12.5x | 🟡 Premium |"
        ),
        "company_overview": "Bank swasta dengan basis CASA tertinggi di Indonesia.",
        "profitability_efficiency": "ROE 22.4% melampaui median sektor perbankan (14.5%).",
        "valuation_discount": "Diperdagangkan pada PER 21.5x, diskon MoS 12.7% terhadap fair value.",
        "balance_sheet_cashflow": "ROA 3.4% memberikan bantalan risiko insolvensi sangat tinggi.",
        "growth_prospects": "Pertumbuhan transaksi digital dan pertumbuhan kredit stabil 10-12% YoY.",
        "bullish_points": [
            "Dominasi ekosistem pembayaran dan transaksi retail di Indonesia",
            "Biaya dana (CoF) sangat rendah berkat CASA >80%",
            "Kualitas aset prima dengan NPL terjaga di bawah 2%"
        ],
        "bearish_points": [
            "Valuasi premium (PBV ~4.8x) membatasi upside jangka pendek",
            "Siklus suku bunga ketat dapat menekan pertumbuhan kredit modal kerja"
        ],
        "conviction_score": 9.2,
        "investment_classification": "💎 Value Pick",
        "executive_verdict": "Sangat layak untuk alokasi inti portofolio jangka panjang."
    }
    report = CIOInvestmentReport.model_validate(data)
    assert report.conviction_score == 9.2
    assert report.investment_classification == "💎 Value Pick"
    md = report.to_markdown()
    assert "### 📊 Rangkuman Metrik Kuantitatif & Benchmark Sektor" in md
    assert "| Profitabilitas | ROE |" in md
    assert "### 1. 🏢 Gambaran Umum & Kesehatan Keuangan" in md
    assert "### 7. 🎯 Kesimpulan & Profil Investor" in md
    assert "9.2 / 10.0" in md
    assert "💎 Value Pick" in md
