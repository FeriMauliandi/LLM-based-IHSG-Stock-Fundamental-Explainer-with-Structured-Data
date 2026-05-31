def generate_fundamental_signals(data):
    signals = []

    pbv = data.get("priceToBook")
    if pbv is not None:
        if pbv < 1:
            signals.append(f"Undervalued: PBV di bawah 1 ({pbv:.2f}). Harga pasar lebih rendah dari nilai buku.")
        elif pbv > 3:
            signals.append(f"Overvalued: PBV cukup tinggi ({pbv:.2f}). Evaluasi potensi overprice.")
    
    # Analisis PER
    per = data.get('trailingPE')
    if per is not None:
        if per < 15:
            signals.append(f"PER Sehat: {per:.2f} (di bawah batas ideal 15x).")
        else:
            signals.append(f"PER Tinggi: {per:.2f}. Perlu dicek apakah sebanding dengan growth emiten.")
            
    if not signals:
        return ["Tidak cukup data rasio keuangan untuk menghasilkan sinyal."]

    if data["roe"]:
        signals.append(
            "ROE menunjukkan seberapa efisien perusahaan menggunakan modal pemegang saham"
        )

    if data["free_cashflow"]:
        signals.append(
            "Free Cash Flow menunjukkan apakah perusahaan menghasilkan uang tunai nyata"
        )

    if data["debt_to_equity"]:
        signals.append(
            "Debt to Equity Ratio menunjukkan tingkat ketergantungan perusahaan pada utang"
        )

    return signals

def analyze_volume_trend(ma5_data):
    if "error" in ma5_data:
        return ma5_data["error"]
        
    signals = []
    current_vol = ma5_data['latest_volume']
    ma5_vol = ma5_data['ma5_volume']
    
    if current_vol > (ma5_vol * 2):
        signals.append("🔥 Lonjakan Volume Ekstrem: Volume hari ini melebihi 200% dari rata-rata MA5. Indikasi kuat adanya akumulasi/distribusi besar.")
    elif current_vol > ma5_vol:
        signals.append("Volume Meningkat: Transaksi berada di atas rata-rata 5 hari terakhir.")
    else:
        signals.append("Volume Kering: Transaksi di bawah rata-rata MA5, pasar sedang sepi peminat.")
        
    return signals