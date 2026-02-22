"""프로바이더 공통 인터페이스. 새 지표는 이 프로토콜을 구현해 providers에 추가한다."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol


@dataclass
class BriefItem:
    """표준화된 브리핑 항목 하나. state 캐시 키는 change_pct 계산용."""
    name: str
    value: str
    change: float | None = None
    change_pct: float | None = None
    link: str | None = None
    state_key: str | None = None  # 전일값 캐시 키 (없으면 name 기반으로 사용)
    numeric_value: float | None = None  # state 저장/변동률 계산용


@dataclass
class BriefData:
    """브리핑에 사용할 수집 데이터. sections: 섹션명 -> BriefItem 리스트."""
    date: str
    sections: Dict[str, List[BriefItem]] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


class Provider(Protocol):
    """지표 수집 프로바이더 프로토콜."""

    def fetch(self, state: Dict[str, Any] | None) -> BriefData:
        """현재 state를 참고해 데이터를 수집해 BriefData로 반환한다."""
        ...
