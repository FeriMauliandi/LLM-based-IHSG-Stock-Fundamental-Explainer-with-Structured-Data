import streamlit as st
import pandas as pd
from datetime import datetime

from data.data_fetcher import fetch_fundamental_data
from data.screener import run_stock_screener, POPULAR_IHSG_STOCKS
from reason.signals import generate_fundamental_signals
from reason.scoring import calculate_fundamental_score
from reason.valuation import calculate_fair_value
from chains.analysis_chain import build_analysis_chain, build_comparison_chain

st.set_page_config(
    page_title="AI IHSG Stock Screener & Fundamental Analyzer",
    page_icon="📈",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-green { color: #1e7e34; font-weight: bold; }
    .badge-yellow { color: #d39e00; font-weight: bold; }
    .badge-red { color: #bd2130; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analisa & Screener Saham IHSG Berbasis AI")
st.caption("Aplikasi Pintar Analisis Fundamental Saham, Estimasi Harga Wajar (Fair Value), dan Screener Saham Undervalued.")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "BBCA"

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

# Sidebar Info & Settings
with st.sidebar:
    st.header("⚙️ Pengaturan & Panduan")
    st.markdown("""
    **Pilar Skor Fundamental (0-100):**
    - 🟢 **Profitabilitas (25 pt):** ROE, ROA, Net Margin
    - 🏷️ **Valuasi (25 pt):** PER, PBV, Diskon Harga
    - 🛡️ **Solvabilitas & Kas (25 pt):** DER, FCF, Current Ratio
    - 🚀 **Pertumbuhan & Dividen (25 pt):** Rev Growth, Div Yield
    """)
    st.divider()
    if st.button("🗑️ Hapus Riwayat Analisis"):
        st.session_state.history = []
        st.success("Riwayat dihapus!")
        st.rerun()

# Tabs Interface
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Screener Saham Undervalued",
    "📊 Analisis Detail & AI",
    "⚔️ Komparasi Saham",
    "🧮 Kalkulator Fair Value"
])

# ==========================================
# TAB 1: SCREENER SAHAM UNDEVALUED & SEHAT
# ==========================================
with tab1:
    st.subheader("🔍 Stock Screener IHSG (Saringan Saham Undervalued & Sehat)")
    st.markdown("Cari saham IHSG pilihan berdasarkan kriteria kesehatan fundamental dan tingkat diskon harga.")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        min_score = st.slider("Min. Skor Fundamental", 0, 100, 50, step=5)
    with col_f2:
        max_pe = st.number_input("Maks. PER (x)", value=20.0, step=1.0)
    with col_f3:
        min_roe = st.number_input("Min. ROE (%)", value=8.0, step=1.0)
    with col_f4:
        max_der = st.number_input("Maks. DER (Utang)", value=2.0, step=0.1)

    st.markdown("**Atau Pilih Preset Strategi:**")
    cp1, cp2, cp3 = st.columns(3)
    preset_clicked = None
    if cp1.button("💎 Saham Undervalued & Sehat (High MoS)"):
        min_score, max_pe, min_roe, max_der = 60, 15.0, 10.0, 1.2
        preset_clicked = "undervalued"
    if cp2.button("💰 Saham Dividen Royal"):
        min_score, max_pe, min_roe, max_der = 50, 25.0, 8.0, 2.0
        preset_clicked = "dividen"
    if cp3.button("🛡️ Saham Bluechip & Giant"):
        min_score, max_pe, min_roe, max_der = 65, 30.0, 12.0, 1.5
        preset_clicked = "bluechip"

    run_screen = st.button("🚀 Jalankan Screener Sekarang", type="primary")

    if run_screen or preset_clicked or "screener_data" not in st.session_state:
        with st.spinner("Sedang memindai dan menganalisis saham IHSG..."):
            screener_results = run_stock_screener(
                tickers=POPULAR_IHSG_STOCKS,
                min_score=min_score,
                max_pe=max_pe,
                min_roe=min_roe,
                max_der=max_der
            )
            st.session_state.screener_data = screener_results

    if "screener_data" in st.session_state and st.session_state.screener_data:
        df_screener = pd.DataFrame(st.session_state.screener_data)

        # Show Table
        display_cols = [
            "Badge", "Ticker", "Nama Perusahaan", "Sektor", "Harga",
            "Score", "Kategori", "PER (x)", "PBV (x)", "ROE (%)",
            "Net Margin (%)", "DER (x)", "Div Yield (%)", "Fair Value", "MoS (%)", "Valuasi"
        ]

        st.dataframe(
            df_screener[display_cols],
            column_config={
                "Score": st.column_config.ProgressColumn("Skor Fundamental", min_value=0, max_value=100, format="%d pt"),
                "Harga": st.column_config.NumberColumn("Harga (Rp)", format="Rp %d"),
                "Fair Value": st.column_config.NumberColumn("Harga Wajar", format="Rp %d"),
                "MoS (%)": st.column_config.NumberColumn("MoS (%)", format="%.1f%%"),
                "PER (x)": st.column_config.NumberColumn("PER", format="%.1fx"),
                "PBV (x)": st.column_config.NumberColumn("PBV", format="%.2fx"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.1f%%"),
                "Net Margin (%)": st.column_config.NumberColumn("Net Margin", format="%.1f%%"),
                "Div Yield (%)": st.column_config.NumberColumn("Div Yield", format="%.1f%%"),
            },
            hide_index=True,
            use_container_width=True
        )

        st.info("💡 **Tips:** Klik tombol di bawah untuk menganalisis salah satu saham secara detail menggunakan AI.")
        selected_from_screener = st.selectbox(
            "Pilih Saham dari Hasil Screener untuk Diberi Penjelasan AI:",
            options=[row["Ticker"] for row in st.session_state.screener_data]
        )
        if st.button("🔎 Menganalisis Saham Terpilih dengan AI"):
            st.session_state.selected_ticker = selected_from_screener
            st.success(f"Saham {selected_from_screener} dipilih. Buka Tab **Analisis Detail & AI**!")


# ==========================================
# TAB 2: ANALISIS DETAIL & AI
# ==========================================
with tab2:
    st.subheader("📊 Analisis Detail & Penjelasan AI")

    c_input, c_btn = st.columns([3, 1])
    with c_input:
        ticker_input = st.text_input(
            "Masukkan Kode Saham IHSG (misal: BBCA, BBRI, BBNI, TLKM, ADRO):",
            value=st.session_state.selected_ticker
        )
    with c_btn:
        st.write("") # spacing
        st.write("")
        analyze = st.button("⚡ Analisis Sekarang", type="primary")

    if analyze and ticker_input:
        ticker = normalize_ticker(ticker_input)
        st.session_state.selected_ticker = ticker_input.upper().replace(".JK", "")

        with st.spinner(f"Mengambil data keuangan & menganalisis {ticker}..."):
            data = fetch_fundamental_data(ticker)

            if "error" in data:
                st.error(data["error"])
            else:
                signals = generate_fundamental_signals(data)
                score_info = calculate_fundamental_score(data)
                val_info = calculate_fair_value(data)

                # Format metrics string for prompt
                metrics_summary = f"""
                - Nama Perusahaan: {data.get('company_name')}
                - Sektor / Industri: {data.get('sector')} / {data.get('industry')}
                - PER (Trailing): {data.get('pe')}x
                - PBV (Price to Book): {data.get('pb')}x
                - ROE (Return on Equity): {(data.get('roe') or 0)*100:.1f}%
                - ROA (Return on Assets): {(data.get('roa') or 0)*100:.1f}%
                - Net Margin: {(data.get('profit_margin') or 0)*100:.1f}%
                - DER (Debt to Equity): {data.get('debt_to_equity')}x
                - Current Ratio: {data.get('current_ratio')}x
                - Dividend Yield: {(data.get('dividend_yield') or 0)*100:.1f}%
                - Free Cash Flow: {data.get('free_cashflow')}
                - Market Cap: Rp {data.get('market_cap'):,}
                """

                signal_text = "\n".join(f"- {s}" for s in signals)

                # Run LLM Chain
                chain = load_chain()
                ai_explanation = chain.invoke({
                    "ticker": ticker,
                    "company_name": data.get("company_name"),
                    "price": data.get("price"),
                    "score": score_info["total_score"],
                    "category": score_info["category"],
                    "fair_value": val_info.get("fair_value", "N/A"),
                    "mos": val_info.get("margin_of_safety", "N/A"),
                    "metrics": metrics_summary,
                    "signals": signal_text
                })

                analysis_result = {
                    "ticker": ticker,
                    "company_name": data.get("company_name"),
                    "time": datetime.now().strftime("%d %b %Y %H:%M"),
                    "metrics": data,
                    "signals": signals,
                    "score_info": score_info,
                    "val_info": val_info,
                    "analysis": ai_explanation
                }

                # Update history
                st.session_state.history = [item for item in st.session_state.history if item["ticker"] != ticker]
                st.session_state.history.insert(0, analysis_result)
                st.session_state.history = st.session_state.history[:6]

    # Render Latest Selected Analysis
    if st.session_state.history:
        latest = st.session_state.history[0]
        m = latest["metrics"]
        s_info = latest["score_info"]
        v_info = latest["val_info"]

        st.divider()
        st.markdown(f"## {s_info['badge']} {latest['company_name']} ({latest['ticker']})")
        st.caption(f"Sektor: {m.get('sector')} | Dianalisis pada: {latest['time']}")

        # Key Metrics Grid
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Harga Terkini", f"Rp {m.get('price'):,}" if m.get("price") else "N/A")
        with m2:
            st.metric("Fundamental Score", f"{s_info['total_score']} / 100", delta=s_info['category'])
        with m3:
            fv = v_info.get('fair_value')
            st.metric("Harga Wajar (Fair Value)", f"Rp {fv:,.0f}" if fv else "N/A", delta=v_info.get('status'))
        with m4:
            mos = v_info.get('margin_of_safety')
            st.metric("Margin of Safety (MoS)", f"{mos:.1f}%" if mos is not None else "N/A")
        with m5:
            pe_val = m.get('pe')
            st.metric("PER / PBV", f"{pe_val:.1f}x / {m.get('pb'):.2f}x" if pe_val else "N/A")

        # Visual Breakdown 4 Pilar Fundamental
        st.subheader("📊 Breakdown 4 Pilar Fundamental")
        col_p1, col_p2 = st.columns([2, 1])

        with col_p1:
            df_pillars = pd.DataFrame(list(s_info["pillars"].items()), columns=["Pilar", "Skor (Maks 25)"])
            st.bar_chart(df_pillars.set_index("Pilar"))

        with col_p2:
            st.markdown("**Poin Positif & Catatan:**")
            for det in s_info["details"]:
                st.markdown(f"- {det}")

        # AI Explanation Output
        st.subheader("🤖 Penjelasan AI (Bahasa Sederhana)")
        st.markdown(latest["analysis"])

        # Signals Section
        st.subheader("🎯 Sinyal & Indikator Terdeteksi")
        for sig in latest["signals"]:
            st.markdown(f"- {sig}")

        with st.expander("📄 Data Fundamental Lengkap (Raw Data)"):
            st.json(latest["metrics"])


# ==========================================
# TAB 3: KOMPARASI SAHAM HEAD-TO-HEAD
# ==========================================
with tab3:
    st.subheader("⚔️ Komparasi Saham Head-to-Head")
    st.markdown("Bandingkan beberapa saham IHSG sekaligus untuk menentukan mana yang paling sehat dan atraktif secara fundamental.")

    if len(st.session_state.history) < 2:
        st.info("ℹ️ Lakukan analisis pada minimal 2 saham di Tab 2 atau jalankan Screener untuk mengisi riwayat perbandingan.")
    else:
        tickers_in_history = [item["ticker"] for item in st.session_state.history]
        selected_to_compare = st.multiselect(
            "Pilih Saham untuk Dibandingkan:",
            options=tickers_in_history,
            default=tickers_in_history[:3]
        )

        if selected_to_compare:
            comparison_items = [item for item in st.session_state.history if item["ticker"] in selected_to_compare]

            # Comparison Table
            comp_data = []
            for item in comparison_items:
                m = item["metrics"]
                s = item["score_info"]
                v = item["val_info"]
                comp_data.append({
                    "Ticker": item["ticker"].replace(".JK", ""),
                    "Nama": item["company_name"],
                    "Score": s["total_score"],
                    "Harga": m.get("price"),
                    "Fair Value": v.get("fair_value"),
                    "MoS (%)": v.get("margin_of_safety"),
                    "PER (x)": round(m.get("pe"), 2) if m.get("pe") else None,
                    "PBV (x)": round(m.get("pb"), 2) if m.get("pb") else None,
                    "ROE (%)": round(m.get("roe") * 100, 2) if m.get("roe") else None,
                    "Net Margin (%)": round(m.get("profit_margin") * 100, 2) if m.get("profit_margin") else None,
                    "DER (x)": round(m.get("debt_to_equity"), 2) if m.get("debt_to_equity") else None,
                    "Div Yield (%)": round(m.get("dividend_yield") * 100, 2) if m.get("dividend_yield") else None,
                })

            df_comp = pd.DataFrame(comp_data)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

            if st.button("🤖 Minta AI Bandingkan & Tentukan Pemenang", type="primary"):
                with st.spinner("AI sedang membandingkan kesehatan fundamental saham-saham ini..."):
                    comp_chain = load_comparison_chain()

                    stocks_str = ""
                    for item in comparison_items:
                        m = item["metrics"]
                        s = item["score_info"]
                        v = item["val_info"]
                        stocks_str += f"\n--- SAHAM: {item['ticker']} ({item['company_name']}) ---\n"
                        stocks_str += f"- Fundamental Score: {s['total_score']}/100 ({s['category']})\n"
                        stocks_str += f"- Harga Terkini: Rp {m.get('price')} | Fair Value: Rp {v.get('fair_value')} (MoS: {v.get('margin_of_safety')}%)\n"
                        stocks_str += f"- PER: {m.get('pe')}x | PBV: {m.get('pb')}x | ROE: {(m.get('roe') or 0)*100:.1f}%\n"
                        stocks_str += f"- Net Margin: {(m.get('profit_margin') or 0)*100:.1f}% | DER: {m.get('debt_to_equity')}x\n"

                    comp_result = comp_chain.invoke({"stocks_data": stocks_str})

                st.markdown("### 🏆 Hasil Perbandingan Fundamental oleh AI")
                st.markdown(comp_result)


# ==========================================
# TAB 4: KALKULATOR FAIR VALUE & MOS
# ==========================================
with tab4:
    st.subheader("🧮 Kalkulator Valuasi & Margin of Safety (MoS)")
    st.markdown("Hitung estimasi harga wajar saham menggunakan Metode **Graham Number**, **PER Target**, dan **PBV Target**.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        calc_price = st.number_input("Harga Pasar Terkini (Rp)", value=5000.0, step=100.0)
        calc_eps = st.number_input("Laba Per Saham / EPS (Rp)", value=400.0, step=10.0)
        calc_bvps = st.number_input("Nilai Buku Per Saham / BVPS (Rp)", value=3000.0, step=50.0)
    with col_v2:
        calc_target_pe = st.number_input("Target PER Acuan (x)", value=15.0, step=1.0)
        calc_target_pbv = st.number_input("Target PBV Acuan (x)", value=1.8, step=0.1)

    if st.button("🧮 Hitung Harga Wajar", type="primary"):
        mock_data = {
            "price": calc_price,
            "eps": calc_eps,
            "book_value": calc_bvps,
            "roe": (calc_eps / calc_bvps) if calc_bvps > 0 else 0.15
        }
        res_val = calculate_fair_value(mock_data)

        st.divider()
        r1, r2, r3 = st.columns(3)
        r1.metric("Harga Terkini", f"Rp {calc_price:,.0f}")
        r2.metric("Estimasi Fair Value", f"Rp {res_val['fair_value']:,.0f}", delta=res_val['status'])
        r3.metric("Margin of Safety (MoS)", f"{res_val['margin_of_safety']:.1f}%")

        st.markdown("### Rincian Model Valuasi:")
        for k, v in res_val.get("estimates", {}).items():
            st.write(f"- **{k}:** Rp {v:,.2f}")
