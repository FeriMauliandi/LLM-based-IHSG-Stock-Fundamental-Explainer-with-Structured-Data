# 🎨 Frontend Web App - AI IHSG Stock Screener

Antarmuka pengguna (UI) modern, interaktif, dan responsif yang dibangun menggunakan **HTML5 + Tailwind CSS + Vanilla JavaScript**.

---

## 🌟 Fitur Tampilan UI

1. **🔍 Stock Screener Tab**
   - Slider Min Skor Fundamental (0-100)
   - Batas Maks PER, Min ROE (%), Maks DER
   - 3 Preset Cepat: *Undervalued & Sehat*, *Dividen Royal*, dan *Bluechip Giant*
   - Tabel hasil screening interaktif dengan badge warna dan progress bar
   - Tombol shortcut *"Analisis AI"* langsung pada setiap baris saham

2. **📊 Analisis Detail & AI Tab**
   - Pencarian kode ticker saham IHSG (contoh: BBCA, BBRI, BMRI, TLKM, ASII, ADRO, ICBP)
   - Quick-select chip buttons untuk saham-saham populer
   - 5 Hero Metric Cards: Harga Terkini, Skor Fundamental, Fair Value, Margin of Safety (MoS %), PER / PBV
   - Visual Progress Bar untuk 4 Pilar Fundamental (Profitabilitas, Valuasi, Solvabilitas, Pertumbuhan)
   - Laporan narasi AI bahasa Indonesia (Markdown rendered via Marked.js)
   - Indikator sinyal kuantitatif terdeteksi
   - Breakdown 4 Model Fair Value (Graham Number, PE Benchmark, ROE-adjusted PBV, EPV)

3. **⚔️ Komparasi Saham Head-to-Head Tab**
   - Bandingkan 2 hingga 8 saham sekaligus secara berdampingan
   - Preset sektor cepat: *Big 4 Banks*, *Batu Bara*, *Consumer Goods*
   - Matriks perbandingan metrik finansial
   - Kartu putusan rekomendasi pemenang dari AI

4. **🧮 Kalkulator Fair Value Tab**
   - Input mandiri: Harga Pasar, EPS, Nilai Buku (BVPS), Target PER, Target PBV, Net Margin
   - Menghitung konsensus harga wajar dan tingkat diskon (Margin of Safety)

---

## 🚀 Cara Menjalankan UI

### Opsi 1: Otomatis via FastAPI Backend (Paling Praktis)
Cukup jalankan server backend:
```bash
python backend/main.py
```
Lalu buka browser Anda di:
👉 **[http://localhost:8000/app/](http://localhost:8000/app/)**

### Opsi 2: Buka Langsung File HTML
Buka file `frontend/index.html` langsung di browser Anda (klik ganda dari File Explorer) atau gunakan ekstensi Live Server VS Code.
Pastikan backend FastAPI sudah berjalan di `http://localhost:8000`.
