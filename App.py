import streamlit as st
from datetime import datetime

from data.data_fetcher import fetch_fundamental_data
from reason.signals import generate_fundamental_signals
from chains.analysis_chain import build_analysis_chain
from chains.comparison_chain import build_comparison_chain


st.set_page_config(
    page_title="AI Fundamental Stock Analyzer",
    layout="centered"
)

st.title("Analisa Fundamental Saham IHSG Berbasis AI")
st.caption("Sumber data: Yahoo Finance (yFinance)")

if "history" not in st.session_state:
    st.session_state.history = []

ticker_input = st.text_input(
    "Masukkan kode saham IHSG (BUMI, GOTO, DADA)",
    value="DADA"
)

analyze = st.button("Analisis")


def normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()
    if not ticker.endswith(".JK"):
        ticker = f"{ticker}.JK"
    return ticker


@st.cache_resource
def load_chain():
    return build_analysis_chain()

@st.cache_resource
def load_comparison_chain():
    return build_comparison_chain()


if analyze and ticker_input:
    ticker = normalize_ticker(ticker_input)

    with st.spinner("Mengambil data & menganalisis fundamental..."):
        data = fetch_fundamental_data(ticker)
        signals = generate_fundamental_signals(data)
        chain = load_chain()

        metrics_text = "\n".join(
            f"- {k}: {v}" for k, v in data.items() if k != "ticker"
        )

        signal_text = "\n".join(
            f"- {s}" for s in signals
        )

        price = data.get("price")


        result = chain.invoke({
            "ticker": ticker,
            "price": price,
            "metrics": metrics_text,
            "signals": signal_text
        })

    analysis_result = {
        "ticker": ticker,
        "time": datetime.now().strftime("%d %b %Y %H:%M"),
        "metrics": data,
        "signals": signals,
        "analysis": result
    }

    st.session_state.history.insert(0, analysis_result)
    st.session_state.history = st.session_state.history[:4]


if st.session_state.history:
    latest = st.session_state.history[0]

    st.subheader(f"Penjelasan Fundamental Saham ({latest['ticker']})")
    st.caption(f"Dianalisis pada {latest['time']}")
    st.write(latest["analysis"])



        
if len(st.session_state.history) > 1:
    st.subheader("Riwayat Analisis (Maks. 4 Saham Terakhir)")

    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"{idx+1}. {item['ticker']} — {item['time']}"):
            st.markdown("### Ringkasan AI")
            st.write(item["analysis"])

if st.session_state.history:
    if st.button("🗑️ Hapus Semua Riwayat Analisis"):
        st.session_state.history = []
        st.success("Riwayat analisis berhasil dihapus.")
        st.rerun()

if len(st.session_state.history) > 1:
    st.subheader("Analisa Perbandingan Fundamental (AI)")

    if st.button("Tentukan Saham Paling Sehat"):
        with st.spinner("AI sedang membandingkan fundamental..."):
            comparison_chain = load_comparison_chain()

            combined_data = ""
            for item in st.session_state.history:
                combined_data += f"\nSaham: {item['ticker']}\n"
                combined_data += "Data Fundamental:\n"
                for k, v in item["metrics"].items():
                    combined_data += f"- {k}: {v}\n"

            comparison_result = comparison_chain.invoke({
                "stocks_data": combined_data
            })

        st.markdown("### Hasil Perbandingan Fundamental")
        st.write(comparison_result)
