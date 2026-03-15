import yfinance as yf
import requests
import time
from datetime import datetime

# === TES VRAIS TOKENS ===
BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"
CHAT_ID = "8150604747"

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

def get_prices():
    prix = {}
    for sym, ticker in ACTIONS.items():
        try:
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not data.empty:
                prix[sym] = round(data['Close'].iloc[-1], 2)
            else:
                hist = yf.Ticker(ticker).history(period="1d")
                if not hist.empty:
                    prix[sym] = round(hist['Close'].iloc[-1], 2)
                else:
                    prix[sym] = None
        except:
            prix[sym] = None
        time.sleep(1)
    return prix

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    prix = get_prices()
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = f"📊 *Cotations Bourse de Casa*\n_{timestamp}_\n\n"
    for sym, nom in NOMS.items():
        p = prix.get(sym)
        message += f"• *{sym}* ({nom}) : {p if p else 'indisponible'} DH\n"
    send_telegram(message)

if __name__ == "__main__":
    main()
