"""
텔레그램 테스트 메시지 전송 스크립트.
.env의 TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID를 사용합니다.
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(text: str) -> bool:
    """텔레그램으로 메시지를 전송합니다."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("오류: .env에 TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 설정해주세요.")
        print("  .env.example을 참고해 .env 파일을 만들고 값을 채워주세요.")
        return False

    url = TELEGRAM_API_URL.format(token=TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("메시지 전송 성공.")
        return True
    except requests.RequestException as e:
        print(f"전송 실패: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                print("응답 내용:", e.response.json())
            except Exception:
                print("응답 본문:", e.response.text[:500])
        return False


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "테스트 메시지입니다."
    success = send_telegram_message(message)
    sys.exit(0 if success else 1)
