import concurrent.futures
from data.data_fetcher import fetch_fundamental_data
from reason.scoring import calculate_fundamental_score
from reason.valuation import calculate_fair_value

# Daftar saham populer IHSG lintas sektor (dikurasi, tanpa saham spekulatif)
POPULAR_IHSG_STOCKS = [
    # Perbankan
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", "BTPS.JK",
    # Telekomunikasi & Teknologi
    "TLKM.JK", "ISAT.JK", "GOTO.JK",
    # Otomotif & Industri
    "ASII.JK", "AUTO.JK",
    # Consumer Goods & Makanan
    "UNVR.JK", "ICBP.JK", "INDF.JK", "MYOR.JK", "KLBF.JK",
    # Retail
    "AMRT.JK", "MAPI.JK", "ACES.JK",
    # Pertambangan & Energi
    "ADRO.JK", "PTBA.JK", "ITMG.JK", "ANTM.JK", "MEDC.JK", "PGAS.JK",
    # Semen & Konstruksi
    "SMGR.JK",
    # Properti
    "CTRA.JK", "BSDE.JK",
    # Farmasi & Lainnya
    "SIDO.JK", "ERAA.JK"
]

def fetch_single_stock_summary(ticker: str) -> dict | None:
    """Mengambil dan merangkum data fundamental satu saham."""
    try:
        data = fetch_fundamental_data(ticker)
        if not data or "error" in data:
            return None

        score_info = calculate_fundamental_score(data)
        val_info = calculate_fair_value(data)

        roe_pct = (data.get("roe") * 100) if data.get("roe") is not None else None
        npm_pct = (data.get("profit_margin") * 100) if data.get("profit_margin") is not None else None
        div_pct = (data.get("dividend_yield") * 100) if data.get("dividend_yield") is not None else None

        return {
            "Ticker": data["ticker"].replace(".JK", ""),
            "Nama Perusahaan": data.get("company_name", ticker),
            "Sektor": data.get("sector", "N/A"),
            "Harga": data.get("price"),
            "Score": score_info["total_score"],
            "Kategori": score_info["category"],
            "Badge": score_info["badge"],
            "PER (x)": round(data["pe"], 2) if data.get("pe") is not None else None,
            "PBV (x)": round(data["pb"], 2) if data.get("pb") is not None else None,
            "ROE (%)": round(roe_pct, 2) if roe_pct is not None else None,
            "Net Margin (%)": round(npm_pct, 2) if npm_pct is not None else None,
            "DER (x)": round(data["debt_to_equity"], 2) if data.get("debt_to_equity") is not None else None,
            "Div Yield (%)": round(div_pct, 2) if div_pct is not None else None,
            "Fair Value": val_info.get("fair_value"),
            "MoS (%)": val_info.get("margin_of_safety"),
            "Valuasi": val_info.get("status", "N/A"),
            "_raw_data": data,
            "_score_info": score_info,
            "_val_info": val_info
        }
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None


def run_stock_screener(
    tickers: list[str] = None,
    min_score: int = 50,
    max_pe: float = 25.0,
    min_roe: float = 8.0,
    max_der: float = 2.0
) -> list[dict]:
    """
    Melakukan screening saham IHSG secara paralel dan menyaring sesuai kriteria pengguna.

    PERBAIKAN: Saham dengan data None pada metrik kunci (PER, ROE) sekarang
    di-reject — bukan lolos default. Ini memastikan hanya saham dengan data
    lengkap dan berkualitas yang muncul di hasil screener.
    """
    if not tickers:
        tickers = POPULAR_IHSG_STOCKS

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_stock_summary, t): t for t in tickers}
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result()
            except Exception:
                continue

            if res is None:
                continue

            # ==========================================
            # FILTER KETAT — Saham harus punya data lengkap
            # ==========================================
            # PER harus tersedia, positif, dan di bawah threshold
            pe_val = res["PER (x)"]
            if pe_val is None or pe_val <= 0 or pe_val > max_pe:
                pe_ok = False
            else:
                pe_ok = True

            # ROE harus tersedia dan di atas threshold
            roe_val = res["ROE (%)"]
            if roe_val is None or roe_val < min_roe:
                roe_ok = False
            else:
                roe_ok = True

            # DER: jika tersedia harus di bawah threshold, None tetap lolos
            # (beberapa industri tidak melaporkan DER secara standar via yfinance)
            der_val = res["DER (x)"]
            if der_val is not None and der_val > max_der:
                der_ok = False
            else:
                der_ok = True

            # Skor fundamental harus di atas minimum
            score_ok = res["Score"] >= min_score

            if score_ok and pe_ok and roe_ok and der_ok:
                results.append(res)

    # Urutkan: Score tertinggi, lalu MoS tertinggi sebagai tiebreaker
    results.sort(key=lambda x: (x["Score"], x.get("MoS (%)", 0) or 0), reverse=True)
    return results
