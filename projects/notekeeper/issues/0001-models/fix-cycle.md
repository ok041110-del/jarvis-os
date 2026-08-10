# Fix Cycle: Note dataclass field-ordering crash

## 실제로 재현된 결함

`validation.md`(첫 real Review)가 지적: `tags: list =
field(default_factory=list)`가 `created_at: str`보다 앞에 선언돼
있어, dataclass의 "기본값 없는 필드는 기본값 있는 필드보다 앞에
와야 한다" 규칙을 어긴다.

실제로 import해서 재현:

```
$ python3 -c "import notekeeper.models"
TypeError: non-default argument 'created_at' follows default argument
```

**모듈이 아예 import되지 않는다** — 이번 프로젝트 전체에서 발견된
결함 중 가장 심각한 등급(런타임 결함이 아니라 로드 자체가 불가능).

## Fix

원본 코드 + 실제 traceback을 그대로 `backend_agent_code_generation()`
(기존 Capability)에 입력해 재호출. 반환된 코드는 필드 순서를
`id, title, body, created_at, tags`로 바꿔 문제를 해소했다(`tags`가
유일하게 기본값을 가진 필드이므로 맨 뒤로).

## 검증

```
$ python3 -c "
import notekeeper.models as m
n = m.Note.new('Hello', 'World body')
d = n.to_dict()
n2 = m.Note.from_dict(d)
print(n == n2)"
True
```

재수정된 코드에 대한 두 번째 real Review는 이 버그를 더 이상
지적하지 않았고, 나머지 지적(타입 검증 부재, `id`/`created_at`
불변성 부재, `repr`이 `body` 전체를 노출)은 실제로 재현되지 않은
스타일/견고성 제안이라 반영하지 않았다.
