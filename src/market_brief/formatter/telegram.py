"""텔레그램용 브리핑 메시지 포맷팅. HTML 링크로 클릭 이동 가능 (Markdown 파싱 오류 방지)."""
from market_brief.providers.base import BriefData, BriefItem


def _escape_html(s: str) -> str:
    """HTML 엔티티 이스케이프. Telegram parse_mode=HTML에서 태그/엔티티 오류 방지."""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _format_item(item: BriefItem) -> str:
    """한 항목을 '이름: 값 (변동률) 링크' 형태로. 링크는 HTML <a href="...">클릭 이동</a>."""
    name = _escape_html(item.name)
    value = _escape_html(item.value)
    part = f"{name}: {value}"
    if item.change_pct is not None:
        sign = "+" if item.change_pct >= 0 else ""
        part += f" ({sign}{item.change_pct:.1f}%)"
    if item.link and item.link.strip():
        # URL 내 &, " 도 이스케이프해 href 깨짐 방지
        url = item.link.strip().replace("&", "&amp;").replace('"', "&quot;")
        part += f' <a href="{url}">클릭 이동</a>'
    return part


def format_brief_telegram(data: BriefData, title_suffix: str = "") -> str:
    """BriefData를 텔레그램 HTML에 적합한 텍스트로 만든다. sections는 섹션명 -> List[BriefItem]."""
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
