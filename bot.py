import ccxt
import pandas as pd
import requests
import time
import os
from threading import Thread
from flask import Flask

# --- FLASK WEB SUNUCUSU (Render'ın kapanmaması için) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot aktif ve 7/24 çalışıyor!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM VE BOT AYARLARI ---
TELEGRAM_TOKEN = "8980949450:AAG0-IxO3GvxPXyO2OA8i-I9qgQCJpru2pI"
CHAT_ID = "8463383361"

SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
TIMEFRAME = '5m'
THRESHOLD = 50

notified_states = {symbol: False for symbol in SYMBOLS}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram mesajı gönderilemedi:", e)

def calculate_wavetrend(symbol, timeframe='1h', n1=10, n2=21):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    ap = (df['high'] + df['low'] + df['close']) / 3
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    
    wt1 = ci.ewm(span=n2, adjust=False).mean()
    wt2 = wt1.rolling(window=4).mean()
    
    return wt1.iloc[-1], wt2.iloc[-1]

def bot_loop():
    print("Kripto WaveTrend Botu Çalışıyor...")
    send_telegram("🚀 WaveTrend Takip Botu Başlatıldı!")

    while True:
        for symbol in SYMBOLS:
            try:
                wt1, wt2 = calculate_wavetrend(symbol, TIMEFRAME)
                print(f"[{symbol}] WT1: {wt1:.2f} | WT2: {wt2:.2f}")

                if wt1 < THRESHOLD and not notified_states[symbol]:
                    msg = f"🚨 **ALARM: {symbol}**\nWaveTrend (WT1) değeri {THRESHOLD} seviyesinin altına düştü!\nGüncel WT1: {wt1:.2f}"
                    send_telegram(msg)
                    notified_states[symbol] = True

                elif wt1 >= THRESHOLD:
                    notified_states[symbol] = False

            except Exception as e:
                print(f"{symbol} taranırken hata oluştu:", e)
            
            time.sleep(2)

        print("--- 5 Dakika Sonra Tekrar Taranacak ---")
        time.sleep(300)

if __name__ == "__main__":
    # Web sunucusunu arka planda çalıştır
    server_thread = Thread(target=run_flask)
    server_thread.start()
    
    # Bot tarama döngüsünü başlat
    bot_loop()
