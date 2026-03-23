import csv
import json
import math
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data/raw")
OUTPUT_FILE = "data_correlations.json"

FILE_NAMES = {
    "XAU": "Or",
    "XAG": "Argent",
    "COPPER": "Cuivre",
    "ZINC": "Zinc",
    "LEAD": "Plomb",
    "MNG": "Managem_SA",
    "SMI": "Smi",
    "CMT": "Miniere_touissit",
}

CORRELATIONS = [
    ("XAU", "MNG"),
    ("XAU", "SMI"),
    ("XAG", "MNG"),
    ("XAG", "SMI"),
    ("COPPER", "CMT"),
    ("ZINC", "CMT"),
    ("LEAD", "CMT"),
]

def parse_float(value):
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).replace('.', '').replace(',', '.')
    try:
        return float(value)
    except:
        return None

def load_prices(symbol):
    file_name = FILE_NAMES.get(symbol)
    if not file_name:
        return []
    file = DATA_DIR / f"historical_data-{file_name}.csv"
    if not file.exists():
        return []
    prices = []
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        try:
            close_idx = header.index("Cours")
        except:
            return []
        for row in reader:
            if len(row) <= close_idx:
                continue
            price = parse_float(row[close_idx])
            if price is not None:
                prices.append(price)
    if len(prices) > 0:
        prices.reverse()
    return prices

def pearson_corr(x, y):
    n = len(x)
    if n < 30:
        return 0
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    sum_y2 = sum(yi * yi for yi in y)
    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
    if denominator == 0:
        return 0
    return round(numerator / denominator, 3)

def main():
    all_symbols = set()
    for metal, action in CORRELATIONS:
        all_symbols.add(metal)
        all_symbols.add(action)

    data = {}
    for sym in all_symbols:
        data[sym] = load_prices(sym)

    results = []
    for metal, action in CORRELATIONS:
        metal_prices = data.get(metal, [])
        action_prices = data.get(action, [])
        if len(metal_prices) < 30 or len(action_prices) < 30:
            continue
        metal_last = metal_prices[-30:]
        action_last = action_prices[-30:]
        corr = pearson_corr(metal_last, action_last)
        results.append({
            "metal": metal,
            "action": action,
            "correlation": corr,
            "interpretation": "Forte corrélation" if abs(corr) > 0.7 else "Corrélation modérée" if abs(corr) > 0.4 else "Faible corrélation"
        })
    output = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "correlations": results
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
