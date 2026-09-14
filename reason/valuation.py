import math

def calculate_fair_value(data: dict) -> dict:
    """
    Menghitung estimasi Harga Wajar (Fair Value) dan Margin of Safety (MoS %)
    menggunakan metode Graham Number, Standard PE Model, dan ROE-based PBV Model.
    """
    if "error" in data:
        return {"error": data["error"]}

    price = data.get("price") or data.get("latest_close")
    eps = data.get("eps")
    bvps = data.get("book_value")
    roe = data.get("roe")
    target_pe = data.get("target_pe", 15.0)
    target_pbv = data.get("target_pbv")

    if not price or price <= 0:
        return {"error": "Harga saham tidak valid."}

    estimates = {}

    # 1. Graham Number Model
    if eps and bvps and eps > 0 and bvps > 0:
        graham_val = math.sqrt(22.5 * eps * bvps)
        estimates["Graham Number"] = round(graham_val, 2)

    # 2. Fair PE Model (Berdasarkan PER Acuan 15.0x atau disesuaikan)
    if eps and eps > 0:
        pe_val = eps * target_pe
        estimates[f"PE Benchmark ({target_pe:g}x)"] = round(pe_val, 2)

    # 3. Fair PBV Model (Berdasarkan input target PBV atau ROE, contoh ROE 15% -> Target PBV 1.5x, min 1.0x)
    if bvps and bvps > 0 and (target_pbv or (roe and roe > 0)):
        effective_target_pbv = target_pbv if target_pbv else max(1.0, roe * 10)
        pbv_val = bvps * effective_target_pbv
        estimates["PBV Model (ROE-adjusted)"] = round(pbv_val, 2)

    if not estimates:
        return {
            "status": "Data EPS / Book Value tidak lengkap untuk estimasi harga wajar.",
            "price": price,
            "fair_value": None,
            "margin_of_safety": None,
            "estimates": {}
        }

    # Hitung Rata-rata Fair Value
    avg_fair_value = sum(estimates.values()) / len(estimates)
    mos_pct = ((avg_fair_value - price) / avg_fair_value) * 100

    valuation_status = "Undervalued (Diskon)" if mos_pct > 10 else ("Fairly Valued (Wajar)" if mos_pct >= -10 else "Overvalued (Mahal)")

    return {
        "status": valuation_status,
        "price": price,
        "fair_value": round(avg_fair_value, 2),
        "margin_of_safety": round(mos_pct, 2),
        "estimates": estimates
    }
