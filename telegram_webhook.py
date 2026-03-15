import json
import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8342446918:AAG4cuQKWZypIeAmfTy45PB0r7hQ8QFjhqo"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        
        if text.startswith('/graph'):
            # Exemple: /graph IAM
            parts = text.split()
            if len(parts) == 2:
                sym = parts[1].upper()
                # Lancer le script de génération de graphique
                subprocess.Popen(['python', 'generate_chart.py', sym, str(chat_id)])
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
