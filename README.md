# LLM-based IHSG Stock Fundamental Explainer with Structured Data

AI-powered system untuk menjelaskan fundamental saham IHSG dengan bahasa sederhana menggunakan LLM, LangChain, dan data terstruktur dari Yahoo Finance.

## Gambaran Umum

Proyek ini adalah AI Agent berbasis LLM yang bertujuan membantu investor pemula maupun non-finansial memahami indikator fundamental saham IHSG secara mudah, ringkas, dan kontekstual.
Alih-alih menampilkan angka mentah (PE Ratio, ROE, Market Cap, dll), sistem ini:

 - Mengambil data keuangan terstruktur dari Yahoo Finance

 - Memprosesnya menggunakan LangChain

 - Menghasilkan penjelasan natural language dalam Bahasa Indonesia


## Arsitektur Sistem

```
[yFinance API]
      ↓
[Structured Financial Data]
      ↓
[LangChain Prompt + LLM (OpenRouter)]
      ↓
[Fundamental Explanation Engine]
      ↓
[Streamlit Web App]
```


## Data yang Digunakan (Structured Data)

Data diambil menggunakan **yfinance**, meliputi:

* Harga saham terkini
* Market Capitalization
* Revenue
* Net Income
* PE Ratio
* PB Ratio
* ROE
* Debt to Equity

Semua data dikonversi ke **dictionary / JSON** sebelum dikirim ke LLM.

**Inilah yang dimaksud *Structured Data***


## Tech Stack

* **Python 3.10+**
* **LangChain** (LLM orchestration)
* **OpenRouter API** (LLM provider)
* **yfinance** (financial data)
* **Streamlit** (UI)

---

## Cara Menjalankan

### 1️⃣ Clone Repo

```bash
git clone https://github.com/FeryMauliandi/LLM-based-IHSG-Stock-Fundamental-Explainer-with-Structured-Data.git
cd LLM-based-IHSG-Stock-Fundamental-Explainer-with-Structured-Data
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set API Key OpenRouter

```bash
export OPENROUTER_API_KEY=your_api_key
```

*(Windows: gunakan `setx`)*

### 4️⃣ Jalankan Streamlit

```bash
streamlit run App.py
```

---

**Fery Mauliandi**
AI Engineer | LLM & Applied AI Enthusiast

---

⭐ Jika repo ini membantu atau menarik, jangan lupa kasih **Star**!
