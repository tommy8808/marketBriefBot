"""feedparser로 RSS에서 새 글 제목/링크 n개를 가져온다."""
import logging
from typing import List, Tuple
import feedparser

logger = logging.getLogger("market_brief.providers.rss")


def fetch_rss_entries(feed_url: str, max_entries: int = 5) -> List[Tuple[str, str]]:
    """
    RSS 피드에서 최대 max_entries개의 (제목, 링크) 튜플 리스트 반환.
    실패 시 빈 리스트.
    """
    try:
        parsed = feedparser.parse(feed_url)
        if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", None):
            logger.debug("rss parse error %s", feed_url)
            return []
        entries = getattr(parsed, "entries", [])[:max_entries]
        out = []
        for e in entries:
            title = (e.get("title") or "").strip() or "(제목 없음)"
            link = (e.get("link") or "").strip()
            out.append((title, link))
        return out
    except Exception as e:
        logger.warning("rss fetch %s: %s", feed_url, e)
        return []
