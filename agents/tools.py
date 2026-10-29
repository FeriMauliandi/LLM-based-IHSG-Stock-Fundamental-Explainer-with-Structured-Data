"""
Financial Diagnostics & Peer Benchmarking Tools for Stock AI Agents.
These tools provide quantitative insights dynamically invoked during agent analysis.
"""
from typing import Dict, Any, Optional

# Empirical median metrics for IDX (IHSG) sectors (2024-2026 reference)
IHSG_SECTOR_BENCHMARKS = {
    "financial": {
        "sector_name": "Financial Services (Perbankan & Asuransi)",
        "median_pe": 12.5,
        "median_pbv": 1.6,
        "median_roe": 14.5,
        "median_der": 4.5,
        "median_npm": 22.0
    },
    "energy": {
        "sector_name": "Energy (Batu Bara & Migas)",
        "median_pe": 6.8,
        "median_pbv": 1.15,
        "median_roe": 17.5,
        "median_der": 0.65,
        "median_npm": 16.0
    },
    "consumer": {
        "sector_name": "Consumer Staples & Discretionary",
        "median_pe": 17.5,
        "median_pbv": 2.7,
        "median_roe": 16.0,
        "median_der": 0.85,
        "median_npm": 9.0
    },
    "telecom": {
        "sector_name": "Telecommunication & Technology",
        "median_pe": 16.0,
        "median_pbv": 2.1,
        "median_roe": 12.5,
        "median_der": 1.15,
        "median_npm": 12.5
    },
    "basic": {
        "sector_name": "Basic Materials (Nikel, Emas, Semen)",
        "median_pe": 11.5,
        "median_pbv": 1.45,
        "median_roe": 12.0,
        "median_der": 0.75,
        "median_npm": 10.5
    },
    "industrial": {
        "sector_name": "Industrials & Otomotif",
        "median_pe": 10.5,
        "median_pbv": 1.25,
        "median_roe": 11.5,
        "median_der": 0.70,
        "median_npm": 7.5
    },
    "property": {
        "sector_name": "Real Estate & Properti",
        "median_pe": 13.5,
        "median_pbv": 0.75,
        "median_roe": 6.8,
        "median_der": 0.60,
        "median_npm": 14.0
    },
    "healthcare": {
        "sector_name": "Healthcare & Farmasi",
        "median_pe": 21.0,
        "median_pbv": 2.6,
        "median_roe": 13.5,
        "median_der": 0.45,
        "median_npm": 11.0
    },
    "default": {
        "sector_name": "IHSG Composite Benchmark",
        "median_pe": 13.5,
        "median_pbv": 1.5,
        "median_roe": 12.0,
        "median_der": 0.85,
        "median_npm": 11.0
    }
}


def _detect_sector_key(sector: Optional[str], industry: Optional[str]) -> str:
    combined = f"{sector or ''} {industry or ''}".lower()
    if any(k in combined for k in ["financial", "bank", "insurance"]):
        return "financial"
    if any(k in combined for k in ["energy", "coal", "oil", "gas", "petroleum"]):
        return "energy"
    if any(k in combined for k in ["consumer", "food", "beverage", "retail"]):
        return "consumer"
    if any(k in combined for k in ["telecom", "technology", "tech", "software"]):
        return "telecom"
    if any(k in combined for k in ["basic material", "mining", "metal", "gold", "nickel", "chemical"]):
        return "basic"
    if any(k in combined for k in ["industrial", "auto", "machinery", "conglomerate"]):
        return "industrial"
    if any(k in combined for k in ["real estate", "property"]):
        return "property"
    if any(k in combined for k in ["health", "pharma", "hospital"]):
        return "healthcare"
    return "default"


