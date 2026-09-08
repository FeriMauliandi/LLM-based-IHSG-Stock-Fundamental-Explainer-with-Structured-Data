def calculate_fundamental_score(data: dict) -> dict:
    """
    Menghitung Skor Kesehatan Fundamental (0 - 100) berdasarkan 4 Pilar:
    1. Profitabilitas (25)
    2. Valuasi (25)
    3. Solvabilitas & Arus Kas (25)
    4. Pertumbuhan & Dividen (25)
    """
    if "error" in data:
        return {
            "total_score": 0,
            "category": "Data Tidak Valid",
            "badge": "🔴",
            "pillars": {"Profitabilitas": 0, "Valuasi": 0, "Solvabilitas & Kas": 0, "Pertumbuhan & Dividen": 0},
            "details": ["Tidak ada data fundamental."]
        }

    details = []

    # 1. Profitabilitas (Max 25)
    prof_score = 0
    roe = data.get("roe")
    if roe is not None:
        roe_pct = roe * 100
        if roe_pct >= 15:
            prof_score += 10
            details.append("ROE >= 15% (+10)")
        elif roe_pct >= 10:
            prof_score += 7
            details.append("ROE >= 10% (+7)")
        elif roe_pct >= 5:
            prof_score += 4
            details.append("ROE >= 5% (+4)")

    roa = data.get("roa")
    if roa is not None:
        roa_pct = roa * 100
        if roa_pct >= 8:
            prof_score += 5
            details.append("ROA >= 8% (+5)")
        elif roa_pct >= 4:
            prof_score += 3
            details.append("ROA >= 4% (+3)")

    npm = data.get("profit_margin")
    if npm is not None:
        npm_pct = npm * 100
        if npm_pct >= 15:
            prof_score += 10
            details.append("Net Margin >= 15% (+10)")
        elif npm_pct >= 8:
            prof_score += 6
            details.append("Net Margin >= 8% (+6)")
        elif npm_pct >= 3:
            prof_score += 3
            details.append("Net Margin >= 3% (+3)")

    prof_score = min(prof_score, 25)

    # 2. Valuasi (Max 25)
    val_score = 0
    pe = data.get("pe")
    if pe is not None and pe > 0:
        if pe <= 12:
            val_score += 12
            details.append("PER <= 12x Murah (+12)")
        elif pe <= 18:
            val_score += 8
            details.append("PER <= 18x Wajar (+8)")
        elif pe <= 25:
            val_score += 4
            details.append("PER <= 25x Moderat (+4)")

    pb = data.get("pb")
    if pb is not None and pb > 0:
        if pb <= 1.2:
            val_score += 13
            details.append("PBV <= 1.2x Diskon (+13)")
        elif pb <= 2.2:
            val_score += 8
            details.append("PBV <= 2.2x Wajar (+8)")
        elif pb <= 3.5:
            val_score += 4
            details.append("PBV <= 3.5x Moderat (+4)")

    val_score = min(val_score, 25)

    # 3. Solvabilitas & Kas (Max 25)
    solv_score = 0
    der = data.get("debt_to_equity")
    if der is not None:
        if der <= 0.8:
            solv_score += 10
            details.append("DER <= 0.8x Sangat Sehat (+10)")
        elif der <= 1.5:
            solv_score += 6
            details.append("DER <= 1.5x Terkendali (+6)")
        elif der <= 2.2:
            solv_score += 3
            details.append("DER <= 2.2x Waspada (+3)")

    curr_ratio = data.get("current_ratio")
    if curr_ratio is not None:
        if curr_ratio >= 1.5:
            solv_score += 5
            details.append("Current Ratio >= 1.5x (+5)")
        elif curr_ratio >= 1.0:
            solv_score += 3
            details.append("Current Ratio >= 1.0x (+3)")

    fcf = data.get("free_cashflow")
    ocf = data.get("operating_cashflow")
    if fcf is not None and fcf > 0:
        solv_score += 10
        details.append("Free Cash Flow Positif (+10)")
    elif ocf is not None and ocf > 0:
        solv_score += 5
        details.append("Operating Cash Flow Positif (+5)")

    solv_score = min(solv_score, 25)

    # 4. Pertumbuhan & Dividen (Max 25)
    growth_score = 0
    rev_g = data.get("revenue_growth")
    if rev_g is not None:
        rev_pct = rev_g * 100
        if rev_pct >= 10:
            growth_score += 8
            details.append("Pertumbuhan Pendapatan >= 10% (+8)")
        elif rev_pct > 0:
            growth_score += 4
            details.append("Pertumbuhan Pendapatan Positif (+4)")

    earn_g = data.get("earnings_growth")
    if earn_g is not None:
        earn_pct = earn_g * 100
        if earn_pct >= 10:
            growth_score += 8
            details.append("Pertumbuhan Laba Bersih >= 10% (+8)")
        elif earn_pct > 0:
            growth_score += 4
            details.append("Pertumbuhan Laba Positif (+4)")

    div_y = data.get("dividend_yield")
    if div_y is not None and div_y > 0:
        div_pct = div_y * 100
        if div_pct >= 4.5:
            growth_score += 9
            details.append("Dividend Yield >= 4.5% Tinggi (+9)")
        elif div_pct >= 2.0:
            growth_score += 5
            details.append("Dividend Yield >= 2.0% (+5)")
        else:
            growth_score += 2
            details.append("Membayar Dividen (+2)")

    growth_score = min(growth_score, 25)

    total_score = prof_score + val_score + solv_score + growth_score

    if total_score >= 80:
        category = "Sangat Sehat (Strong Fundamental)"
        badge = "🟢"
    elif total_score >= 60:
        category = "Sehat (Good Fundamental)"
        badge = "🟡"
    elif total_score >= 40:
        category = "Moderat (Needs Attention)"
        badge = "🟧"
    else:
        category = "Lemah / Berisiko Tinggi"
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
