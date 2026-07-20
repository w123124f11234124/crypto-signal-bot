from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
import time
import urllib.request


# --- RENDER İÇİN MİNİK WEB SUNUCUSU ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Bot 7/24 Aktif!")


def run_web_server():
  server = HTTPServer(("0.0.0.0", 10000), SimpleHTTPRequestHandler)
  server.serve_forever()


# --- AYARLARINIZ ---
BOT_TOKEN = "8800165896:AAHDSixZvv7UMVYWmerLEwoBi5DhcPoUwqQ"
CHAT_ID = "@Bvg564bot"  # Sinyallerin düşeceği kanal
COINS = [COINS =
    # Major & Katman 1/2
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "AVAXUSDT",
    "DOGEUSDT",
    "DOTUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "SHIBUSDT",
    "LTCUSDT",
    "NEARUSDT",
    "APTUSDT",
    "ARBUSDT",
    "OPUSDT",
    "SUIUSDT",
    "ATOMUSDT",
    "BCHUSDT",
    "ALGOUSDT",
    "FTMUSDT",
    "ETCUSDT",
    "TRXUSDT",
    "XLMUSDT",
    "BNBUSDT",
    "CROUSDT",
    "CFXUSDT",
    "KASUSDT",
    # Yapay Zeka & Veri
    "FETUSDT",
    "RENDERUSDT",
    "GRTUSDT",
    "ARKMUSDT",
    "ROSEUSDT",
    "IOUSDT",
    "VANAUSDT",
    "ACTUSDT",
    # Memecoinler & Popüler Tokenlar
    "PEPEUSDT",
    "WIFUSDT",
    "FLOKIUSDT",
    "BONKUSDT",
    "DOGSUSDT",
    "CATIUSDT",
    "HMSTRUSDT",
    "MEWUSDT",
    "MOGUSDT",
    # DeFi & Ekosistem
    "INJUSDT",
    "TIAUSDT",
    "RUNEUSDT",
    "AEROUSDT",
    "1INCHUSDT",
    "NEXOUSDT",
    "ASTRUSDT",
    "ZETAUSDT",
    "ENSUSDT",
]


def send_telegram(chat_id, message):
  """Belirtilen CHAT_ID'ye mesaj atar"""
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  data = json.dumps({
      "chat_id": chat_id,
      "text": message,
      "parse_mode": "Markdown",
  }).encode("utf-8")

  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}
  )
  try:
    urllib.request.urlopen(req)
    print("Mesaj başarıyla gönderildi!")
  except Exception as e:
    print("Mesaj gönderme hatası:", e)


def check_user_messages():
  """Gelen /start mesajlarını dinler ve cevap verir"""
  last_update_id = 0
  while True:
    try:
      url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
      req = urllib.request.urlopen(url)
      data = json.loads(req.read().decode("utf-8"))

      for update in data.get("result", []):
        last_update_id = update["update_id"]
        if "message" in update and "text" in update["message"]:
          text = update["message"]["text"]
          user_chat_id = update["message"]["chat"]["id"]

          if text == "/start":
            reply = (
                "👋 **Merhaba! Sinyal Botu Aktif.**\n\n"
                "Arka planda piyasayı tarıyorum, alım fırsatı olduğunda kanala sinyal atacağım!"
            )
            send_telegram(user_chat_id, reply)
    except Exception as e:
      print("Mesaj dinleme hatası:", e)
      time.sleep(5)


def crypto_loop():
  """Kripto piyasasını tarar ve kanala sinyal atar"""
  time.sleep(5)
  # Bot açılır açılmaz kanala test mesajı gönderir:
  send_telegram(
      CHAT_ID, "🚀 **Sinyal Botu Başarıyla Başlatıldı ve Canlıda!**"
  )

  while True:
    for coin in COINS:
      try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode("utf-8"))

        price = float(data["lastPrice"])
        price_change = float(data["priceChangePercent"])

        # KOŞUL: Düşüş yaşandığında Sinyal At
        if price_change <= -2.0:  # Testi rahat görmeniz için -%2 yaptık
          msg = (
              f"🚨 **KRİPTO AL SİNYALİ** 🚨\n\n"
              f"🪙 **Koin:** #{coin}\n"
              f"💵 **Fiyat:** ${price}\n"
              f"📉 **24s Değişim:** %{price_change:.2f}"
          )
          send_telegram(CHAT_ID, msg)
      except Exception as e:
        print(f"{coin} hatası:", e)

    time.sleep(300)  # 5 dakikada bir kontrol et


if __name__ == "__main__":
  # 1. Web Sunucusunu Başlat
  Thread(target=run_web_server, daemon=True).start()
  # 2. Gelen /start Mesajlarını Dinlemeyi Başlat
  Thread(target=check_user_messages, daemon=True).start()
  # 3. Kripto Tarayıcısını Başlat
  crypto_loop()
