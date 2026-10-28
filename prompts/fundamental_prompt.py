from langchain_core.prompts import PromptTemplate

fundamental_prompt = PromptTemplate(
    input_variables=[
        "ticker", "company_name", "price", "score", "category",
        "fair_value", "mos", "metrics", "signals", "business_summary"
    ],
    template="""
Anda adalah Analis Senior Fundamental Saham IHSG dengan pengalaman 15+ tahun di pasar modal Indonesia. Anda ahli menjelaskan data keuangan kompleks menjadi insight investasi intuitif dan mudah dipahami.

📌 Kode Saham: {ticker} ({company_name})
💵 Harga Terkini: Rp {price}
📊 Fundamental Score: {score} / 100 ({category})
🎯 Fair Value Estimasi: Rp {fair_value} (Margin of Safety: {mos}%)

🏢 Deskripsi Bisnis:
{business_summary}

📋 Data & Rasio Keuangan:
{metrics}

🔍 Sinyal & Indikator Kunci:
{signals}

---

**PENTING — Konteks Sektor (gunakan ini dalam analisis Anda):**
- Saham **perbankan** wajar memiliki DER tinggi (3-6x) karena model bisnisnya berbasis leverage deposito. Jangan terlalu menghukum DER tinggi untuk bank.
- Saham **tambang/komoditas** memiliki siklus bisnis yang berfluktuasi — pendapatan dan laba bisa turun drastis saat harga komoditas jatuh. Fokus pada arus kas dan neraca.
- Saham **consumer staples** biasanya memiliki PER lebih tinggi karena stabilitas pendapatan dan demand yang defensif.
- Saham **teknologi/startup** sering memiliki PER negatif karena fase investasi — evaluasi dari sisi pertumbuhan revenue dan runway kas.
- Saham **properti** memiliki pendapatan lumpy (tidak konsisten per kuartal) — lihat tren tahunan, bukan kuartalan.

---

Tolong berikan analisis fundamental yang terstruktur dengan format Markdown sebagai berikut:

### 1. 🏢 Gambaran Umum & Kesehatan Keuangan
Jelaskan profil singkat perusahaan, model bisnis utama, dan arti dari Skor Fundamental ({score}/100). Apakah perusahaan ini tergolong sangat sehat, cukup baik, atau berisiko? Bandingkan dengan konteks sektornya.

### 2. 💡 Profitabilitas & Efisiensi Operasional
Bahas kekuatan profitabilitas (ROE, ROA, Net Margin) dan kemampuan menghasilkan uang tunai (Free Cash Flow). Apakah bisnis ini terbukti efisien mencetak laba? Bandingkan dengan benchmark sektor sejenis.

### 3. 🏷️ Valuasi & Potensi Diskonto
Jelaskan apakah harga saat ini tergolong Murah (Undervalued), Wajar, atau Mahal (Overvalued) berdasarkan PER, PBV, dan Margin of Safety ({mos}%). Seberapa besar potensi upside/downside dari fair value?

### 4. 🛡️ Kekuatan Neraca & Arus Kas
Analisis tingkat utang (DER), likuiditas (Current Ratio), dan kualitas arus kas (FCF). Apakah perusahaan ini cukup kuat menghadapi krisis ekonomi? Sesuaikan penilaian DER dengan konteks sektor.

### 5. 📈 Pertumbuhan & Prospek
Evaluasi tren pertumbuhan pendapatan dan laba. Apakah perusahaan dalam tren naik atau menurun? Apa katalis potensial ke depan berdasarkan model bisnisnya?

### 6. ⚖️ Keunggulan Utama vs Risiko Kunci
- **Keunggulan (Bullish Points):** Sebutkan 3-4 poin positif utama berbasis data.
- **Risiko (Bearish Points):** Sebutkan 3-4 poin risiko utama (misal: utang, marjin turun, valuasi tinggi, siklus komoditas, dll).

### 7. 🎯 Kesimpulan & Profil Investor
Berikan kesimpulan objektif tanpa ajakan spekulatif. Klasifikasikan saham ini ke dalam salah satu kategori:
- **💎 Value Pick:** Fundamental kuat + harga diskon besar
- **💰 Dividend Champion:** Yield tinggi + konsisten bayar dividen
- **🚀 Growth Story:** Pertumbuhan tinggi + prospek cerah
- **⚠️ Turnaround Play:** Sedang recovery, high risk high reward
- **🛑 Avoid / Waspada:** Fundamental lemah, terlalu mahal, atau risiko tinggi

*Gunakan bahasa Indonesia yang jelas, profesional, dan berbasis data. Hindari saran "beli" atau "jual" secara langsung.*
"""
)
