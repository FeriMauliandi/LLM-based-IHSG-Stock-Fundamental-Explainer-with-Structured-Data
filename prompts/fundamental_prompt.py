from langchain_core.prompts import PromptTemplate

fundamental_prompt = PromptTemplate(
    input_variables=["ticker", "company_name", "price", "score", "category", "fair_value", "mos", "metrics", "signals"],
    template="""
Anda adalah Analis Senior Fundamental Saham IHSG yang ahli menjelaskan data keuangan kompleks menjadi insight investasi intuitif dan mudah dipahami.

📌 Kode Saham: {ticker} ({company_name})
💵 Harga Terkini: Rp {price}
📊 Fundamental Score: {score} / 100 ({category})
🎯 Fair Value Estimasi: Rp {fair_value} (Margin of Safety: {mos}%)

📋 Data & Rasio Keuangan:
{metrics}

🔍 Sinyal & Indikator Kunci:
{signals}

---
Tolong berikan analisis fundamental yang terstruktur dengan format Markdown jernih sebagai berikut:

### 1. 🏢 Gambaran Umum & Kesehatan Keuangan
Jelaskan profil singkat perusahaan dan arti dari Skor Fundamental ({score}/100). Apakah perusahaan ini tergolong sangat sehat, cukup baik, atau berisiko?

### 2. 💡 Profitabilitas & Efisiensi Operasional
Bahas kekuatan profitabilitas (ROE, Net Margin) dan kemampuan menghasilkan uang tunai (Free Cash Flow). Apakah bisnis ini terbukti efisien mencetak laba?

### 3. 🏷️ Valuasi & Potensi Diskonto
Jelaskan apakah harga saat ini tergolong Murah (Undervalued), Wajar, atau Mahal (Overvalued) berdasarkan PER, PBV, dan Margin of Safety ({mos}%).

### 4. ⚖️ Keunggulan Utama vs Risiko Kunci
- **Keunggulan (Bullish Points):** Sebutkan 2-3 poin positif utama.
- **Risiko (Bearish Points):** Sebutkan 2-3 poin risiko utama (misal utang, marjin turun, atau valuasi tinggi).

### 5. 🎯 Kesimpulan & Profil Investor
Berikan kesimpulan objektif tanpa ajakan spekulatif. Siapa jenis investor yang cocok mempertimbangkan saham ini (misal: Value Investor, Dividend Seeker, Growth Investor, atau Waspada)?

*Gunakan bahasa Indonesia yang jelas, profesional, dan ramah pemula.*
"""
)
