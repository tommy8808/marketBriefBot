"""feedparser로 RSS에서 피드 제목/새 글을 가져온다."""
import logging
from typing import List, Tuple
import feedparser

logger = logging.getLogger("market_brief.providers.rss")


def fetch_rss(feed_url: str, max_entries: int = 5) -> Tuple[str | None, List[Tuple[str, str]]]:
    """
    RSS 피드에서 (피드 제목, (글제목, 링크) 리스트)를 반환.
    실패 시 (None, []).
    """
    try:
        parsed = feedparser.parse(feed_url)
        if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", None):
            logger.debug("rss parse error %s", feed_url)
            return None, []

        feed_title = None
        feed = getattr(parsed, "feed", None)
        if isinstance(feed, dict):
            feed_title = (feed.get("title") or "").strip() or None
        else:
            # feedparser는 feed가 FeedParserDict처럼 동작할 수 있음
            try:
                feed_title = (getattr(feed, "title", None) or "").strip() or None
            except Exception:
                feed_title = None

        entries = getattr(parsed, "entries", [])[:max_entries]
        out: List[Tuple[str, str]] = []
        for e in entries:
            title = (e.get("title") or "").strip() or "(제목 없음)"
            link = (e.get("link") or "").strip()
            out.append((title, link))
        return feed_title, out
    except Exception as e:
        logger.warning("rss fetch %s: %s", feed_url, e)
        return None, []


def fetch_rss_entries(feed_url: str, max_entries: int = 5) -> List[Tuple[str, str]]:
    """
    RSS 피드에서 최대 max_entries개의 (제목, 링크) 튜플 리스트 반환.
    실패 시 빈 리스트.
    """
    _, entries = fetch_rss(feed_url, max_entries=max_entries)
    return entries
