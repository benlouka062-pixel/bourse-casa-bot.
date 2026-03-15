import sys
import yfinance as yf
import requests
import json
import urllib.parse
from datetime import datetime, timedelta

# === CONFIGURATION ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"

# Mapping symboles
ACTIONS = {
    "ADH": "ADH.MS", "DHO": "DHO.MS", "ENL": "ENL.MS", "IAM": "IAM.MS",
    "AGZ": "AGZ.MS", "TQM": "TQM.MS", "ATW": "ATW.MS", "BCP": "BCP.MS",
    "CIH": "CIH.MS", "MNG": "MNG.MS", "SMI": "SMI.MS", "CMT": "CMT.MS"
}

def send_telegram_photo(chat_id, image_url, caption=""):
    """Envoie une photo via Telegram (URL)"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            print("✅ Image envoyée")
        else:
            print(f"❌ Erreur {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def send_telegram_message(chat_id, text):
    """Envoie un message texte"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def generate_quickchart_url(sym, prices):
    """Génère une URL QuickChart pour un graphique des prix"""
    
    # Préparer les données
    dates = [(datetime.now() - timedelta(days=i)).strftime("%d/%m") for i in range(len(prices)-1, -1, -1)]
    
    chart_config = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": [{
                "label": f"{sym} - Prix",
                "data": prices,
                "borderColor": "#00ff9d",
                "backgroundColor": "rgba(0,255,157,0.1)",
                "fill": True,
                "tension": 0.4
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": f"{sym} - Derniers prix",
                "color": "#ffffff"
            },
            "legend": {
                "labels": {"fontColor": "#ffffff"}
            },
            "scales": {
                "xAxes": [{"ticks": {"fontColor": "#aaaaaa"}}],
                "yAxes": [{"ticks": {"fontColor": "#aaaaaa"}}]
            },
            "backgroundColor": "#0b0e14"
        }
    }
    
    # Convertir en JSON et encoder pour URL
    json_str = json.dumps(chart_config)
    encoded = urllib.parse.quote(json_str)
    return f"https://quickchart.io/chart?width=600&height=400&c={encoded}"

def is_market_open():
    """Vérifie si le marché est ouvert (approximatif)"""
    now = datetime.now()
    # Bourse ouverte: lundi-vendredi, 9h-17h
    if now.weekday() >= 5:  # 5 = samedi, 6 = dimanche
        return False
    if now.hour < 9 or now.hour >= 17:
        return False
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_chart.py SYMBOLE CHAT_ID")
        return
    
    sym = sys.argv[1].upper()
    chat_id = sys.argv[2]
    
    if sym not in ACTIONS:
        send_telegram_message(chat_id, f"❌ Symbole {sym} inconnu")
        return
    
    ticker = ACTIONS[sym]
    
    # Vérifier si le marché est ouvert
    if not is_market_open():
        send_telegram_message(chat_id, f"📊 *{sym}*\nMarché fermé aujourd'hui. Les graphiques seront disponibles à la réouverture.\n\nTu peux quand même consulter les données historiques sur le dashboard.")
        return
    
    try:
        # Récupérer les données (30 derniers jours)
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        
        if data.empty:
            send_telegram_message(chat_id, f"❌ Pas de données pour {sym}")
            return
        
        # Extraire les prix
        prices = data['Close'].tolist()
        dernier_prix = prices[-1]
        variation = ((prices[-1] - prices[-2]) / prices[-2]) * 100 if len(prices) > 1 else 0
        
        # Générer l'URL du graphique QuickChart
        chart_url = generate_quickchart_url(sym, prices[-10:])  # 10 derniers jours
        
        # Message de légende
        caption = f"📊 *{sym}* – {ACTIONS[sym]}\n"
        caption += f"💰 Prix: {dernier_prix:.2f} DH\n"
        caption += f"📈 Variation: {variation:+.2f}%\n"
        caption += f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Envoyer l'image
        send_telegram_photo(chat_id, chart_url, caption)
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
