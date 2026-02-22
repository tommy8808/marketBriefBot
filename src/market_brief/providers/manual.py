"""데이터 소스가 불명확한 항목: env에 값이 있으면 표시, 없으면 N/A."""
import os
from dotenv import load_dotenv

from market_brief.providers.base import BriefItem

load_dotenv()


def get_manual_item(name: str, env_key: str, link: str | None = None, state_key: str | None = None) -> BriefItem:
    """env_key에 해당하는 환경 변수 값을 보여준다. 없으면 N/A."""
    value = (os.getenv(env_key) or "").strip() or "N/A"
    return BriefItem(
        name=name,
        value=value,
        change=None,
        change_pct=None,
        link=link or None,
        state_key=state_key or env_key,
        numeric_value=None,
    )


def get_manual_value(env_key: str) -> str | None:
    """환경 변수 값을 반환. 없거나 빈 문자열이면 None."""
    v = (os.getenv(env_key) or "").strip()
    return v or None
