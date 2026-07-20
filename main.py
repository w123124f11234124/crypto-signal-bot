import json
from threading import Thread
import time
import urllib.request
from flask import Flask

# Render'ın uykuda kalmaması için minik bir web sunucusu
app = Flask(__name__)


@app.route('/')
def home():
  return 'Bot 7/24 Aktif Çalışıyor!'


# --- AYARLAR ---
BOT_TOKEN = "BOTFATHER_TOKENINIZ"
CHAT_ID = "@kanal_kullanici_adiniz"
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]


def send_telegram(message):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  data = json.dumps({
      "chat_id": CHAT_ID,
      "text": message,
      "parse_mode": "Markdown",
  }).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}
  )
  try:
    urllib.request.urlopen(req)
  except Exception as e:
    print("Telegram hatası:", e)


def crypto_loop():
  while True:
    for coin in COINS:
      try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode("utf-8"))
        price = float(data["lastPrice"])
        price_change = float(data["priceChangePercent"])

        if price_change <= -4.0:
          msg = (
              f"🚨 **KRİPTO AL SİNYALİ** 🚨\n\n"
              f"🪙 **Koin:** #{coin}\n"
              f"💵 **Fiyat:** ${price}\n"
              f"📉 **24s Değişim:** %{price_change:.2f}"
          )
          send_telegram(msg)
      except Exception as e:
        print("Hata:", e)
    time.sleep(300)


# Arka planda taramayı başlat
Thread(target=crypto_loop).start()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
