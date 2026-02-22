"""FRED API로 시계열 최신값/전일값을 가져오는 provider. API 키 없으면 스킵 가능."""
import logging
import os
from typing import Tuple
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("market_brief.providers.fred")

FRED_OBS_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_latest(series_id: str, api_key: str | None = None) -> Tuple[float | None, float | None]:
    """
    FRED 시리즈의 최신값, 전일값을 반환. (latest, previous).
    api_key가 없거나 빈 문자열이면 (None, None) 반환(스킵).
    """
    key = (api_key or os.getenv("FRED_API_KEY") or "").strip()
    if not key:
        logger.debug("FRED API key not set, skipping %s", series_id)
        return None, None
    try:
        params = {
            "series_id": series_id,
            "api_key": key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 2,
        }
        r = requests.get(FRED_OBS_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        obs = data.get("observations") or []
        if len(obs) < 1:
            return None, None
        def to_float(o: dict) -> float | None:
            v = (o.get("value") or "").strip()
            if v in ("", "."):
                return None
            try:
                return float(v)
            except ValueError:
                return None
        latest = to_float(obs[0])
        previous = to_float(obs[1]) if len(obs) >= 2 else None
        return latest, previous
    except Exception as e:
        logger.warning("FRED fetch %s: %s", series_id, e)
        return None, None
