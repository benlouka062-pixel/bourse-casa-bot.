import yfinance as yf
import json
import time
import os
from datetime import datetime

# === TES VRAIS TOKENS ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"
CHAT_ID = "8150604747"

# === DONNÉES PAR DÉFAUT TEMPORAIRES (UNIQUEMENT SI AUCUNE DONNÉE RÉELLE) ===
DEFAULT_PRICES = {
    "ADH": 25.50, "DHO": 148.30, "ENL": 176.20, "IAM": 142.80,
    "AGZ": 2180.00, "TQM": 795.00, "ATW": 452.00, "BCP": 281.00,
    "CIH": 324.00, "MNG": 1985.00, "SMI": 1590.00, "CMT": 1105.00
}

DEFAULT_RSI = 50
DEFAULT_SIGNAL = "ATTENTE"

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

# === FONCTIONS ===
def calculer_rsi(prix_historique):
    if len(prix_historique) < 15:
        return 50
    gains = 0
    pertes = 0
    for i in range(1, 15):
        diff = prix_historique[-i] - prix_historique[-i-1]
        if diff > 0:
            gains += diff
        else:
            pertes += abs(diff)
    if pertes == 0:
        return 100
    rs = gains / pertes
    return round(100 - (100 / (1 + rs)), 1)

def calculer_support_resistance(prix_historique, periode=20):
    if len(prix_historique) < periode:
        return None, None
    support = min(prix_historique[-periode:])
    resistance = max(prix_historique[-periode:])
    return round(support, 2), round(resistance, 2)

def get_price_and_rsi(sym, ticker):
    try:
        hist = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if not hist.empty:
            prix = round(hist['Close'].iloc[-1], 2)
            prix_list = hist['Close'].tolist()
            rsi = calculer_rsi(prix_list)
            support, resistance = calculer_support_resistance(prix_list)
            
            if rsi < 30:
                signal = "ACHAT"
            elif rsi > 70:
                signal = "VENTE"
            else:
                signal = "ATTENTE"
            
            return {
                "sym": sym,
                "nom": NOMS[sym],
                "prix": prix,
                "rsi": rsi,
                "signal": signal,
                "support": support,
                "resistance": resistance,
                "source": "RÉEL"
            }
    except Exception as e:
        print(f"Erreur {sym}: {e}")
    
    # Fallback temporaire (disparaîtra dès qu'un vrai prix sera trouvé)
    prix_defaut = DEFAULT_PRICES.get(sym, 100)
    return {
        "sym": sym,
        "nom": NOMS[sym],
        "prix": prix_defaut,
        "rsi": DEFAULT_RSI,
        "signal": DEFAULT_SIGNAL,
        "support": round(prix_defaut * 0.97, 2),
        "resistance": round(prix_defaut * 1.03, 2),
        "source": "DÉFAUT (temporaire)"
    }

def get_masi():
    try:
        masi = yf.download("^MASI", period="1d", progress=False)
        if not masi.empty:
            return round(masi['Close'].iloc[-1], 2)
    except:
        pass
    return None

def get_metaux():
    """Récupère les métaux via GoldAPI (à implémenter)"""
    # Version simplifiée en attendant l'API réelle
    return {
        "precieux": {
            "XAU": {"nom": "Or", "prix": 2350.50, "variation": 0.8},
            "XAG": {"nom": "Argent", "prix": 28.75, "variation": 1.2}
        },
        "industriels": {
            "XCU": {"nom": "Cuivre", "prix": 4.25, "variation": 0.3},
            "XPB": {"nom": "Plomb", "prix": 2150, "variation": -0.2},
            "XZN": {"nom": "Zinc", "prix": 2580, "variation": 0.5}
        }
    }

def lire_ancien_cache():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {"actions": []}

def main():
    print("🔍 Récupération des données...")
    
    ancien_cache = lire_ancien_cache()
    actions_data = []
    
    for sym, ticker in ACTIONS.items():
        data = get_price_and_rsi(sym, ticker)
        actions_data.append(data)
        print(f"  {sym}: {data['prix']} DH ({data['source']})")
        time.sleep(1)
    
    masi = get_masi()
    metaux = get_metaux()
    
    output = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "source": "📡 SYSTÈME HYBRIDE (réel + fallback temporaire)",
        "masi": masi,
        "volume": "N/A",
        "variation": "N/A",
        "actions": actions_data,
        "metaux": metaux
    }
    
    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Fichier data.json généré avec {len(actions_data)} actions")
    print(f"   ⚠️  Les données par défaut seront remplacées dès que les vrais prix arriveront")

if __name__ == "__main__":
    main()
