import csv
import json
import math
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_FILE = "data.json"

SYMBOL_MAP = {
    "Addoha": "ADH", "Afriquia_gaz": "AGZ", "Argent": "XAG", "Attijariwafa_bk": "ATW",
    "Auto_hall": "AH", "Cartier_saada": "CRS", "Colorado": "COL", "Cuivre": "COPPER",
    "Delta_holding": "DHO", "Ennakl_Automobiles_SA": "ENL", "Managem_SA": "MNG",
    "Marocaine_Ste_de_Therapeutique": "SOT", "Masi_20": "MASI", "Miniere_touissit": "CMT",
    "Moroccan_All_Shares": "MAS", "Or": "XAU", "Plomb": "LEAD", "Risma": "RIS",
    "Smi": "SMI", "Stokvis_nord": "SNA", "Taqa_Morocco_SA": "TQM",
    "Travaux_Generaux_De_Construction": "TGCC", "Zinc": "ZINC",
}

FULL_NAMES = {
    "ADH": "ADDOHA", "AGZ": "AFRIQUIA GAZ", "XAG": "Argent", "ATW": "Attijariwafa bank",
    "AH": "Auto Hall", "CRS": "CARTIER SAADA", "COL": "COLORADO", "COPPER": "Cuivre",
    "DHO": "DELTA HOLDING", "ENL": "ENNAKL", "MNG": "MANAGEM", "SOT": "SOTHEMA",
    "MASI": "MASI", "CMT": "TOUISSIT", "MAS": "Moroccan All Shares", "XAU": "Or",
    "LEAD": "Plomb", "RIS": "RISMA", "SMI": "SMI", "SNA": "STOKVIS NORD",
    "TQM": "TAQA MOROCCO", "TGCC": "TGCC", "ZINC": "Zinc",
}

def parse_float(value):
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).replace('.', '').replace(',', '.')
    try:
        return float(value)
    except:
        return None

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def calculate_adx(high, low, close, period=14):
    if len(close) < period + 1:
        return 20
    tr = []
    for i in range(1, len(close)):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr.append(max(hl, hc, lc))
    dm_plus, dm_minus = [], []
    for i in range(1, len(high)):
        up = high[i] - high[i-1]
        down = low[i-1] - low[i]
        dm_plus.append(up if up > down and up > 0 else 0)
        dm_minus.append(down if down > up and down > 0 else 0)
    atr = sum(tr[:period]) / period
    di_plus = (sum(dm_plus[:period]) / period) / atr * 100
    di_minus = (sum(dm_minus[:period]) / period) / atr * 100
    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100
    return round(dx, 2)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    if len(prices) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0, "crossover": None}
    def ema(data, period):
        k = 2 / (period + 1)
        ema_val = [data[0]]
        for price in data[1:]:
            ema_val.append(price * k + ema_val[-1] * (1 - k))
        return ema_val
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(prices))]
    signal_line = ema(macd_line, signal)
    histogram = macd_line[-1] - signal_line[-1]
    crossover = None
    if len(macd_line) > 1 and len(signal_line) > 1:
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            crossover = "bullish"
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            crossover = "bearish"
    return {"macd": round(macd_line[-1], 3), "signal": round(signal_line[-1], 3), "histogram": round(histogram, 3), "crossover": crossover}

def calculate_supertrend(high, low, close, period=10, multiplier=3):
    if len(close) < period:
        return 0
    atr = []
    for i in range(1, len(close)):
        tr = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        atr.append(tr)
    atr_avg = sum(atr[:period]) / period if len(atr) >= period else atr[0]
    upper_band = (high[-1] + low[-1]) / 2 + multiplier * atr_avg
    lower_band = (high[-1] + low[-1]) / 2 - multiplier * atr_avg
    if close[-1] > upper_band:
        return 1
    elif close[-1] < lower_band:
        return -1
    return 0

def main():
    all_data = []
    for file in DATA_DIR.glob("*.csv"):
        base = file.name.replace("historical_data-", "").replace(".csv", "")
        if base not in SYMBOL_MAP:
            continue
        sym = SYMBOL_MAP[base]
        closes, highs, lows = [], [], []
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            try:
                close_idx = header.index("Cours")
                high_idx = header.index("Plus haut")
                low_idx = header.index("Plus bas")
            except:
                continue
            for row in reader:
                if len(row) <= max(close_idx, high_idx, low_idx):
                    continue
                price = parse_float(row[close_idx])
                high = parse_float(row[high_idx])
                low = parse_float(row[low_idx])
                if price is not None and high is not None and low is not None:
                    closes.append(price)
                    highs.append(high)
                    lows.append(low)
        if len(closes) < 30:
            continue
        closes.reverse()
        highs.reverse()
        lows.reverse()
        current = closes[-1]
        rsi = calculate_rsi(closes)
        adx = calculate_adx(highs, lows, closes)
        macd = calculate_macd(closes)
        supertrend = calculate_supertrend(highs, lows, closes)
        all_data.append({
            "sym": sym,
            "nom": FULL_NAMES.get(sym, sym),
            "prix": round(current, 2),
            "rsi": rsi,
            "adx": adx,
            "macd": macd,
            "supertrend": supertrend,
            "source": "REEL"
        })
    output = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "actions": all_data}
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"✅ {len(all_data)} actifs")

if __name__ == "__main__":
    main()
