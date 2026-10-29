"""
Pydantic Schemas for Structured Outputs in Stock AI Agents.
Ensures deterministic, type-safe, and verifiable outputs from LLM Agents.
"""
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class ValuationAnalysisSchema(BaseModel):
    """Schema hasil evaluasi dari Valuation & Capital Efficiency Analyst."""
    valuation_status: Literal["UNDERVALUED", "FAIRLY_VALUED", "OVERVALUED"] = Field(
        ..., description="Status valuasi saham terhadap nilai wajar"
    )
    is_value_trap: bool = Field(
        ..., description="True jika harga murah karena penurunan fundamental riil / bisnis merugi (Value Trap)"
    )
    mos_credibility_score: float = Field(
        ..., ge=1.0, le=10.0, description="Kredibilitas Margin of Safety skala 1.0 - 10.0"
    )
    upside_downside_pct: float = Field(
        ..., description="Estimasi potensi apresiasi harga (+) atau penurunan (-) dalam persen"
    )
    valuation_memo: str = Field(
        ..., description="Narasi penjelasan detail valuasi dan perbandingan efisiensi modal vs sektor"
    )


class RiskAnalysisSchema(BaseModel):
    """Schema hasil evaluasi dari Solvency & Downside Risk Officer."""
    resilience_score: float = Field(
        ..., ge=1.0, le=10.0, description="Skor ketahanan neraca dalam menghadapi krisis (1.0 - 10.0)"
    )
    insolvency_risk_level: Literal["LOW", "MODERATE", "HIGH"] = Field(
        ..., description="Tingkat risiko kebangkrutan atau tekanan likuiditas utang"
    )
    cash_flow_quality: Literal["STRONG_FCF", "MODERATE_CASH", "NEGATIVE_CASH_BURN"] = Field(
        ..., description="Kualitas arus kas operasional dan arus kas bebas (FCF)"
    )
    top_risks: List[str] = Field(
        ..., min_length=2, max_length=5, description="3-4 risiko finansial dan operasional terbesar emiten"
    )
    risk_memo: str = Field(
        ..., description="Narasi evaluasi beban utang (DER), likuiditas, dan uji ketahanan kas"
    )


class CIOInvestmentReport(BaseModel):
    """
    Schema laporan investasi akhir dari Chief Investment Officer (Synthesis Agent).
    Memadukan ringkasan data kuantitatif dalam tabel komparatif disusul narasi analitis mendalam.
    """
    quantitative_scorecard_table: str = Field(
        ...,
        description=(
            "Tabel Markdown kuantitatif ringkas membandingkan metrik emiten vs benchmark industri. "
            "Format: | Pilar Fundamental | Indikator Kunci | Nilai Emiten | Benchmark Sektor | Status / Evaluasi |"
        )
    )
    company_overview: str = Field(
        ..., description="1. Gambaran umum profil bisnis, monetisasi, dan kesehatan keuangan"
    )
    profitability_efficiency: str = Field(
        ..., description="2. Pembahasan kekuatan profitabilitas (ROE, ROA, Net Margin) vs sektor"
    )
    valuation_discount: str = Field(
        ..., description="3. Evaluasi valuasi harga pasar vs Fair Value dan Margin of Safety"
    )
    balance_sheet_cashflow: str = Field(
        ..., description="4. Solvabilitas utang (DER), likuiditas kas, dan hasil uji financial distress"
    )
    growth_prospects: str = Field(
        ..., description="5. Tren pertumbuhan pendapatan/laba dan katalis potensial masa depan"
    )
    bullish_points: List[str] = Field(
        ..., min_length=2, max_length=5, description="6. 3-4 Poin keunggulan utama (Bull Case)"
    )
    bearish_points: List[str] = Field(
        ..., min_length=2, max_length=5, description="6. 3-4 Poin risiko utama (Bear Case)"
    )
    conviction_score: float = Field(
        ..., ge=1.0, le=10.0, description="Tingkat keyakinan investasi skala 1.0 - 10.0"
    )
    investment_classification: Literal[
        "💎 Value Pick",
        "💰 Dividend Champion",
        "🚀 Growth Compounder",
        "⚠️ High Risk / Watchlist"
    ] = Field(
        ..., description="Klasifikasi profil investor untuk saham ini"
    )
    executive_verdict: str = Field(
        ..., description="7. Kesimpulan objektif dan rekomendasi alokasi portofolio"
    )

    def to_markdown(self) -> str:
        """Mengonversi Pydantic Schema ke Markdown kuantitatif terstruktur (Tabel Data + Narasi 7 Bagian)."""
        table_block = ""
        if self.quantitative_scorecard_table:
            clean_table = self.quantitative_scorecard_table.strip()
            table_block = f"### 📊 Rangkuman Metrik Kuantitatif & Benchmark Sektor\n{clean_table}\n\n---\n\n"

        bull_str = "\n".join(
            f"- {p}" if not p.strip().startswith("-") else p for p in self.bullish_points
        )
        bear_str = "\n".join(
            f"- {p}" if not p.strip().startswith("-") else p for p in self.bearish_points
        )

        return f"""{table_block}### 1. 🏢 Gambaran Umum & Kesehatan Keuangan
{self.company_overview}

### 2. 💡 Profitabilitas & Efisiensi Operasional
{self.profitability_efficiency}

### 3. 🏷️ Valuasi & Potensi Diskonto
{self.valuation_discount}

### 4. 🛡️ Kekuatan Neraca & Arus Kas
{self.balance_sheet_cashflow}

### 5. 📈 Pertumbuhan & Prospek
{self.growth_prospects}

### 6. ⚖️ Keunggulan Utama vs Risiko Kunci
**Keunggulan (Bullish Points):**
{bull_str}

**Risiko (Bearish Points):**
{bear_str}

### 7. 🎯 Kesimpulan & Profil Investor
- **Tingkat Keyakinan (Conviction Score):** {self.conviction_score:.1f} / 10.0
- **Klasifikasi Saham:** {self.investment_classification}

{self.executive_verdict}
"""
