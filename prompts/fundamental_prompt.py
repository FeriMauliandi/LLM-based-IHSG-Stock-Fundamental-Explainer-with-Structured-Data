from langchain_core.prompts import PromptTemplate

fundamental_prompt = PromptTemplate(
    input_variables=["ticker", "price", "metrics", "signals"],
    template="""
Anda adalah asisten analisis fundamental saham yang berpengalaman menjelaskan analisa fundamental kepada pemula.

Kode saham: {ticker}

Data fundamental:
{metrics}

Sinyal awal yang terdeteksi:
{signals}

Tugas Anda:
1. Sebutkan kode saham, harga, dan bisnis summary
2. Jelaskan arti masing-masing indikator fundamental di atas serta nilai aktual dengan bahasa Indonesia yang sederhana.
3. Jelaskan kondisi perusahaan secara umum berdasarkan data fundamental tersebut (misalnya sehat, cukup baik, atau berisiko).
4. Sebutkan kekuatan utama dan risiko utama perusahaan berdasarkan data.
5. Apakah saham perusahaan tersebut bisa dibilang undervalue dan berpotensi naik berdasarkan data value dan volume.

Gunakan bahasa yang mudah dipahami oleh pemula.
Hindari istilah teknis yang berlebihan.
Jangan memberikan rekomendasi beli atau jual saham.
"""
)
