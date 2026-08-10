# Planning: Add Note data model to notekeeper

## 요구사항 분석: notekeeper `Note` 데이터 모델 추가

**목표**
notekeeper 프로젝트에 메모 한 건을 표현하는 최소한의 데이터 모델을 도입하는 것이 목표다. 외부 의존성 없이 Python 표준 라이브러리(`dataclasses`, `uuid`, `datetime`)만으로 `models.py`에 `Note`를 정의하여, 이후 저장소(파일/DB) 계층이나 API 계층이 이 모델을 기반으로 메모를 생성·직렬화·역직렬화할 수 있도록 하는 것이 핵심 가치다.

**범위**
- `Note`는 `id: str`, `title: str`, `body: str`, `tags: list[str]`, `created_at: str`(ISO 8601 UTC) 5개 필드를 갖는 `@dataclass`.
- 생성 편의를 위한 클래스 메서드 `Note.new(title, body, tags=None)`:
  - `id`는 `uuid4()` 기반으로 매 호출마다 새로 생성.
  - `created_at`은 호출 시점의 UTC 시각을 ISO 8601 문자열로 자동 채움.
  - `tags`가 `None`이면 빈 리스트를 새로 만들어 저장(모든 인스턴스가 동일 리스트 객체를 공유하는 mutable default 버그를 피해야 함).
- 직렬화 왕복을 위한 `to_dict()` / `from_dict(data)`: `Note.from_dict(note.to_dict())`가 원본과 값이 동일한 `Note`를 재구성해야 하며, 이는 JSON 저장/전송을 염두에 둔 요구.
- 이번 범위는 데이터 모델 정의에 한정되며, 파일 I/O, 영속성 계층, 수정(update)/삭제 메서드, 유효성 검증 로직, CLI나 API 엔드포인트는 포함하지 않는다.

**리스크 및 유의점**
- **Mutable default 함정**: `tags: list[str]`를 dataclass 필드로 선언할 때 `field(default_factory=list)`를 쓰지 않으면 인스턴스 간 리스트가 공유되는 전형적 버그가 발생할 수 있음 — 요구사항에서도 명시적으로 경고하고 있다.
- **시간대 처리**: "UTC"와 "ISO 8601"을 동시에 만족해야 하므로, naive datetime을 쓰는지 aware datetime(`timezone.utc`)을 쓰는지에 따라 `created_at` 문자열의 형식(`Z` 접미사 유무, `+00:00` 포함 여부)이 달라질 수 있다. 왕복 직렬화 시 문자열 포맷이 파싱 가능한 형태로 일관되게 유지되어야 한다.
- **왕복 동등성(round-trip equality)**: `to_dict`/`from_dict`가 값 기준으로 원본과 동일해야 한다는 요구는, 필드 순서·타입 변환(특히 `tags` 리스트가 원본과 별개 객체인지, 값만 같은지)까지 신경 써야 함을 의미한다. 부주의하게 구현하면 `list`가 아닌 다른 시퀀스 타입으로 역직렬화되거나, 알 수 없는 키가 섞인 `dict`를 넘겼을 때 예외 처리가 불명확해질 수 있다.
- **id 충돌/검증 부재**: `id`가 항상 `new()`를 통해서만 생성된다는 보장이 없다면(예: `from_dict`로 임의의 `id` 문자열이 들어올 경우) uuid 형식 검증이 없다는 점이 잠재적 리스크이나, 요구사항상 검증 로직은 범위 밖으로 보인다.
- **확장성 여유 부족**: 현재 스펙은 단일 파일·단일 클래스로 매우 단순하지만, 추후 메모 수정 시각(`updated_at`), 소유자, 버전 관리 등이 필요해질 경우 이번 설계가 확장 지점을 어떻게 열어둘지는 별도 논의가 필요하다(이번 요구사항에는 포함되지 않음).

이 분석에 동의하면 실제 `models.py` 구현으로 진행할 수 있다.

