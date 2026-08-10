# Design: Add Note data model to notekeeper

## 설계 제안: `notekeeper.models.Note`

### 접근 방식
`models.py`는 단일 책임만 진다 — "메모라는 개념을 표준 라이브러리만으로 값 객체로 표현하고, dict 형태로 왕복 변환 가능하게 만드는 것". 저장소나 API에 대한 지식은 이 모듈에 전혀 들어가지 않는다. `@dataclass`로 5개 필드를 그대로 선언하고, 생성 로직(`new`)과 직렬화 로직(`to_dict`/`from_dict`)을 각각 별도 메서드로 분리해 "필드 정의"와 "생성 정책"과 "직렬화 형식"을 서로 독립적으로 바꿀 수 있게 한다.

### 책임 분리
- **필드 선언부**: 데이터 셰이프만 표현. 기본값은 `tags` 한 곳에만 존재하며 반드시 `field(default_factory=list)`로 선언해 인스턴스 간 리스트 공유를 원천 차단한다. `id`, `created_at`은 dataclass 필드 자체에는 기본값을 주지 않아, "필드 정의만으로는 유효한 Note가 안 만들어진다"를 강제하지 않되, 직접 생성자 호출(`Note(id=..., title=..., ...)`)도 여전히 허용해 `from_dict`가 이를 재사용할 수 있게 한다.
- **`Note.new(title, body, tags=None)`**: 유일한 "신규 생성" 경로. `uuid4()` 문자열과 `datetime.now(timezone.utc)`를 여기서만 생성한다. `tags`가 `None`이면 새 빈 리스트를, 값이 주어지면 그 값을 그대로 참조하지 않고 `list(tags)`로 복사해 저장한다 — 호출자가 넘긴 리스트를 나중에 mutate해도 Note 내부 상태가 오염되지 않도록 방어한다.
- **`to_dict()`**: dataclass 필드를 dict로 펼치되, `tags`는 얕은 복사(`list(self.tags)`)로 내보내 반환된 dict를 수정해도 원본 Note에 영향이 없게 한다.
- **`from_dict(data)`**: `data`의 5개 키를 그대로 필드에 매핑해 새 `Note`를 만든다. 이때도 `tags`는 복사해서 저장. 알 수 없는 키는 무시할지 에러를 낼지 결정이 필요한데, 요구사항이 검증 로직을 범위 밖으로 뒀으므로 "필요한 키만 뽑아서 쓰고 나머지는 무시" — `data[k] for k in (...)` 방식으로 구현해 초과 키에 관대하게, 누락 키에는 자연스러운 `KeyError`가 나도록 한다(별도 커스텀 예외는 만들지 않음).

### 시간 포맷 결정
`created_at`은 `datetime.now(timezone.utc).isoformat()`로 생성한다. 이 방식은 `+00:00` 접미사가 붙는 형태(`2026-08-10T12:34:56.789012+00:00`)가 되며, `datetime.fromisoformat()`으로 다시 파싱 가능하다는 장점이 있다. `Z` 접미사 대신 `+00:00`을 택하는 이유는 표준 라이브러리 왕복(파싱 필요 시)에 별도 후처리가 필요 없기 때문이다. 다만 이번 스코프에서는 `created_at`을 문자열로만 다루고 실제로 다시 `datetime`으로 파싱하는 로직은 넣지 않으므로, 이 결정은 "향후 파싱 코드가 추가될 때 마찰이 적은 포맷을 미리 선택해둔다"는 정도의 의미다.

### 왕복 동등성 보장
dataclass는 필드 값 기준 `__eq__`를 자동 생성하므로, `Note.from_dict(note.to_dict()) == note`가 성립하려면 `to_dict`/`from_dict`가 타입을 보존하기만 하면 된다 (`tags`가 항상 `list`로 유지되는 한 문제 없음). 별도의 `__eq__` 커스터마이징은 필요 없다.

### 리스크 및 대응
- **mutable default**: `field(default_factory=list)` + `new()`/`from_dict()` 양쪽에서 `list(tags)` 복사로 이중 방어.
- **시간대 포맷 불일치**: `isoformat()` 사용을 통일하고, 별도 포맷 유틸을 만들지 않음으로써 포맷 분기 지점을 하나로 최소화.
- **id 검증 부재**: 요구사항대로 범위 밖으로 명시. 다만 `from_dict`가 임의 문자열 id를 받아들이는 것은 의도된 유연성(예: 마이그레이션, 테스트 픽스처)으로 문서화.
- **확장성**: `updated_at`, `owner` 등 향후 필드는 이번 설계에 영향 없이 dataclass 필드 추가 + `to_dict`/`from_dict` 매핑 갱신만으로 확장 가능한 구조이므로 별도 훅을 미리 만들 필요는 없다고 판단.

이 설계로 진행해도 괜찮은지 확인해주시면 `models.py` 구현으로 넘어가겠습니다.

