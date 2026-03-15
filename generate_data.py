import yfinance as yf
import json
import time
from datetime import datetime

# === TES VRAIS TOKENS ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"
CHAT_ID = "8150604747"

# Actions à suivre
ACTIONS = {
    "ADH": "ADH.MS",
    "DHO": "DHO.MS",
    "ENL": "ENL.MS",
    "IAM": "IAM.MS",
    "AGZ": "AGZ.MS",
    "TQM": "TQM.MS",
    "ATW": "ATW.MS",
    "BCP": "BCP.MS",
    "CIH": "CIH.MS",
    "MNG": "MNG.MS",
    "SMI": "SMI.MS",
    "CMT": "CMT.MS"
}

NOMS = {
    "ADH": "ADDOHA", "DHO": "DELTA HOLDING", "ENL": "ENNAKL", "IAM": "ITISSALAT",
    "AGZ": "AFRIQUIA GAZ", "TQM": "TAQA MOROCCO", "ATW": "ATTIJARI", "BCP": "BCP",
    "CIH": "CIH", "MNG": "MANAGEM", "SMI": "SMI", "CMT": "CMT"
}

def calculer_rsi(prix_historique):
    """Calcule le RSI à partir d'une liste de prix"""
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

def get_price_and_rsi(sym, ticker):
    """Récupère le prix et calcule le RSI"""
    try:
        # Données historiques pour le RSI
        hist = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if hist.empty:
            return None, None
        
        # Dernier prix
        prix = round(hist['Close'].iloc[-1], 2)
        
        # Calcul RSI
        prix_list = hist['Close'].tolist()
        rsi = calculer_rsi(prix_list)
        
        # Déterminer le signal
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
            "signal": signal
        }
    except Exception as e:
        print(f"Erreur {sym}: {e}")
        return None

def get_masi():
    """Récupère l'indice MASI"""
    try:
        masi = yf.download("^MASI", period="1d", progress=False)
        if not masi.empty:
            return round(masi['Close'].iloc[-1], 2)
    except:
        pass
    return None

def main():
    print("🔍 Récupération des données réelles...")
    
    actions_data = []
    for sym, ticker in ACTIONS.items():
        data = get_price_and_rsi(sym, ticker)
        if data:
            actions_data.append(data)
        time.sleep(1)
    
    masi = get_masi()
    
    # Structure finale
    output = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "masi": masi,
        "volume": "N/A",  # À améliorer plus tard
        "variation": "N/A",
        "actions": actions_data
    }
    
    # Sauvegarde dans un fichier JSON
    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Fichier data.json généré avec {len(actions_data)} actions")

if __name__ == "__main__":
    main()
