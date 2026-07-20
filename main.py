# Test için koşulu esnettik (Düşüş şartını kaldırdık)
if price_change != 0:
  msg = f"🧪 **TEST SİNYALİ** 🧪\n\n🪙 Koin: #{coin}\n💵 Fiyat: ${price}"
  send_telegram(msg)
