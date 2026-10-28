def calculate_fundamental_score(data: dict) -> dict:
    """
    Menghitung Skor Kesehatan Fundamental (0 - 100) berdasarkan 4 Pilar
    dengan sistem Reward & Penalty serta adaptasi khusus sektor:
    1. Profitabilitas (Max 25)
    2. Valuasi (Max 25)
    3. Solvabilitas & Arus Kas / Ketahanan Modal (Max 25)
    4. Pertumbuhan & Dividen (Max 25)

    Fitur Unggulan:
    - Sector-Aware: Membedakan sektor Keuangan/Bank (di mana ROA 2-4% adalah kelas dunia dan DER tidak standar)
      dengan sektor Korporasi/Industri Umum.
    - Reward & Penalty: Metrik destruktif (rugi, ekuitas negatif, penurunan tajam) menerima penalti.
    - Kategori 5-tier yang objektif untuk memfilter saham berkualitas tinggi.
    """
    if "error" in data:
        return {
            "total_score": 0,
            "category": "Data Tidak Valid",
            "badge": "🔴",
            "pillars": {
                "Profitabilitas": 0,
                "Valuasi": 0,
                "Solvabilitas & Kas": 0,
                "Pertumbuhan & Dividen": 0
            },
            "details": ["Tidak ada data fundamental."]
        }

    details = []
    sector = (data.get("sector") or "").lower()
    industry = (data.get("industry") or "").lower()
    is_financial = "financial" in sector or "bank" in industry or "insurance" in industry

    # ==========================================
    # 1. PROFITABILITAS (Max 25)
    # ==========================================
    prof_score = 0

    roe = data.get("roe")
    if roe is not None:
        roe_pct = roe * 100
        if roe_pct >= 20:
            prof_score += 10
            details.append("✅ ROE >= 20% Excellent (+10)")
        elif roe_pct >= 15:
            prof_score += 10
            details.append("✅ ROE >= 15% Kuat (+10)")
        elif roe_pct >= 10:
            prof_score += 7
            details.append("✅ ROE >= 10% Sehat (+7)")
        elif roe_pct >= 5:
            prof_score += 4
            details.append("⚠️ ROE >= 5% Rendah (+4)")
        elif roe_pct >= 0:
            prof_score += 1
            details.append("⚠️ ROE 0-5% Minim (+1)")
        else:
            prof_score -= 5
            details.append("❌ ROE Negatif — modal terkikis (-5)")

    roa = data.get("roa")
    if roa is not None:
        roa_pct = roa * 100
        if is_financial:
            # Sektor Bank: ROA 2-4% adalah standar profitabilitas perbankan tier-1 dunia
            if roa_pct >= 3.0:
                prof_score += 6
                details.append("✅ ROA Bank >= 3.0% Sangat Prima (+6)")
            elif roa_pct >= 2.0:
                prof_score += 5
                details.append("✅ ROA Bank >= 2.0% Sangat Kuat (+5)")
            elif roa_pct >= 1.2:
                prof_score += 3
                details.append("✅ ROA Bank >= 1.2% Sehat (+3)")
            elif roa_pct >= 0:
                prof_score += 1
            else:
                prof_score -= 3
                details.append("❌ ROA Bank Negatif (-3)")
        else:
            # Sektor Non-Keuangan
            if roa_pct >= 8:
                prof_score += 5
                details.append("✅ ROA >= 8% (+5)")
            elif roa_pct >= 4:
                prof_score += 3
                details.append("✅ ROA >= 4% (+3)")
            elif roa_pct >= 0:
                prof_score += 0
            else:
                prof_score -= 3
                details.append("❌ ROA Negatif (-3)")

    npm = data.get("profit_margin")
    if npm is not None:
        npm_pct = npm * 100
        if npm_pct >= 20:
            prof_score += 10
            details.append("✅ Net Margin >= 20% Sangat Tebal (+10)")
        elif npm_pct >= 15:
            prof_score += 9
            details.append("✅ Net Margin >= 15% (+9)")
        elif npm_pct >= 8:
            prof_score += 6
            details.append("✅ Net Margin >= 8% Sehat (+6)")
        elif npm_pct >= 3:
            prof_score += 3
            details.append("⚠️ Net Margin >= 3% Tipis (+3)")
        elif npm_pct >= 0:
            prof_score += 0
        else:
            prof_score -= 5
            details.append("❌ Net Margin Negatif — rugi bersih (-5)")

    prof_score = max(min(prof_score, 25), 0)

    # ==========================================
    # 2. VALUASI (Max 25)
    # ==========================================
    val_score = 0

    pe = data.get("pe")
    if pe is not None:
        if pe < 0:
            val_score -= 8
            details.append("❌ PER Negatif — perusahaan rugi (-8)")
        elif pe <= 8:
            val_score += 12
            details.append("✅ PER <= 8x Sangat Murah (+12)")
        elif pe <= 12:
            val_score += 12
            details.append("✅ PER <= 12x Murah (+12)")
        elif pe <= 18:
            val_score += 8
            details.append("✅ PER <= 18x Wajar (+8)")
        elif pe <= 25:
            val_score += 4
            details.append("⚠️ PER <= 25x Moderat (+4)")
        elif pe <= 40:
            val_score += 1
            details.append("⚠️ PER <= 40x Premium (+1)")
        else:
            val_score -= 3
            details.append("❌ PER > 40x Sangat Mahal (-3)")

    pb = data.get("pb")
    if pb is not None:
        if pb < 0:
            val_score -= 5
            details.append("❌ PBV Negatif — ekuitas negatif (-5)")
        elif pb <= 0.8:
            val_score += 13
            details.append("✅ PBV <= 0.8x Deep Discount (+13)")
        elif pb <= 1.2:
            val_score += 13
            details.append("✅ PBV <= 1.2x Diskon (+13)")
        elif pb <= 2.2:
            val_score += 8
            details.append("✅ PBV <= 2.2x Wajar (+8)")
        elif pb <= 3.5:
            val_score += 4
            details.append("⚠️ PBV <= 3.5x Moderat (+4)")
        elif pb <= 5.0:
            val_score += 1
            details.append("⚠️ PBV <= 5.0x Premium (+1)")
        else:
            val_score -= 4
            details.append("❌ PBV > 5.0x Sangat Mahal (-4)")

    val_score = max(min(val_score, 25), 0)

    # ==========================================
    # 3. SOLVABILITAS & KETAHANAN KAS (Max 25)
    # ==========================================
    solv_score = 0

    if is_financial:
        # Penilaian khusus sektor Perbankan & Lembaga Keuangan:
        # Bank tidak dinilai dari DER/CR konvensional, melainkan dari profit buffer & konsistensi laba
        npm = data.get("profit_margin")
        if npm is not None and npm > 0:
            npm_pct = npm * 100
            if npm_pct >= 30:
                solv_score += 10
                details.append("✅ Bank Profit Buffer Sangat Tebal (NPM >= 30%) (+10)")
            elif npm_pct >= 20:
                solv_score += 7
                details.append("✅ Bank Profit Buffer Kuat (NPM >= 20%) (+7)")
            elif npm_pct >= 10:
                solv_score += 4
                details.append("✅ Bank Profit Buffer Wajar (+4)")

        # Kualitas profitabilitas jangka panjang (ROA + ROE)
        if roe is not None and roe >= 0.15:
            solv_score += 8
            details.append("✅ Bank Capital Compounding Sangat Solid (ROE >= 15%) (+8)")
        elif roe is not None and roe >= 0.10:
            solv_score += 5
            details.append("✅ Bank Capital Compounding Sehat (+5)")

        # Stabilitas Neraca dasar perbankan
        solv_score += 7
        details.append("✅ Struktur Permodalan Perbankan Terpantau (+7)")

    else:
        # Penilaian standar untuk korporasi industri / non-keuangan:
        der = data.get("debt_to_equity")
        if der is not None:
            if der <= 0.5:
                solv_score += 10
                details.append("✅ DER <= 0.5x Sangat Konservatif (+10)")
            elif der <= 0.8:
                solv_score += 10
                details.append("✅ DER <= 0.8x Sangat Sehat (+10)")
            elif der <= 1.5:
                solv_score += 6
                details.append("✅ DER <= 1.5x Terkendali (+6)")
            elif der <= 2.2:
                solv_score += 3
                details.append("⚠️ DER <= 2.2x Waspada (+3)")
            elif der <= 3.0:
                solv_score += 0
                details.append("⚠️ DER <= 3.0x Tinggi (+0)")
            else:
                solv_score -= 5
                details.append("❌ DER > 3.0x Sangat Tinggi (-5)")

        curr_ratio = data.get("current_ratio")
        if curr_ratio is not None:
            if curr_ratio >= 2.0:
                solv_score += 5
                details.append("✅ Current Ratio >= 2.0x Sangat Likuid (+5)")
            elif curr_ratio >= 1.5:
                solv_score += 5
                details.append("✅ Current Ratio >= 1.5x (+5)")
            elif curr_ratio >= 1.0:
                solv_score += 3
                details.append("✅ Current Ratio >= 1.0x (+3)")
            elif curr_ratio >= 0.7:
                solv_score += 0
                details.append("⚠️ Current Ratio < 1.0x Likuiditas Ketat (+0)")
            else:
                solv_score -= 3
                details.append("❌ Current Ratio < 0.7x Risiko Likuiditas (-3)")

        fcf = data.get("free_cashflow")
        ocf = data.get("operating_cashflow")
        if fcf is not None:
            if fcf > 0:
                solv_score += 10
                details.append("✅ Free Cash Flow Positif (+10)")
            else:
                market_cap = data.get("market_cap")
                if market_cap and market_cap > 0 and abs(fcf) > market_cap * 0.05:
                    solv_score -= 3
                    details.append("❌ FCF Negatif Signifikan (-3)")
                else:
                    solv_score -= 1
                    details.append("⚠️ Free Cash Flow Negatif (-1)")
        elif ocf is not None and ocf > 0:
            solv_score += 5
            details.append("✅ Operating Cash Flow Positif (+5)")

    solv_score = max(min(solv_score, 25), 0)

    # ==========================================
    # 4. PERTUMBUHAN & DIVIDEN (Max 25)
    # ==========================================
    growth_score = 0

    rev_g = data.get("revenue_growth")
    if rev_g is not None:
        rev_pct = rev_g * 100
        if rev_pct >= 20:
            growth_score += 8
            details.append("✅ Revenue Growth >= 20% Sangat Kuat (+8)")
        elif rev_pct >= 10:
            growth_score += 8
            details.append("✅ Revenue Growth >= 10% (+8)")
        elif rev_pct > 0:
            growth_score += 4
            details.append("✅ Revenue Growth Positif (+4)")
        elif rev_pct > -10:
            growth_score -= 2
            details.append("⚠️ Revenue Sedikit Menurun (-2)")
        else:
            growth_score -= 5
            details.append("❌ Revenue Menurun Tajam >= 10% (-5)")

    earn_g = data.get("earnings_growth")
    if earn_g is not None:
        earn_pct = earn_g * 100
        if earn_pct >= 20:
            growth_score += 8
            details.append("✅ Earnings Growth >= 20% Sangat Kuat (+8)")
        elif earn_pct >= 10:
            growth_score += 8
            details.append("✅ Earnings Growth >= 10% (+8)")
        elif earn_pct > 0:
            growth_score += 4
            details.append("✅ Earnings Growth Positif (+4)")
        elif earn_pct > -10:
            growth_score -= 2
            details.append("⚠️ Laba Sedikit Menurun (-2)")
        else:
            growth_score -= 5
            details.append("❌ Laba Menurun Tajam >= 10% (-5)")

    div_y = data.get("dividend_yield")
    if div_y is not None and div_y > 0:
        div_pct = div_y * 100
        if div_pct >= 6.0:
            growth_score += 9
            details.append("✅ Dividend Yield >= 6% Sangat Tinggi (+9)")
        elif div_pct >= 4.5:
            growth_score += 9
            details.append("✅ Dividend Yield >= 4.5% Tinggi (+9)")
        elif div_pct >= 2.0:
            growth_score += 5
            details.append("✅ Dividend Yield >= 2.0% (+5)")
        else:
            growth_score += 2
            details.append("✅ Membayar Dividen (+2)")

    growth_score = max(min(growth_score, 25), 0)

    # ==========================================
    # TOTAL SCORE & KATEGORI (5-Tier)
    # ==========================================
    total_score = prof_score + val_score + solv_score + growth_score

    if total_score >= 80:
        category = "Sangat Sehat (Strong Fundamental)"
        badge = "🟢"
    elif total_score >= 65:
        category = "Sehat (Good Fundamental)"
        badge = "🟡"
    elif total_score >= 50:
        category = "Cukup (Fair Fundamental)"
        badge = "🟧"
    elif total_score >= 35:
        category = "Lemah (Weak Fundamental)"
        badge = "🟠"
    else:
        category = "Sangat Lemah / Berisiko Tinggi"
        badge = "🔴"

    return {
        "total_score": total_score,
        "category": category,
        "badge": badge,
        "pillars": {
            "Profitabilitas": prof_score,
            "Valuasi": val_score,
            "Solvabilitas & Kas": solv_score,
            "Pertumbuhan & Dividen": growth_score
        },
        "details": details
    }
