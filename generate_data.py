import yfinance as yf
import requests
import json
import time
import os
from datetime import datetime, timedelta

# === TES VRAIS TOKENS ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"
CHAT_ID = "8150604747"

# === GOLDAPI ===
GOLD_API_KEY = "goldapi-kqb19mlv7mcz7-io"

# === DONNÉES PAR DÉFAUT ===
DEFAULT_PRICES = {
    "ADH": 25.50, "DHO": 148.30, "ENL": 176.20, "IAM": 142.80,
    "AGZ": 2180.00, "TQM": 795.00, "ATW": 452.00, "BCP": 281.00,
    "CIH": 324.00, "MNG": 1985.00, "SMI": 1590.00, "CMT": 1105.00
}

# Mapping des actions
ACTIONS = {
    "ADH": "ADH.MS", "DHO": "DHO.MS", "ENL": "ENL.MS", "IAM": "IAM.MS",
    "AGZ": "AGZ.MS", "TQM": "TQM.MS", "ATW": "ATW.MS", "BCP": "BCP.MS",
    "CIH": "CIH.MS", "MNG": "MNG.MS", "SMI": "SMI.MS", "CMT": "CMT.MS"
}

NOMS = {
    "ADH": "ADDOHA", "DHO": "DELTA HOLDING", "ENL": "ENNAKL", "IAM": "ITISSALAT",
    "AGZ": "AFRIQUIA GAZ", "TQM": "TAQA MOROCCO", "ATW": "ATTIJARI", "BCP": "BCP",
    "CIH": "CIH", "MNG": "MANAGEM", "SMI": "SMI", "CMT": "CMT"
}

# === FONCTIONS TECHNIQUES ===
def calculer_rsi(prix_historique, periode=14):
    if len(prix_historique) < periode + 1:
        return 50
    deltas = [prix_historique[i] - prix_historique[i-1] for i in range(1, len(prix_historique))]
    gains = [d if d > 0 else 0 for d in deltas][-periode:]
    pertes = [-d if d < 0 else 0 for d in deltas][-periode:]
    gain_moyen = sum(gains) / periode
    perte_moyenne = sum(pertes) / periode
    if perte_moyenne == 0:
        return 100
    rs = gain_moyen / perte_moyenne
    return round(100 - (100 / (1 + rs)), 1)

def calculer_macd(prix_historique):
    if len(prix_historique) < 26:
        return 0, 0, 0
    import pandas as pd
    df = pd.DataFrame(prix_historique, columns=['close'])
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return round(macd.iloc[-1], 2), round(signal.iloc[-1], 2), round(macd.iloc[-1] - signal.iloc[-1], 2)

def calculer_bollinger(prix_historique, periode=20):
    if len(prix_historique) < periode:
        return prix_historique[-1], prix_historique[-1], prix_historique[-1]
    import pandas as pd
    df = pd.DataFrame(prix_historique, columns=['close'])
    sma = df['close'].rolling(window=periode).mean().iloc[-1]
    std = df['close'].rolling(window=periode).std().iloc[-1]
    return round(sma + 2*std, 2), round(sma, 2), round(sma - 2*std, 2)

def get_historique(ticker, jours=30):
    try:
        hist = yf.download(ticker, period=f"{jours}d", interval="1d", progress=False)
        if not hist.empty:
            return [round(p, 2) for p in hist['Close'].tolist()]
    except:
        pass
    return []

