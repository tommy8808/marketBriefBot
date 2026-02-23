"""Telegram brief message formatting. HTML links for click-to-open (avoids Markdown parse errors)."""
from market_brief.providers.base import BriefData, BriefItem


def _escape_html(s: str) -> str:
    """Escape HTML entities for Telegram parse_mode=HTML."""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _format_item(item: BriefItem) -> str:
    """Format one item as 'name: value (change%) link'. Link as HTML <a href='...'>click</a>."""
    name = _escape_html(item.name)
    value = _escape_html(item.value)
    # Header/separator line: no value, no link -> output name only
    if (not item.value) and (not item.link) and (item.change_pct is None) and (item.change is None):
        return name
    # Separator line (dashes only)
    if item.name.strip("-").strip() == "" and not item.value and not item.link:
        return name

    part = f"{name}: {value}"
    if item.change_pct is not None:
        sign = "+" if item.change_pct >= 0 else ""
        part += f" ({sign}{item.change_pct:.1f}%)"
    if item.link and item.link.strip():
        url = item.link.strip().replace("&", "&amp;").replace('"', "&quot;")
        part += f' <a href="{url}">클릭 이동</a>'
    return part


def format_brief_telegram(data: BriefData, title_suffix: str = "") -> str:
    """Build Telegram HTML text from BriefData. sections: section_name -> List[BriefItem]."""
    lines = [f"📌 오늘의 브리핑{title_suffix} · {_escape_html(data.date)}", ""]
    for section_name, items in data.sections.items():
        if not items:
            continue
        lines.append(f"▫️ {_escape_html(section_name)}")
        for it in items:
            if isinstance(it, BriefItem):
                lines.append("  " + _format_item(it))
            else:
                lines.append("  " + _escape_html(str(it)))
        lines.append("")
    return "\n".join(lines).strip()
