import yfinance as yf
import pandas as pd

def fetch_fundamental_data(ticker: str) -> dict:
    """
    Mengambil data fundamental dan historis dari Yahoo Finance untuk ticker tertentu (contoh: BBCA.JK).
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info if isinstance(stock.info, dict) else {}

        # Fallback historis
        hist = stock.history(period="10d")
        if hist.empty:
            # Tetap kembalikan error jika saham benar-benar tidak berdata
            return {"error": f"Data historis untuk {ticker} tidak ditemukan. Pastikan kode saham benar."}

        # 1. Daily Value & Volume
        hist['Value'] = hist['Close'] * hist['Volume']
        hist['MA5_Volume'] = hist['Volume'].rolling(window=5).mean()
        hist['MA5_Value'] = hist['Value'].rolling(window=5).mean()
        
        latest_data = hist.iloc[-1]
        
        # Determine price
        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or float(latest_data['Close'])

        # Normalize DE Ratio (yfinance sometimes returns DER as percentage like 120.5 for 1.205 or raw ratio)
        der_raw = info.get("debtToEquity")
        der = None
        if der_raw is not None:
            der = der_raw / 100.0 if der_raw > 10 else der_raw

        # Dividend yield normalized
        div_yield = info.get("dividendYield")
        if div_yield is not None and div_yield > 1:
            div_yield = div_yield / 100.0

        # ROE & ROA normalized
        roe = info.get("returnOnEquity")
        roa = info.get("returnOnAssets")
        net_margin = info.get("profitMargins")

        # Growth
        rev_growth = info.get("revenueGrowth")
        earn_growth = info.get("earningsGrowth")

        pb = info.get("priceToBook")

        # Volume & MA5 safety
        latest_vol = int(latest_data['Volume']) if pd.notna(latest_data['Volume']) else 0
        ma5_vol = int(latest_data['MA5_Volume']) if pd.notna(latest_data['MA5_Volume']) else latest_vol
        latest_val = float(latest_data['Value']) if pd.notna(latest_data['Value']) else 0.0
        ma5_val = float(latest_data['MA5_Value']) if pd.notna(latest_data['MA5_Value']) else latest_val

        return {
            "ticker": ticker,
            "company_name": info.get("shortName") or info.get("longName") or ticker,
            "sector": info.get("sector") or "N/A",
            "industry": info.get("industry") or "N/A",
            "price": price,
            "longbussines_summary": info.get("longBusinessSummary") or "Deskripsi bisnis tidak tersedia.",
            "market_cap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb": pb,
            "roe": roe,
            "roa": roa,
            "profit_margin": net_margin,
            "revenue_growth": rev_growth,
            "earnings_growth": earn_growth,
            "free_cashflow": info.get("freeCashflow"),
            "operating_cashflow": info.get("operatingCashflow"),
            "debt_to_equity": der,
            "current_ratio": info.get("currentRatio"),
            "dividend_yield": div_yield,
            "eps": info.get("trailingEps"),
            "book_value": info.get("bookValue"),
            "date": latest_data.name.strftime("%Y-%m-%d"),
            "latest_close": float(latest_data['Close']),
            "latest_volume": latest_vol,
            "ma5_volume": ma5_vol,
            "latest_value": latest_val,
            "ma5_value": ma5_val
        }

    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return {"error": f"Gagal mengambil data untuk {ticker}: {str(e)}"}
