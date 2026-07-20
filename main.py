from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
import time
import urllib.request


# --- RENDER WEB SUNUCUSU ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"WaveTrend Botu Aktif!")


def run_web_server():
  server = HTTPServer(("0.0.0.0", 10000), SimpleHTTPRequestHandler)
  server.serve_forever()


# --- AYARLAR ---
BOT_TOKEN = "8800165896:AAHDSixZvv7UMVYWmerLEwoBi5DhcPoUwqQ"
CHAT_ID = "@Bvg564bot"  # Sinyallerin düşeceği kanal

# Midas Koin Listesi
COINS = [
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
    "FETUSDT",
    "RENDERUSDT",
    "GRTUSDT",
    "ARKMUSDT",
    "ROSEUSDT",
    "IOUSDT",
    "VANAUSDT",
    "ACTUSDT",
    "PEPEUSDT",
    "WIFUSDT",
    "FLOKIUSDT",
    "BONKUSDT",
    "DOGSUSDT",
    "CATIUSDT",
    "HMSTRUSDT",
    "MEWUSDT",
    "MOGUSDT",
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
    print("Sinyal mesajı gönderildi!")
  except Exception as e:
    print("Telegram gönderme hatası:", e)


def calculate_ema(series, period):
  """Basit EMA hesaplayıcı"""
  alpha = 2 / (period + 1)
  ema = [series[0]]
  for val in series[1:]:
    ema.append(alpha * val + (1 - alpha) * ema[-1])
  return ema


def get_wavetrend_cross_lb(symbol, interval="15m", n1=10, n2=21):
  """Binance mum verilerinden WaveTrend (wt1 / wt_cross_lb) hesaplar"""
  try:
    # Son 100 mum verisini çek (15 dakikalık grafikler için)
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    req = urllib.request.urlopen(url)
    klines = json.loads(req.read().decode("utf-8"))

    # HLC3 (High + Low + Close) / 3
    ap = [
        (float(k[2]) + float(k[3]) + float(k[4])) / 3.0 for k in klines
    ]  # [high, low, close]
    last_price = float(klines[-1][4])

    # ESA = EMA(AP, n1)
    esa = calculate_ema(ap, n1)

    # D = EMA(Abs(AP - ESA), n1)
    diff = [abs(ap[i] - esa[i]) for i in range(len(ap))]
    d = calculate_ema(diff, n1)

    # CI = (AP - ESA) / (0.015 * D)
    ci = []
    for i in range(len(ap)):
      denominator = 0.015 * d[i]
      ci.append((ap[i] - esa[i]) / denominator if denominator != 0 else 0)

    # WT1 = EMA(CI, n2)
    wt1 = calculate_ema(ci, n2)

    # En güncel tamamlanan/oluşan WaveTrend değeri
    return round(wt1[-1], 2), last_price
  except Exception as e:
    print(f"{symbol} WaveTrend hesaplama hatası:", e)
    return None, None


def crypto_loop():
  time.sleep(5)
  send_telegram(
      CHAT_ID,
      "🚀 **WaveTrend (wt_cross_lb < 53) Sinyal Botu Başlatıldı!**\n"
      "Midas koinleri 15d periyotta taranıyor...",
  )

  # Aynı koine sürekli spam mesaj atmaması için son sinyal hafızası
  signaled_coins = {}

  while True:
    for coin in COINS:
      wt_val, price = get_wavetrend_cross_lb(coin, interval="15m")

      if wt_val is not None:
        # KOŞUL: WaveTrend 53'ün altındaysa ve yakın zamanda bildirilmediyse
        if wt_val < 53:
          if coin not in signaled_coins or (time.time() - signaled_coins[coin]) > 3600:  # 1 saatte 1 tekrar
            msg = (
                f"🚨 **WAVETREND AL SİNYALİ** 🚨\n\n"
                f"🪙 **Koin:** #{coin}\n"
                f"📊 **WT Value:** `{wt_val}` (Limit: < 53)\n"
                f"💵 **Fiyat:** ${price}\n"
                f"⏱️ **Periyot:** 15 Dakikalık"
            )
            send_telegram(CHAT_ID, msg)
            signaled_coins[coin] = time.time()

      time.sleep(0.2)  # Binance API limitlerine takılmamak için kısa bekleme

    # Tüm liste bittikten sonra 3 dakikada bir tekrar tara
    time.sleep(180)


if __name__ == "__main__":
  Thread(target=run_web_server, daemon=True).start()
  crypto_loop()
