import smtplib
from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Clés API Binance (remplace par les tiennes)
api_key = 'smACYHXHeMflofUo11hlZfyZlzQSBxaG6oZhdyp9flf3b8zOff6N2Ho2rXwgSkhc'
api_secret = 'n8PxYktHoU4dMo6O6h4G6yar82jkqJe5TZwXFe7KCMEAIqEDuPWzOcGMlKlkbe7f'

# Création de l'instance de client Binance
client = Client(api_key, api_secret)

# Récupérer les données de la paire BTC/USDT (Bitcoin en USD) depuis un an
candles = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1DAY, "1 year ago UTC")

# Convertir les données en DataFrame
data = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_vol", "number_of_trades", "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"])

# Convertir le timestamp en date
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data['close'] = data['close'].astype(float)

# Calcul des indicateurs techniques
# Moyenne Mobile (SMA50 et SMA200)
data['SMA50'] = data['close'].rolling(window=50).mean()
data['SMA200'] = data['close'].rolling(window=200).mean()

# Calcul du RSI (Relative Strength Index)
delta = data['close'].diff()  # Différence entre la fermeture actuelle et la précédente
gain = delta.where(delta > 0, 0)  # Si la différence est positive, c'est un gain
loss = -delta.where(delta < 0, 0)  # Si la différence est négative, c'est une perte
average_gain = gain.rolling(window=14).mean()  # Moyenne des gains sur 14 jours
average_loss = loss.rolling(window=14).mean()  # Moyenne des pertes sur 14 jours
rs = average_gain / average_loss  # Ratio des gains moyens et pertes moyens
data['RSI'] = 100 - (100 / (1 + rs))  # Calcul du RSI

# Calcul du MACD
fast_ema = data['close'].ewm(span=12, adjust=False).mean()  # Exponentielle moyenne rapide
slow_ema = data['close'].ewm(span=26, adjust=False).mean()  # Exponentielle moyenne lente
data['MACD'] = fast_ema - slow_ema  # MACD = EMA rapide - EMA lente
data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()  # Signal (EMA de MACD)

# Fonction pour envoyer un email d'alerte
def send_email(subject, body, to_email):
    from_email = "zalux.11@gmail.com"
    password = "zoyt rfin kuzr djpl"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Connexion au serveur SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)

    # Envoi de l'email
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

# Détection des signaux d'achat et de vente
# Acheter si la SMA50 croise au-dessus de la SMA200
if data['SMA50'].iloc[-1] > data['SMA200'].iloc[-1]:
    subject = "Signal d'Achat : Bitcoin Est Rentable !"
    body = "Le Bitcoin est dans une phase haussière, avec la SMA50 croisant au-dessus de la SMA200.\n\nRSI actuel : {:.2f}\nMACD : {:.2f}".format(data['RSI'].iloc[-1], data['MACD'].iloc[-1])
    send_email(subject, body, "jujulax12@gmail.com")
    print("Alerte d'achat envoyée.")
# Vendre si la SMA50 croise en-dessous de la SMA200
elif data['SMA50'].iloc[-1] < data['SMA200'].iloc[-1]:
    subject = "Signal de Vente : Bitcoin Est en Danger !"
    body = "Le Bitcoin est dans une phase baissière, avec la SMA50 croisant en-dessous de la SMA200.\n\nRSI actuel : {:.2f}\nMACD : {:.2f}".format(data['RSI'].iloc[-1], data['MACD'].iloc[-1])
    send_email(subject, body, "jujulax12@gmail.comm")
    print("Alerte de vente envoyée.")
# Vérifier le RSI pour alerte (overbought/oversold)
elif data['RSI'].iloc[-1] > 70:
    subject = "Alerte : Bitcoin est en Overbought !"
    body = "Le RSI du Bitcoin est supérieur à 70 (zone de surachat).\n\nRSI actuel : {:.2f}\nMACD : {:.2f}".format(data['RSI'].iloc[-1], data['MACD'].iloc[-1])
    send_email(subject, body, "jujulax12@gmail.com")
    print("Alerte de surachat envoyée.")
elif data['RSI'].iloc[-1] < 30:
    subject = "Alerte : Bitcoin est en Oversold !"
    body = "Le RSI du Bitcoin est inférieur à 30 (zone de survente).\n\nRSI actuel : {:.2f}\nMACD : {:.2f}".format(data['RSI'].iloc[-1], data['MACD'].iloc[-1])
    send_email(subject, body, "jujulax12@gmail.com")
    print("Alerte de survente envoyée.")
else:
    print("Pas de signal d'achat ou de vente détecté.")
