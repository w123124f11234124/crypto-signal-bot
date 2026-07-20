from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from threading import Thread
import time
import urllib.request

logging.basicConfig(level=logging.INFO)


# --- RENDER WEB SUNUCUSU (Uyumama Garantisi) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"WaveTrend Botu 7/24 Aktif!")

  def log_message(self, format, *args):
    return


def run_web_server():
  try:
    server = HTTPServer(("0.0.0.0", 10000), SimpleHTTPRequestHandler)
    server.serve_forever()
  except Exception as e:
    logging.error(f"Web sunucu hatasi: {e}")


# --- AYARLARINIZ ---
BOT_TOKEN = "8800165896:AAHDSixZvv7UMVYWmerLEwoBi5DhcPoUwqQ"
CHAT_ID = "@bvg564bot"

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


def send_telegram(target_chat_id, message):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  data = json.dumps({
      "chat_id": target_chat_id,
      "text": message,
      "parse_mode": "Markdown",
  }).encode("utf-8")

  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}
  )
  try:
    with urllib.request.urlopen(req, timeout=10) as response:
      pass
  except Exception as e:
    logging.error(f"Telegram gonderim hatasi ({target_chat_id}): {e}")


def listen_telegram_messages():
  offset = 0
  logging.info("Telegram mesaj dinleyicisi baslatildi.")
  while True:
    try:
      url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
      req = urllib.request.Request(url)
      with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))

      for update in data.get("result", []):
        offset = update["update_id"] + 1
        if "message" in update and "text" in update["message"]:
          text = update["message"]["text"]
          user_id = update["message"]["chat"]["id"]

          if text.startswith("/start"):
            reply = (
                "🟢 **WaveTrend Botu Aktif ve Calisiyor!**\n\n"
                "📊 Midas koinleri 15 dakikalik periyotta taraniyor.\n"
                "🚨 WaveTrend (`wt_cross_lb`) **53 altina** dustugunde kanala"
                " otomatik sinyal atilacaktir."
            )
            send_telegram(user_id, reply)
    except Exception as e:
      time.sleep(3)


def calculate_ema(series, period):
  alpha = 2 / (period + 1)
  ema = [series[0]]
  for val in series[1:]:
    ema.append(alpha * val + (1 - alpha) * ema[-1])
  return ema


def get_wavetrend_cross_lb(symbol, interval="15m", n1=10, n2=21):
  try:
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
      klines = json.loads(resp.read().decode("utf-8"))

    ap = [(float(k[2]) + float(k[3]) + float(k[4])) / 3.0 for k in klines]
    last_price = float(klines[-1][4])

    esa = calculate_ema(ap, n1)
    diff = [abs(ap[i] - esa[i]) for i in range(len(ap))]
    d = calculate_ema(diff, n1)

    ci = []
    for i in range(len(ap)):
      den = 0.015 * d[i]
      ci.append((ap[i] - esa[i]) / den if den != 0 else 0)

    wt1 = calculate_ema(ci, n2)
    return round(wt1[-1], 2), last_price
  except Exception as e:
    return None, None


def crypto_loop():
  time.sleep(5)
  send_telegram(
      CHAT_ID,
      "🚀 **WaveTrend (wt_cross_lb < 53) Sinyal Botu Basariyla Baslatildi!**\n"
      "Tüm Midas koinleri taranmaya baslandi...",
  )

  signaled_coins = {}

  while True:
    for coin in COINS:
      wt_val, price = get_wavetrend_cross_lb(coin, interval="15m")

      if wt_val is not None and wt_val < 53:
        now = time.time()
        # Aynı koine 1 saat boyunca tekrar tekrar mesaj atıp spam yapmaz
        if coin not in signaled_coins or (now - signaled_coins[coin]) > 3600:
          msg = (
              f"🚨 **WAVETREND AL SİNYALİ** 🚨\n\n"
              f"🪙 **Koin:** #{coin}\n"
              f"📊 **WT Value:** `{wt_val}` (Limit: < 53)\n"
              f"💵 **Fiyat:** ${price}\n"
              f"⏱️ **Periyot:** 15 Dakikalık"
          )
          send_telegram(CHAT_ID, msg)
          signaled_coins[coin] = now

      time.sleep(0.1)

    time.sleep(120)  # Tüm koinler bittiğinde 2 dakika bekleip baştan tara


if __name__ == "__main__":
  Thread(target=run_web_server, daemon=True).start()
  Thread(target=listen_telegram_messages, daemon=True).start()
  crypto_loop()
