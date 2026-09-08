import concurrent.futures
from data.data_fetcher import fetch_fundamental_data
from reason.scoring import calculate_fundamental_score
from reason.valuation import calculate_fair_value

# Daftar saham populer IHSG lintas sektor
POPULAR_IHSG_STOCKS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK",
    "TLKM.JK", "ASII.JK", "UNVR.JK", "ICBP.JK", "INDF.JK",
    "ADRO.JK", "PTBA.JK", "ITMG.JK", "PGAS.JK", "ANTM.JK",
    "KLBF.JK", "SMGR.JK", "MYOR.JK", "AMRT.JK", "MAPI.JK",
    "MEDC.JK", "AUTO.JK", "ACES.JK", "ISAT.JK", "GOTO.JK"
]

def fetch_single_stock_summary(ticker: str) -> dict | None:
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
        "PER (x)": round(data.get("pe"), 2) if data.get("pe") else None,
        "PBV (x)": round(data.get("pb"), 2) if data.get("pb") else None,
        "ROE (%)": round(roe_pct, 2) if roe_pct is not None else None,
        "Net Margin (%)": round(npm_pct, 2) if npm_pct is not None else None,
        "DER (x)": round(data.get("debt_to_equity"), 2) if data.get("debt_to_equity") is not None else None,
        "Div Yield (%)": round(div_pct, 2) if div_pct is not None else None,
        "Fair Value": val_info.get("fair_value"),
        "MoS (%)": val_info.get("margin_of_safety"),
        "Valuasi": val_info.get("status", "N/A"),
        "_raw_data": data,
        "_score_info": score_info,
        "_val_info": val_info
    }


def run_stock_screener(tickers: list[str] = None, min_score: int = 50, max_pe: float = 25.0, min_roe: float = 8.0, max_der: float = 2.0) -> list[dict]:
    """
    Melakukan screening saham IHSG secara paralel dan menyaring sesuai kriteria pengguna.
    """
    if not tickers:
        tickers = POPULAR_IHSG_STOCKS

    results = []

    # Menggunakan ThreadPoolExecutor untuk fetching paralel super cepat
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_stock_summary, t): t for t in tickers}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                # Filter kriteria
                pe_ok = (res["PER (x)"] is not None and res["PER (x)"] <= max_pe and res["PER (x)"] > 0) or (res["PER (x)"] is None)
                roe_ok = (res["ROE (%)"] is not None and res["ROE (%)"] >= min_roe) or (res["ROE (%)"] is None)
                der_ok = (res["DER (x)"] is not None and res["DER (x)"] <= max_der) or (res["DER (x)"] is None)
                score_ok = res["Score"] >= min_score

                if score_ok and pe_ok and roe_ok and der_ok:
                    results.append(res)

    # Urutkan berdasarkan Score tertinggi
    results.sort(key=lambda x: x["Score"], reverse=True)
    return results
