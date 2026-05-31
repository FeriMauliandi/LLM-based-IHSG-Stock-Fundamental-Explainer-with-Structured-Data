import yfinance as yf

def fetch_fundamental_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        hist = stock.history(period="10d")
        
        if hist.empty:
            return {"error": f"Data historis {ticker} tidak ditemukan."}
            
        # 1. Estimasi Daily Value (Nilai Transaksi = Harga Close * Volume)
        hist['Value'] = hist['Close'] * hist['Volume']
        
        # 2. Hitung MA5 untuk Volume dan Value menggunakan pandas .rolling()
        hist['MA5_Volume'] = hist['Volume'].rolling(window=5).mean()
        hist['MA5_Value'] = hist['Value'].rolling(window=5).mean()
        
        latest_data = hist.iloc[-1]

        return {
            "ticker": ticker,
            "price": info.get("currentPrice"),
            "longbussines_summary": info.get("longBusinessSummary"),
            "market_cap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "pb": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "revenue_growth": info.get("revenueGrowth"),
            "free_cashflow": info.get("freeCashflow"),
            "debt_to_equity": info.get("debtToEquity"),
            "valuation": info.get("valuation"),
            "date": latest_data.name.strftime("%Y-%m-%d"),
            "latest_close": latest_data['Close'],
            "latest_volume": int(latest_data['Volume']),
            "ma5_volume": int(latest_data['MA5_Volume']),
            "latest_value": float(latest_data['Value']),
            "ma5_value": float(latest_data['MA5_Value'])
    }


    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return None


