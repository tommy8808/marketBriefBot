"""더미 프로바이더: 실제 API 없이 샘플 데이터를 반환한다."""
from datetime import date

from market_brief.providers.base import BriefData, Provider


class DummyProvider(Provider):
    """샘플 브리핑용 더미 데이터."""

    def fetch(self, state: dict | None) -> BriefData:
        today = date.today().isoformat()
        return BriefData(
            date=today,
            sections={
                "지수": {
                    "KOSPI": "2,500.00 (+0.5%)",
                    "KOSDAQ": "850.00 (-0.2%)",
                    "S&P500": "5,100.00 (+0.3%)",
                },
                "환율": {
                    "USD/KRW": "1,350.00",
                    "JPY/KRW": "9.05",
                },
                "금리": {
                    "기준금리": "3.50%",
                    "국고채 3년": "3.20%",
                },
            },
            meta={"source": "dummy", "state_used": str(state)[:50] if state else "none"},
        )
