"""IPolicyEngine — Port. Core는 이 Interface만 알고 Casbin/OPA 등 구현은 모른다."""
from abc import ABC, abstractmethod
from jarvis_core.policy.models import PolicyRequest, PolicyDecision


class IPolicyEngine(ABC):
    @abstractmethod
    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        """허용/거부를 판단해 반환한다(PDP). 절대 예외를 던지지 않는다.

        Fail-Closed 계약(ADR-0005 결정 4): 구현체 내부에서 어떤 오류가 나든
        (정책 파일 파싱 실패, 백엔드 연결 불가 등) 이를 잡아
        `PolicyDecision(allow=False, ...)`로 변환해 반환해야 한다. 호출자(PEP)는
        이 메서드가 항상 값을 반환한다고 가정하며, try/except로 방어하지 않는다.
        """
        raise NotImplementedError
