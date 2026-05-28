import os
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import time
import schedule

# Your credentials
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, payload)

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_signal(symbol, interval, timeframe_label):
    try:
        ticker = yf.Ticker(symbol)
        period = "30d" if interval == "1h" else "7d"
        data = ticker.history(period=period, interval=interval)

        if data.empty:
            print(f"{symbol} — No data returned")
            return

        data['RSI'] = calculate_rsi(data)
        latest = data.iloc[-1]
        rsi = round(latest['RSI'], 2)
        price = round(latest['Close'], 2)

        print(f"[{timeframe_label}] {symbol} | Price: ${price} | RSI: {rsi}")

        if interval == "1h":
            if 65 <= rsi < 70:
                send_telegram_message(
                    f"⚠️ <b>SETUP DEVELOPING — {symbol} (1H)</b>\n"
                    f"Price: ${price}\n"
                    f"RSI: {rsi} (Approaching Overbought)\n"
                    f"Timeframe: 1 Hour\n"
                    f"🕐 {datetime.now().strftime('%H:%M')}"
                )
            elif 31 < rsi <= 35:
                send_telegram_message(
                    f"⚠️ <b>SETUP DEVELOPING — {symbol} (1H)</b>\n"
                    f"Price: ${price}\n"
                    f"RSI: {rsi} (Approaching Oversold)\n"
                    f"Timeframe: 1 Hour\n"
                    f"🕐 {datetime.now().strftime('%H:%M')}"
                )
            elif rsi >= 70:
                send_telegram_message(
                    f"🔴 <b>SELL SIGNAL — {symbol} (1H)</b>\n"
                    f"Price: ${price}\n"
                    f"RSI: {rsi} (Overbought)\n"
                    f"Timeframe: 1 Hour\n"
                    f"🕐 {datetime.now().strftime('%H:%M')}"
                )
            elif rsi <= 30:
                send_telegram_message(
                    f"🟢 <b>BUY SIGNAL — {symbol} (1H)</b>\n"
                    f"Price: ${price}\n"
                    f"RSI: {rsi} (Oversold)\n"
                    f"Timeframe: 1 Hour\n"
                    f"🕐 {datetime.now().strftime('%H:%M')}"
                )

        elif interval == "15m":
            if rsi >= 70:
                send_telegram_message(
                    f"🔴 <b>SELL ENTRY — {symbol} (15min)</b>\n"
                    f"Price: ${price}\n"
                    f"RSI: {rsi} (Overbought)\n"
                    f"Timeframe: 15 Min\n"
                    f"⚡ <b>Possible Entry Point</b>\n"
                    f"🕐 {datetime.now().strftime('%H:%M')}"
                )
            elif rsi <= 30:
                send_telegram_message(
                    f"🟢 <b>BUY ENTRY — {symbol} (15min)</b>\n"
                    f"Price: ${price}\n"
                    f"RSI: {rsi} (Oversold)\n"
                    f"Timeframe: 15 Min\n"
                    f"⚡ <b>Possible Entry Point</b>\n"
                    f"🕐 {datetime.now().strftime('%H:%M')}"
                )

    except Exception as e:
        print(f"Error with {symbol} on {timeframe_label}: {e}")

symbols = [
    "AAPL",
    "TSLA",
    "QQQ",
    "SPY",
    "AMZN",
]

def run_scan():
    print("=" * 50)
    print(f"🔍 Scanning {len(symbols)} tickers — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    print("\n📊 1 HOUR TIMEFRAME")
    for symbol in symbols:
        check_signal(symbol, "1h", "1H")

    print("\n⚡ 15 MIN TIMEFRAME")
    for symbol in symbols:
        check_signal(symbol, "15m", "15min")

    print("\n✅ Scan complete!")

# Schedule it
schedule.every(15).minutes.do(run_scan)
schedule.every(1).hours.do(run_scan)

# Run once immediately on startup
run_scan()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
