"""Stage 2 — Intent Recognition. Request_Processing_Kernel_v1.md 참고.

PoC 규모의 최소 구현: 실제 NLU 모델 없이, 텍스트 길이/공백 여부로만
confidence를 매긴다. 이건 기능 품질(Won't 항목)이 아니라 "Kernel이 모호한
입력을 다음 단계로 넘기지 않고 여기서 걸러낸다"는 아키텍처 동작을 보여주기
위한 최소 규칙일 뿐이다.
"""
from .models import Intent

CONFIDENCE_THRESHOLD = 0.3


def recognize(raw_text: str) -> Intent:
    text = raw_text.strip()
    if not text:
        return Intent(raw_text=raw_text, primary_intent="", entities=[], confidence=0.0)
    tokens = text.split()
    confidence = min(1.0, 0.4 + 0.1 * len(tokens))  # 아주 단순한 휴리스틱 (PoC 한정)
    return Intent(raw_text=text, primary_intent=text, entities=tokens, confidence=confidence)


def needs_clarification(intent: Intent) -> bool:
    return intent.confidence < CONFIDENCE_THRESHOLD
