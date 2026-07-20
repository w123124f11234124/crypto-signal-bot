import json
from threading import Thread
import time
import urllib.request
from flask import Flask

# Render'ın kapanmaması için Web Sunucusu
app = Flask(__name__)


@app.route('/')
def home():
  return 'Sinyal Botu 7/24 Aktif!'


# --- AYARLARINIZ ---
BOT_TOKEN = '8800165896:AAHDSixZvv7UMVYWmerLEwoBi5DhcPoUwqQ'
CHAT_ID = '@Bvg564bot'  # Örn: @kriptosinyallerim
COINS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


def send_telegram(message):
  url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
  data = json.dumps({
      'chat_id': CHAT_ID,
      'text': message,
      'parse_mode': 'Markdown',
  }).encode('utf-8')

  req = urllib.request.Request(
      url, data=data, headers={'Content-Type': 'application/json'}
  )
  try:
    urllib.request.urlopen(req)
    print('Telegram mesajı gönderildi!')
  except Exception as e:
    print('Telegram gönderme hatası:', e)


def crypto_loop():
  # Render açılır açılmaz test mesajı atması için
  time.sleep(5)
  send_telegram('🤖 **Sinyal Botu Başarıyla Başlatıldı ve Canlıda!**')

  while True:
    for coin in COINS:
      try:
        url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={coin}'
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))

        price = float(data['lastPrice'])
        price_change = float(data['priceChangePercent'])

        # Koşul: %3 ve üzeri düşüşlerde mesaj at
        if price_change <= -3.0:
          msg = (
              f'🚨 **KRİPTO AL SİNYALİ** 🚨\n\n'
              f'🪙 **Koin:** #{coin}\n'
              f'💵 **Fiyat:** ${price}\n'
              f'📉 **24s Değişim:** %{price_change:.2f}'
          )
          send_telegram(msg)
      except Exception as e:
        print(f'{coin} hatası:', e)

    # 5 dakikada bir kontrol et
    time.sleep(300)


# Arka plan tarama thread'i
Thread(target=crypto_loop, daemon=True).start()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
