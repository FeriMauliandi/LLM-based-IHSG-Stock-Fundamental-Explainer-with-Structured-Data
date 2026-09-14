from functools import lru_cache
from pathlib import Path

import yfinance as yf
import pandas as pd

YFINANCE_CACHE_DIR = Path(__file__).resolve().parents[1] / ".yfinance_cache"
YFINANCE_CACHE_DIR.mkdir(exist_ok=True)
yf.set_tz_cache_location(str(YFINANCE_CACHE_DIR))

EQUITY_FIELDS = (
    "Stockholders Equity",
    "Total Stockholder Equity",
    "Common Stock Equity",
    "Total Equity Gross Minority Interest",
)
SHARES_FIELDS = (
    "Ordinary Shares Number",
    "Share Issued",
    "Common Stock Shares Outstanding",
)


def _normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()
    if "." not in ticker:
        ticker = f"{ticker}.JK"
    return ticker


def _to_float(value):
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _latest_statement_value(statement: pd.DataFrame, field_names: tuple[str, ...]):
    if statement is None or statement.empty:
        return None

    for field in field_names:
        if field in statement.index:
            values = statement.loc[field].dropna()
            if not values.empty:
                return _to_float(values.iloc[0])

    return None


def _calculate_book_value_per_share(stock, info: dict):
    try:
        balance_sheet = stock.balance_sheet
    except Exception:
        balance_sheet = pd.DataFrame()

    equity = _latest_statement_value(balance_sheet, EQUITY_FIELDS)
    shares = _latest_statement_value(balance_sheet, SHARES_FIELDS)
    if shares is None:
        shares = _to_float(info.get("sharesOutstanding"))

    if equity is None or shares is None or equity <= 0 or shares <= 0:
        return None

    return equity / shares


@lru_cache(maxsize=32)
def _get_currency_rate(from_currency: str, to_currency: str):
    if not from_currency or not to_currency or from_currency == to_currency:
        return 1.0

    try:
        fx_hist = yf.Ticker(f"{from_currency}{to_currency}=X").history(period="5d")
        if fx_hist is not None and not fx_hist.empty:
            closes = fx_hist["Close"].dropna()
            if not closes.empty and closes.iloc[-1] > 0:
                return float(closes.iloc[-1])
    except Exception:
        return None

    return None


def _convert_currency(value, from_currency: str, to_currency: str):
    value = _to_float(value)
    if value is None:
        return None, None

    rate = _get_currency_rate(from_currency, to_currency)
    if rate is None:
        return value, None

    return value * rate, rate


def fetch_fundamental_data(ticker: str) -> dict:
    """
    Mengambil data fundamental dan historis dari Yahoo Finance untuk ticker tertentu (contoh: BBCA.JK).
    """
    try:
        ticker = _normalize_ticker(ticker)
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

        yahoo_pb = info.get("priceToBook")
        yahoo_book_value = info.get("bookValue")
        calculated_book_value = _calculate_book_value_per_share(stock, info)
        price_currency = info.get("currency")
        financial_currency = info.get("financialCurrency") or price_currency
        raw_book_value = calculated_book_value or yahoo_book_value
        book_value, book_value_fx_rate = _convert_currency(raw_book_value, financial_currency, price_currency)

        calculated_pb = None
        if book_value and book_value > 0:
            calculated_pb = price / book_value

        pb = calculated_pb or yahoo_pb
        if calculated_pb:
            if calculated_book_value:
                pb_source = "calculated_from_balance_sheet"
            else:
                pb_source = "calculated_from_yfinance_book_value"
            if book_value_fx_rate and financial_currency != price_currency:
                pb_source = f"{pb_source}_converted_{financial_currency}_to_{price_currency}"
        else:
            pb_source = "yfinance_priceToBook"

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
            "pb_source": pb_source,
            "yfinance_pb": yahoo_pb,
            "currency": price_currency,
            "financial_currency": financial_currency,
            "book_value_fx_rate": book_value_fx_rate,
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
            "book_value": book_value,
            "yfinance_book_value": yahoo_book_value,
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
