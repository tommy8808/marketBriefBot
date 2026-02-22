"""브리핑 상태(전일 값 등)를 JSON 파일로 저장/로드한다."""
import json
import os
from pathlib import Path
from typing import Any, Dict

# 프로젝트 루트(teleBot) 기준 data 폴더. store.py → state → market_brief → src → 루트
def _state_dir() -> Path:
    try:
        base = Path(__file__).resolve().parents[3]
        if base.exists():
            return base / "data"
    except IndexError:
        pass
    return Path.cwd() / "data"


STATE_FILENAME = "market_brief_state.json"


def _state_path() -> Path:
    path = _state_dir() / STATE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_state() -> Dict[str, Any] | None:
    """저장된 상태를 읽는다. 없거나 실패 시 None."""
    path = _state_path()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_state(data: Any) -> None:
    """브리핑 결과를 상태로 저장한다. BriefData 또는 {last_date, items} dict."""
    path = _state_path()
    payload = {}
    if isinstance(data, dict):
        payload = {k: v for k, v in data.items()}
    else:
        if hasattr(data, "date"):
            payload["last_date"] = data.date
        if hasattr(data, "sections"):
            payload["sections"] = data.sections
        if hasattr(data, "meta"):
            payload["meta"] = data.meta
        if hasattr(data, "items"):
            payload["items"] = data.items
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
