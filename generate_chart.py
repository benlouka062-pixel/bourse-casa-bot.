import sys
import yfinance as yf
import requests
from datetime import datetime, timedelta

# === CONFIGURATION ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"

# Mapping symboles
ACTIONS = {
    "ADH": "ADH.MS", "DHO": "DHO.MS", "ENL": "ENL.MS", "IAM": "IAM.MS",
    "AGZ": "AGZ.MS", "TQM": "TQM.MS", "ATW": "ATW.MS", "BCP": "BCP.MS",
    "CIH": "CIH.MS", "MNG": "MNG.MS", "SMI": "SMI.MS", "CMT": "CMT.MS"
}

def send_telegram_photo(chat_id, photo_url, caption=""):
    """Envoie une photo via Telegram (URL)"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
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

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_chart.py SYMBOLE CHAT_ID")
        return
    
    sym = sys.argv[1].upper()
    chat_id = sys.argv[2]
    
    if sym not in ACTIONS:
        send_telegram_photo(chat_id, "", f"❌ Symbole {sym} inconnu")
        return
    
    ticker = ACTIONS[sym]
    
    # Récupérer les données
    try:
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if data.empty:
            send_telegram_photo(chat_id, "", f"❌ Pas de données pour {sym}")
            return
        
        # Dernier prix et variation
        dernier_prix = data['Close'].iloc[-1]
        variation = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        
        # Construction de l'URL du graphique TradingView
        # (widget embed public)
        chart_url = f"https://s.tradingview.com/widgetembed/?symbol=MAD:{ticker}&interval=D&theme=dark"
        
        caption = f"📊 *{sym}* – {ACTIONS[sym]}\n"
        caption += f"💰 Prix: {dernier_prix:.2f} DH\n"
        caption += f"📈 Variation: {variation:+.2f}%\n"
        caption += f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        send_telegram_photo(chat_id, chart_url, caption)
        
    except Exception as e:
        send_telegram_photo(chat_id, "", f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
