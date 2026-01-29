from langchain_core.prompts import PromptTemplate

comparison_prompt = PromptTemplate.from_template("""
Anda adalah analis saham IHSG.

Berikut adalah beberapa saham beserta data fundamentalnya:

{stocks_data}

Tugas Anda:
- Bandingkan kesehatan fundamental saham-saham di atas
- Tentukan saham mana yang paling sehat secara fundamental
- Jelaskan alasan pemilihan Anda secara logis
- Gunakan bahasa Indonesia sederhana
- berikan rekomendasi beli atau jual
""")
