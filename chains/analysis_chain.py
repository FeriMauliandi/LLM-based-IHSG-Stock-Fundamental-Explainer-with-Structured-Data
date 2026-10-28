import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from prompts.fundamental_prompt import fundamental_prompt
from prompts.comparison_prompt import comparison_prompt

load_dotenv()

# Daftar model Groq aktif yang dicoba berurutan dengan fallback otomatis
GROQ_MODELS_TO_TRY = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b"
]


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
    return ResilientGroqChain(fundamental_prompt, temperature=0.4)


def build_comparison_chain():
    return ResilientGroqChain(comparison_prompt, temperature=0.3)
