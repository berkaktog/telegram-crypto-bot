import ccxt
import pandas as pd
import pandas_ta as ta
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Telegram Bot bilgileri
TOKEN = "8007415166:AAE3MW-JWOrwo_1Fh0b0iGepcZpWNhErFSA"
CHAT_ID = 1481505017

# Binance bağlantısı
exchange = ccxt.binance()

# Coin sinyal stratejisi
def get_strong_uptrend_symbols():
    markets = exchange.load_markets()
    symbols = [symbol for symbol in markets if "/USDT" in symbol and not any(st in symbol for st in ['DOWN', 'UP', 'BEAR', 'BULL'])]

    strong_uptrends = []

    for symbol in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=100)
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

            # RSI & EMA Stratejisi
            df['rsi'] = ta.rsi(df['close'], length=14)
            df['ema20'] = ta.ema(df['close'], length=20)
            df['ema50'] = ta.ema(df['close'], length=50)

            if (
                df['rsi'].iloc[-1] > 55 and
                df['ema20'].iloc[-1] > df['ema50'].iloc[-1] and
                df['close'].iloc[-1] > df['ema20'].iloc[-1]
            ):
                strong_uptrends.append(symbol)
        except Exception as e:
            continue

    return strong_uptrends[:5]

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Merhaba! Ben senin kripto takip botunum.\n"
        "📈 /sinyal yazarak anlık en güçlü coinleri görebilirsin.\n"
        "🔔 Her sabah 09:00'da otomatik sinyal göndereceğim!"
    )

# /sinyal komutu
async def sinyal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Coin'ler taranıyor, lütfen bekleyin...")

    signals = get_strong_uptrend_symbols()
    if signals:
        msg = "📈 Yükselişe Geçen Coinler:\n\n"
        msg += "\n".join([f"✅ {symbol}" for symbol in signals])
    else:
        msg = "🚫 Şu an yükselişe geçmiş uygun coin bulunamadı."

    await update.message.reply_text(msg)

# Botu başlat
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("sinyal", sinyal))

print("✅ Bot çalışıyor...")
app.run_polling()
