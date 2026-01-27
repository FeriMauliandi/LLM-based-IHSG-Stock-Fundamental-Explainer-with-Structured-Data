import streamlit as st

from data.data_fetcher import fetch_fundamental_data
from reason.signals import generate_fundamental_signals
from chains.analysis_chain import build_analysis_chain

st.set_page_config(
    page_title="AI Fundamental Stock Analyzer",
    layout="centered"
)

st.title("Analisa Fundamental Saham berbasis AI")
st.caption("Sc: yFinance (Yahoo Finance)")

ticker = st.text_input(
    "Masukkan kode saham (contoh: LPKR.JK) JK = saham IHSG",
    value="BBCA.JK"
)

analyze = st.button("Analisis")

@st.cache_resource
def load_chain():
    return build_analysis_chain()

if analyze and ticker:
    with st.spinner("Fetch data & analisa fundamental..."):
        data = fetch_fundamental_data(ticker)
        signals = generate_fundamental_signals(data)
        chain = load_chain()

        metrics_text = "\n".join(
            f"- {k}: {v}" for k, v in data.items() if k != "ticker"
        )

        signal_text = "\n".join(
            f"- {s}" for s in signals
        )

        result = chain.invoke({
            "ticker": ticker,
            "metrics": metrics_text,
            "signals": signal_text
        })

    st.subheader("Penjelasan Fundamental Saham")
    st.write(result)

    with st.expander("Data Fundamental (Mentah)"):
        st.json(data)

    with st.expander("Keterangan Indikator"):
        st.write(signal_text)
