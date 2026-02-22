"""Stooq CSV 엔드포인트로 심볼 시세(종가, 전일종가)를 가져오는 provider."""
import logging
from typing import Tuple
from urllib.parse import urlencode

from market_brief.providers.http_csv import safe_fetch_csv

logger = logging.getLogger("market_brief.providers.stooq")

STOOQ_BASE = "https://stooq.com/q/d/l/"


def _stooq_url(symbol: str, days_back: int = 30) -> str:
    """Stooq 일봉 CSV. d1/d2 없이 요청하면 최근 데이터 반환."""
    params = {"s": symbol, "i": "d"}
    return f"{STOOQ_BASE}?{urlencode(params)}"


def fetch_stooq_close(symbol: str) -> Tuple[float | None, float | None]:
    """
    Stooq에서 심볼의 최신 종가, 전일 종가를 반환.
    (current_close, previous_close). 실패 시 (None, None).
    """
    url = _stooq_url(symbol)
    rows = safe_fetch_csv(url)
    if not rows or len(rows) < 2:
        logger.debug("stooq insufficient rows for %s", symbol)
        return None, None
    # 헤더 행 제거(첫 행이 Date인 경우), 최신일이 마지막에 오도록 정렬
    header = rows[0]
    data_rows = rows[1:] if header[0].lower() in ("date", "data") else rows
    if not data_rows:
        return None, None
    # Stooq CSV: Date, Open, High, Low, Close, Volume
    try:
        # 마지막 행 = 최신, 그 이전 = 전일
        def parse_close(row: Tuple[str, ...]) -> float | None:
            if len(row) < 5:
                return None
            s = (row[4] or "").strip()
            if not s or s.lower() in ("nan", "n/a", ""):
                return None
            return float(s.replace(",", "."))

        current = parse_close(data_rows[-1])
        previous = parse_close(data_rows[-2]) if len(data_rows) >= 2 else None
        return current, previous
    except (ValueError, IndexError) as e:
        logger.debug("stooq parse error %s: %s", symbol, e)
        return None, None
