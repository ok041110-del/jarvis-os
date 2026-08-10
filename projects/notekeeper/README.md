# NoteKeeper

Development HQ를 이용해 만든 세 번째 Dogfooding 프로젝트(Testbed)다.
`projects/textkit`(순수 함수 3개, 상태 없음)보다 실제로 더 복잡한
과제를 다룬다 — **데이터 모델 + 파일 기반 영속 저장소 + 검색 + CLI**로
이어지는 4개의 실제로 연결된 Issue를 통해, 상태(파일 I/O)가 있는
프로젝트에서 자연스럽게 발생하는 것(모델 → 저장소 → 검색 → CLI로
이어지는 다단계 의존, "찾음/못 찾음"·"파일 있음/없음/손상"류 조건
분기, Review 이후 실제 수정)을 관찰한다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용해 만든 결과물이다.** 이 디렉토리는 Development HQ
코드(`development-hq/mvp`)를 한 줄도 수정하지 않는다 —
`runner.py`가 그 안의 기존 함수를 import해서 순서대로 호출할 뿐이다.

## 무엇을 하는가

로컬 파일 기반 메모 관리 라이브러리+CLI(`src/notekeeper/`)를 Issue
4개로 나눠 만든다.

1. `models.py` — `Note` 데이터 모델(dataclass, `Note.new()`로 id/생성
   시각 자동 부여, `to_dict()`/`from_dict()` JSON 왕복)
2. `store.py` — `NoteStore`(JSON 파일 기반 영속 저장소): `add`/`get`/
   `delete`/`list`/`save`/`load`. 파일이 없을 때, 있을 때, 손상됐을
   때를 모두 다뤄야 한다.
3. `search.py` — `search_notes()`(제목/본문 부분 일치, 태그 일치,
   둘 다 지정 시 AND 결합)
4. `cli.py` — 위 세 모듈을 실제로 import해서 쓰는 argparse 기반 CLI
   (`add`/`list`/`show`/`search`/`delete` 서브커맨드, `--store PATH`로
   저장 위치 지정)

각 Issue는 `projects/textkit`와 동일한 흐름(Issue -> Project
Intelligence(선행 Issue 실제 코드를 Context로 포함) -> Planning ->
Design -> Implementation(code_generation) ->
src/notekeeper/<module>.py 저장 -> Validation
(`workflow_0002.run_mvp_0002` 재사용)}으로 실행되고, 결과를
`issues/<issue-id>/planning.md`, `design.md`, `implementation.md`,
`validation.md`로 저장한다.

Development HQ의 어떤 Capability도 파일을 쓰거나 테스트를 실행하지
않는다(Engine 호출은 여전히 상태 없는 text-in/text-out 함수다) —
`runner.py`가 실제 소스 파일을 쓰고, 사람이 `test_execution` 제안을
읽어 실제 pytest 코드로 옮겨 실행한다. `notekeeper` 자신의 JSON 파일
영속화는 이 프로젝트가 만드는 **제품 기능**이며, Development HQ 내부
Context 전달 메커니즘과는 무관하다 — IMPLEMENTATION_RULES.md의
"Memory Service(영속화 계층) 구현 금지"는 Development HQ 자신의 Task
간 Context 전달에 적용되는 규칙이며(In-memory 변수로만), 여기서
변경되지 않는다: `runner.py`가 각 Issue의 Context를 넘기는 방식은
여전히 in-memory 변수(`existing_files` 리스트, 문자열 결합)뿐이다.

## Out of Scope

- 새 Capability, Task Dispatcher 일반화, Runtime, Stage Runner,
  Pipeline Runner, Event Bus, Scheduler, Multi-Agent, Engine Adapter,
  Model Routing, Kernel Component, Production caller, Prompt Cache —
  모두 이번 프로젝트 범위 밖이다.
- 이 프로젝트는 Production caller 후보가 **아니다**. `runner.py`는
  `projects/development-hq-devkit/runner.py`·
  `projects/textkit/runner.py`와 정확히 같은 성격(검증 목적
  스크립트)이며, production 위치로 승격하려는 시도가 아니다.
- `core/execution_layer`를 참조하지 않는다.
- Git 자동 Commit, Pull Request 자동 생성 — Engine이나 runner가 하지
  않는다.
- 동시성/잠금(lock) — 단일 프로세스 사용을 전제한다.

## Development HQ Update Policy

`projects/development-hq-devkit/README.md`·`projects/textkit/README.md`와
동일: 이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는
근거로 쓰지 않는다. 반복 관찰된 뒤에만 Observation → Evidence Review
→ Governance 절차로 넘긴다. Observe First, Decide Later.