def get_price_and_indicators(sym, ticker):
    try:
        hist = yf.download(ticker, period="2mo", interval="1d", progress=False)
        if not hist.empty:
            prix = round(hist['Close'].iloc[-1], 2)
            prix_list = hist['Close'].tolist()
            rsi = calculer_rsi(prix_list)
            macd, signal_macd, hist_macd = calculer_macd(prix_list)
            bb_haut, bb_mid, bb_bas = calculer_bollinger(prix_list)
            
            support = round(min(prix_list[-20:]), 2)
            resistance = round(max(prix_list[-20:]), 2)
            
            if rsi < 30:
                signal = "ACHAT"
            elif rsi > 70:
                signal = "VENTE"
            else:
                signal = "ATTENTE"
            
            # Récupérer l'historique pour les graphiques
            historique = get_historique(ticker, 30)
            
            return {
                "sym": sym,
                "nom": NOMS[sym],
                "prix": prix,
                "rsi": rsi,
                "macd": macd,
                "signal_macd": signal_macd,
                "histogram_macd": hist_macd,
                "bb_haut": bb_haut,
                "bb_mid": bb_mid,
                "bb_bas": bb_bas,
                "support": support,
                "resistance": resistance,
                "signal": signal,
                "historique": historique,
                "source": "RÉEL"
            }
    except Exception as e:
        print(f"Erreur {sym}: {e}")
    
    # Fallback temporaire
    prix_defaut = DEFAULT_PRICES.get(sym, 100)
    historique = [prix_defaut * (0.95 + 0.01 * i) for i in range(30)]
    return {
        "sym": sym,
        "nom": NOMS[sym],
        "prix": prix_defaut,
        "rsi": 50,
        "macd": 0,
        "signal_macd": 0,
        "histogram_macd": 0,
        "bb_haut": round(prix_defaut * 1.05, 2),
        "bb_mid": prix_defaut,
        "bb_bas": round(prix_defaut * 0.95, 2),
        "support": round(prix_defaut * 0.97, 2),
        "resistance": round(prix_defaut * 1.03, 2),
        "signal": "ATTENTE",
        "historique": historique,
        "source": "DÉFAUT"
    }

def get_masi():
    try:
        masi = yf.download("^MASI", period="1d", progress=False)
        if not masi.empty:
            return round(masi['Close'].iloc[-1], 2)
    except:
        pass
    return None

def get_metaux_reels():
    metals = {"precieux": {}, "industriels": {}}
    
    # Or
    try:
        url = "https://www.goldapi.io/api/XAU/USD"
        headers = {'x-access-token': GOLD_API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            metals["precieux"]["XAU"] = {
                "nom": "Or", "prix": round(data.get('price', 2350), 2),
                "variation": round(data.get('cp', 0.8), 2)
            }
        else:
            metals["precieux"]["XAU"] = {"nom": "Or", "prix": 2350.50, "variation": 0.8}
    except:
        metals["precieux"]["XAU"] = {"nom": "Or", "prix": 2350.50, "variation": 0.8}
    
    time.sleep(1)
    
    # Argent
    try:
        url = "https://www.goldapi.io/api/XAG/USD"
        headers = {'x-access-token': GOLD_API_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            metals["precieux"]["XAG"] = {
                "nom": "Argent", "prix": round(data.get('price', 28.75), 2),
                "variation": round(data.get('cp', 1.2), 2)
            }
        else:
            metals["precieux"]["XAG"] = {"nom": "Argent", "prix": 28.75, "variation": 1.2}
    except:
        metals["precieux"]["XAG"] = {"nom": "Argent", "prix": 28.75, "variation": 1.2}
    
    # Métaux industriels (simulés pour l'instant)
    metals["industriels"] = {
        "XCU": {"nom": "Cuivre", "prix": 4.25, "variation": 0.3},
        "XPB": {"nom": "Plomb", "prix": 2150, "variation": -0.2},
        "XZN": {"nom": "Zinc", "prix": 2580, "variation": 0.5}
    }
    
    return metals

def main():
    print("🔍 Récupération des données...")
    
    actions_data = []
    for sym, ticker in ACTIONS.items():
        data = get_price_and_indicators(sym, ticker)
        actions_data.append(data)
        print(f"  {sym}: {data['prix']} DH ({data['source']})")
        time.sleep(1)
    
    masi = get_masi()
    metaux = get_metaux_reels()
    
    output = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "source": "📡 GOLDAPI + INDICATEURS",
        "masi": masi,
        "volume": "N/A",
        "variation": "N/A",
        "actions": actions_data,
        "metaux": metaux
    }
    
    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Fichier data.json généré avec {len(actions_data)} actions")
    print(f"🏅 Or: {metaux['precieux'].get('XAU', {}).get('prix', 'N/A')} USD")
    print(f"🏅 Argent: {metaux['precieux'].get('XAG', {}).get('prix', 'N/A')} USD")

if __name__ == "__main__":
    main()
