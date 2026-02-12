# telegram_uploader.py
import requests
import config


def send_report_to_telegram(report_md: str):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment variables.")
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": report_md[:4000],  # Telegram一条消息最大4096字符
        #"parse_mode": "Markdown"
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    return resp.json()
