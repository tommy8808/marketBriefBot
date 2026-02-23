"""
Run brief: collect from providers -> format -> save state -> send Telegram.
"""
import logging
import os
import sys
from pathlib import Path
from datetime import date

# Add src to sys.path when running script directly (so market_brief is importable)
def _ensure_src_path():
    try:
        import market_brief  # noqa: F401
        return
    except ImportError:
        pass
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


_ensure_src_path()

from dotenv import load_dotenv

from market_brief.formatter.telegram import format_brief_telegram
from market_brief.providers.brief_items import run_all_sections
from market_brief.state.store import load_state, save_state
from market_brief.telegram_client import send_telegram_message
from market_brief.providers.base import BriefData

load_dotenv()

logger = logging.getLogger("market_brief")


def _setup_logging() -> None:
    """Configure logging to data/log.txt. No-op if already configured."""
    if logger.handlers:
        return
    try:
        root = Path(__file__).resolve().parents[2]
        log_dir = root / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "log.txt"
    except (IndexError, OSError):
        log_file = Path("data") / "log.txt"
        log_file.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(fmt)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def run() -> None:
    """Collect from providers in order, build brief message, send Telegram, save state."""
    _setup_logging()

    try:
        logger.info("브리핑 시작")
        state = load_state()
        sections, items_for_state = run_all_sections(state)

        data = BriefData(
            date=date.today().isoformat(),
            sections=sections,
            meta={"items_state": items_for_state},
        )

        message = format_brief_telegram(data)
        if not send_telegram_message(message):
            logger.error("텔레그램 발송 실패")
            sys.exit(1)

        save_state({
            "last_date": data.date,
            "items": items_for_state,
        })
        logger.info("브리핑 발송 완료.")
    except Exception as e:
        logger.exception("브리핑 실행 중 예외 발생")
        err_msg = f"⚠️ 브리핑 실행 오류\n\n{type(e).__name__}: {e}"
        send_telegram_message(err_msg, parse_mode=None)
        sys.exit(1)


if __name__ == "__main__":
    run()