def peer_benchmark_tool(
    ticker: str,
    sector: Optional[str] = None,
    industry: Optional[str] = None,
    pe: Optional[float] = None,
    pbv: Optional[float] = None,
    roe: Optional[float] = None
) -> Dict[str, Any]:
    """
    Membandingkan valuasi dan profitabilitas saham terhadap median sektor IHSG.
    """
    key = _detect_sector_key(sector, industry)
    bench = IHSG_SECTOR_BENCHMARKS.get(key, IHSG_SECTOR_BENCHMARKS["default"])

    roe_val = (roe * 100) if (roe is not None and roe < 1.5) else roe

    pe_discount = None
    if pe is not None and pe > 0:
        pe_discount = ((bench["median_pe"] - pe) / bench["median_pe"]) * 100

    pbv_discount = None
    if pbv is not None and pbv > 0:
        pbv_discount = ((bench["median_pbv"] - pbv) / bench["median_pbv"]) * 100

    roe_gap = None
    if roe_val is not None:
        roe_gap = roe_val - bench["median_roe"]

    # Diagnosis status
    notes = []
    if pe_discount is not None:
        if pe_discount > 20:
            notes.append(f"Diskon PER {pe_discount:.1f}% di bawah median industri ({bench['median_pe']}x)")
        elif pe_discount < -20:
            notes.append(f"Premium PER {abs(pe_discount):.1f}% di atas median industri ({bench['median_pe']}x)")
        else:
            notes.append(f"PER in-line dengan median industri ({bench['median_pe']}x)")

    if roe_gap is not None:
        if roe_gap > 3.0:
            notes.append(f"Efisiensi ROE unggul (+{roe_gap:.1f}% pts vs median {bench['median_roe']}%)")
        elif roe_gap < -3.0:
            notes.append(f"Efisiensi ROE tertinggal ({roe_gap:.1f}% pts vs median {bench['median_roe']}%)")

    summary_text = f"Sektor: {bench['sector_name']}. " + "; ".join(notes) if notes else "Data perbandingan terbatas."

    return {
        "tool_name": "peer_benchmark_tool",
        "sector_key": key,
        "sector_name": bench["sector_name"],
        "peer_median_pe": bench["median_pe"],
        "peer_median_pbv": bench["median_pbv"],
        "peer_median_roe": bench["median_roe"],
        "pe_discount_pct": round(pe_discount, 1) if pe_discount is not None else None,
        "pbv_discount_pct": round(pbv_discount, 1) if pbv_discount is not None else None,
        "roe_gap_pts": round(roe_gap, 1) if roe_gap is not None else None,
        "summary": summary_text
    }


def financial_distress_tool(
    ticker: str,
    sector: Optional[str] = None,
    industry: Optional[str] = None,
    roa: Optional[float] = None,
    roe: Optional[float] = None,
    current_ratio: Optional[float] = None,
    debt_to_equity: Optional[float] = None,
    profit_margin: Optional[float] = None
) -> Dict[str, Any]:
    """
    Menghitung skor ketahanan solvabilitas & indikator risiko kebangkrutan / distress.
    Mengadaptasi Altman Z-Score Emerging Market untuk non-keuangan,
    serta Prudential Asset Quality Buffer untuk perbankan/keuangan.
    """
    key = _detect_sector_key(sector, industry)

    if key == "financial":
        # Financial / Banking Prudential Assessment
        roa_pct = (roa * 100) if (roa is not None and roa < 1.0) else roa
        npm_pct = (profit_margin * 100) if (profit_margin is not None and profit_margin < 1.0) else profit_margin

        is_prime_bank = (roa_pct is not None and roa_pct >= 2.0)
        is_safe_bank = (roa_pct is not None and roa_pct >= 1.2)

        if is_prime_bank:
            status = "Safe / Prime Banking"
            desc = f"Ketahanan bank sangat prima. ROA ({roa_pct:.2f}%) berada di kuartil teratas perbankan Indonesia (buffer laba sangat kuat terhadap potensi NPL)."
            risk_level = "LOW"
        elif is_safe_bank:
            status = "Adequate Banking"
            desc = f"Ketahanan permodalan dan profitabilitas memadai (ROA {roa_pct:.2f}%). Risiko likuiditas terkontrol."
            risk_level = "MODERATE"
        else:
            status = "Watchlist / Low Margin"
            desc = f"ROA ({roa_pct:.2f}% if roa_pct else 'N/A') di bawah standar perbankan sehat. Rentan terhadap pemburukan kualitas kredit (CKPN)."
            risk_level = "HIGH"

        return {
            "tool_name": "financial_distress_tool",
            "model": "Bank Prudential Quality Assessment",
            "status": status,
            "risk_level": risk_level,
            "score": roa_pct,
            "summary": desc
        }

    # Non-Financial: Emerging Market Altman Z-Score Proxy
    # Z' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    cr = current_ratio if current_ratio is not None else 1.2
    x1 = min(max((cr - 1.0) * 0.25, -0.5), 0.5)

    roe_val = roe if roe is not None else 0.10
    x2 = min(max(roe_val * 0.4, -0.4), 0.6)

    roa_val = roa if roa is not None else 0.05
    x3 = min(max(roa_val * 1.5, -0.5), 0.8)

    der = debt_to_equity if (debt_to_equity is not None and debt_to_equity > 0) else 1.0
    x4 = min(1.0 / der, 4.0)

    z_score = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4

    if z_score > 2.6:
        status = "Safe Zone"
        risk_level = "LOW"
        desc = f"Altman Z-Score Proxy ({z_score:.2f} > 2.60): Neraca sangat sehat, probabilitas tekanan finansial/kebangkrutan sangat rendah."
    elif z_score >= 1.1:
        status = "Grey Zone"
        risk_level = "MODERATE"
        desc = f"Altman Z-Score Proxy ({z_score:.2f} [1.10 - 2.60]): Posisi keuangan moderat. Perlu dipantau ketat beban bunga dan jatuh tempo utang."
    else:
        status = "Distress Zone"
        risk_level = "HIGH"
        desc = f"Altman Z-Score Proxy ({z_score:.2f} < 1.10): Risiko solvabilitas tinggi. Beban utang menekan profitabilitas dan likuiditas."

    return {
        "tool_name": "financial_distress_tool",
        "model": "Emerging Market Altman Z-Score Proxy",
        "z_score": round(z_score, 2),
        "status": status,
        "risk_level": risk_level,
        "summary": desc
    }


