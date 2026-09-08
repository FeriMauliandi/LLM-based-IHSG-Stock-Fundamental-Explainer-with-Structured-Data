from langchain_core.prompts import PromptTemplate

comparison_prompt = PromptTemplate.from_template("""
Anda adalah Analis Saham IHSG Senior.

Berikut adalah data perbandingan beberapa saham IHSG beserta skor fundamental, rasio keuangan, dan estimasi valuasinya:

{stocks_data}

Tugas Anda:
1. **Peringkat Kesehatan Fundamental:** Urutkan saham dari yang paling kuat hingga yang paling berisiko secara fundamental.
2. **Perbandingan Finansial:** Bandingkan profitabilitas (ROE/Margin), valuasi (PER/PBV), dan beban utang (DER).
3. **Pemenang / Saham Paling Menarik:** Tentukan saham mana yang paling sehat dan menawarkan risk-to-reward terbaik untuk investasi jangka panjang, disertai alasan objektif.
4. **Strategi Pemilihan:** Berikan panduan singkat kapan investor sebaiknya memilih masing-masing saham tersebut.

Gunakan bahasa Indonesia yang terstruktur, jelas, dan lugas.
""")
