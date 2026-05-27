"""
CryptoPulse - 自动推送版
每小时推送到Slack，不需要@mention
"""
import requests, time, json
from datetime import datetime

TOKEN = "YOUR_SLACK_BOT_TOKEN"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE = "https://slack.com/api"

def post(msg):
    r = requests.post(f"{BASE}/chat.postMessage", headers=HEADERS, 
        json={"channel": "U0B6F0PKB6V", "text": msg}, timeout=10)
    return r.json().get("ok")

def get_price(s):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}USDT", timeout=5)
        return float(r.json()["price"])
    except: return 0

print("CryptoPulse Auto-Poster started")
post("🤖 CryptoPulse已上线！每小时自动推送行情。")

last_signal = ""
while True:
    try:
        now = datetime.now()
        if now.minute == 0:  # 整点推送
            pairs = {"BTC":0,"ETH":0,"BNB":0,"SOL":0}
            for s in pairs:
                pairs[s] = get_price(s)
            
            # Load signals
            try:
                with open("/home/administrator/crypto_signals/live_signals.json") as f:
                    sigs = json.load(f)["signals"]
            except: sigs = {}
            
            msg = f"📊 *{now.strftime('%H:%M')} 行情*\n"
            for s,p in pairs.items():
                if p > 0:
                    sg = sigs.get(f"{s}USDT",{}).get("signal","-")
                    e = {"BUY":"🟢","SELL":"🔴","HOLD":"⚪"}.get(sg,"")
                    msg += f"{e} {s}: ${p:,.2f}\n"
            
            signal_str = "".join(sigs.get(f"{s}USDT",{}).get("signal","") for s in ["BTC","ETH","BNB","SOL"])
            if signal_str != last_signal:
                post(msg)
                last_signal = signal_str
                print(f"Posted {now.strftime('%H:%M')}")
        
        time.sleep(30)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
