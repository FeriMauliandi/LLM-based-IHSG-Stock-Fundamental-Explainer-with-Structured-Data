# 🚀 FastAPI Backend - AI IHSG Stock Screener & Analyzer

Backend API berbasis **FastAPI** dalam 1 file mandiri (`main.py`) yang mencakup semua fungsi fundamental analysis, screening saham IHSG, komparasi head-to-head, kalkulator fair value, dan rekomendasi AI.

---

## 🏃 Cara Menjalankan Backend

Jalankan langsung menggunakan Python:
```bash
python backend/main.py
```

Atau menggunakan `uvicorn`:
```bash
uvicorn backend.main:app --reload --port 8000
```

Setelah server aktif:
- **Interactive Swagger UI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Root API Status**: [http://localhost:8000/](http://localhost:8000/)

---

## 📡 Daftar Endpoint Utama

| Metode | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| `GET` | `/` | Info status & daftar endpoint API |
| `GET` | `/health` | Health check & verifikasi API Key Groq |
| `GET` | `/api/stocks/popular` | Daftar ticker saham IHSG populer terkurasi |
| `GET` | `/api/stocks/{ticker}` | Analisis fundamental, skor 4 pilar, harga wajar, sinyal (`?include_ai=true/false`) |
| `POST` | `/api/stocks/analyze` | Analisis saham via payload POST `{ "ticker": "BBCA", "include_ai": true }` |
| `GET` | `/api/screener/presets` | Daftar preset screener (*undervalued*, *dividen*, *bluechip*) |
| `POST` | `/api/screener/run` | Menjalankan screener saham IHSG paralel dengan filter skor/PER/ROE/DER |
| `POST` | `/api/compare` | Komparasi 2-8 saham sekaligus + putusan pemenang dari AI |
| `POST` | `/api/valuation/calculate` | Kalkulator multi-model Fair Value berdasarkan input manual |
