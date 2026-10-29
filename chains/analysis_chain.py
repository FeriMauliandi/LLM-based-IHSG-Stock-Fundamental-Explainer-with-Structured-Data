import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from agents.graph import build_stock_agent_graph

load_dotenv()

# Daftar model Groq aktif yang dicoba berurutan dengan fallback otomatis
GROQ_MODELS_TO_TRY = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b"
]

comparison_prompt = PromptTemplate.from_template("""
Anda adalah Analis Saham IHSG Senior dengan pengalaman 15+ tahun di pasar modal Indonesia.

Berikut adalah data perbandingan beberapa saham IHSG beserta skor fundamental, rasio keuangan, dan estimasi valuasinya:

{stocks_data}

---

**KONTEKS SEKTOR:**
- Saham perbankan wajar memiliki DER tinggi (3-6x) karena model bisnis leverage deposito.
- Saham tambang/komoditas memiliki siklus bisnis yang berfluktuasi.
- Saham consumer staples biasanya memiliki PER lebih tinggi karena stabilitas pendapatan.

---

Tugas Anda: Buat analisis perbandingan mendalam dengan format berikut:

### 📊 Tabel Ranking Kesehatan Fundamental
Urutkan saham dari yang paling kuat hingga paling lemah. Untuk setiap saham berikan:
- Peringkat
- Alasan 1-2 kalimat mengapa di posisi tersebut

### 💡 Perbandingan Detail per Aspek

**Profitabilitas (ROE / Net Margin):**
Saham mana yang paling efisien menghasilkan laba? Mana yang paling lemah? Berikan angka perbandingan.

**Valuasi (PER / PBV / MoS):**
Saham mana yang paling murah (undervalued)? Mana yang terlalu mahal? Kuantifikasi perbedaannya.

**Beban Utang & Risiko (DER / Current Ratio):**
Saham mana yang paling konservatif? Mana yang berisiko tinggi karena leverage? Pertimbangkan konteks sektor.

**Pertumbuhan (Revenue Growth / Earnings Growth):**
Saham mana yang tumbuh paling cepat? Mana yang stagnan atau menurun?

**Arus Kas & Dividen:**
Saham mana yang paling royal membagikan dividen dan memiliki arus kas terbaik?

### 🏆 Rekomendasi Kontekstual

1. **💎 Terbaik untuk Value Investor:** (diskon besar + fundamental kuat) — dan alasannya
2. **💰 Terbaik untuk Dividend Seeker:** (yield tinggi + konsisten) — dan alasannya
3. **🚀 Terbaik untuk Growth Investor:** (pertumbuhan tinggi + prospek cerah) — dan alasannya
4. **🛑 Saham yang Perlu Diwaspadai:** dan alasannya berdasarkan data

### ⚠️ Catatan Risiko
Sebutkan risiko utama yang perlu dipertimbangkan untuk keputusan investasi dari masing-masing saham.

**Gunakan bahasa Indonesia yang terstruktur, jelas, dan profesional. Berikan analisis objektif berbasis data, bukan spekulasi.**
""")


def get_groq_llm(model_name: str = None, temperature: float = 0.4):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    selected_model = model_name or "openai/gpt-oss-120b"
    return ChatGroq(
        model_name=selected_model,
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=2
    )


class ResilientGroqChain:
    """
    Chain pembungkus khusus provider Groq yang secara otomatis
    mencoba model cadangan jika model utama mencapai rate limit atau error.
    """
    def __init__(self, prompt, temperature=0.4):
        self.prompt = prompt
        self.temperature = temperature

    def invoke(self, inputs: dict) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "dummy" or "your_groq_api_key" in api_key.lower():
            return (
                "⚠️ **API Key Groq belum dikonfigurasi.**\n\n"
                "Untuk mengaktifkan fitur analisis dan komparasi AI secepat kilat:\n"
                "1. Buka file `.env` di folder proyek\n"
                "2. Masukkan `GROQ_API_KEY=gsk_...` (dapatkan gratis di [console.groq.com/keys](https://console.groq.com/keys))\n"
                "3. Restart aplikasi Streamlit Anda.\n\n"
                "*Catatan: Seluruh data metrik, skor fundamental kuantitatif 4 pilar, dan kalkulator harga wajar tetap berjalan 100% tanpa API Key.*"
            )

        last_exception = None
        for model in GROQ_MODELS_TO_TRY:
            try:
                llm = get_groq_llm(model_name=model, temperature=self.temperature)
                if not llm:
                    break
                chain = self.prompt | llm | StrOutputParser()
                return chain.invoke(inputs)
            except Exception as e:
                print(f"Model Groq '{model}' gagal: {e}. Beralih ke model cadangan berikutnya...")
                last_exception = e

        return f"Maaf, tidak dapat menghubungi model Groq saat ini. Pastikan kuota atau koneksi internet Anda aman. Detail error: {last_exception}"


def build_analysis_chain():
    """
    Mengembalikan StateGraph Multi-Agent LangGraph
    (Tool Engine + Valuation Analyst + Risk Officer + CIO Synthesis).
    """
    return build_stock_agent_graph()


def build_comparison_chain():
    """
    Chain komparasi head-to-head untuk membandingkan beberapa saham sekaligus.
    """
    return ResilientGroqChain(comparison_prompt, temperature=0.3)
