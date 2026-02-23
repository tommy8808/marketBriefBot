"""Fetch feed title and entries from RSS via feedparser."""
import logging
from typing import List, Tuple
import feedparser

logger = logging.getLogger("market_brief.providers.rss")


def fetch_rss(feed_url: str, max_entries: int = 5) -> Tuple[str | None, List[Tuple[str, str]]]:
    """
    Return (feed_title, [(entry_title, link), ...]). On failure return (None, []).
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
    Return up to max_entries (title, link) tuples. On failure return [].
    """
    _, entries = fetch_rss(feed_url, max_entries=max_entries)
    return entries
