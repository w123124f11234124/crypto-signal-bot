import json
import time
import urllib.request

# --- AYARLAR ---
BOT_TOKEN = "BOTFATHER_TOKENINIZI_BURAYA_YAZIN"
CHAT_ID = "@kanal_kullanici_adiniz"  # Veya sayısal ID: -100123456789
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT"]  # Takip edilecek koinler


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
    print("Telegram mesajı başarıyla gönderildi!")
  except Exception as e:
    print("Telegram gönderme hatası:", e)


def check_crypto_signals():
  for coin in COINS:
    try:
      # Binance API'sinden 24 saatlik fiyat verisi çek
      url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}"
      req = urllib.request.urlopen(url)
      data = json.loads(req.read().decode("utf-8"))

      price = float(data["lastPrice"])
      price_change = float(data["priceChangePercent"])

      # GÖSTERGE SİNYAL KOŞULU:
      # Örneğin günlük %4'ten fazla düşen koinlerde "AL / DÜŞÜŞ FIRSATI" sinyali at
      if price_change <= -4.0:
        msg = (
            f"🚨 **KRİPTO AL SİNYALİ** 🚨\n\n"
            f"🪙 **Koin:** #{coin}\n"
            f"💵 **Fiyat:** ${price}\n"
            f"📉 **24s Değişim:** %{price_change:.2f}\n\n"
            f"💡 *Fiyat sert dip yaptı, göstergeler alım bölgesinde!*"
        )
        send_telegram(msg)
    except Exception as e:
      print(f"{coin} verisi çekilirken hata oluştu:", e)


if __name__ == "__main__":
  print("Ücretsiz Sinyal Botu Başlatıldı!")
  while True:
    try:
      check_crypto_signals()
      # Binance API'sine yük bindirmemek ve ban yememek için 5 dakikada bir kontrol et
      time.sleep(300)
    except Exception as e:
      print("Genel döngü hatası:", e)
      time.sleep(30)
