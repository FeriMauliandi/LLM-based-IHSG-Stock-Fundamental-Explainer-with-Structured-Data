# 📈 AI IHSG Stock Screener & Fundamental Analyzer

Aplikasi berbasis AI dan Python untuk analisis fundamental saham Bursa Efek Indonesia (IHSG), estimasi harga wajar (*Fair Value*), dan penyaringan saham *undervalued* berkualitas tinggi secara otomatis.

---

## 🌟 Fitur Utama

1. **🔍 Smart Stock Screener (IHSG)**
   - Menyaring saham-saham pilihan IHSG berdasarkan batas Skor Fundamental, batas PER, minimal ROE, dan maksimal DER.
   - Filter ketat yang menolak saham dengan data metrik kosong (*data integrity check*).
   - Preset strategi investasi: *Undervalued & Sehat (High MoS)*, *Dividen Royal*, dan *Bluechip Giant*.

2. **📊 Analisis Detail & Penjelasan AI Bahasa Indonesia**
   - Mengambil data keuangan terkini dari Yahoo Finance secara otomatis.
   - Penjelasan komprehensif dari AI dengan konteks sektoral (misal perbankan vs pertambangan vs consumer goods).
   - Breakdown 4 pilar fundamental lengkap dengan sistem **Reward & Penalty**.

3. **🧮 Multi-Model Fair Value & Margin of Safety (MoS)**
   - Menggabungkan 4 model valuasi:
     1. **Graham Number** (Kombinasi klasik EPS & BVPS)
     2. **PE Benchmark Model** (Target PER acuan)
     3. **ROE-adjusted PBV Model** (Target PBV proporsional terhadap efisiensi ekuitas)
     4. **Earnings Power Value (EPV)** (Kemampuan laba berkelanjutan disesuaikan *cost of equity*)
   - Perhitungan akhir menggunakan *weighted blend* (60% rata-rata terbobot + 40% median) untuk mengeliminasi dampak outlier.

4. **⚔️ Komparasi Saham Head-to-Head**
   - Bandingkan hingga beberapa saham pilihan sekaligus dalam satu tabel interaktif.
   - Penilaian komparatif berbasis AI yang menentukan pemenang investasi secara objektif (kategori *Value*, *Dividend*, *Growth*, atau *Avoid*).

5. **🛡️ Scoring Khusus Sektor (Sector-Aware)**
   - Sektor perbankan (Financial Services) tidak lagi dihukum secara salah karena DER atau ketiadaan Current Ratio.
   - Metrik disesuaikan dengan standar industri keuangan dunia (ROA bank > 2% diakui sebagai kelas prima, buffer laba bersih, dll).

---

## ⚙️ Persyaratan Sistem & Instalasi

### 1. Prasyarat
- Python 3.10 atau lebih baru
- Koneksi internet (untuk mengambil data dari Yahoo Finance & Groq API)

### 2. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi API Key (Opsional untuk AI Explanation)
Salin template konfigurasi:
```bash
cp .env.example .env
```
Buka `.env` dan masukkan API Key Groq Anda (dapatkan gratis di [console.groq.com/keys](https://console.groq.com/keys)):
```env
GROQ_API_KEY=gsk_xxxxxxxxx
```
> **Catatan:** Fitur analisis kuantitatif, scoring fundamental, kalkulator fair value, dan screener tetap berjalan 100% normal meskipun tanpa API Key. API Key Groq digunakan untuk analisis AI ultra-cepat (Llama 3.3 70B, Gemma 2, dll).

### 4. Menjalankan Aplikasi

#### Opsi A: Menggunakan Docker & Docker Compose (Direkomendasikan)
Menjalankan seluruh ekosistem (FastAPI Backend, Web UI, dan Streamlit Dashboard) secara instan:
```bash
docker compose up --build
```
Aplikasi dapat diakses di:
- **FastAPI Backend & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Web UI Landing Page (Tentang Proyek):** [http://localhost:8000/app/landing.html](http://localhost:8000/app/landing.html)
- **Web UI Terminal Dashboard (Screener & AI):** [http://localhost:8000/app/](http://localhost:8000/app/)
- **Streamlit Analytics Dashboard:** [http://localhost:8501](http://localhost:8501)

#### Opsi B: Menjalankan Mandiri (Lokal / Python)
Jalankan salah satu atau kedua layanan:
```bash
# 1. Jalankan Streamlit Dashboard
streamlit run App.py

# 2. Jalankan FastAPI Backend & Web UI
python backend/main.py
```

---

## 📂 Struktur Proyek

```text
Stock AI Agents/
├── .github/workflows/
│   └── ci-cd.yaml             # Pipeline CI/CD GitHub Actions (Lint, Test, Docker Build & GHCR)
├── agents/                    # Arsitektur Multi-Agent berbasis LangGraph
│   ├── graph.py               # StateGraph orchestrator (Tool Engine -> Valuation -> Risk -> CIO)
│   ├── subagents.py           # Specialized LLM Agents & nodes
│   ├── tools.py               # Dynamic Tools (Peer Benchmark, Altman Z-Score, Dividend Safety)
│   └── state.py               # Agent State & Observability Tracing definition
├── backend/
│   └── main.py                # REST API FastAPI dengan metadata trace multi-agent & static app
├── chains/
│   └── analysis_chain.py      # Entry point orkestrasi analitik & fallback provider
├── data/
│   ├── data_fetcher.py        # Pengambil data dari Yahoo Finance & normalisasi mata uang
│   └── screener.py            # Mesin screening saham paralel multithreading
├── frontend/                  # Modern Web UI (HTML5, Tailwind CSS, Vanilla JS)
│   ├── index.html
│   ├── app.js
│   └── style.css
├── reason/
│   ├── scoring.py             # Algoritma Skor Fundamental (4 Pilar, Reward & Penalty, Sector-aware)
│   ├── signals.py             # Generator sinyal kuantitatif (Valuasi, Margin, FCF Yield, Volume)
│   └── valuation.py           # Kalkulator Fair Value multi-model & Margin of Safety
├── tests/
│   └── test_multi_agent.py    # Unit tests arsitektur agent & tools kuantitatif
├── .dockerignore              # Aturan pengecualian build Docker
├── .env.example               # Template environment variables
├── .gitignore                 # Konfigurasi Git ignore
├── App.py                     # Entry point UI Streamlit (Tabs, Multi-Agent Trace, Charts)
├── ci-cd.yaml                 # Spesifikasi workflow CI/CD
├── docker-compose.yml         # Konfigurasi orkestrasi multi-service Docker
├── Dockerfile                 # Multi-stage Docker image (backend & streamlit)
├── requirements.txt           # Dependensi Python
└── README.md                  # Dokumentasi proyek
```

---

## ⚖️ Disclaimer
Aplikasi ini ditujukan untuk keperluan edukasi dan analisis riset investasi semata. Keputusan investasi saham sepenuhnya berada di tangan masing-masing investor. Selalu lakukan *Do Your Own Research* (DYOR).
