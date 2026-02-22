"""전일/이전 값 저장. JSON 파일로 유지한다."""
from market_brief.state.store import load_state, save_state

__all__ = ["load_state", "save_state"]
