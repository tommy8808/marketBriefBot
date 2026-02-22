"""지표 수집 프로바이더. 각 지표별로 모듈을 추가해 확장한다."""
from market_brief.providers.base import BriefData, BriefItem, Provider
from market_brief.providers.dummy import DummyProvider

__all__ = ["BriefData", "BriefItem", "Provider", "DummyProvider"]