def dividend_sustainability_tool(
    ticker: str,
    dividend_yield: Optional[float] = None,
    free_cashflow: Optional[float] = None,
    profit_margin: Optional[float] = None
) -> Dict[str, Any]:
    """
    Menguji apakah dividen yang dibayarkan didukung arus kas operasi riil
    atau berpotensi menjadi 'Dividend Trap'.
    """
    yield_pct = (dividend_yield * 100) if (dividend_yield is not None and dividend_yield < 1.0) else (dividend_yield or 0.0)

    if yield_pct <= 0.05:
        return {
            "tool_name": "dividend_sustainability_tool",
            "status": "No / Negligible Dividend",
            "is_sustainable": True,
            "summary": "Perusahaan fokus pada reinvestasi pertumbuhan (pertumbuhan modal) atau belum membagikan dividen reguler."
        }

    is_fcf_positive = (free_cashflow is not None and free_cashflow > 0)

    if yield_pct >= 6.0 and not is_fcf_positive and free_cashflow is not None:
        return {
            "tool_name": "dividend_sustainability_tool",
            "status": "Dividend Trap Risk (High Yield, Negative FCF)",
            "is_sustainable": False,
            "yield_pct": round(yield_pct, 2),
            "summary": f"Peringatan: Yield tinggi ({yield_pct:.1f}%) namun Free Cash Flow negatif. Dividen berisiko dipotong jika dibiayai utang atau menguras kas internal."
        }

    if is_fcf_positive:
        return {
            "tool_name": "dividend_sustainability_tool",
            "status": "Cash-backed Sustainable Dividend",
            "is_sustainable": True,
            "yield_pct": round(yield_pct, 2),
            "summary": f"Dividen aman ({yield_pct:.1f}% yield): Didukung oleh Arus Kas Bebas (FCF) positif dan profitabilitas yang solid."
        }

    return {
        "tool_name": "dividend_sustainability_tool",
        "status": "Moderate Dividend Safety",
        "is_sustainable": True,
        "yield_pct": round(yield_pct, 2),
        "summary": f"Membagikan dividen dengan yield {yield_pct:.1f}%. Data FCF terbatas, perlu verifikasi payout ratio riil."
    }
