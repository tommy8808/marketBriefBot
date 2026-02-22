"""
항목별 provider: us10y, commodities, private_company, vix, adr_index, fx_rates, bdi, blogs.
각 함수는 (section_name, List[BriefItem]) 반환. 실패 시 N/A 항목 반환.
"""
import os
import logging
from typing import Dict, List, Tuple
from dotenv import load_dotenv

from market_brief.providers.base import BriefItem
from market_brief.providers.fred import fetch_fred_latest
from market_brief.providers.stooq import fetch_stooq_close
from market_brief.providers.rss import fetch_rss_entries
from market_brief.providers.manual import get_manual_item, get_manual_value

load_dotenv()
logger = logging.getLogger("market_brief.providers.brief_items")

NA = BriefItem(name="—", value="N/A", change=None, change_pct=None, link=None, state_key=None, numeric_value=None)


def _item_with_change(
    name: str,
    value: float,
    prev: float | None,
    state_key: str,
    link: str | None = None,
    fmt: str = "{:.2f}",
) -> BriefItem:
    """숫자 value로 BriefItem 생성. prev 또는 state에서 변동률 계산은 main에서 적용."""
    change = (value - prev) if prev is not None else None
    change_pct = (100.0 * (value - prev) / prev) if prev and prev != 0 else None
    return BriefItem(
        name=name,
        value=fmt.format(value),
        change=change,
        change_pct=change_pct,
        link=link,
        state_key=state_key,
        numeric_value=value,
    )


def _apply_state_to_items(
    items: List[BriefItem],
    state: Dict | None,
) -> List[BriefItem]:
    """state['items']에 전일값이 있으면 변동률을 채운다. numeric_value는 유지."""
    if not state or not items:
        return items
    cache = (state.get("items") or {})
    out = []
    for it in items:
        if it.numeric_value is not None and it.state_key:
            prev = cache.get(it.state_key)
            if prev is not None:
                prev_f = float(prev) if not isinstance(prev, (int, float)) else prev
                change = it.numeric_value - prev_f
                change_pct = (100.0 * change / prev_f) if prev_f != 0 else None
                out.append(BriefItem(
                    name=it.name,
                    value=it.value,
                    change=change,
                    change_pct=change_pct,
                    link=it.link,
                    state_key=it.state_key,
                    numeric_value=it.numeric_value,
                ))
                continue
        out.append(it)
    return out


