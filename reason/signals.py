def generate_fundamental_signals(data: dict) -> list[str]:
    """
    Menghasilkan sinyal fundamental kuantitatif berdasarkan data rasio keuangan.
    """
    if "error" in data:
        return [data["error"]]

    signals = []

    # 1. Analisis Valuasi (PBV)
    pbv = data.get("pb")
    if pbv is not None:
        if pbv < 1.0:
            signals.append(f"🟢 Undervalued (PBV {pbv:.2f}x < 1.0x): Harga pasar di bawah nilai buku bersih (diskon asset).")
        elif pbv <= 3.0:
            signals.append(f"🟡 PBV Wajar ({pbv:.2f}x): Valuasi berimbang dibanding nilai ekuitas.")
        else:
            signals.append(f"🔴 PBV Tinggi ({pbv:.2f}x > 3.0x): Valuasi premium, pastikan dibarengi ROE tinggi.")

    # 2. Analisis PER
    per = data.get("pe")
    if per is not None:
        if per < 0:
            signals.append("🔴 PER Negatif: Perusahaan dalam kondisi rugi bersih.")
        elif per <= 15:
            signals.append(f"🟢 PER Atraktif ({per:.2f}x <= 15x): Berada di area wajar/murah untuk saham berkembang.")
        elif per <= 25:
            signals.append(f"🟡 PER Moderat ({per:.2f}x): Diperdagangkan dengan ekspektasi pertumbuhan menengah.")
        else:
            signals.append(f"🔴 PER Tinggi ({per:.2f}x > 25x): Saham mahal atau pasar berekspektasi tinggi.")

    # 3. Analisis Profitabilitas (ROE & ROA & Net Margin)
    roe = data.get("roe")
    if roe is not None:
        roe_pct = roe * 100
        if roe_pct >= 15:
            signals.append(f"🟢 ROE Sangat Kuat ({roe_pct:.1f}% >= 15%): Efisiensi modal saham sangat tinggi.")
        elif roe_pct >= 8:
            signals.append(f"🟡 ROE Cukup Baik ({roe_pct:.1f}%): Tingkat pengembalian ekuitas memadai.")
        else:
            signals.append(f"🔴 ROE Rendah ({roe_pct:.1f}% < 8%): Penggunaan modal pemegang saham kurang efisien.")

    profit_margin = data.get("profit_margin")
    if profit_margin is not None:
        npm_pct = profit_margin * 100
        if npm_pct >= 10:
            signals.append(f"🟢 Net Profit Margin Sehat ({npm_pct:.1f}% >= 10%): Perusahaan memiliki keunggulan marjin.")
        elif npm_pct < 0:
            signals.append(f"🔴 Net Margin Negatif ({npm_pct:.1f}%): Operasional mengalami kerugian.")

    # 4. Solvabilitas & Utang (DER)
    der = data.get("debt_to_equity")
    if der is not None:
        if der <= 1.0:
            signals.append(f"🟢 Utang Aman (DER {der:.2f}x <= 1.0x): Risiko kebangkrutan/beban bunga sangat terukur.")
        elif der <= 2.0:
            signals.append(f"🟡 Utang Moderat (DER {der:.2f}x): Perlu pemantauan terhadap beban keuangan.")
        else:
            signals.append(f"🔴 Utang Tinggi (DER {der:.2f}x > 2.0x): Berisiko jika kondisi ekonomi melambat.")

    # 5. Arus Kas (Free Cash Flow)
    fcf = data.get("free_cashflow")
    if fcf is not None:
        if fcf > 0:
            signals.append("🟢 Free Cash Flow Positif: Perusahaan menghasilkan kas riil yang dapat digunakan untuk ekspansi/dividen.")
        else:
            signals.append("🔴 Free Cash Flow Negatif: Perusahaan membakar kas atau dalam fase investasi intensif.")

    # 6. Dividen Yield
    div_yield = data.get("dividend_yield")
    if div_yield is not None and div_yield > 0:
        div_pct = div_yield * 100
        if div_pct >= 4.0:
            signals.append(f"💰 Dividend Yield Menarik ({div_pct:.1f}% >= 4%): Memberikan imbal hasil pasif yang baik.")
        else:
            signals.append(f"ℹ️ Dividend Yield ({div_pct:.1f}%).")

    # 7. Volume Signal
    vol_signals = analyze_volume_trend(data)
    signals.extend(vol_signals)

    if not signals:
        return ["Data rasio keuangan belum cukup lengkap untuk membentuk sinyal."]

    return signals


def analyze_volume_trend(data: dict) -> list[str]:
    signals = []
    current_vol = data.get('latest_volume', 0)
    ma5_vol = data.get('ma5_volume', 0)
    
    if ma5_vol > 0 and current_vol > 0:
        ratio = current_vol / ma5_vol
        if ratio >= 2.0:
            signals.append(f"🔥 Lonjakan Volume Ekstrem ({ratio:.1f}x MA5): Volume loncat di atas 200% rata-rata 5 hari. Indikasi akumulasi/distribusi besar.")
        elif ratio > 1.2:
            signals.append("📊 Volume Meningkat di atas rata-rata 5 hari.")
        elif ratio < 0.6:
            signals.append("💤 Volume Kering: Transaksi sepi di bawah rata-rata MA5.")

    return signals
