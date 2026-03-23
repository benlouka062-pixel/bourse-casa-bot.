import json
import subprocess
import os
from datetime import datetime

DATA_FILE = "data.json"
LOG_FILE = "logs/notifications_sent.json"

def send_notification(title, message):
    try:
        subprocess.run([
            "termux-notification",
            "--title", title,
            "--content", message,
            "--priority", "high"
        ], timeout=5)
    except Exception as e:
        print(f"Erreur notification: {e}")

def load_sent_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_sent_log(log):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f)

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    sent_log = load_sent_log()
    today = datetime.now().strftime("%Y-%m-%d")
    metals = {}
    for action in data["actions"]:
        if action["sym"] in ["XAU", "XAG", "COPPER", "ZINC", "LEAD"]:
            metals[action["sym"]] = action.get("breakout", False)
    print(f"📢 Vérification des signaux à {datetime.now().strftime('%H:%M:%S')}")
    for action in data["actions"]:
        sym = action["sym"]
        if sym in metals:
            continue
        rsi = action["rsi"]
        adx = action.get("adx", 20)
        prix = action["prix"]
        support = action.get("support", 0)
        resistance = action.get("resistance", 0)
        breakout = action.get("breakout", False)
        divergence = action.get("divergence")
        correlations = action.get("correlations", [])
        key = f"{sym}_{today}"
        if rsi < 40 and adx > 20:
            if key not in sent_log or sent_log[key] != "buy_zone":
                send_notification(f"📉 {sym} - Zone d'achat", f"RSI={rsi} | ADX={adx} | Prix={prix} DH")
                sent_log[key] = "buy_zone"
        elif rsi > 60 and adx > 20:
            if key not in sent_log or sent_log[key] != "sell_zone":
                send_notification(f"📈 {sym} - Zone de vente", f"RSI={rsi} | ADX={adx} | Prix={prix} DH")
                sent_log[key] = "sell_zone"
        if breakout:
            if key not in sent_log or sent_log[key] != "breakout":
                send_notification(f"🚀 {sym} - Breakout", f"Prix={prix} > résistance={resistance}")
                sent_log[key] = "breakout"
        if prix < support:
            if key not in sent_log or sent_log[key] != "under_support":
                send_notification(f"⚠️ {sym} - Sous support", f"Prix={prix} < support={support}")
                sent_log[key] = "under_support"
        if divergence:
            if key not in sent_log or sent_log[key] != f"divergence_{divergence}":
                send_notification(f"🔄 {sym} - Divergence {divergence}", f"RSI={rsi}")
                sent_log[key] = f"divergence_{divergence}"
        if correlations and sym in ["MNG", "SMI", "CMT"]:
            for corr in correlations:
                metal = corr["metal"]
                corr_value = corr["correlation"]
                metal_breakout = metals.get(metal, False)
                if abs(corr_value) > 0.6 and metal_breakout:
                    corr_key = f"{sym}_corr_{metal}_{today}"
                    if corr_key not in sent_log:
                        send_notification(f"⚡ {sym} - Signal corrélé", f"Corrélation {corr_value:.2f} avec {metal} en breakout")
                        sent_log[corr_key] = "sent"
    save_sent_log(sent_log)
    print("✅ Vérification terminée")

if __name__ == "__main__":
    main()
