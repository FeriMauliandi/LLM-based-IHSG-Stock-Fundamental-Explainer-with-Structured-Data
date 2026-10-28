def generate_fundamental_signals(data: dict) -> list[str]:
    """
    Menghasilkan sinyal fundamental kuantitatif berdasarkan data rasio keuangan.
    Diperkaya dengan sinyal pertumbuhan, likuiditas, forward PE, dan konsistensi ROE-PBV.
    """
    if "error" in data:
        return [data["error"]]

    signals = []

    # 1. Analisis Valuasi (PBV)
    pbv = data.get("pb")
    if pbv is not None:
        if pbv < 0:
            signals.append(f"🔴 PBV Negatif ({pbv:.2f}x): Ekuitas negatif — perusahaan secara teknis tidak solven.")
        elif pbv < 0.7:
            signals.append(f"🟢 Deep Undervalued (PBV {pbv:.2f}x < 0.7x): Harga jauh di bawah nilai buku bersih.")
        elif pbv < 1.0:
            signals.append(f"🟢 Undervalued (PBV {pbv:.2f}x < 1.0x): Harga pasar di bawah nilai buku bersih.")
        elif pbv <= 2.0:
            signals.append(f"🟡 PBV Wajar ({pbv:.2f}x): Valuasi berimbang dibanding nilai ekuitas.")
        elif pbv <= 3.0:
            signals.append(f"🟡 PBV Agak Premium ({pbv:.2f}x): Pasar membayar premium, pastikan dibarengi ROE tinggi.")
        else:
            signals.append(f"🔴 PBV Tinggi ({pbv:.2f}x > 3.0x): Valuasi premium tinggi, risiko downside besar jika kinerja turun.")

    # 2. Analisis PER (Trailing)
    per = data.get("pe")
    if per is not None:
        if per < 0:
            signals.append("🔴 PER Negatif: Perusahaan dalam kondisi rugi bersih — tidak cocok untuk value investing.")
        elif per <= 8:
            signals.append(f"🟢 PER Sangat Murah ({per:.2f}x <= 8x): Valuasi sangat atraktif, periksa apakah ada alasan fundamental.")
        elif per <= 15:
            signals.append(f"🟢 PER Atraktif ({per:.2f}x <= 15x): Berada di area wajar/murah untuk saham berkembang.")
        elif per <= 25:
            signals.append(f"🟡 PER Moderat ({per:.2f}x): Diperdagangkan dengan ekspektasi pertumbuhan menengah.")
        elif per <= 40:
            signals.append(f"🟠 PER Agak Mahal ({per:.2f}x): Pasar sudah mengapresiasi pertumbuhan cukup tinggi.")
        else:
            signals.append(f"🔴 PER Sangat Tinggi ({per:.2f}x > 40x): Saham sangat mahal atau pasar berekspektasi berlebihan.")

    # 3. Forward PE vs Trailing PE (proyeksi laba)
    forward_pe = data.get("forward_pe")
    if forward_pe is not None and per is not None and per > 0 and forward_pe > 0:
        if forward_pe < per * 0.8:
            signals.append(f"🟢 Forward PE ({forward_pe:.1f}x) jauh lebih rendah dari Trailing PE ({per:.1f}x): Laba diproyeksikan naik signifikan.")
        elif forward_pe > per * 1.2:
            signals.append(f"🔴 Forward PE ({forward_pe:.1f}x) lebih tinggi dari Trailing PE ({per:.1f}x): Laba diproyeksikan menurun.")

    # 4. Analisis Profitabilitas (ROE & Net Margin)
    roe = data.get("roe")
    if roe is not None:
        roe_pct = roe * 100
        if roe_pct >= 20:
            signals.append(f"🟢 ROE Excellent ({roe_pct:.1f}% >= 20%): Pengembalian modal ekuitas sangat tinggi.")
        elif roe_pct >= 15:
            signals.append(f"🟢 ROE Sangat Kuat ({roe_pct:.1f}% >= 15%): Efisiensi modal saham sangat tinggi.")
        elif roe_pct >= 8:
            signals.append(f"🟡 ROE Cukup Baik ({roe_pct:.1f}%): Tingkat pengembalian ekuitas memadai.")
        elif roe_pct >= 0:
            signals.append(f"🟠 ROE Rendah ({roe_pct:.1f}% < 8%): Penggunaan modal pemegang saham kurang efisien.")
        else:
            signals.append(f"🔴 ROE Negatif ({roe_pct:.1f}%): Perusahaan merugi atas modal pemegang saham.")

    profit_margin = data.get("profit_margin")
    if profit_margin is not None:
        npm_pct = profit_margin * 100
        if npm_pct >= 20:
            signals.append(f"🟢 Net Margin Sangat Kuat ({npm_pct:.1f}% >= 20%): Perusahaan memiliki moat/keunggulan kompetitif tinggi.")
        elif npm_pct >= 10:
            signals.append(f"🟢 Net Profit Margin Sehat ({npm_pct:.1f}% >= 10%): Perusahaan memiliki keunggulan marjin.")
        elif npm_pct >= 3:
            signals.append(f"🟡 Net Margin Tipis ({npm_pct:.1f}%): Marjin keuntungan rendah, rentan terhadap kenaikan biaya.")
        elif npm_pct >= 0:
            signals.append(f"🟠 Net Margin Sangat Tipis ({npm_pct:.1f}%): Profitabilitas minim.")
        else:
            signals.append(f"🔴 Net Margin Negatif ({npm_pct:.1f}%): Operasional mengalami kerugian.")

    # 5. Solvabilitas & Utang (DER)
    der = data.get("debt_to_equity")
    if der is not None:
        if der <= 0.5:
            signals.append(f"🟢 Utang Sangat Rendah (DER {der:.2f}x <= 0.5x): Perusahaan sangat konservatif dalam penggunaan utang.")
        elif der <= 1.0:
            signals.append(f"🟢 Utang Aman (DER {der:.2f}x <= 1.0x): Risiko kebangkrutan sangat terukur.")
        elif der <= 2.0:
            signals.append(f"🟡 Utang Moderat (DER {der:.2f}x): Perlu pemantauan terhadap beban keuangan.")
        elif der <= 3.0:
            signals.append(f"🟠 Utang Cukup Tinggi (DER {der:.2f}x): Leverage mulai berisiko, terutama saat suku bunga naik.")
        else:
            signals.append(f"🔴 Utang Tinggi (DER {der:.2f}x > 3.0x): Berisiko tinggi jika kondisi ekonomi melambat.")

    # 6. Likuiditas (Current Ratio)
    curr_ratio = data.get("current_ratio")
    if curr_ratio is not None:
        if curr_ratio >= 2.0:
            signals.append(f"🟢 Likuiditas Sangat Baik (CR {curr_ratio:.2f}x >= 2.0x): Aset lancar berlimpah untuk menutupi kewajiban jangka pendek.")
        elif curr_ratio >= 1.5:
            signals.append(f"🟢 Likuiditas Baik (CR {curr_ratio:.2f}x >= 1.5x): Mampu menutupi kewajiban jangka pendek.")
        elif curr_ratio >= 1.0:
            signals.append(f"🟡 Likuiditas Cukup (CR {curr_ratio:.2f}x): Batas minimum kemampuan bayar jangka pendek.")
        else:
            signals.append(f"🔴 Likuiditas Rendah (CR {curr_ratio:.2f}x < 1.0x): Risiko gagal bayar kewajiban jangka pendek.")

    # 7. Arus Kas (Free Cash Flow) + FCF Yield
    fcf = data.get("free_cashflow")
    if fcf is not None:
        if fcf > 0:
            market_cap = data.get("market_cap")
            if market_cap and market_cap > 0:
                fcf_yield = (fcf / market_cap) * 100
                if fcf_yield >= 8:
                    signals.append(f"🟢 FCF Yield Sangat Tinggi ({fcf_yield:.1f}%): Kas yang dihasilkan sangat besar relatif terhadap valuasi.")
                elif fcf_yield >= 4:
                    signals.append(f"🟢 FCF Yield Baik ({fcf_yield:.1f}%): Arus kas riil yang sehat.")
                else:
                    signals.append("🟢 Free Cash Flow Positif: Perusahaan menghasilkan kas riil.")
            else:
                signals.append("🟢 Free Cash Flow Positif: Perusahaan menghasilkan kas riil untuk ekspansi/dividen.")
        else:
            signals.append("🔴 Free Cash Flow Negatif: Perusahaan membakar kas atau dalam fase investasi intensif.")

    # 8. Dividen Yield
    div_yield = data.get("dividend_yield")
    if div_yield is not None and div_yield > 0:
        div_pct = div_yield * 100
        if div_pct >= 6.0:
            signals.append(f"💰 Dividend Yield Sangat Tinggi ({div_pct:.1f}% >= 6%): Imbal hasil pasif excellent, periksa sustainability.")
        elif div_pct >= 4.0:
            signals.append(f"💰 Dividend Yield Menarik ({div_pct:.1f}% >= 4%): Memberikan imbal hasil pasif yang baik.")
        elif div_pct >= 2.0:
            signals.append(f"ℹ️ Dividend Yield Moderat ({div_pct:.1f}%): Dividen tersedia tapi bukan fokus utama.")
        else:
            signals.append(f"ℹ️ Dividend Yield Rendah ({div_pct:.1f}%).")

    # 9. Pertumbuhan Revenue
    rev_growth = data.get("revenue_growth")
    if rev_growth is not None:
        rev_pct = rev_growth * 100
        if rev_pct >= 20:
            signals.append(f"🚀 Revenue Growth Sangat Kuat ({rev_pct:.1f}% >= 20%): Bisnis dalam fase ekspansi agresif.")
        elif rev_pct >= 10:
            signals.append(f"🟢 Revenue Growth Solid ({rev_pct:.1f}% >= 10%): Tren bisnis positif.")
        elif rev_pct > 0:
            signals.append(f"🟡 Revenue Growth Moderat ({rev_pct:.1f}%): Bisnis tumbuh namun lambat.")
        elif rev_pct > -10:
            signals.append(f"🟠 Revenue Sedikit Menurun ({rev_pct:.1f}%): Waspada terhadap tren perlambatan.")
        else:
            signals.append(f"🔴 Revenue Menurun Tajam ({rev_pct:.1f}%): Bisnis mengalami kontraksi signifikan.")

    # 10. Pertumbuhan Earnings
    earn_growth = data.get("earnings_growth")
    if earn_growth is not None:
        earn_pct = earn_growth * 100
        if earn_pct >= 20:
            signals.append(f"🚀 Earnings Growth Sangat Kuat ({earn_pct:.1f}% >= 20%): Profitabilitas meningkat signifikan.")
        elif earn_pct >= 10:
            signals.append(f"🟢 Earnings Growth Solid ({earn_pct:.1f}% >= 10%): Laba bersih meningkat sehat.")
        elif earn_pct > 0:
            signals.append(f"🟡 Earnings Growth Moderat ({earn_pct:.1f}%): Laba naik tapi tidak agresif.")
        elif earn_pct > -10:
            signals.append(f"🟠 Laba Sedikit Menurun ({earn_pct:.1f}%): Waspada terhadap erosi profitabilitas.")
        else:
            signals.append(f"🔴 Laba Menurun Tajam ({earn_pct:.1f}%): Profitabilitas terganggu serius.")

    # 11. Volume Signal
    vol_signals = analyze_volume_trend(data)
    signals.extend(vol_signals)

    # 12. ROE vs PBV Consistency Check
    #     Jika PBV tinggi tapi ROE rendah, itu red flag
    if roe is not None and pbv is not None and roe > 0 and pbv > 0:
        roe_pct = roe * 100
        expected_pbv_max = roe_pct / 5  # ROE 15% → PBV max ~3x reasonable
        if pbv > expected_pbv_max and roe_pct < 15:
            signals.append(f"⚠️ PBV ({pbv:.2f}x) terlalu tinggi untuk ROE ({roe_pct:.1f}%): Valuasi tidak didukung oleh profitabilitas.")

    if not signals:
        return ["Data rasio keuangan belum cukup lengkap untuk membentuk sinyal."]

    return signals


def analyze_volume_trend(data: dict) -> list[str]:
    """Menganalisis tren volume perdagangan terhadap rata-rata MA5."""
    signals = []
    current_vol = data.get('latest_volume', 0)
    ma5_vol = data.get('ma5_volume', 0)

    if ma5_vol > 0 and current_vol > 0:
        ratio = current_vol / ma5_vol
        if ratio >= 3.0:
            signals.append(f"🔥 Lonjakan Volume Sangat Ekstrem ({ratio:.1f}x MA5): Kemungkinan ada aksi korporasi atau berita besar.")
        elif ratio >= 2.0:
            signals.append(f"🔥 Lonjakan Volume Ekstrem ({ratio:.1f}x MA5): Indikasi akumulasi/distribusi besar.")
        elif ratio > 1.3:
            signals.append(f"📊 Volume Meningkat ({ratio:.1f}x MA5): Minat pasar meningkat di atas rata-rata 5 hari.")
        elif ratio < 0.5:
            signals.append("💤 Volume Sangat Kering: Transaksi sangat sepi, likuiditas rendah — hati-hati saat jual.")
        elif ratio < 0.7:
            signals.append("💤 Volume Kering: Transaksi sepi di bawah rata-rata MA5.")

    return signals
