"""
CryptoPulse - Slack Crypto Agent (零配置版)
直接在频道里 @CryptoPulse 发消息就行
"""
import os, json, requests, logging, sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=bot_token)

def get_price(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT", timeout=5)
        return float(r.json()["price"])
    except: return 0

@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "").lower()
    
    if "price" in text:
        for sym in ["btc", "eth", "bnb", "sol"]:
            if sym in text:
                p = get_price(sym.upper())
                say(f"📊 {sym.upper()}/USDT: **${p:,.2f}**")
                return
        # Default BTC
        p = get_price("BTC")
        say(f"📊 BTC/USDT: **${p:,.2f}**\nTry: price btc / price eth / price sol")

    elif "signal" in text:
        try:
            with open("/home/administrator/crypto_signals/live_signals.json") as f:
                data = json.load(f)
            msg = "📈 实时信号:\n"
            for s, v in data["signals"].items():
                e = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}.get(v["signal"], "⚪")
                msg += f"{e} {s}: {v['signal']}\n"
            say(msg)
        except:
            say("⚠️ 信号数据暂时不可用")

    elif "report" in text:
        pairs = ["BTC", "ETH", "BNB", "SOL"]
        msg = f"📊 *每日报告 {datetime.now().strftime('%m-%d %H:%M')}*\n"
        for s in pairs:
            p = get_price(s)
            msg += f"• {s}: ${p:,.2f}\n"
        say(msg)

    elif "help" in text:
        say("🤖 CryptoPulse 命令:\n• `price btc` - 实时价格\n• `signal` - 交易信号\n• `report` - 市场报告\n• `help` - 帮助")

    else:
        say("👋 试试:\n• `@CryptoPulse price btc`\n• `@CryptoPulse signal`\n• `@CryptoPulse report`")

logging.info("Starting...")
SocketModeHandler(app, app_token).start()
