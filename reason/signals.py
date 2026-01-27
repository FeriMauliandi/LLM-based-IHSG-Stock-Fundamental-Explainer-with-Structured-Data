def generate_fundamental_signals(data):
    signals = []

    if data["pe"]:
        signals.append(
            f"PER (Price to Earnings Ratio) menunjukkan berapa mahal harga saham dibanding laba"
        )

    if data["pb"]:
        signals.append(
            "PB Ratio menunjukkan perbandingan harga saham dengan nilai buku perusahaan"
        )

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
