import math


def calculate_fair_value(data: dict) -> dict:
    """
    Menghitung estimasi Harga Wajar (Fair Value) dan Margin of Safety (MoS %)
    menggunakan metode:
    1. Graham Number
    2. PE Benchmark Model
    3. ROE-adjusted PBV Model
    4. Earnings Power Value (EPV)

    Fair value akhir menggunakan weighted blend (60% weighted avg + 40% median)
    untuk mengurangi dampak outlier dan menghasilkan estimasi yang lebih robust.
    """
    if "error" in data:
        return {"error": data["error"]}

    price = data.get("price") or data.get("latest_close")
    eps = data.get("eps")
    bvps = data.get("book_value")
    roe = data.get("roe")
    target_pe = data.get("target_pe", 15.0)
    target_pbv = data.get("target_pbv")
    profit_margin = data.get("profit_margin")

    if not price or price <= 0:
        return {"error": "Harga saham tidak valid."}

    estimates = {}
    weights = {}

    # 1. Graham Number Model
    #    Formula klasik Benjamin Graham: sqrt(22.5 * EPS * BVPS)
    if eps and bvps and eps > 0 and bvps > 0:
        graham_val = math.sqrt(22.5 * eps * bvps)
        estimates["Graham Number"] = round(graham_val, 2)
        weights["Graham Number"] = 1.0

    # 2. Fair PE Model (PER Benchmark)
    #    Sederhana namun efektif: EPS * target PE ratio
    if eps and eps > 0:
        pe_val = eps * target_pe
        key = f"PE Benchmark ({target_pe:g}x)"
        estimates[key] = round(pe_val, 2)
        weights[key] = 1.5  # Higher weight — most transparent & widely used

    # 3. Fair PBV Model (ROE-adjusted)
    #    Target PBV disesuaikan berdasarkan ROE perusahaan
    #    ROE 15% → PBV ~1.5x, ROE 25% → PBV ~2.5x, clamped [0.8, 4.0]
    if bvps and bvps > 0 and (target_pbv or (roe and roe > 0)):
        if target_pbv:
            effective_target_pbv = target_pbv
        else:
            roe_pct = roe * 100
            effective_target_pbv = max(0.8, min(roe_pct / 10.0, 4.0))
        pbv_val = bvps * effective_target_pbv
        estimates["PBV Model (ROE-adjusted)"] = round(pbv_val, 2)
        weights["PBV Model (ROE-adjusted)"] = 1.0

    # 4. Earnings Power Value (EPV)
    #    Present value of sustainable earnings: EPS / Cost of Equity
    #    Disesuaikan dengan risk premium pasar Indonesia
    if eps and eps > 0:
        cost_of_equity = 0.10  # 10% default cost of equity untuk ekuitas Indonesia
        # Adjust berdasarkan profitabilitas
        if profit_margin and profit_margin > 0.15:
            cost_of_equity = 0.09  # Lower risk untuk high-margin companies
        elif profit_margin and profit_margin < 0.05:
            cost_of_equity = 0.12  # Higher risk untuk low-margin companies

        epv = eps / cost_of_equity
        # Apply conservative discount (80%) untuk emerging market risk
        epv_conservative = epv * 0.80
        estimates["Earnings Power Value (EPV)"] = round(epv_conservative, 2)
        weights["Earnings Power Value (EPV)"] = 1.2

    if not estimates:
        return {
            "status": "Data EPS / Book Value tidak lengkap untuk estimasi harga wajar.",
            "price": price,
            "fair_value": None,
            "margin_of_safety": None,
            "estimates": {}
        }

    # Calculate weighted average fair value
    total_weight = sum(weights.get(k, 1.0) for k in estimates)
    weighted_sum = sum(v * weights.get(k, 1.0) for k, v in estimates.items())
    avg_fair_value = weighted_sum / total_weight

    # Calculate median for robustness against outliers
    sorted_estimates = sorted(estimates.values())
    n = len(sorted_estimates)
    if n % 2 == 0:
        median_fair_value = (sorted_estimates[n // 2 - 1] + sorted_estimates[n // 2]) / 2
    else:
        median_fair_value = sorted_estimates[n // 2]

    # Final fair value: blend weighted average (60%) and median (40%)
    # Ini mengurangi dampak outlier sambil tetap menghargai bobot model
    final_fair_value = avg_fair_value * 0.6 + median_fair_value * 0.4

    mos_pct = ((final_fair_value - price) / final_fair_value) * 100

    if mos_pct > 20:
        valuation_status = "🟢 Undervalued (Diskon Besar)"
    elif mos_pct > 10:
        valuation_status = "🟢 Undervalued (Diskon)"
    elif mos_pct >= -10:
        valuation_status = "🟡 Fairly Valued (Wajar)"
    elif mos_pct >= -25:
        valuation_status = "🔴 Overvalued (Mahal)"
    else:
        valuation_status = "🔴 Overvalued (Sangat Mahal)"

    return {
        "status": valuation_status,
        "price": price,
        "fair_value": round(final_fair_value, 2),
        "margin_of_safety": round(mos_pct, 2),
        "weighted_avg": round(avg_fair_value, 2),
        "median": round(median_fair_value, 2),
        "estimates": estimates
    }
