import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Error: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in your .env file!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if data.get("ok"):
            print("✅ Success! Telegram alert sent successfully. Check your Telegram app!")
        else:
            print(f"❌ Failed to send Telegram alert: {data.get('description')}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_message = "🚀 *Test Alert*\nYour QA Job Agent notification system is now successfully linked to Telegram!"
    send_telegram_alert(test_message)
