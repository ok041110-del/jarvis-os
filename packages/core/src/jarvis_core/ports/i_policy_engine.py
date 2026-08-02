"""IPolicyEngine — Port. Core는 이 Interface만 알고 Casbin/OPA 등 구현은 모른다."""
from abc import ABC, abstractmethod
from jarvis_core.policy.models import PolicyRequest, PolicyDecision


class IPolicyEngine(ABC):
    @abstractmethod
    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        raise NotImplementedError
