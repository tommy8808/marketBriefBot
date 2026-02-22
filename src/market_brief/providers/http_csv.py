"""CSV/텍스트 기반 시세 요청·파싱·예외 처리 공통 함수."""
import csv
import io
import logging
from typing import Callable, List, Tuple
import requests

logger = logging.getLogger("market_brief.providers.http_csv")

DEFAULT_TIMEOUT = 15
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MarketBrief/1.0)",
}


def fetch_text(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    headers: dict | None = None,
    params: dict | None = None,
) -> str:
    """URL에서 텍스트(CSV 등)를 가져온다. 실패 시 예외 발생."""
    h = {**DEFAULT_HEADERS, **(headers or {})}
    try:
        r = requests.get(url, headers=h, params=params, timeout=timeout)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        logger.warning("fetch_text failed %s: %s", url, e)
        raise


def parse_csv(
    text: str,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
    skip_empty: bool = True,
) -> List[Tuple[str, ...]]:
    """CSV 텍스트를 파싱해 행 리스트(튜플)로 반환. 인코딩 오류 시 utf-8/split 폴백."""
    try:
        reader = csv.reader(io.StringIO(text.strip()), delimiter=delimiter)
        rows = [tuple(row) for row in reader]
    except Exception:
        rows = [tuple(line.strip().split(delimiter)) for line in text.strip().splitlines() if line.strip()]
    if skip_empty:
        rows = [r for r in rows if any(cell.strip() for cell in r)]
    return rows


def fetch_csv(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    delimiter: str = ",",
    params: dict | None = None,
) -> List[Tuple[str, ...]]:
    """URL에서 CSV를 가져와 파싱한 행 리스트를 반환. 실패 시 예외."""
    text = fetch_text(url, timeout=timeout, params=params)
    return parse_csv(text, delimiter=delimiter)


def safe_fetch_csv(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    delimiter: str = ",",
    params: dict | None = None,
) -> List[Tuple[str, ...]] | None:
    """fetch_csv와 동일하나 실패 시 None 반환, 예외 로깅."""
    try:
        return fetch_csv(url, timeout=timeout, delimiter=delimiter, params=params)
    except Exception as e:
        logger.debug("safe_fetch_csv %s: %s", url, e)
        return None
