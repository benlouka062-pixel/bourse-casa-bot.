import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from datetime import datetime

# === CONFIGURATION ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"
CHAT_ID = "8150604747"

# === MAPPING DES URLS INVESTING.COM ===
INVESTING_URLS = {
    "ADH": "https://www.investing.com/equities/addoha",
    "DHO": "https://www.investing.com/equities/delta-holding",
    "ENL": "https://www.investing.com/equities/ennakl",
    "IAM": "https://www.investing.com/equities/iam",
    "AGZ": "https://www.investing.com/equities/afriquia-gaz",
    "TQM": "https://www.investing.com/equities/taqa-morocco",
    "ATW": "https://www.investing.com/equities/attijariwafa-bank",
    "BCP": "https://www.investing.com/equities/bcp",
    "CIH": "https://www.investing.com/equities/cih",
    "MNG": "https://www.investing.com/equities/managem",
    "SMI": "https://www.investing.com/equities/smi",
    "CMT": "https://www.investing.com/equities/ciments-du-maroc"
}

NOMS = {
    "ADH": "ADDOHA", "DHO": "DELTA HOLDING", "ENL": "ENNAKL", "IAM": "ITISSALAT",
    "AGZ": "AFRIQUIA GAZ", "TQM": "TAQA MOROCCO", "ATW": "ATTIJARI", "BCP": "BCP",
    "CIH": "CIH", "MNG": "MANAGEM", "SMI": "SMI", "CMT": "CMT"
}

# === FONCTION DE SCRAPING INVESTING.COM (améliorée) ===
def get_price_from_investing(symbol, url):
    """Scrape le prix depuis Investing.com en utilisant les données structurées."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠️ {symbol}: HTTP {r.status_code}")
            return None

        soup = BeautifulSoup(r.text, 'html.parser')

        # 1. Chercher dans les balises script de type application/ld+json
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Parcourir récursivement les données
                if isinstance(data, dict):
                    if 'price' in data:
                        return float(data['price'])
                    if 'offers' in data and isinstance(data['offers'], dict):
                        if 'price' in data['offers']:
                            return float(data['offers']['price'])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            if 'price' in item:
                                return float(item['price'])
                            if 'offers' in item and isinstance(item['offers'], dict) and 'price' in item['offers']:
                                return float(item['offers']['price'])
            except:
                continue

        # 2. Chercher dans les balises meta
        price_meta = soup.find('meta', {'property': 'product:price:amount'})
        if price_meta and price_meta.get('content'):
            return float(price_meta['content'])

        # 3. Chercher dans les balises span avec attributs spécifiques
        price_span = soup.find('span', {'data-test': 'instrument-price-last'})
        if price_span:
            text = price_span.text.strip().replace(',', '').replace(' ', '')
            match = re.search(r'(\d+\.?\d*)', text)
            if match:
                return float(match.group(1))

        # 4. Regex générale dans le texte (près de "MAD" ou "price")
        page_text = soup.text
        match = re.search(r'(\d+\.?\d*)\s*MAD', page_text)
        if match:
            return float(match.group(1))
        match = re.search(r'[Pp]rice["\']?\s*:\s*["\']?(\d+\.?\d*)', page_text)
        if match:
            return float(match.group(1))

    except Exception as e:
        print(f"  ❌ Erreur scraping {symbol}: {e}")
    return None

# === FONCTIONS POUR LES INDICATEURS (simplifiés) ===
def calculer_rsi(prix_historique):
    """RSI simplifié (pour l'exemple, on pourra améliorer)"""
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

# === FONCTION POUR LES MÉTAUX VIA GOLDAPI ===
def get_metaux_reels():
    metals = {"precieux": {}, "industriels": {}}
    GOLD_API_KEY = "goldapi-kqb19mlv7mcz7-io"

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

    # Métaux industriels (simulés, on pourra les remplacer plus tard)
    metals["industriels"] = {
        "XCU": {"nom": "Cuivre", "prix": 4.25, "variation": 0.3},
        "XPB": {"nom": "Plomb", "prix": 2150, "variation": -0.2},
        "XZN": {"nom": "Zinc", "prix": 2580, "variation": 0.5}
    }
    return metals

# === GESTION DU CACHE ===
def lire_ancien_cache():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {"actions": []}

# === MAIN ===
def main():
    print("🔍 Récupération des données (Investing.com)...")

    ancien_cache = lire_ancien_cache()
    anciennes_actions = {a['sym']: a for a in ancien_cache.get('actions', [])}

    actions_data = []
    source_globale = "📡 INVESTING.COM"

    for sym, url in INVESTING_URLS.items():
        print(f"  → {sym}...", end=" ")
        prix = get_price_from_investing(sym, url)

        if prix:
            # Générer un petit historique factice autour du prix
            historique = [prix * (0.95 + 0.01 * i) for i in range(10)]
            rsi = calculer_rsi(historique)

            support = round(prix * 0.97, 2)
            resistance = round(prix * 1.03, 2)

            if rsi < 30:
                signal = "ACHAT"
            elif rsi > 70:
                signal = "VENTE"
            else:
                signal = "ATTENTE"

            action_data = {
                "sym": sym,
                "nom": NOMS[sym],
                "prix": prix,
                "rsi": rsi,
                "signal": signal,
                "support": support,
                "resistance": resistance,
                "source": "RÉEL",
                "historique": historique[-5:]
            }
            actions_data.append(action_data)
            print(f"✅ {prix} DH")
            source_globale = "📡 TEMPS RÉEL"
        else:
            # Pas de prix → on utilise le cache si disponible
            if sym in anciennes_actions:
                ancien = anciennes_actions[sym].copy()
                ancien['source'] = "💾 CACHE"
                actions_data.append(ancien)
                print(f"💾 cache ({ancien.get('prix', '?')} DH)")
                source_globale = "💾 CACHE"
            else:
                print("❌ aucune donnée")
        time.sleep(2)  # Pause pour respecter le site

    # Récupérer les métaux
    metaux = get_metaux_reels()

    output = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "source": source_globale,
        "masi": None,
        "volume": "N/A",
        "variation": "N/A",
        "actions": actions_data,
        "metaux": metaux
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Fichier data.json généré avec {len(actions_data)} actions")
    print(f"📦 Source: {source_globale}")

if __name__ == "__main__":
    main()