def fetch_us10y(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """US 10Y: FRED DGS10 우선, 없으면 Stooq."""
    section = "us10y"
    # FRED
    latest, prev = fetch_fred_latest("DGS10")
    if latest is not None:
        return section, [_item_with_change("US 10Y", latest, prev, "us10y", link="https://fred.stlouisfed.org/series/DGS10")]
    # Stooq: US 10Y 종목 코드 (예: 10Y 종목)
    cur, prev_stooq = fetch_stooq_close("10Y.US")
    if cur is not None:
        return section, [_item_with_change("US 10Y", cur, prev_stooq, "us10y")]
    return section, [get_manual_item("US 10Y", "US10Y_MANUAL", link="https://fred.stlouisfed.org/series/DGS10", state_key="us10y")]


def fetch_commodities(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """env에 심볼 리스트(쉼표 구분). Stooq로 각각 조회."""
    section = "commodities"
    syms = (os.getenv("BRIEF_COMMODITIES_SYMBOLS") or "CL.F,WTI.F,BZ.F").strip().split(",")
    syms = [s.strip() for s in syms if s.strip()]
    items = []
    for s in syms:
        cur, prev = fetch_stooq_close(s)
        key = f"commodities.{s}"
        if cur is not None:
            items.append(_item_with_change(s, cur, prev, key))
        else:
            items.append(BriefItem(name=s, value="N/A", state_key=key))
    return section, items if items else [NA]


def fetch_private_company(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """manual + 링크."""
    section = "private_company"
    link = get_manual_value("BRIEF_PRIVATE_COMPANY_LINK")
    item = get_manual_item("Private Company", "BRIEF_PRIVATE_COMPANY", link=link or None, state_key="private_company")
    return section, [item]


def fetch_vix(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """VIX: Stooq."""
    section = "vix"
    cur, prev = fetch_stooq_close("^VIX")
    if cur is not None:
        return section, [_item_with_change("VIX", cur, prev, "vix", link="https://stooq.com/q/?s=^vix")]
    return section, [get_manual_item("VIX", "VIX_MANUAL", state_key="vix")]


def fetch_adr_index(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """ADR Index: manual 또는 Stooq 심볼."""
    section = "adr_index"
    manual = get_manual_value("BRIEF_ADR_INDEX")
    if manual:
        return section, [get_manual_item("ADR Index", "BRIEF_ADR_INDEX", state_key="adr_index")]
    sym = os.getenv("BRIEF_ADR_INDEX_SYMBOL") or "^BKX"
    cur, prev = fetch_stooq_close(sym)
    if cur is not None:
        return section, [_item_with_change("ADR Index", cur, prev, "adr_index")]
    return section, [get_manual_item("ADR Index", "BRIEF_ADR_INDEX", state_key="adr_index")]


def fetch_fx_rates(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """환율: Stooq 또는 manual."""
    section = "fx_rates"
    pairs = (os.getenv("BRIEF_FX_PAIRS") or "USDKRW=X,JPYKRW=X").strip().split(",")
    pairs = [p.strip() for p in pairs if p.strip()]
    items = []
    for p in pairs:
        cur, prev = fetch_stooq_close(p)
        key = f"fx.{p}"
        if cur is not None:
            items.append(_item_with_change(p, cur, prev, key))
        else:
            items.append(BriefItem(name=p, value="N/A", state_key=key))
    return section, items if items else [NA]


def fetch_bdi(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """BDI: Stooq 시도, 안 되면 manual."""
    section = "bdi"
    cur, prev = fetch_stooq_close("^BALDR")
    if cur is not None:
        return section, [_item_with_change("BDI", cur, prev, "bdi")]
    return section, [get_manual_item("BDI", "BDI_MANUAL", state_key="bdi")]


def fetch_blogs(state: Dict | None) -> Tuple[str, List[BriefItem]]:
    """RSS로 블로그 새 글 n개."""
    section = "blogs"
    url = os.getenv("BRIEF_BLOGS_RSS_URL") or ""
    n = int(os.getenv("BRIEF_BLOGS_RSS_COUNT") or "5")
    if not url.strip():
        return section, [BriefItem(name="(RSS URL 없음)", value="N/A", link=None)]
    entries = fetch_rss_entries(url.strip(), max_entries=n)
    items = [
        BriefItem(name=e[0][:80], value="글 보기", link=e[1], state_key=None)
        for e in entries
    ]
    return section, items if items else [NA]


# 순서대로 실행할 항목별 fetcher
SECTION_FETCHERS = [
    fetch_us10y,
    fetch_commodities,
    fetch_private_company,
    fetch_vix,
    fetch_adr_index,
    fetch_fx_rates,
    fetch_bdi,
    fetch_blogs,
]


def run_all_sections(state: Dict | None) -> Tuple[Dict[str, List[BriefItem]], Dict[str, float]]:
    """
    모든 항목을 순서대로 수집. (sections, items_for_state) 반환.
    items_for_state: state 저장용 { state_key: numeric_value }.
    """
    sections = {}
    items_for_state = {}
    for fetcher in SECTION_FETCHERS:
        try:
            name, items = fetcher(state)
            items = _apply_state_to_items(items, state)
            sections[name] = items
            for it in items:
                if it.state_key and it.numeric_value is not None:
                    items_for_state[it.state_key] = it.numeric_value
        except Exception as e:
            section_name = getattr(fetcher, "__name__", "").replace("fetch_", "") or "unknown"
            logger.warning("section %s failed: %s", section_name, e)
            sections[section_name] = [NA]
    return sections, items_for_state
