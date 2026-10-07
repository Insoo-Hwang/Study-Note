# Virtual Stock Exchange — 구현 가이드

> 가상 증권 거래소를 **주문 → 체결 → 정산 → 조회**의 단일 흐름으로 구현하는 이직용 백엔드 포트폴리오.
> 자료구조, 동시성, 트랜잭션, 이벤트 정합성, 조회 최적화를 각각 **"문제 재현 → 개선 → 측정"** 경험으로 남긴다.
>
> 원칙: **면접에서 이야기할 문제가 생기지 않는 기능은 만들지 않는다.** `main`은 항상 실행 가능한 상태로 유지한다.

**사용법**: 아래 일정표에서 오늘 세션의 링크를 누른다 → 그 단계의 **오늘 할 일 / 구현 / 판단할 것 / 완료 기준**만 보고 작업한다. 설계 배경은 각 기능의 맨 위에, 전체 구조는 [전체 그림](#overview)에 있다.

---

<a id="schedule"></a>

# 일정표

10주 · 주 3~4회 · 회당 1~2시간. **D1~D3 필수, D4 선택(버퍼).** Week 4와 7은 넘치기 쉬우니 D4를 비워둔다. 진행 칸의 ☐를 ✅로 바꿔가며 쓴다.

### Week 1 — 셋업 · OrderBook

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 1.5h | [1. 프로젝트 셋업](#f1) | 앱 기동, `./gradlew test` · CI 통과 | ☐ |
| D2 · 1.5h | [2-1. Order 상태 전이](#f2-1) | 상태 전이 테스트 통과 | ☐ |
| D3 · 1.5h | [2-2. OrderBook 자료구조](#f2-2) | OrderBook 단위 테스트 통과 | ☐ |
| D4 | 버퍼 · ADR "OrderBook 자료구조 선택" | | ☐ |

### Week 2 — Matching · 주문 API

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 2h | [3-1. Matching Engine](#f3-1) | 체결 테스트 전부 통과 | ☐ |
| D2 · 1.5h | [3-2. 주문 취소 · 검증](#f3-2) | 부분 체결 후 잔량만 취소 | ☐ |
| D3 · 1.5h | [4. 주문 API + Lock 처리기](#f4) | HTTP로 SELL 10 → BUY 5 → 잔량 5 | ☐ |
| D4 | 버퍼 | | ☐ |

### Week 3 — 영속화 · 복구 · 동시성 검증

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 2h | [5-1. 체결 결과 저장](#f5-1) | DB == 메모리 | ☐ |
| D2 · 2h | [5-2. 재시작 복구 · Rebuild](#f5-2) | 재시작 후 미체결 주문 + FIFO 복원 | ☐ |
| D3 · 1.5h | [6. 동시성 테스트 · 불변식 검증기](#f6) | Lock 제거 시 실패 재현 기록 | ☐ |
| D4 | 버퍼 · ADR "Source of Truth" | | ☐ |

### Week 4 — Single Writer · 측정 `🏷 v0.1-trading`

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 2h | [7-1. Single Writer](#f7-1) | 두 모드 데모 통과, Queue 가득 → 503 | ☐ |
| D2 · 1.5h | [7-2. 호가 Snapshot](#f7-2) | 두 모드 불변식 통과, 호가 Level 집계 | ☐ |
| D3 · 2h | [7-3. 측정: Lock vs Single Writer](#f7-3) | benchmarks 기록 + Tag | ☐ |
| D4 | **비워둘 것** · 여유 시 JMH | | ☐ |

### Week 5 — 계좌 · 예약 · 정산

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 1.5h | [8-1. 계좌 · 보유주식 도메인](#f8-1) | 도메인 단위 테스트 통과 | ☐ |
| D2 · 2h | [8-2. 자산 예약 · 해제](#f8-2) | 주문 → 예약, 취소 → 해제 | ☐ |
| D3 · 2h | [8-3. 정산 (동기)](#f8-3) | 체결 → 돈 · 주식 이동, 가격 개선 차액 해제 | ☐ |
| D4 | 버퍼 · ADR "예약 위치" | | ☐ |

### Week 6 — Lock · Deadlock `🏷 v0.2-account`

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 1.5h | [9-1. 초과 예약 재현 → Pessimistic Lock](#f9-1) | Lock 전 실패 기록 / Lock 후 통과 | ☐ |
| D2 · 1.5h | [9-2. Deadlock 재현 → Lock 순서](#f9-2) | 정렬 전 Deadlock 기록 / 정렬 후 통과 | ☐ |
| D3 · 1.5h | [9-3. 자산 불변식 · 트랜잭션 범위](#f9-3) | 전체 불변식 통과 + Tag | ☐ |
| D4 | 선택: Optimistic 실측 | | ☐ |

### Week 7 — Kafka `🏷 v0.3-event`

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 2h | [10-1. Outbox + Kafka 발행](#f10-1) | 체결 → Outbox → 토픽 도착 | ☐ |
| D2 · 1.5h | [10-2. Settlement Consumer](#f10-2) | 체결 → 잠시 후 계좌 반영 | ☐ |
| D3 · 2h | [10-3. Idempotency · Kafka 장애](#f10-3) | 중복 1회 반영, Kafka 중단 후 복구 + Tag | ☐ |
| D4 | **비워둘 것** | | ☐ |

### Week 8 — 체결 내역 조회

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 1.5h | [11-1. Offset 조회 + 대량 데이터](#f11-1) | 100만 건 적재, API 동작 | ☐ |
| D2 · 2h | [11-2. 측정: EXPLAIN + Index](#f11-2) | 조건 / 수치 / Plan 기록 | ☐ |
| D3 · 1.5h | [11-3. Cursor Pagination](#f11-3) | 중복·누락 없음, Offset vs Cursor 기록 | ☐ |
| D4 | 선택: 500만 건, Index INSERT 비용 | | ☐ |

### Week 9 — Redis · 통합 `🏷 v1.0`

| 세션 | 오늘 구현할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 2h | [12-1. Redis 현재가](#f12-1) | 체결 → 현재가 반영, 값 없음 → DB | ☐ |
| D2 · 1.5h | [12-2. Redis 장애 격리 + 측정](#f12-2) | Redis 중지에도 주문 정상, DB vs Redis 기록 | ☐ |
| D3 · 1.5h | [13-1. 통합 테스트](#f13-1) | 전체 흐름 한 테스트 통과 + Tag | ☐ |
| D4 | 버퍼 | | ☐ |

### Week 10 — 면접 준비 (새 기능 없음)

| 세션 | 오늘 할 것 | 완료 기준 | 진행 |
|---|---|---|---|
| D1 · 2h | [13-2. README](#f13-2) | README 완성 | ☐ |
| D2 · 1.5h | [13-3. 면접 답변](#f13-3) | 핵심 질문 · AI 질문 2분 답변 | ☐ |
| D3 · 1.5h | [13-4. 손코딩 · 데모 리허설](#f13-4) | 손코딩 3개 · 데모 3분 | ☐ |
| D4 | 선택 과제 회수 (JMH → Optimistic 실측 → 500만 건) | | ☐ |

### 일정이 밀릴 때

```text
Week 2 끝 속도 점검  → devlog에 적은 실제 소요 시간 합 ÷ 계획 시간 합
                       1.5배를 넘으면 아래 컷을 미리 적용하고, 남은 일정을 그 비율로 다시 본다
                       (밀린 걸 Week 10에서 메우려 하지 않는다)
1주 이내 지연        → 그 주 D4로 흡수
Week 4 끝에 미완     → 100,000건 측정 빼고 Tag
Week 7 Kafka 막힘    → v0.2-account(동기 정산)로 두고 Week 8 진행 (Kafka 의존 없음)
                       Week 9 현재가는 커밋 후 Spring ApplicationEvent로 대신
Week 9 부족          → 통합 테스트를 핵심 시나리오 1개로 축소
Week 10은 줄이지 않는다 — 면접 준비가 이 프로젝트의 목적이다

절대 빼지 않는 것    → 불변식 테스트, Lock 제거 시 실패 재현, Deadlock 재현, 측정 3종, ADR
```

---

<a id="rules"></a>

# 매 세션 규칙

## 세션 루틴

```text
[시작 5분]      지난 devlog의 "다음 할 일" 확인 → 일정표에서 오늘 단계 열기
[노트 10~15분]  단계의 "학습 노트" 중 ★ 표시된 절만 읽기 (나머지는 막힐 때 · 면접 전에)
[설계 15분]     "판단할 것"부터 결정 (필요하면 ADR 초안)
[구현 40~80분]
[마무리 10분]   테스트 green → 커밋 → devlog + ai-log 한 줄 → 일정표 ☐ → ✅
```

## 기록 파일 (1. 셋업에서 만든다)

```text
docs/devlog.md        세션마다: 한 것 / 결정한 것 / 막힌 것 / 다음 할 일
docs/decisions/       ADR — 판단이 필요했던 것마다 1개 (문제 / 대안 / 선택 / 이유)
docs/benchmarks.md    측정 조건 / 수치 / 해석
docs/ai-log.md        AI를 쓴 세션마다 한 줄 (형식은 면접 준비 > AI 활용 질문)
```

이 네 파일이 README와 면접 답변의 재료가 된다.

## AI에게 맡길 것 vs 직접 할 것

```text
직접 = 실제 로직 + 커리어상 내가 성장하는 부분
       (처음 다루는 기술의 핵심 사용법 포함: 동시성, Kafka Producer/Consumer, Redis 연동)
AI   = 단순 노동
       (설정 파일, 반복 코드, 정해진 형식의 스크립트, 이미 한 번 직접 짠 것의 변형)

애매하면: "면접에서 이 코드를 설명하라고 하면 내가 짠 것처럼 말해야 하나?" → Yes면 직접
```

| AI | 직접 |
|---|---|
| build.gradle, docker-compose, application.yml | OrderBook, Matching, 상태 전이 |
| DTO, Controller, 예외 핸들러, Entity/Repository | 예약 · 정산 금액 계산 |
| Flyway DDL · 시드 초안 (제약 조건은 내가 검토) | 트랜잭션 경계, Lock 순서, 멱등 처리 순서 |
| 테스트 케이스 목록 초안, 테스트 골격 | 테스트 기대값, 불변식 정의 |
| 내가 짠 동시성 실행기의 변형 | Worker/Queue, 첫 동시성 실행기 |
| 데이터 생성 SQL, k6 스크립트, 결과 표 | Kafka Producer/Consumer, Outbox Publisher, Redis 연동 |
| 내가 짠 코드 리뷰, 면접관 역할 | 정책 결정, 측정 결과 해석 |

작업 규칙:

```text
1. 핵심 로직: 내가 먼저 짠다 → AI에게 "버그와 엣지 케이스만 지적해줘, 수정 코드는 주지 마"
2. 반복 코드: AI가 짠다 → 한 줄씩 설명할 수 있을 때만 커밋
3. AI 코드와 내 핵심 로직은 커밋을 나눈다 → git 이력이 AI 활용 범위의 증거가 된다
4. 30분 이상 막히면 AI에게 원인 후보를 묻고, 이해한 뒤 devlog에 기록
```

---

<a id="overview"></a>

# 전체 그림 (참고용)

## 흐름

```text
Client
  │ POST /orders
  ▼
Order API ── 검증 + 자산 예약 (계좌 Row Lock, 짧은 트랜잭션 — 8-2에서 A안을 고른 경우)
  │
  ▼ 종목별 Bounded Queue
Matching Worker (종목별 Single Writer)
  │ 1. 메모리 OrderBook에서 Matching
  │ 2. 하나의 DB 트랜잭션: Order / Trade 저장 + Outbox INSERT
  │ 3. 호가 Snapshot 갱신 → 응답
  ▼
Outbox Publisher ──▶ Kafka  [topic: trade-executed, key: stockCode]
                        ├── Settlement Consumer  (group: settlement)  → 계좌 · 보유주식 반영 (멱등)
                        └── MarketData Consumer  (group: market-data) → Redis 현재가 갱신

조회
  호가        ← Worker가 발행한 메모리 Snapshot
  체결 내역   ← DB (복합 Index + Cursor)
  현재가      ← Redis (장애 시 DB Fallback)
  계좌        ← DB
```

| 영역 | 면접에서 보여줄 것 | 기능 |
|---|---|---|
| 체결 | 자료구조 선택, Price-Time Priority | [2](#f2), [3](#f3) |
| 동시성 | Lock → Single Writer 전환과 측정 | [4](#f4), [6](#f6), [7](#f7) |
| 영속화 | Source of Truth, 장애 복구 | [5](#f5) |
| 자산 | 예약 · 정산 정합성, Deadlock 방지 | [8](#f8), [9](#f9) |
| 이벤트 | 발행 신뢰성과 중복 안전성 | [10](#f10) |
| 조회 | 대용량 조회 개선과 장애 격리 | [11](#f11), [12](#f12) |

## 만들지 않는 것

판단 기준: **이 기능을 만들면서 면접에서 말할 문제(정합성, 동시성, 성능, 장애)가 생기는가?**

| 제외 | 이유 | 대신 |
|---|---|---|
| 종목 생성/조회 API, 종목 거래 상태 | 순수 CRUD | Flyway 시드 |
| 계좌 생성 / 입금 / 주식 입고 API | 핵심은 예약 · 정산 | 시드 / 테스트 Fixture |
| 계좌별 주문 · 체결 목록 API | 단순 조회, 조회 최적화는 체결 내역에서 다룸 | — |
| 호가 단위(Tick Size) 검증 | 산수 검증 | — |
| 자전거래 방지 | 도메인 규칙일 뿐 기술 문제로 이어지지 않음 | — |
| 시장가 / IOC / FOK / 공매도 | 매칭 규칙만 늘어남 | — |
| SSE 실시간 시세 | 연결 관리라는 별도 문제로 범위만 커짐 | 현재가 API |
| 호가 Snapshot Kafka 이벤트 | Throttle · 직렬화 부가 작업이 큼 | 메모리 Snapshot |
| 최근 체결 · 종목 정보 Redis 캐시 | Cursor 첫 페이지와 같음 / 캐시할 부하 없음 | — |
| PriorityQueue · Optimistic Lock 실측 | 결론이 정해져 있음 | ADR (실측은 선택) |
| 결제망, 증거금, 신용, 배당, VI 등 | 금융 시스템 복제가 목적이 아님 | — |

## 기술 스택

```text
Java 21, Spring Boot 3.x, Spring Web, Spring Data JPA, PostgreSQL, Flyway
Kafka (KRaft 단일 노드), Redis
JUnit 5, Testcontainers, Awaitility, k6, JMH(선택)
Gradle, Docker Compose
```

| 기술 | 쓰는 곳 | 쓰지 않는 곳 | 들어오는 시점 |
|---|---|---|---|
| Kafka | `trade-executed` 토픽 1개 | 주문 접수, 호가 | Week 7 |
| Redis | 현재가 1종 | 호가, 체결 내역, 종목 정보, 분산 락 | Week 9 |

## 패키지 구조 (Modular Monolith)

```text
exchange
├── trading      주문, OrderBook, Matching, Worker, 체결 내역 조회
├── account      계좌, 보유주식, 예약, Settlement
├── market       현재가 (MarketData Consumer, Redis)
├── outbox       Outbox 저장 / Publisher
└── common
각 패키지: domain / application / infrastructure / presentation
```

## 도메인 모델

```java
class Stock    { String code; String name; }                       // Flyway 시드

class Order {
    Long id; Long accountId; String stockCode;
    OrderSide side;            // BUY, SELL
    long price; long quantity; long remainingQuantity;
    OrderStatus status;        // OPEN, PARTIALLY_FILLED, FILLED, CANCELLED
    long sequence;             // 종목별 단조 증가, 같은 가격 FIFO 기준, DB에 저장
    LocalDateTime createdAt;
}

class Trade {
    Long id; String stockCode;
    Long buyOrderId; Long sellOrderId;
    Long buyerAccountId; Long sellerAccountId;
    long buyOrderPrice;        // 가격 개선 차액 해제용
    long price;                // 체결가 = Resting Order 가격
    long quantity; LocalDateTime executedAt;
}

class Account  { Long id; long balance; long reservedBalance; }        // available = balance - reserved
class Position { Long id; Long accountId; String stockCode;
                 long quantity; long reservedQuantity; }              // available = quantity - reserved
```

가격과 금액은 `long`(원 단위 정수). 곱셈은 `Math.multiplyExact`로 overflow를 막는다.

## API

```http
POST   /orders                                {accountId, stockCode, side, price, quantity}
GET    /orders/{orderId}
DELETE /orders/{orderId}

GET /stocks/{stockCode}/orderbook
GET /stocks/{stockCode}/trades?cursor=&size=
GET /stocks/{stockCode}/price

GET /accounts/{accountId}                     잔고 / 예약금 / 보유 종목
```

## 측정 3종

| 실험 | 비교 | 대응 질문 | 단계 |
|---|---|---|---|
| 체결 동시성 | Lock vs Single Writer | Lock과 Single Writer 차이는? | [7-3](#f7-3) |
| 체결 내역 조회 | Offset vs Cursor, Index 전후 | 대용량 조회를 어떻게 최적화했나? | [11-2](#f11-2), [11-3](#f11-3) |
| 현재가 조회 | DB vs Redis | Redis를 왜 썼나? | [12-2](#f12-2) |

수치가 예상과 달라도 괜찮다. **왜 그렇게 나왔는지 설명하는 것**이 핵심이다. 기록은 `docs/benchmarks.md`에 조건 / 수치 / 해석으로 남긴다.

## Flyway · Git Tag

```text
V1__create_stock_order_trade.sql      (종목 시드)              ← 5-1
V2__create_account_position.sql       (데모 계좌 · 보유 시드)   ← 8-1
V3__create_outbox_processed_event.sql                          ← 10-1
V4__add_trade_indexes.sql                                      ← 11-2
이미 커밋한 마이그레이션은 수정하지 않고 새 버전을 추가한다

v0.1-trading   Week 4   체결 엔진 + Single Writer + 측정
v0.2-account   Week 6   예약 + 동기 정산 + Lock       ← Kafka에서 막혀도 돌아갈 지점
v0.3-event     Week 7   Kafka + Outbox + Idempotency
v1.0           Week 9   조회 최적화 + Redis + 통합 테스트
```

---

# 기능 상세

각 단계는 같은 형식이다.

```text
목표            오늘 끝나면 무엇이 되는가 (한 줄)
학습 노트       Study-Note에서 관련된 절. ★ = 작업 전에 먼저 읽기, 나머지는 참고
할 일           순서대로. [직접] = 내가 짠다, [AI] = AI에게 맡긴다
판단할 것       코드를 짜기 전에 정할 것. 큰 결정은 ADR
결과물          세션이 끝났을 때 저장소에 있어야 하는 것 (코드 / 테스트 / 기록)
이렇게 나오면 성공   실제로 확인했을 때 보여야 하는 출력
완료 기준       체크리스트. 다 체크되면 커밋하고 일정표 ✅
```

클래스 이름은 예시다. 바꿔도 되지만 한 번 정하면 끝까지 유지한다. 기본 패키지는 `exchange`로 가정한다.

---

<a id="f1"></a>

## 1. 프로젝트 셋업 `W1-D1 · 1.5h`

**목표**: 앞으로 10주 동안 쓸 뼈대. 앱이 뜨고, 실제 PostgreSQL(Testcontainers) 위에서 테스트가 돈다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [단위-통합-테스트 › 컨텍스트를 하나로 모으는 기반 클래스](../../10-테스트-운영/단위-통합-테스트/단위-통합-테스트.md#컨텍스트를-하나로-모으는-기반-클래스) — `IntegrationTestSupport`가 바로 이것
- ★ [Mock-SpringTest-Testcontainers › Testcontainers — 진짜를 띄운다](../../10-테스트-운영/Mock-SpringTest-Testcontainers/Mock-SpringTest-Testcontainers.md#testcontainers--진짜를-띄운다) — H2 대신 실제 PostgreSQL로 테스트하는 이유
- [Mock-SpringTest-Testcontainers › Testcontainers는 컨테이너를 재사용한다](../../10-테스트-운영/Mock-SpringTest-Testcontainers/Mock-SpringTest-Testcontainers.md#testcontainers는-컨테이너를-재사용한다) — 테스트가 느려질 때 다시 보기
- [Spring-Boot와-예외처리 › 환경별 설정 분리](../../05-Spring/Spring-Boot와-예외처리/Spring-Boot와-예외처리.md#환경별-설정-분리) — `application.yml` / `application-test.yml` 나누기
- [03-Docker-Compose › depends_on 과 healthcheck](../../infra/03-Docker-Compose/03-Docker-Compose.md#depends_on-과-healthcheck) — `docker compose ps`의 (healthy)가 무슨 뜻인지
- [02-Docker › Port Mapping](../../infra/02-Docker/02-Docker.md#port-mapping) — `localhost:5432`로 컨테이너 DB에 붙는 원리
- [07-CI-CD › Workflow](../../infra/07-CI-CD/07-CI-CD.md#workflow) — `ci.yml`의 on / jobs / steps 구조

**할 일**

1. [AI] Spring Boot 3.x / Java 21 / Gradle 프로젝트 생성 — 의존성: Web, Data JPA, Validation, Flyway, PostgreSQL Driver, Testcontainers(PostgreSQL, JUnit), Awaitility
2. [AI] `docker-compose.yml` — PostgreSQL 16 하나만 (Kafka/Redis는 Week 7, 9에 추가)
3. [AI] `application.yml`(local) / `application-test.yml`(test) — DB 접속, `spring.jpa.hibernate.ddl-auto=validate`, Flyway 활성화
4. [AI] 통합 테스트 베이스 `IntegrationTestSupport` — Testcontainers PostgreSQL + `@ServiceConnection`
5. [AI] 패키지 생성: `trading / account / market / outbox / common`, 각각 `domain / application / infrastructure / presentation`
6. [직접] `docs/devlog.md`, `docs/decisions/`, `docs/benchmarks.md`, `docs/ai-log.md` 생성, `git init` 후 첫 커밋
7. [AI] `.github/workflows/ci.yml` — push마다 `./gradlew test` (GitHub Actions 우분투 러너는 Docker가 있어 Testcontainers가 그대로 돈다). README 맨 위 CI 배지는 W10에서
8. [직접] GitHub 저장소(public)에 push → Actions가 초록인지 확인
9. [직접] AI가 만든 build.gradle, yml, ci.yml을 한 줄씩 읽고 모르는 설정은 devlog에 메모

**판단할 것**

- Lombok 사용 여부 (쓴다면 `@Data`는 금지, `@Getter` 정도만 — 도메인 객체의 setter를 막기 위해)
- `ddl-auto=validate`로 두는 이유: 스키마는 Flyway만 바꾼다
- CI를 첫날 넣는 이유: "main은 항상 실행 가능"을 말이 아니라 초록 배지로 증명한다. 면접관이 저장소를 열었을 때 가장 먼저 보는 신호 중 하나다

**결과물**

- 코드: `build.gradle`, `docker-compose.yml`, `application.yml`, `application-test.yml`, `.github/workflows/ci.yml`, `ExchangeApplication`, 빈 패키지 구조
- 테스트: `IntegrationTestSupport`, `ExchangeApplicationTests.contextLoads()`
- 기록: `docs/` 파일 4개, devlog 첫 줄, ai-log 첫 줄 (셋업을 AI에게 맡겼으므로)

**이렇게 나오면 성공**

```text
$ docker compose up -d && docker compose ps
NAME         SERVICE    STATUS
postgres     postgres   running (healthy)

$ ./gradlew bootRun
... Started ExchangeApplication in 2.3 seconds

$ ./gradlew test
ExchangeApplicationTests > contextLoads() PASSED
BUILD SUCCESSFUL
```

**완료 기준**

- [ ] `docker compose up` 후 `bootRun`이 에러 없이 뜬다
- [ ] `./gradlew test`가 Testcontainers로 PostgreSQL을 띄워 통과한다
- [ ] `docs/` 4개 파일과 첫 커밋이 있다
- [ ] GitHub Actions CI가 초록이다

[↑ 일정표](#schedule)

---

<a id="f2"></a>

## 2. 주문 도메인 & OrderBook

**왜**: "왜 이 자료구조를 선택했나요?"에 답하기 위한 기능. 면접에서 화이트보드로 다시 짜라고 할 수 있는 부분이라 전부 직접 짠다.

**설계**

```java
class OrderBook {
    NavigableMap<Long, Deque<Order>> bids;   // 매수: 높은 가격 우선
    NavigableMap<Long, Deque<Order>> asks;   // 매도: 낮은 가격 우선
    Map<Long, OrderLocation> orderIndex;     // orderId → side / price
}
```

| 자료구조 | 해결하는 문제 | 비용 |
|---|---|---|
| `TreeMap<Price, …>` | 가격 Level 정렬, 최우선 가격 접근 (`bids.lastEntry()`, `asks.firstEntry()`) | 삽입/삭제 O(log P) |
| `Deque<Order>` | 같은 가격 안에서 시간 우선(FIFO) | 앞에서 꺼내기 O(1) |
| `HashMap orderIndex` | 취소 시 주문 위치를 바로 찾기 | 메모리 추가 |

```text
면접 포인트
왜 PriorityQueue가 아니라 TreeMap + Deque인가?
  → PriorityQueue는 임의 주문 삭제가 O(N), 가격 Level 단위 집계(호가)가 어렵다
왜 HashMap Index를 하나 더 두었나? 메모리를 더 쓰는 대신 어떤 시간을 줄였나?
```

<a id="f2-1"></a>

### 2-1. Order 상태 전이 `W1-D2 · 1.5h`

**목표**: 주문이 체결 · 취소되면서 상태가 바뀌는 규칙을 Order 객체 하나에 가둔다. 이후 모든 기능이 이 규칙을 믿고 쓴다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [JDBC-MyBatis-JPA › 영속성 컨텍스트 — JPA의 심장](../../07-트랜잭션-데이터접근/JDBC-MyBatis-JPA/JDBC-MyBatis-JPA.md#영속성-컨텍스트--jpa의-심장) — Order를 Entity로 메모리에 오래 두면 생기는 문제 → 분리 판단 근거
- ★ [JDBC-MyBatis-JPA › 엔티티를 안전하게 설계하기](../../07-트랜잭션-데이터접근/JDBC-MyBatis-JPA/JDBC-MyBatis-JPA.md#엔티티를-안전하게-설계하기) — setter 없이 상태를 메서드로만 바꾸는 형태
- [Generic-Exception-Stream › 예외를 고르는 흐름](../../03-Java/Generic-Exception-Stream/Generic-Exception-Stream.md#예외를-고르는-흐름) — `IllegalArgumentException` vs `IllegalStateException`
- [객체지향-SOLID › 네 가지 기둥](../../03-Java/객체지향-SOLID/객체지향-SOLID.md#네-가지-기둥) — 캡슐화 — 상태 전이 규칙을 객체 안에 가두는 이유

**할 일**

1. [AI] `OrderSide`(BUY, SELL), `OrderStatus`(OPEN, PARTIALLY_FILLED, FILLED, CANCELLED) enum
2. [직접] `Order` 생성 팩토리 `Order.create(id, accountId, stockCode, side, price, quantity)` — 생성 시 `remainingQuantity = quantity`, `status = OPEN`. **id는 밖에서 받는다** (아래 판단)
3. [직접] `fill(long qty)` — `0 < qty <= remaining`이 아니면 `IllegalArgumentException`, 종료된 주문이면 `IllegalStateException`. 남은 수량에 따라 PARTIALLY_FILLED / FILLED
4. [직접] `cancel()` — OPEN, PARTIALLY_FILLED만 가능. 그 외 `IllegalStateException`
5. [직접] `remaining()`, `isFilled()`, `isActive()` 같은 조회 메서드
6. [AI] 상태 전이 테스트 케이스 "목록"만 뽑게 한다 → [직접] 기대값을 손으로 채워 `OrderTest` 작성
7. [AI] `Trade` 클래스 (필드만. 생성 로직은 3-1에서)

**판단할 것**

- 메모리 OrderBook에 들어갈 Order를 **JPA Entity로 쓸지, 순수 도메인 객체로 분리할지**
    - Entity 겸용: 코드가 적음 / 오래 메모리에 머무는 detached entity, dirty checking 혼동
    - 분리(추천): 매핑 코드 추가 / 엔진이 JPA와 무관해져 테스트와 측정이 쉬움
- **취소할 때 `remainingQuantity`를 0으로 만들지, 그대로 둘지**
    - 그대로 두는 것을 추천: "quantity - remaining = 체결 수량 합" 불변식이 유지되고, 8-2에서 해제할 예약 금액(remaining × price)을 바로 계산할 수 있다
- **주문 ID는 Matching 전에 정해져 있어야 한다** — `orderIndex`의 키, Trade의 `buyOrderId` / `sellOrderId`, HTTP 응답에 모두 필요하다. 그런데 DB 저장은 Matching **뒤에** 일어난다(5장). 그래서 DB IDENTITY(INSERT 때 부여)는 쓸 수 없다 → 2주차엔 `AtomicLong`, 5-1에서 DB 시퀀스로 바꾼다

**결과물**

- 코드: `trading.domain.Order`, `OrderSide`, `OrderStatus`, `Trade`
- 테스트: `OrderTest` (아래 케이스 전부)
- 기록: ADR-001 "도메인 객체와 JPA Entity 분리", devlog

**이렇게 나오면 성공**

```text
OrderTest
  ✔ 생성하면 OPEN, remaining = quantity
  ✔ 100주 중 30주 체결 → PARTIALLY_FILLED, remaining 70
  ✔ 이어서 70주 체결 → FILLED, remaining 0
  ✔ remaining보다 많이 체결 → IllegalArgumentException
  ✔ 0주 / 음수 체결 → IllegalArgumentException
  ✔ FILLED 주문에 fill → IllegalStateException
  ✔ PARTIALLY_FILLED 주문 cancel → CANCELLED, remaining 70 유지
  ✔ FILLED / CANCELLED 주문 cancel → IllegalStateException
```

**완료 기준**

- [ ] `OrderTest` 전부 통과
- [ ] Order에 public setter가 없다 (상태는 `fill` / `cancel`로만 바뀐다)

[↑ 일정표](#schedule)

<a id="f2-2"></a>

### 2-2. OrderBook 자료구조 `W1-D3 · 1.5h`

**목표**: 종목 하나의 호가창을 메모리에 들고, 최우선 주문을 O(log P)로 찾고, 임의 주문을 바로 찾아 지울 수 있다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [해시-트리-비교 › TreeMap — 비교하며 내려간다](../../01-복잡도-자료구조/해시-트리-비교/해시-트리-비교.md#treemap--비교하며-내려간다) — 가격 Level을 TreeMap으로 두는 근거 (O(log n))
- ★ [해시-트리-비교 › 경계 메서드 구분](../../01-복잡도-자료구조/해시-트리-비교/해시-트리-비교.md#경계-메서드-구분) — `firstEntry` / `lastEntry` / `pollFirstEntry` 차이
- ★ [Heap-PriorityQueue › Heap과 이진 탐색 트리(TreeMap)](../../01-복잡도-자료구조/Heap-PriorityQueue/Heap-PriorityQueue.md#heap과-이진-탐색-트리treemap) — "왜 PriorityQueue가 아닌가" 답변 재료
- [Collection-선택-기준 › `ArrayDeque` vs `PriorityQueue` vs `LinkedList`](../../01-복잡도-자료구조/Collection-선택-기준/Collection-선택-기준.md#arraydeque-vs-priorityqueue-vs-linkedlist) — 같은 가격 FIFO에 ArrayDeque를 쓰는 이유
- [탐색-정렬 › Comparable과 Comparator](../../02-알고리즘/탐색-정렬/탐색-정렬.md#comparable과-comparator) — bids를 `Comparator.reverseOrder()`로 둘 때
- [equals-hashCode › `==`와 `equals`](../../03-Java/equals-hashCode/equals-hashCode.md#와-equals) — `Deque.remove(order)`는 equals로 찾는다 — Order의 equals를 어떻게 둘지
- [Amortized-Analysis › 한눈에 보기](../../01-복잡도-자료구조/Amortized-Analysis/Amortized-Analysis.md#한눈에-보기) — ArrayDeque 뒤에 추가하는 비용이 평균 O(1)인 이유

**할 일**

1. [직접] `OrderLocation(OrderSide side, long price)` record
2. [직접] `OrderBook(String stockCode)` — `bids`, `asks`, `orderIndex` 필드
3. [직접] `add(Order)` — 해당 가격 Level의 Deque 뒤에 추가, `orderIndex`에 등록
4. [직접] `peekBestOpposite(OrderSide incomingSide)` — BUY가 들어오면 최저 매도의 맨 앞, SELL이면 최고 매수의 맨 앞. 없으면 `null`
5. [직접] `removeBest(Order)` — 최우선 Level 맨 앞 주문 제거, Level이 비면 Level 삭제, `orderIndex`에서도 제거
6. [직접] `remove(long orderId)` — `orderIndex`로 위치를 찾아 Deque에서 제거 → `Optional<Order>` 반환
7. [직접] 테스트 · 검증용 조회: `bestBidPrice()`, `bestAskPrice()`, `size()`, `levelsOf(side)` (가격 → 주문 id 목록)
8. [AI] 테스트 케이스 목록 생성 → [직접] 기대값 채워 `OrderBookTest`
9. [AI 리뷰] 완성 후 "빈 Deque가 남는 경우, orderIndex와 Book이 불일치하는 경우를 찾아줘. 수정 코드는 주지 마"

**판단할 것**

- bids를 자연 정렬 + `lastEntry()`로 할지, `Comparator.reverseOrder()` + `firstEntry()`로 할지
- 빈 Level 삭제 시점: 제거할 때 바로 (추천) vs 조회할 때 정리

**결과물**

- 코드: `trading.domain.OrderBook`, `OrderLocation`
- 테스트: `OrderBookTest`
- 기록: ai-log에 AI 리뷰 결과 (지적 / 반영 / 기각), devlog

**이렇게 나오면 성공**

```text
OrderBookTest
  ✔ BUY 69,900 / 70,100 / 70,000 추가 → bestBidPrice = 70,100
  ✔ SELL 70,300 / 70,100 / 70,200 추가 → bestAskPrice = 70,100
  ✔ 같은 가격 BUY A, B, C 순서로 추가 → peekBestOpposite(SELL) = A
  ✔ B를 remove(orderId) → 70,000 Level = [A, C]
  ✔ Level의 마지막 주문 제거 → 그 가격 Level 자체가 사라진다
  ✔ 없는 orderId remove → Optional.empty
  ✔ 어떤 조작 순서든 orderIndex.size() == Book 안 주문 수
```

**완료 기준**

- [ ] `OrderBookTest` 전부 통과
- [ ] 빈 Deque가 남는 경로가 없다
- [ ] 셀프 체크: "왜 PriorityQueue가 아닌가"를 30초 안에 말할 수 있다

[↑ 일정표](#schedule)

---

<a id="f3"></a>

## 3. Matching & 취소

**왜**: Price-Time Priority와 부분 체결을 정확히 구현했는지가 체결 엔진의 핵심.

**설계**

```text
체결 조건: BUY 가격 >= SELL 가격
체결 가격: 먼저 OrderBook에 있던 Resting Order의 가격

예시
SELL  70,000 10주 / 70,000 20주 / 70,100 30주
신규 BUY  70,000 25주
→ 첫 SELL 10주 전량 체결
→ 두 번째 SELL 15주 부분 체결 (잔량 5주)
→ BUY 25주 전량 체결
→ 70,100 SELL은 가격 조건이 맞지 않아 그대로
```

```java
while (incoming.hasRemainingQuantity()) {
    Order resting = book.peekBestOpposite(incoming.side());
    if (resting == null || !canMatch(incoming, resting)) break;

    long quantity = Math.min(incoming.remaining(), resting.remaining());
    trades.add(execute(incoming, resting, quantity));   // 체결가 = resting.price

    if (resting.isFilled()) book.removeBest(resting);
}
if (incoming.hasRemainingQuantity()) book.add(incoming);
```

결과는 `MatchResult`(신규 주문, Trade 목록, 변경된 Resting 주문 목록)로 반환한다. [5-1](#f5-1)에서 이 객체를 그대로 저장한다.

<a id="f3-1"></a>

### 3-1. Matching Engine `W2-D1 · 2h`

**목표**: 주문 하나를 넣으면 가격 → 시간 우선으로 체결하고, 무엇이 바뀌었는지 `MatchResult`로 돌려준다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [단위-통합-테스트 › 경계값은 단위 테스트로 채운다](../../10-테스트-운영/단위-통합-테스트/단위-통합-테스트.md#경계값은-단위-테스트로-채운다) — BUY = SELL, 수량 딱 맞음 같은 경계 케이스 작성법
- [단위-통합-테스트 › 테스트 이름이 문서가 되게 쓴다](../../10-테스트-운영/단위-통합-테스트/단위-통합-테스트.md#테스트-이름이-문서가-되게-쓴다) — `MatchingEngineTest` 메서드 이름 짓기
- [시간-공간-복잡도 › 복잡도를 계산하는 과정](../../01-복잡도-자료구조/시간-공간-복잡도/시간-공간-복잡도.md#복잡도를-계산하는-과정) — Matching 루프의 복잡도(체결 k건 × O(log P))를 말할 수 있게

**할 일**

1. [직접] `MatchResult(Order incoming, List<Trade> trades, List<Order> updatedRestings)` record
2. [직접] `canMatch(incoming, resting)` — BUY면 `incoming.price >= resting.price`, SELL이면 `<=`
3. [직접] `execute(incoming, resting, qty)` — 양쪽 `fill(qty)`, Trade 생성 (체결가 = resting.price, buyOrderPrice = BUY 쪽 주문가)
4. [직접] `MatchingEngine.match(Order incoming, OrderBook book)` — 위 설계의 루프
5. [직접] 아래 "이렇게 나오면 성공"의 기대값을 **코드를 돌리기 전에 손으로** 먼저 적는다
6. [AI] 완료 기준 케이스의 테스트 골격 → [직접] 5번의 기대값으로 assert 채우기
7. [AI 리뷰] "무한 루프 가능성, remaining이 0인 주문이 Book에 남는 경우, 체결가를 incoming 가격으로 쓰는 실수"

**판단할 것**

- `MatchResult`에 무엇을 담을지 (5-1에서 저장할 때 필요한 것이 다 있는가)
- Trade의 id는 이 시점엔 없다 (5-1에서 DB가 부여) → id 없이 생성 가능하게

**결과물**

- 코드: `trading.domain.MatchingEngine`, `MatchResult`, `Trade` 생성 로직
- 테스트: `MatchingEngineTest`
- 기록: devlog, ai-log (리뷰 결과)

**이렇게 나오면 성공**

```text
시나리오: SELL S1 70,000×10, S2 70,000×20, S3 70,100×30 → BUY B1 70,000×25

MatchResult
  incoming       B1  FILLED            remaining 0
  trades         [ (B1 ← S1) 70,000 × 10,  (B1 ← S2) 70,000 × 15 ]
  updatedResting S1  FILLED            remaining 0
                 S2  PARTIALLY_FILLED  remaining 5

OrderBook 이후
  asks  70,000: [S2(5)]   70,100: [S3(30)]
  bids  (없음)

MatchingEngineTest
  ✔ BUY 70,000 vs SELL 70,000 → 체결
  ✔ BUY 70,100 vs SELL 70,000 → 체결가 70,000, buyOrderPrice 70,100
  ✔ BUY 69,900 vs SELL 70,000 → 미체결, BUY가 bids에 남음
  ✔ 10 vs 10 → 양쪽 FILLED, Book 비어 있음
  ✔ BUY 20 vs SELL 10 → BUY PARTIALLY_FILLED 잔량 10이 bids에 남음
  ✔ 위 시나리오 결과 그대로
  ✔ 여러 Level 쓸기: BUY 70,100×40 → 70,000×10, 70,000×20, 70,100×10
  ✔ 같은 가격 S1, S2 → 항상 S1 먼저 체결
```

**완료 기준**

- [ ] `MatchingEngineTest` 전부 통과
- [ ] 체결가가 항상 Resting 가격이다
- [ ] 체결 후 Book에 remaining 0인 주문이 없다

[↑ 일정표](#schedule)

<a id="f3-2"></a>

### 3-2. 주문 취소 · 검증 `W2-D2 · 1.5h`

**목표**: 걸려 있는 주문의 잔량을 취소할 수 있고, 잘못된 주문은 엔진에 들어가기 전에 거절된다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [선형-자료구조-비교 › 연산별 시간 복잡도](../../01-복잡도-자료구조/선형-자료구조-비교/선형-자료구조-비교.md#연산별-시간-복잡도) — `ArrayDeque.remove(o)`가 O(n)인 이유 → 취소 방식 판단
- [Collection-선택-기준 › 순서 유지 구현체 (`LinkedHashMap`·`LinkedHashSet`)](../../01-복잡도-자료구조/Collection-선택-기준/Collection-선택-기준.md#순서-유지-구현체-linkedhashmaplinkedhashset) — 취소 O(1) 대안으로 Level을 LinkedHashMap으로 둘 때
- ★ [Spring-Boot와-예외처리 › 도메인 예외에 정보를 담는다](../../05-Spring/Spring-Boot와-예외처리/Spring-Boot와-예외처리.md#도메인-예외에-정보를-담는다) — `InvalidOrderException` 등 예외 설계
- [Spring-MVC-요청흐름 › 요청 DTO와 검증](../../05-Spring/Spring-MVC-요청흐름/Spring-MVC-요청흐름.md#요청-dto와-검증) — `@Positive` 등 Bean Validation

```text
취소 가능: OPEN, PARTIALLY_FILLED / 취소 불가: FILLED, CANCELLED
100주 주문 → 70주 체결 → 취소 → 70주는 유지, 잔량 30주만 취소

검증: quantity <= 0, price <= 0, 없는 종목 → 거절
      상한도 둔다 (예: price <= 10,000,000, quantity <= 1,000,000)
        → 없으면 price × quantity가 long 범위를 넘어 Math.multiplyExact가 500을 낸다
      (잔고 / 보유수량 부족은 8-2에서 추가)
```

**할 일**

1. [직접] 취소 방식 결정 (아래 표) → ADR-002
2. [직접] `MatchingEngine.cancel(long orderId, OrderBook book)` — Book에서 제거 + `order.cancel()`. Book에 없으면 "취소 불가" 결과
3. [AI] 예외 클래스: `InvalidOrderException`, `StockNotFoundException`, `OrderNotCancellableException`
4. [AI] `OrderValidator` — 수량 · 가격 · 종목 존재 검사 (Bean Validation `@Positive` + 종목 조회)
5. [AI] 검증 실패 테스트 → [직접] 취소 테스트 기대값 작성

**판단할 것** → ADR-002

- **취소 방식**: `orderIndex`로 가격 Level은 바로 찾지만 `ArrayDeque.remove(order)`는 O(Level 안 주문 수)

| 방식 | 장점 | 단점 |
|---|---|---|
| Deque에서 바로 제거 | 단순 | 한 가격에 주문이 몰리면 느림 |
| Lazy Cancel (상태만 CANCELLED, 매칭 때 skip) | 취소 O(1) | 호가 수량 집계 시 보정 필요 |

**결과물**

- 코드: `MatchingEngine.cancel`, `OrderValidator`, 예외 3종
- 테스트: `CancelTest`, `OrderValidatorTest`
- 기록: ADR-002 "주문 취소 방식", devlog

**이렇게 나오면 성공**

```text
CancelTest
  ✔ OPEN 주문 취소 → CANCELLED, Book에서 사라짐
  ✔ BUY 100주가 SELL 70주와 체결된 뒤 취소 → CANCELLED, remaining 30, 체결 Trade 70주는 그대로
  ✔ 취소된 BUY와 같은 가격의 SELL이 새로 들어와도 체결되지 않음
  ✔ FILLED 주문 취소 → OrderNotCancellableException
  ✔ 이미 CANCELLED 주문 재취소 → OrderNotCancellableException

OrderValidatorTest
  ✔ quantity 0 / -1 → InvalidOrderException
  ✔ price 0 / -1 → InvalidOrderException
  ✔ price · quantity 상한 초과 → InvalidOrderException (500이 아니라 400)
  ✔ 종목 "999999" → StockNotFoundException
```

**완료 기준**

- [ ] 두 테스트 클래스 통과
- [ ] ADR-002에 선택과 이유가 있다

[↑ 일정표](#schedule)

---

<a id="f4"></a>

## 4. 주문 API + Lock 처리기 `W2-D3 · 1.5h`

**왜**: 동시성 설계의 출발점(V1). 먼저 Lock으로 정합성을 확보하고, 이후 [7. Single Writer](#f7)로 바꾸며 비교한다.

**설계**

```java
synchronized (orderBook) {
    MatchResult result = matchingEngine.match(order, orderBook);
    persist(result);   // 5-1부터. Commit도 Lock 안에서 — 밖에서 하면 커밋 순서가 sequence 순서와 어긋난다
}
```

**목표**: HTTP로 주문 · 취소 · 조회를 할 수 있는 인메모리 체결 엔진. 여기서부터 "실행 가능한 프로그램"이 된다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [Thread-동기화 › `synchronized`가 잠그는 것](../../04-동시성/Thread-동기화/Thread-동기화.md#synchronized가-잠그는-것) — `synchronized(orderBook)`이 정확히 무엇을 막는지
- ★ [Atomic-Concurrent-Collection › `ConcurrentHashMap` — 복합 연산을 원자적으로](../../04-동시성/Atomic-Concurrent-Collection/Atomic-Concurrent-Collection.md#concurrenthashmap--복합-연산을-원자적으로) — `OrderBookRegistry`의 `computeIfAbsent`
- ★ [Spring-Boot와-예외처리 › 에러 응답 형식을 하나로 고정한다](../../05-Spring/Spring-Boot와-예외처리/Spring-Boot와-예외처리.md#에러-응답-형식을-하나로-고정한다) — `{code, message}` 응답 형식
- [REST-API-설계 › `code`를 주는 이유](../../09-웹-보안/REST-API-설계/REST-API-설계.md#code를-주는-이유) — `INVALID_ORDER` 같은 에러 코드를 두는 이유
- [REST-API-설계 › 상태 코드는 클라이언트의 분기문이다](../../09-웹-보안/REST-API-설계/REST-API-설계.md#상태-코드는-클라이언트의-분기문이다) — 400 / 404 / 409 고르기
- [Spring-MVC-요청흐름 › 컨트롤러는 얇게 유지한다](../../05-Spring/Spring-MVC-요청흐름/Spring-MVC-요청흐름.md#컨트롤러는-얇게-유지한다) — Controller가 `OrderProcessor`에만 의존하게

**할 일**

1. [직접] `OrderProcessor` 인터페이스 — `PlaceResult place(Order)`, `CancelResult cancel(long orderId)`, `OrderBookView orderBook(String stockCode)`
    - [AI] `PriceLevel(price, totalQuantity, orderCount)`, `OrderBookView(asks, bids)` record (7-2에서 Snapshot으로 확장)
2. [직접] `OrderBookRegistry` — `ConcurrentHashMap<String, OrderBook>`, 종목별 sequence 발급기, 주문 ID 발급기(`AtomicLong`, 2-1 판단 참고)
3. [직접] `LockBasedOrderProcessor` — 종목 OrderBook을 꺼내 `synchronized` 안에서 Matching / 취소, 호가 조회도 Lock 안에서 Level 집계
4. [AI] `OrderController` — `POST /orders`, `GET /orders/{id}`, `DELETE /orders/{id}`
5. [AI] `StockQueryController` — `GET /stocks/{code}/orderbook`, `GET /stocks/{code}/trades` (인메모리 목록)
6. [AI] 인메모리 저장소 `InMemoryOrderStore`, `InMemoryTradeStore`, 고정 종목 목록 (5-1에서 DB로 교체)
7. [AI] `@RestControllerAdvice` — 예외 → `{code, message}` 응답
8. [AI] `http/demo.http` (VSCode REST Client 확장)
9. [직접] `demo.http`를 순서대로 실행해 결과 확인

**판단할 것**

- 주문 응답에 무엇을 담을지 (추천: 주문 상태 + 이번 요청으로 생긴 체결 목록)
- 에러 코드: 400 `INVALID_ORDER` / 404 `STOCK_NOT_FOUND`, `ORDER_NOT_FOUND` / 409 `ORDER_NOT_CANCELLABLE`

**결과물**

- 코드: `OrderProcessor`, `LockBasedOrderProcessor`, `OrderBookRegistry`, Controller 2개, DTO, 예외 핸들러, 인메모리 저장소
- 테스트: `OrderApiTest` (MockMvc 또는 RestClient로 아래 시나리오)
- 기록: `http/demo.http`, devlog

**이렇게 나오면 성공**

```http
POST /orders  {"accountId":2,"stockCode":"005930","side":"SELL","price":70000,"quantity":10}
→ 201 {"orderId":1,"status":"OPEN","remainingQuantity":10,"trades":[]}

POST /orders  {"accountId":1,"stockCode":"005930","side":"BUY","price":70000,"quantity":5}
→ 201 {"orderId":2,"status":"FILLED","remainingQuantity":0,
       "trades":[{"price":70000,"quantity":5,"buyOrderId":2,"sellOrderId":1}]}

GET /stocks/005930/orderbook
→ 200 {"asks":[{"price":70000,"totalQuantity":5,"orderCount":1}],"bids":[]}

POST /orders  {... "quantity":0}          → 400 {"code":"INVALID_ORDER", ...}
POST /orders  {... "stockCode":"999999"}  → 404 {"code":"STOCK_NOT_FOUND", ...}
DELETE /orders/2                          → 409 {"code":"ORDER_NOT_CANCELLABLE", ...}
DELETE /orders/1                          → 200 {"orderId":1,"status":"CANCELLED","remainingQuantity":5}
```

**완료 기준**

- [ ] `demo.http` 전체가 위 응답대로 나온다
- [ ] `OrderApiTest` 통과
- [ ] Controller가 `OrderProcessor` 인터페이스에만 의존한다 (7-1에서 갈아끼울 준비)

[↑ 일정표](#schedule)

---

<a id="f5"></a>

## 5. 영속화 & 복구

**왜**: "서버가 죽으면 메모리에 있던 호가창은?" — 거래소 프로젝트에서 가장 먼저 나오는 질문.

**설계**

```text
Worker / Lock 내부 처리 순서
1. sequence 부여 (종목별 단조 증가)
2. 메모리 OrderBook에서 Matching → MatchResult
3. 하나의 DB 트랜잭션
   - 신규 Order INSERT, Trade INSERT
   - Resting Order remainingQuantity / status UPDATE
   - Outbox INSERT (10-1부터)
4. Commit 성공 → 호가 Snapshot 갱신 (7-2부터) → 응답
```

DB를 Source of Truth로 두고, 메모리 OrderBook은 **DB로부터 언제든 재구성 가능한 캐시**로 취급한다.

| DB 저장 실패 시 | 장점 | 단점 |
|---|---|---|
| 메모리 Rollback | 빠른 복구 | 역연산 로직이 복잡하고 버그 위험 |
| **Fail-Stop & Rebuild (선택)** | 단순, 정합성 확실 | 재구성 동안 해당 종목 중단 |
| Command Log 선기록 | 재처리 가능, 결정적 재현 | 구현 비용 큼 |

```sql
-- 재시작 / Rebuild 시
SELECT * FROM orders
WHERE stock_code = ? AND status IN ('OPEN', 'PARTIALLY_FILLED')
ORDER BY sequence ASC;
-- sequence 순서대로 다시 적재 → 같은 가격 FIFO 복원, 다음 sequence = max + 1
```

```text
면접 포인트
메모리와 DB 중 무엇이 Source of Truth인가?
체결 후 DB 저장 실패 시 어떤 상태가 되는가?
재시작 후 같은 가격 FIFO 순서가 어떻게 보존되는가?
```

<a id="f5-1"></a>

### 5-1. 체결 결과 저장 `W3-D1 · 2h`

**목표**: 체결 결과가 DB에 원자적으로 남는다. 인메모리 저장소가 사라지고 API가 DB 기준으로 동작한다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [ACID-격리수준 › 트랜잭션 vs `synchronized`](../../07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md#트랜잭션-vs-synchronized) — **Commit이 Lock 밖에서 일어나는 함정**을 이해하는 핵심 절
- ★ [AOP-Proxy-Transactional › 자기호출 — AOP가 안 걸리는 1번 원인](../../05-Spring/AOP-Proxy-Transactional/AOP-Proxy-Transactional.md#자기호출--aop가-안-걸리는-1번-원인) — `MatchResultWriter`를 별도 빈으로 빼야 하는 이유
- [AOP-Proxy-Transactional › 트랜잭션 경계를 어디에 둘까](../../05-Spring/AOP-Proxy-Transactional/AOP-Proxy-Transactional.md#트랜잭션-경계를-어디에-둘까) — 트랜잭션 경계 판단
- ★ [JDBC-MyBatis-JPA › `@Enumerated(EnumType.ORDINAL)`의 함정](../../07-트랜잭션-데이터접근/JDBC-MyBatis-JPA/JDBC-MyBatis-JPA.md#enumeratedenumtypeordinal의-함정) — `OrderStatus` enum 매핑 시 반드시 STRING
- [JDBC-MyBatis-JPA › flush는 커밋이 아니다](../../07-트랜잭션-데이터접근/JDBC-MyBatis-JPA/JDBC-MyBatis-JPA.md#flush는-커밋이-아니다) — 저장 후 DB 조회로 검증할 때 헷갈리는 지점
- [대용량-데이터-분할 › 분산 환경의 기본 키](../../06-데이터베이스/대용량-데이터-분할/대용량-데이터-분할.md#분산-환경의-기본-키) — IDENTITY vs 앱 생성 ID 판단

**할 일**

1. [AI] Flyway `V1__create_stock_order_trade.sql`
    - `stock(code PK, name)` + 시드 2~3종목 (`005930 삼성전자`, `000660 SK하이닉스`, `035420 NAVER`)
    - `orders(id, account_id, stock_code, side, price, quantity, remaining_quantity, status, sequence, created_at)`, `UNIQUE(stock_code, sequence)`
    - `trade(id, stock_code, buy_order_id, sell_order_id, buyer_account_id, seller_account_id, buy_order_price, price, quantity, executed_at)`
2. [직접] DDL 검토: NOT NULL, `UNIQUE(stock_code, sequence)`가 왜 필요한지, `account_id`는 계좌 테이블이 생기는 V2에서 FK 추가
3. [AI] `OrderEntity`, `TradeEntity`, JPA Repository, 도메인 ↔ Entity 매퍼
4. [직접] `MatchResultWriter.write(MatchResult)` — `@Transactional`. 신규 주문 INSERT, Resting 주문 UPDATE, Trade INSERT
5. [직접] `LockBasedOrderProcessor`에서 sequence 부여 → Matching → `write` 호출을 **모두 synchronized 블록 안에서**
6. [직접] **취소도 DB에 반영** — Lock 안에서 `status = CANCELLED` UPDATE. 빠뜨리면 재시작할 때 취소한 주문이 호가창에 되살아난다
7. [직접] 주문 ID를 DB 시퀀스(`orders_id_seq`)에서 Matching 전에 받아오도록 변경 (아래 판단)
8. [AI] 인메모리 저장소 제거, 조회 API를 Repository 기반으로 변경
7. [직접] DB 쿼리로 결과 확인 (아래)

**판단할 것**

- **트랜잭션 경계 함정**: `@Transactional`을 synchronized를 감싸는 바깥 메서드에 붙이면 Commit이 Lock을 **빠져나온 뒤** 일어난다 → 반드시 Lock 안에서 호출되는 별도 빈의 메서드(또는 `TransactionTemplate`)로
- **sequence 생성**: 종목별 `AtomicLong`(시작 시 `max + 1`) vs DB 시퀀스
- **주문 ID 생성** — IDENTITY는 안 된다 (2-1 판단: ID가 Matching 전에 필요)
    - DB 시퀀스 `nextval`을 주문 접수 시점(Lock 밖)에 미리 받기 (추천: 재시작해도 안전, 서버를 늘려도 겹치지 않음)
    - `AtomicLong`(시작 시 `max(id) + 1`) — 더 빠르지만 단일 인스턴스 전제
- **Trade ID**는 Matching 중에 아무도 참조하지 않으므로 IDENTITY여도 된다 (단 10-1의 Outbox payload는 Trade INSERT 뒤에 만든다)

**결과물**

- 코드: `V1__…sql`(+ `orders_id_seq`), Entity 2개, Repository 2개, 매퍼, `MatchResultWriter`
- 테스트: `PersistenceTest` — 데모 시나리오 후 DB 상태 검증
- 기록: devlog (트랜잭션 경계 판단 이유)

**이렇게 나오면 성공**

```text
데모 시나리오 (SELL 10 → BUY 5) 실행 후

SELECT id, side, price, quantity, remaining_quantity, status, sequence FROM orders;
 id | side | price | quantity | remaining_quantity |      status      | sequence
  1 | SELL | 70000 |       10 |                  5 | PARTIALLY_FILLED |        1
  2 | BUY  | 70000 |        5 |                  0 | FILLED           |        2

SELECT buy_order_id, sell_order_id, buy_order_price, price, quantity FROM trade;
 buy_order_id | sell_order_id | buy_order_price | price | quantity
            2 |             1 |           70000 | 70000 |        5

앱 재시작 없이 GET /orders/1 → status PARTIALLY_FILLED, remainingQuantity 5 (DB에서 읽음)
```

**완료 기준**

- [ ] `PersistenceTest` 통과 — DB의 주문/체결이 메모리 결과와 같다
- [ ] 취소한 주문이 DB에서 `CANCELLED`로 바뀐다
- [ ] 인메모리 저장소 코드가 남아 있지 않다
- [ ] Commit이 Lock 안에서 일어난다는 것을 코드로 설명할 수 있다

[↑ 일정표](#schedule)

<a id="f5-2"></a>

### 5-2. 재시작 복구 · Rebuild `W3-D2 · 2h`

**목표**: 서버를 껐다 켜도 호가창이 그대로 돌아오고, DB 저장이 실패하면 해당 종목을 DB 기준으로 다시 맞춘다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [IoC-DI와-Bean › 빈 생명주기 콜백 순서](../../05-Spring/IoC-DI와-Bean/IoC-DI와-Bean.md#빈-생명주기-콜백-순서) — `ApplicationReadyEvent`에서 복구를 돌리는 시점
- ★ [Mock-SpringTest-Testcontainers › 재현할 수 없는 경로를 목으로 만든다](../../10-테스트-운영/Mock-SpringTest-Testcontainers/Mock-SpringTest-Testcontainers.md#재현할-수-없는-경로를-목으로-만든다) — DB 저장 실패를 Spy로 주입하는 방법
- [Mock-SpringTest-Testcontainers › `@MockitoBean` 한 줄이 컨텍스트를 하나 더 만든다](../../10-테스트-운영/Mock-SpringTest-Testcontainers/Mock-SpringTest-Testcontainers.md#mockitobean-한-줄이-컨텍스트를-하나-더-만든다) — 장애 주입 테스트가 느려지는 이유
- [주문-결제-시스템 › 7) 복구의 마지막 층 — 조회 배치와 대사](../../12-시스템설계/주문-결제-시스템/주문-결제-시스템.md#7-복구의-마지막-층--조회-배치와-대사) — "DB 기준으로 다시 맞춘다"는 같은 발상

**할 일**

1. [직접] `OrderBookRecovery.rebuild(stockCode)` — 위 SQL로 미체결 주문을 sequence 순으로 읽어 새 OrderBook에 `add`, 다음 sequence = `max(sequence) + 1` (주문이 없으면 1). 주문 ID를 `AtomicLong`으로 골랐다면 그것도 `max(id) + 1`로 복원
2. [직접] `recoverAll()` — `ApplicationReadyEvent`에서 모든 종목 rebuild, 끝나기 전 주문은 503 `ENGINE_RECOVERING`
3. [직접] Fail-Stop: `MatchResultWriter.write`가 예외를 던지면 → 해당 종목 OrderBook 폐기 → `rebuild` → 요청에는 503 `ORDER_FAILED` 응답
4. [직접] 비교 도구 `OrderBook.dump()` — Level별 (orderId, remaining) 목록. 메모리 Book과 rebuild한 Book을 비교할 때 쓴다
5. [AI] 장애 주입 테스트 골격 — `TradeRepository`를 `@MockitoSpyBean`으로 두고 첫 호출에 예외
6. [AI] 재시작 시뮬레이션 테스트 골격 — Registry를 비우고 `recoverAll()` 호출
7. [직접] 실제 재시작 수동 확인: 주문 몇 개 → `bootRun` 종료 → 재시작 → 호가 조회

**판단할 것**

- Rebuild 중 해당 종목으로 들어온 요청: 대기 vs 즉시 503 (추천: 즉시 503, 단순하고 원인이 드러난다)
- 실패한 요청의 주문은 DB에 없다 → 클라이언트는 재시도해야 한다는 것을 응답 코드로 어떻게 알릴지

**결과물**

- 코드: `OrderBookRecovery`, Fail-Stop 처리, `OrderBook.dump()`
- 테스트: `RecoveryTest`, `FailStopTest`
- 기록: ADR-003 "Source of Truth = DB, Fail-Stop & Rebuild", devlog

**이렇게 나오면 성공**

```text
RecoveryTest
  ✔ 같은 가격 BUY A, B, C (sequence 1, 2, 3) → recoverAll → 70,000 Level = [A, B, C]
  ✔ 부분 체결된 주문은 remaining 그대로 복원
  ✔ FILLED / CANCELLED 주문은 복원되지 않음
  ✔ 복구 후 새 주문의 sequence = 4

FailStopTest
  ✔ Trade 저장 1회 실패 → 응답 503, DB에 해당 주문 없음
  ✔ 실패 직후 memoryBook.dump() == rebuild(DB).dump()
  ✔ 다음 주문은 정상 체결

로그
  WARN  Persist failed, rebuilding stock=005930
  INFO  OrderBook rebuilt stock=005930 openOrders=3 nextSequence=4
```

**완료 기준**

- [ ] 두 테스트 클래스 통과
- [ ] 수동 재시작 후 호가 조회 결과가 재시작 전과 같다
- [ ] ADR-003 작성

[↑ 일정표](#schedule)

---

<a id="f6"></a>

## 6. 동시성 테스트 · 불변식 검증기 `W3-D3 · 1.5h`

**왜**: "정합성을 지켰다"를 증명하는 도구. 이후 모든 기능이 이 검증기를 다시 돌린다.

**설계 — 불변식 전체** (오늘은 "주문 / OrderBook"만, 나머지는 해당 단계에서 추가)

```text
주문 / OrderBook                                                         ← 오늘
  0 <= remainingQuantity <= quantity
  quantity - remainingQuantity = 해당 주문의 Trade 수량 합
  FILLED / CANCELLED 주문은 OrderBook에 없음
  최우선 BUY 가격 < 최우선 SELL 가격 (교차 상태 없음)
  메모리 OrderBook == DB 기준으로 재구성한 OrderBook

자산                                                                     ← 9-3
  0 <= reservedBalance <= balance,  0 <= reservedQuantity <= quantity
  전체 현금 합계 · 종목별 전체 보유 수량 합계는 시드 이후 변하지 않음
  모든 정산이 끝난 뒤: reservedBalance  = Σ(열린 BUY 잔량 × 주문가격)
                      reservedQuantity = Σ(열린 SELL 잔량)

이벤트                                                                   ← 10-3
  모든 Trade에 Outbox 레코드가 정확히 1개
  processed_event 수 = 정산된 Trade 수
```

**목표**: 동시 주문 1,000건을 넣고도 불변식이 지켜진다는 것, 그리고 **Lock을 빼면 실제로 깨진다는 것**을 테스트로 보여준다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [Thread-동기화 › 왜 값이 사라지는가 — `i++`의 세 단계](../../04-동시성/Thread-동기화/Thread-동기화.md#왜-값이-사라지는가--i의-세-단계) — Lock을 빼면 왜 불변식이 깨지는지
- ★ [Atomic-Concurrent-Collection › 동기화 보조 도구](../../04-동시성/Atomic-Concurrent-Collection/Atomic-Concurrent-Collection.md#동기화-보조-도구) — `CountDownLatch`로 동시에 출발시키기
- ★ [ThreadPool-Deadlock › `execute`와 `submit` — 예외 처리가 완전히 다르다](../../04-동시성/ThreadPool-Deadlock/ThreadPool-Deadlock.md#execute와-submit--예외-처리가-완전히-다르다) — 실행기에서 스레드 예외를 놓치지 않으려면
- [Thread-동기화 › 왜 안 보이는가 — 캐시와 메인 메모리](../../04-동시성/Thread-동기화/Thread-동기화.md#왜-안-보이는가--캐시와-메인-메모리) — 가시성 문제 — 7-2와도 연결
- [ThreadPool-Deadlock › 종료 절차](../../04-동시성/ThreadPool-Deadlock/ThreadPool-Deadlock.md#종료-절차) — 테스트 끝에 Executor를 제대로 닫기

**할 일**

1. [직접] `ConcurrencyRunner.run(int threads, List<Runnable> tasks)` — `ExecutorService` + 시작 신호용 `CountDownLatch(1)` + 종료 대기용 `CountDownLatch(n)`, 예외 수집
2. [직접] `InvariantChecker.checkTrading()` → 위반 메시지 `List<String>` 반환 (빈 리스트 = 정상)
3. [AI] 불변식별 집계 SQL 초안 (예: 주문별 `quantity - remaining_quantity` vs `SUM(trade.quantity)`) → [직접] 검토
4. [AI] 랜덤 주문 생성기 — 종목 2개, 가격 69,500~70,500 (100원 단위), 수량 1~100, BUY/SELL 반반, seed 고정
5. [직접] `TradingConcurrencyTest` — 16스레드 × 1,000건 → `checkTrading()`이 빈 리스트
6. [직접] **테스트의 테스트**: 테스트 소스에 Lock 없는 `NoLockOrderProcessor`를 두고 같은 테스트 실행 → 위반이 나오는지 확인
7. [직접] 6번의 실제 출력(위반 메시지 / 예외)을 devlog에 그대로 붙여넣기

**판단할 것**

- 불변식마다 어떤 버그를 잡는지 한 줄씩 적기 (devlog)
- Lock 없는 버전이 매번 깨지지 않으면: 스레드 수 · 주문 수를 늘리거나 반복 실행 (`@RepeatedTest`)
- **"실패를 재현하는 테스트"는 기본 빌드에서 뺀다** — 확률적으로 깨지므로 CI를 불안정하게 만든다. `@Tag("reproduce")`를 붙이고 `./gradlew test`에서 제외, `./gradlew reproduceTest` 같은 별도 태스크로만 실행 (9-1, 9-2의 재현 테스트도 같은 규칙)

**결과물**

- 코드(test): `ConcurrencyRunner`, `InvariantChecker`, `RandomOrderGenerator`, `NoLockOrderProcessor`
- 테스트: `TradingConcurrencyTest` — Lock 있음 통과, Lock 없음은 위반 발생을 assert
- 기록: devlog에 Lock 없음 실패 출력 원문 — **면접에서 "문제를 직접 재현했다"의 증거**

**이렇게 나오면 성공**

```text
Lock 있음
  TradingConcurrencyTest > 동시_주문_1000건_불변식_유지() PASSED
  violations = []

Lock 없음 (실패해야 정상)
  TradingConcurrencyTest > 락이_없으면_불변식이_깨진다() PASSED
  violations = [
    "order 412: quantity-remaining=30 but tradeSum=45",
    "orderbook 005930: bestBid 70,100 >= bestAsk 70,000 (crossed)",
    "memory != db for 005930"
  ]
  또는 ConcurrentModificationException / NullPointerException 발생
```

**완료 기준**

- [ ] Lock 있음: 위반 0건
- [ ] Lock 없음: 위반이 발생하는 것을 테스트가 증명한다
- [ ] 실패 출력 원문이 devlog에 있다

[↑ 일정표](#schedule)

---

<a id="f7"></a>

## 7. Single Writer & 호가 Snapshot

**왜**: "Lock 방식과 Single Writer의 차이는?" — 동시성 설계를 바꾼 이유와 측정 결과로 답한다.

**설계**

```text
Request A ─┐
Request B ─┼─> 종목별 Bounded Queue → Matching Worker → OrderBook
Request C ─┘

workerIndex = Math.floorMod(stockCode.hashCode(), workerCount)
  (Math.abs(hashCode()) % n 은 Integer.MIN_VALUE에서 음수 → 쓰지 않는다)

같은 종목 = 같은 Worker = 순서 보장 / 다른 종목 = 다른 Worker = 병렬
주문 취소도 OrderBook을 바꾸므로 같은 Worker Queue를 거친다

Controller → Command + CompletableFuture를 Queue에 넣음
Worker     → 처리 후 future.complete(result)
Queue 가득 → 즉시 503 (무한 Queue는 지연이 끝없이 늘어나는 장애)
```

Single Writer의 실제 장점 — 종목별 `synchronized`도 같은 종목은 어차피 직렬이라 Lock 경쟁 감소만으로는 차이가 작을 수 있다. 더 본질적인 이유:

```text
처리 순서가 결정적 → 재현 / 디버깅 / 복구가 쉬움
Command 단위 처리 → 배치 저장으로 확장 가능
Queue 적재량으로 부하 상태가 드러남
Command Log / Event Sourcing으로 확장하기 쉬움
```

<a id="f7-1"></a>

### 7-1. Single Writer `W4-D1 · 2h`

**목표**: OrderBook을 수정하는 스레드를 종목별 하나로 제한한다. Lock 모드와 설정으로 바꿔가며 쓸 수 있다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [Atomic-Concurrent-Collection › `BlockingQueue` — 생산자와 소비자](../../04-동시성/Atomic-Concurrent-Collection/Atomic-Concurrent-Collection.md#blockingqueue--생산자와-소비자) — Worker + `ArrayBlockingQueue` 구조 그대로
- ★ [동기-비동기와-메시지큐 › 큐가 밀릴 때 — 백프레셔](../../11-메시징/동기-비동기와-메시지큐/동기-비동기와-메시지큐.md#큐가-밀릴-때--백프레셔) — Bounded Queue + 즉시 503의 근거
- ★ [ThreadPool-Deadlock › `Future`와 `CompletableFuture`](../../04-동시성/ThreadPool-Deadlock/ThreadPool-Deadlock.md#future와-completablefuture-1) — Controller가 Worker 결과를 기다리는 방식
- ★ [주문-결제-시스템 › 3) 타임아웃은 "모름"이다](../../12-시스템설계/주문-결제-시스템/주문-결제-시스템.md#3-타임아웃은-모름이다) — **timeout → 202 PENDING으로 응답하는 근거**
- [ThreadPool-Deadlock › 거부 정책 네 가지](../../04-동시성/ThreadPool-Deadlock/ThreadPool-Deadlock.md#거부-정책-네-가지) — Queue가 찼을 때 선택지 비교
- [ThreadPool-Deadlock › 종료 절차](../../04-동시성/ThreadPool-Deadlock/ThreadPool-Deadlock.md#종료-절차) — Graceful shutdown
- [Thread-동기화 › 인터럽트 — 협력적 취소](../../04-동시성/Thread-동기화/Thread-동기화.md#인터럽트--협력적-취소) — Worker 스레드를 멈추는 올바른 방법
- [선형-자료구조-비교 › 큐 길이는 곧 지연 시간이다](../../01-복잡도-자료구조/선형-자료구조-비교/선형-자료구조-비교.md#큐-길이는-곧-지연-시간이다) — Queue 크기 판단
- [동기-비동기와-메시지큐 › 순서 보장 — 파티션](../../11-메시징/동기-비동기와-메시지큐/동기-비동기와-메시지큐.md#순서-보장--파티션) — "같은 종목 = 같은 Worker"와 같은 원리 (10장 Kafka에서 다시)
- [Spring-Boot와-예외처리 › 설정을 타입 안전하게 묶는다](../../05-Spring/Spring-Boot와-예외처리/Spring-Boot와-예외처리.md#설정을-타입-안전하게-묶는다) — `EngineProperties`
- [08-모니터링 › Micrometer](../../infra/08-모니터링/08-모니터링.md#micrometer) — Queue 적재량 Gauge 노출
- [로그-메트릭-트레이싱 › 로그는 뜨거운 경로에서 비싸다](../../10-테스트-운영/로그-메트릭-트레이싱/로그-메트릭-트레이싱.md#로그는-뜨거운-경로에서-비싸다) — Worker 루프 안의 로그 비용

**할 일**

1. [직접] `Command` sealed interface — `PlaceCommand(Order, CompletableFuture<PlaceResult>)`, `CancelCommand(orderId, CompletableFuture<CancelResult>)`
2. [직접] `MatchingWorker` — 전용 스레드 1개 + `ArrayBlockingQueue<Command>`. 루프: `take()` → 처리(sequence → match → write) → `future.complete` / 예외 시 `completeExceptionally` + Rebuild. 예외가 나도 루프는 계속
3. [직접] `SingleWriterOrderProcessor` — `floorMod`로 Worker 선택 → `queue.offer(cmd)` 실패 시 즉시 `EngineBusyException`(503) → `future.get(timeout)`
    - **timeout은 실패가 아니라 "모름"이다** — Queue에 들어간 Command는 응답이 끊겨도 나중에 처리된다. timeout이면 `202 Accepted {orderId, status:"PENDING"}`로 응답하고, 클라이언트는 `GET /orders/{id}`로 확인한다
4. [직접] 취소는 `orderId → stockCode`를 DB에서 찾아 같은 Worker로
5. [직접] Graceful shutdown — `@PreDestroy`에서 새 Command 거절 → Queue 비울 때까지 처리 → 스레드 join
6. [AI] `EngineProperties(mode, workerCount, queueCapacity, timeoutMs)` + `exchange.engine.mode=lock|single-writer`로 Bean 전환
7. [AI] `EngineBusyException` → 503 `ENGINE_BUSY` 매핑
8. [AI] 테스트 골격: 두 모드로 데모 시나리오, Queue 가득 시나리오 (Worker를 Latch로 멈춰두고 capacity 1에 2건 투입)

**판단할 것**

- Lock 방식은 **지우지 않는다** → 7-3 측정에 필요
- Worker 수(추천: CPU 코어 수 이하), Queue 크기(추천: 1,000), Future timeout(추천: 3초)
- Worker 스레드 이름 규칙 (`matching-worker-0`) → 로그로 "같은 종목은 같은 스레드"를 확인할 수 있게
- **503과 timeout을 구분하는 이유** (8-2에서 돈과 직결된다)
    - `offer` 실패 = 확실히 처리 안 됨 → 503, 클라이언트는 재시도해도 된다
    - timeout = 처리됐는지 모름 → 503으로 응답하면 클라이언트가 재주문해 **이중 주문**이 되고, 8-2 이후엔 예약을 풀어버려 **돈이 새는** 버그가 된다
- 서버가 죽으면 Queue 안의 Command는 사라진다 → 응답을 못 받은 주문이므로 클라이언트 입장에선 "모름"과 같다. 8-2 ADR에서 이 경우의 예약 처리를 다룬다

**결과물**

- 코드: `Command`, `MatchingWorker`, `SingleWriterOrderProcessor`, `EngineProperties`
- 테스트: `SingleWriterTest` (데모 시나리오 · 503 · 같은 종목 같은 스레드)
- 기록: devlog (Worker 수 / Queue 크기 선택 이유)

**이렇게 나오면 성공**

```text
exchange.engine.mode=single-writer 로 demo.http 실행 → 4번과 같은 응답

로그
  [matching-worker-1] place order=1 stock=005930 seq=1
  [matching-worker-1] place order=2 stock=005930 seq=2
  [matching-worker-0] place order=3 stock=000660 seq=1

Queue 가득
  POST /orders → 503 {"code":"ENGINE_BUSY","message":"..."}

Worker 지연 (timeout 초과)
  POST /orders → 202 {"orderId":7,"status":"PENDING"}
  잠시 뒤 GET /orders/7 → 실제 처리 결과 (OPEN / FILLED …)

SingleWriterTest
  ✔ lock / single-writer 두 모드 모두 데모 시나리오 통과
  ✔ capacity 1, Worker 정지 상태에서 2건째 → 503
  ✔ Worker를 timeout보다 오래 멈춤 → 202 PENDING, 재개 후 그 주문이 정상 처리됨
  ✔ 같은 종목 주문은 항상 같은 Worker 스레드에서 처리
  ✔ Worker에서 저장 예외 발생 후에도 다음 주문 정상 처리
```

**완료 기준**

- [ ] `SingleWriterTest` 통과
- [ ] 설정 한 줄로 Lock ↔ Single Writer 전환된다
- [ ] 6번 `TradingConcurrencyTest`가 single-writer 모드에서도 통과

[↑ 일정표](#schedule)

<a id="f7-2"></a>

### 7-2. 호가 Snapshot `W4-D2 · 1.5h`

**목표**: 호가 조회가 Worker 스레드의 OrderBook을 건드리지 않고, Worker가 발행한 불변 Snapshot만 읽는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [Thread-동기화 › `volatile`이 실제로 하는 일 — 메모리 배리어](../../04-동시성/Thread-동기화/Thread-동기화.md#volatile이-실제로-하는-일--메모리-배리어) — Safe Publication의 원리
- ★ [Thread-동기화 › happens-before를 만드는 것들](../../04-동시성/Thread-동기화/Thread-동기화.md#happens-before를-만드는-것들) — `AtomicReference.set` 이후 읽기가 안전한 이유
- ★ [Java-Collection › Iterator와 fail-fast](../../03-Java/Java-Collection/Java-Collection.md#iterator와-fail-fast) — HTTP 스레드가 TreeMap을 읽으면 생기는 `ConcurrentModificationException`
- [Java-Collection › 뷰(view) — 복사본이 아니다](../../03-Java/Java-Collection/Java-Collection.md#뷰view--복사본이-아니다) — Snapshot은 뷰가 아니라 복사본이어야 한다
- [Java-Collection › 불변 컬렉션 세 가지의 차이](../../03-Java/Java-Collection/Java-Collection.md#불변-컬렉션-세-가지의-차이) — `List.copyOf`를 고르는 이유

OrderBook은 Worker 스레드만 수정한다. HTTP 스레드가 `TreeMap`을 직접 읽으면 안전하지 않다.

```java
record PriceLevel(long price, long totalQuantity, int orderCount) {}
record OrderBookSnapshot(List<PriceLevel> asks, List<PriceLevel> bids, long lastSequence) {}
// Worker가 Command 처리 후 상위 N Level의 불변 Snapshot을 만들어 AtomicReference로 교체 (Safe Publication)
// 내부 주문 A 10주, B 20주, C 30주 @70,000 → 외부에는 "70,000원 / 60주 / 3건"
```

**할 일**

1. [AI] `OrderBookSnapshot` record (4에서 만든 `PriceLevel` 재사용, `lastSequence` 추가)
2. [직접] `OrderBook.toSnapshot(int depth)` — 각 측 상위 N Level 집계, `List.copyOf`로 불변
3. [직접] `SnapshotHolder` — 종목별 `AtomicReference<OrderBookSnapshot>`. Worker가 Commit 성공 후 `set`, Rebuild 후에도 `set`
4. [직접] 호가 조회 API를 `SnapshotHolder.get(stockCode)`로 교체 (Lock 모드에서는 Lock 안에서 Snapshot 생성)
5. [AI] 6번 동시성 테스트를 `@ParameterizedTest`로 두 모드 실행, 종목 3개 동시 주문 테스트 추가
6. [직접] Snapshot이 "Commit 후"에만 바뀌는지 확인 (저장 실패 시 이전 Snapshot 유지 → Rebuild 후 갱신)

**판단할 것**

- HTTP 스레드가 `TreeMap`을 직접 읽으면 안 되는 이유: 가시성(다른 스레드의 변경이 안 보이거나 반쯤 보임), `ConcurrentModificationException`
- 왜 `volatile` 하나로 충분한가: Snapshot이 불변이라 참조만 안전하게 바꾸면 된다
- 깊이 N (추천: 10)

**결과물**

- 코드: `PriceLevel`, `OrderBookSnapshot`, `OrderBook.toSnapshot`, `SnapshotHolder`
- 테스트: `OrderBookSnapshotTest`, 두 모드 파라미터화된 `TradingConcurrencyTest`, `MultiStockConcurrencyTest`
- 기록: devlog (Safe Publication을 내 말로 3줄)

**이렇게 나오면 성공**

```text
70,000에 A 10, B 20, C 30 매수, 70,100에 D 5 매도

GET /stocks/005930/orderbook
{
  "asks": [ {"price":70100,"totalQuantity":5,"orderCount":1} ],
  "bids": [ {"price":70000,"totalQuantity":60,"orderCount":3} ],
  "lastSequence": 4
}

TradingConcurrencyTest
  ✔ [1] mode=lock          violations = []
  ✔ [2] mode=single-writer violations = []
MultiStockConcurrencyTest
  ✔ 종목 3개 × 1,000건 동시 → 종목별 불변식 모두 통과
```

**완료 기준**

- [ ] 위 테스트 전부 통과
- [ ] 호가 조회 코드에 OrderBook 직접 참조가 없다 (Single Writer 모드)

[↑ 일정표](#schedule)

<a id="f7-3"></a>

### 7-3. 측정: Lock vs Single Writer `W4-D3 · 2h` `🏷 v0.1-trading`

**목표**: 두 방식의 처리량과 지연을 같은 조건에서 재고, 차이(또는 차이 없음)의 원인을 설명할 수 있다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [장애분석-성능개선 › 처리량의 천장은 계산할 수 있다](../../10-테스트-운영/장애분석-성능개선/장애분석-성능개선.md#처리량의-천장은-계산할-수-있다) — 측정 전에 예상치를 계산해 보기
- ★ [ACID-격리수준 › 커밋 횟수 — 가장 큰 단일 변수](../../07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md#커밋-횟수--가장-큰-단일-변수) — E2E 병목이 DB Commit일 때의 설명 근거
- ★ [장애분석-성능개선 › 평균 vs 백분위](../../10-테스트-운영/장애분석-성능개선/장애분석-성능개선.md#평균-vs-백분위) — p95 / p99를 같이 보는 이유
- [장애분석-성능개선 › 부하 테스트는 이용률을 바꿔 가며 한다](../../10-테스트-운영/장애분석-성능개선/장애분석-성능개선.md#부하-테스트는-이용률을-바꿔-가며-한다) — VU 수를 바꿔 가며 측정
- [장애분석-성능개선 › 성능 개선은 한 번에 하나만](../../10-테스트-운영/장애분석-성능개선/장애분석-성능개선.md#성능-개선은-한-번에-하나만) — 측정 조건 통제
- [시스템설계-답변법 › ⑤ 병목 — 가장 느린 공유 자원을 찾는다](../../12-시스템설계/시스템설계-답변법/시스템설계-답변법.md#⑤-병목--가장-느린-공유-자원을-찾는다) — 해석 3줄 쓰는 틀
- [ConnectionPool과-쿼리튜닝 › 풀이 고갈되면 무슨 일이 일어나는가](../../06-데이터베이스/ConnectionPool과-쿼리튜닝/ConnectionPool과-쿼리튜닝.md#풀이-고갈되면-무슨-일이-일어나는가) — 측정 중 지연의 진짜 원인이 커넥션 대기일 때
- [JVM-메모리-GC › GC 비용은 "만든 양"이 아니라 "살아남은 양"에 비례한다](../../03-Java/JVM-메모리-GC/JVM-메모리-GC.md#gc-비용은-만든-양이-아니라-살아남은-양에-비례한다) — 메모리에 오래 사는 OrderBook이 p99 튐에 주는 영향

**할 일**

1. [AI] `k6/place-orders.js` — 랜덤 BUY/SELL(70,000 ± 500원, 100원 단위, 수량 1~50), 시나리오 2개: 종목 1개 / 종목 3개, VU 50, 각 1,000 · 10,000건
2. [AI] `scripts/reset-db.sh` — 측정 전 orders / trade 비우기 + 앱 재시작
3. [직접] 측정 조건 고정: 같은 머신, 다른 앱 종료, 워밍업 1회(버림), 본 측정 3회 평균
4. [직접] 4가지 조합 측정: {lock, single-writer} × {종목 1개, 종목 3개}
5. [AI] k6 결과를 표로 정리
6. [직접] 해석 작성 — 아래 질문에 답하는 3~5줄
    - 차이가 컸나 작았나? 종목 수에 따라 달라졌나?
    - 병목은 어디였나? (DB Commit 시간 vs 엔진 처리 시간 — 로그나 간단한 타이머로 확인)
7. [직접] README 없이도 이해되게 `docs/benchmarks.md`에 기록 → `git tag v0.1-trading`
8. (선택 · D4) [AI] JMH 설정 → [직접] `MatchingEngine.match`만 측정 → "엔진은 μs, DB는 ms"를 수치로

**판단할 것**

- 무엇을 "한 건"으로 셀지: HTTP 요청 1건 (체결 여부 무관)
- 100,000건은 시간이 남을 때만
- **커넥션 풀이 진짜 병목일 수 있다** — HikariCP 기본 풀은 10개. VU 50이 몰리면 Lock / Worker가 아니라 커넥션 대기가 지연을 만든다. 측정 중 `hikaricp.connections.pending`(Actuator)이나 로그로 확인하고, 풀 크기를 측정 조건에 적는다

**결과물**

- 코드: `k6/place-orders.js`, `scripts/reset-db.sh`
- 기록: `docs/benchmarks.md` "실험 1", devlog
- Git: `v0.1-trading` Tag

**이렇게 나오면 성공** (`docs/benchmarks.md`에 이런 형식으로)

```text
## 실험 1. Lock vs Single Writer (E2E)
환경: M1 / 16GB, PostgreSQL 16 (Docker), VU 50, 워밍업 1회 후 3회 평균

| 모드          | 종목 | 주문 수 | TPS | Avg(ms) | p95(ms) | p99(ms) |
|---------------|------|---------|-----|---------|---------|---------|
| lock          | 1    | 10,000  |     |         |         |         |
| single-writer | 1    | 10,000  |     |         |         |         |
| lock          | 3    | 10,000  |     |         |         |         |
| single-writer | 3    | 10,000  |     |         |         |         |

해석
- (예) 종목 1개에서는 두 방식 차이가 X% 이내였다. 요청당 시간의 대부분이 DB Commit(약 N ms)이었기 때문이다.
- (예) 종목 3개에서는 …
- 그래도 Single Writer를 택한 이유: 처리 순서 결정성, Queue 적재량으로 부하 관측, …
```

**완료 기준**

- [ ] 4개 조합 수치가 표에 있다
- [ ] 해석에 "병목이 어디였는가"가 숫자와 함께 있다
- [ ] `git tag v0.1-trading`

[↑ 일정표](#schedule)

---

<a id="f8"></a>

## 8. 계좌 · 예약 · 정산

**왜**: 체결 결과로 생긴 돈과 주식의 변화를 정확히 반영하는 것. 부분 체결, 취소, 가격 개선까지 맞아야 한다.

**설계 — 예약**

```text
주문 시 돈을 바로 차감하지 않는다 (아직 체결 전, 부분 체결 · 취소 가능)

잔고 1,000,000원, BUY 70,000원 × 10주
balance = 1,000,000 / reservedBalance = 700,000 / available = 300,000

SELL은 보유 주식을 예약: quantity 100, reservedQuantity 50 → available 50

취소 시 해제
  BUY  → 미체결 수량 × 주문가격
  SELL → 미체결 수량
```

**설계 — 가격 개선**

```text
BUY 70,100원 × 10주 → 701,000원 예약
Resting SELL 70,000원 → 체결 700,000원
실제 지급 700,000원, 차액 해제 (70,100 - 70,000) × 10 = 1,000원

이걸 안 하면 차액이 reservedBalance에 계속 남아 사용 가능 금액이 점점 줄어드는 버그
```

**설계 — 정산 규칙**

```text
BUY 측   reservedBalance -= 주문가격 × 체결수량   (예약분 전체 해제)
         balance         -= 체결가격 × 체결수량   (실제 지급액만)
         Position.quantity += 체결수량
SELL 측  Position.reservedQuantity -= 체결수량
         Position.quantity         -= 체결수량
         balance                   += 체결가격 × 체결수량
```

<a id="f8-1"></a>

### 8-1. 계좌 · 보유주식 도메인 `W5-D1 · 1.5h`

**목표**: 예약 · 해제 · 정산 계산이 Account / Position 메서드 안에서 정확히 일어난다. 아직 주문과 연결하지 않는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [JDBC-MyBatis-JPA › 엔티티를 안전하게 설계하기](../../07-트랜잭션-데이터접근/JDBC-MyBatis-JPA/JDBC-MyBatis-JPA.md#엔티티를-안전하게-설계하기) — Account / Position을 Entity로 설계
- [equals-hashCode › JPA 엔티티 — 가장 까다로운 경우](../../03-Java/equals-hashCode/equals-hashCode.md#jpa-엔티티--가장-까다로운-경우) — Entity의 equals / hashCode
- ★ [선착순-쿠폰-시스템 › 5) 1인 1매 — 조회가 아니라 제약으로](../../12-시스템설계/선착순-쿠폰-시스템/선착순-쿠폰-시스템.md#5-1인-1매--조회가-아니라-제약으로) — DB CHECK 제약을 마지막 방어선으로 두는 이유

**할 일**

1. [AI] Flyway `V2__create_account_position.sql`
    - `account(id, balance, reserved_balance)`, `CHECK (reserved_balance BETWEEN 0 AND balance)`
    - `position(id, account_id, stock_code, quantity, reserved_quantity)`, `UNIQUE(account_id, stock_code)`, 같은 CHECK
    - `orders.account_id` FK 추가
    - 시드: 계좌 1 (1,000,000원, 보유 없음) / 계좌 2 (0원, 005930 100주)
2. [직접] `Account` — `reserve(amount)`, `release(amount)`, `settleBuy(orderPrice, tradePrice, qty)`, `receiveCash(amount)`, `available()`. 모든 곱셈은 `Math.multiplyExact`
3. [직접] `Position` — `reserve(qty)`, `release(qty)`, `settleSell(qty)`, `increase(qty)`, `available()`
4. [직접] 위반 시 예외: 사용 가능 금액 초과 예약 → `InsufficientBalanceException`, 보유 초과 → `InsufficientQuantityException`
5. [AI] Entity / Repository, `GET /accounts/{id}` Controller + 응답 DTO
6. [AI] 테스트 Fixture 빌더 `AccountFixture.withCash(…).withStock(…)` → 동시성 테스트용 다수 계좌 생성
7. [직접] `AccountTest`, `PositionTest` 기대값 직접 계산

**판단할 것**

- Account / Position은 **JPA Entity를 도메인으로 겸용해도 되는가?** (Order와 달리 메모리에 오래 머물지 않고, Row Lock 대상이라 Entity가 자연스럽다 — 2-1과 다른 선택을 한 이유를 설명할 수 있게)
- DB CHECK 제약을 둘지 (추천: 둔다. 코드 버그가 있어도 DB가 마지막 방어선)

**결과물**

- 코드: `V2__…sql`, `Account`, `Position`, 예외 2종, Repository, `AccountController`
- 테스트: `AccountTest`, `PositionTest`, `AccountFixture`
- 기록: devlog (Entity 겸용 판단 이유)

**이렇게 나오면 성공**

```text
AccountTest  (잔고 1,000,000)
  ✔ reserve(700,000) → reserved 700,000, available 300,000
  ✔ reserve(300,001) 추가 → InsufficientBalanceException
  ✔ settleBuy(70,100, 70,000, 10) [701,000 예약 상태에서]
       → balance 300,000, reserved 0   (지급 700,000, 차액 1,000 해제)
  ✔ release(1) [reserved 0] → 예외
PositionTest  (보유 100주)
  ✔ reserve(50) → available 50
  ✔ settleSell(10) [50 예약 상태에서] → quantity 90, reserved 40

GET /accounts/1
{ "accountId":1, "balance":1000000, "reservedBalance":0, "availableBalance":1000000, "positions":[] }
GET /accounts/2
{ "accountId":2, "balance":0, "reservedBalance":0, "availableBalance":0,
  "positions":[{"stockCode":"005930","quantity":100,"reservedQuantity":0,"availableQuantity":100}] }
```

**완료 기준**

- [ ] 두 테스트 클래스 통과
- [ ] `GET /accounts/{id}`가 시드 데이터대로 응답

[↑ 일정표](#schedule)

<a id="f8-2"></a>

### 8-2. 자산 예약 · 해제 `W5-D2 · 2h`

**목표**: 주문하면 그만큼 돈 또는 주식이 묶이고, 취소하거나 거절되면 풀린다. 잔고가 부족한 주문은 엔진에 들어가지 못한다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [주문-결제-시스템 › 1) 주문과 결제를 다른 상태로 둔다](../../12-시스템설계/주문-결제-시스템/주문-결제-시스템.md#1-주문과-결제를-다른-상태로-둔다) — "주문 ≠ 자산 이동" — 예약이 필요한 이유
- ★ [주문-결제-시스템 › 6) 보상 — 되돌릴 수 없는 것을 반대 작업으로](../../12-시스템설계/주문-결제-시스템/주문-결제-시스템.md#6-보상--되돌릴-수-없는-것을-반대-작업으로) — Queue 거절 시 예약 해제 = 보상
- ★ [선착순-쿠폰-시스템 › 1) 수량이 넘치는 이유 — 확인과 차감 사이의 틈](../../12-시스템설계/선착순-쿠폰-시스템/선착순-쿠폰-시스템.md#1-수량이-넘치는-이유--확인과-차감-사이의-틈) — 예약에 동시성 문제가 생기는 지점 (9-1 예고)
- [ACID-격리수준 › 트랜잭션 범위를 정하는 기준](../../07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md#트랜잭션-범위를-정하는-기준) — 예약 위치 A / B 판단
- [주문-결제-시스템 › 3) 타임아웃은 "모름"이다](../../12-시스템설계/주문-결제-시스템/주문-결제-시스템.md#3-타임아웃은-모름이다) — timeout일 때 예약을 풀면 안 되는 이유

**할 일**

1. [직접] 예약 위치 결정 (아래 표) → ADR-004
2. [직접] `AssetReservationService.reserve(order)` — BUY: `price × quantity` 현금 예약 / SELL: `quantity` 주식 예약
3. [직접] `release(order, qty)` — BUY: `qty × order.price` / SELL: `qty`
4. [직접] 주문 흐름에 연결: 검증 → **예약** → `OrderProcessor.place` → 결과별 처리
    - Queue 거절(503 `ENGINE_BUSY`), 저장 실패(Fail-Stop) → 처리 안 된 것이 확실 → **해제**
    - timeout(202 `PENDING`) → 처리됐을 수 있다 → **해제하지 않는다** (7-1 판단). 여기서 풀면 체결된 주문의 돈이 새어 나간다
5. [직접] 취소 흐름에 연결: 엔진 취소 성공 → `release(order, order.remaining())`
6. [AI] 예외 → 응답 매핑: `INSUFFICIENT_BALANCE`, `INSUFFICIENT_QUANTITY` (409)
7. [AI] 테스트 골격: 잔고 부족, 보유 부족, 취소 해제, 엔진 거절 시 해제

**판단할 것** → ADR-004 (이번 주 가장 중요한 결정)

| 방식 | 장점 | 단점 |
|---|---|---|
| A. Order API에서 별도 트랜잭션으로 예약 후 Queue 투입 | Worker 트랜잭션이 짧음, 계좌 Lock이 Worker로 번지지 않음 | 예약 후 Queue 거절 / 서버 다운 시 예약이 남을 수 있음 → 보상 해제 필요 |
| B. Worker 트랜잭션 안에서 예약 | 원자성 확실 | 다른 종목 Worker들이 같은 계좌 Row Lock으로 경합 |

- A를 고른다면: 예약과 함께 주문을 `ACCEPTED` 상태로 같은 트랜잭션에 저장하면 고아 예약을 찾을 수 있다. 대신 sequence 부여 시점과 복구 로직이 달라진다
- ADR에 아래 세 장애 시나리오의 결과를 **꼭** 쓴다 (면접 꼬리 질문이 정확히 여기로 온다)
    1. 예약 Commit 직후, Queue에 넣기 전에 서버가 죽으면?
    2. Queue 안에서 처리 대기 중에 서버가 죽으면? (Command 유실 — 7-1)
    3. 취소가 엔진에서 끝나고 예약 해제 전에 서버가 죽으면?
    - 다 막지 못해도 된다. "어떤 상태가 남고, 무엇으로 찾아서 고치는가"(예: 재시작 시 `예약금 ≠ 열린 주문 합`인 계좌를 찾아 보정)를 말할 수 있으면 된다

**결과물**

- 코드: `AssetReservationService`, 주문 / 취소 흐름 연결
- 테스트: `ReservationTest`
- 기록: ADR-004 "자산 예약 위치", devlog

**이렇게 나오면 성공**

```text
계좌 1 (1,000,000원)
POST /orders BUY 70,000 × 10      → 201
GET /accounts/1  → balance 1,000,000, reservedBalance 700,000, availableBalance 300,000
POST /orders BUY 70,000 × 5       → 409 {"code":"INSUFFICIENT_BALANCE"}   (350,000 > 300,000)
DELETE /orders/{첫 주문}           → 200
GET /accounts/1  → reservedBalance 0, availableBalance 1,000,000

계좌 2 (005930 100주)
POST /orders SELL × 60 → 201 / SELL × 50 → 409 {"code":"INSUFFICIENT_QUANTITY"}

ReservationTest
  ✔ BUY → 현금 예약 / SELL → 주식 예약
  ✔ 잔고 · 보유 부족 → 거절되고 엔진에 들어가지 않음
  ✔ 부분 체결 후 취소 → 잔량분만 해제
  ✔ 엔진이 503으로 거절 → 예약이 남지 않음
  ✔ timeout(202 PENDING) → 예약 유지, 이후 체결되면 정상 정산
```

**완료 기준**

- [ ] `ReservationTest` 통과
- [ ] ADR-004에 선택 · 이유 · 서버 다운 시나리오가 있다

[↑ 일정표](#schedule)

<a id="f8-3"></a>

### 8-3. 정산 (동기) `W5-D3 · 2h`

**목표**: 체결이 일어나면 Buyer · Seller의 돈과 주식이 정산 규칙대로 움직인다. 가격 개선 차액까지 정확히.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [AOP-Proxy-Transactional › 롤백 규칙](../../05-Spring/AOP-Proxy-Transactional/AOP-Proxy-Transactional.md#롤백-규칙) — 정산 중 예외 → 전체 Rollback이 되는 조건
- ★ [AOP-Proxy-Transactional › 예외를 잡으면 롤백이 안 된다](../../05-Spring/AOP-Proxy-Transactional/AOP-Proxy-Transactional.md#예외를-잡으면-롤백이-안-된다) — 정산 코드에서 try-catch를 조심할 곳
- [ACID-격리수준 › 원자성 — 되돌리기는 어떻게 가능한가](../../07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md#원자성--되돌리기는-어떻게-가능한가) — 체결 저장과 정산을 같은 트랜잭션에 둘 때

```java
@Transactional
public void settle(Trade trade) {
    Account buyer = ..., seller = ...;           // Lock은 9-1, 9-2에서 강화
    buyer.settleBuy(trade.buyOrderPrice(), trade.price(), trade.quantity());
    buyerPosition.increase(trade.quantity());    // 없으면 새로 생성
    sellerPosition.settleSell(trade.quantity());
    seller.receiveCash(Math.multiplyExact(trade.price(), trade.quantity()));
}
```

**할 일**

1. [직접] `SettlementService.settle(Trade)` — 위 코드. Buyer Position이 없으면 생성
2. [직접] 정산 호출 위치 결정 후 연결 (아래 판단)
3. [AI] 정산 테스트 골격 + 정산 도중 예외 주입(예: Seller Position 저장 시 예외) 테스트
4. [직접] 수동 데모: 아래 "성공" 시나리오를 `demo.http`에 추가해 실행

**판단할 것**

- **정산을 체결 저장과 같은 트랜잭션에서 할지, 체결 Commit 후 별도로 할지**
    - 같은 트랜잭션(추천): 원자적. 대신 체결 처리가 계좌 Lock을 기다리게 된다
    - 별도: 체결은 빠르지만 그 사이 서버가 죽으면 "체결은 됐는데 정산 안 된" 상태
    - 어느 쪽이든 그 단점이 **Week 7에서 Kafka + Outbox로 분리하는 이유**가 된다 → devlog에 기록

**결과물**

- 코드: `SettlementService`, 체결 흐름에 정산 연결
- 테스트: `SettlementTest`
- 기록: devlog (정산 위치 판단과 그 단점), `demo.http` 갱신

**이렇게 나오면 성공**

```text
시드: 계좌 1 = 1,000,000원 / 계좌 2 = 005930 100주

POST SELL 70,000 × 10 (계좌 2)  → 계좌 2 reservedQuantity 10
POST BUY  70,100 × 10 (계좌 1)  → 701,000 예약 → 즉시 70,000에 10주 체결 → 정산

GET /accounts/1
{ "balance":300000, "reservedBalance":0, "availableBalance":300000,
  "positions":[{"stockCode":"005930","quantity":10,"reservedQuantity":0}] }
GET /accounts/2
{ "balance":700000, "reservedBalance":0,
  "positions":[{"stockCode":"005930","quantity":90,"reservedQuantity":0}] }

SettlementTest
  ✔ 위 시나리오 결과 그대로 (가격 개선 1,000원 해제 포함)
  ✔ BUY 20 vs SELL 10 → 10주분만 정산, 나머지 10주분 예약 유지
  ✔ 정산 중 예외 → Account · Position · Trade 모두 Rollback
  ✔ 두 계좌 현금 합계 = 정산 전후 동일 (1,000,000)
```

**완료 기준**

- [ ] `SettlementTest` 통과
- [ ] 데모 시나리오 결과가 위와 같다

[↑ 일정표](#schedule)

---

<a id="f9"></a>

## 9. 자산 동시성: Lock & Deadlock

**왜**: "동시 주문에서 잔고가 초과 사용되지 않게 어떻게 막았나요?" — 문제를 먼저 재현하고 고친 기록이 핵심.

**설계 — 문제**

```text
잔고 1,000,000원
Thread A → 800,000원 예약 / Thread B → 800,000원 예약
→ 둘 다 이전 잔고를 읽으면 둘 다 성공

Trade 1: Buyer A, Seller B → A Lock → B Lock 대기
Trade 2: Buyer B, Seller A → B Lock → A Lock 대기
→ Deadlock
```

**설계 — 해결**

```text
@Lock(PESSIMISTIC_WRITE)  =  SELECT ... FOR UPDATE

Pessimistic을 고른 이유
  같은 계좌에 주문과 정산이 몰리는 도메인 → 충돌이 잦다
  Optimistic은 충돌 시 재시도 비용이 크고, 재시도 실패는 곧 주문 실패
  → "항상 우월"이 아니라 충돌 빈도와 실패 비용에 따라 고른다

Lock 순서 (전역 규칙)
  Account: id 오름차순 → Position: (account_id, stock_code) 오름차순
  SELECT * FROM account WHERE id IN (?, ?) ORDER BY id FOR UPDATE;
```

<a id="f9-1"></a>

### 9-1. 초과 예약 재현 → Pessimistic Lock `W6-D1 · 1.5h`

**목표**: 동시 예약에서 돈이 두 번 쓰이는 현상을 실제로 만들어 기록하고, Row Lock으로 막는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [ACID-격리수준 › 격리 수준으로는 막지 못하는 것 — 갱신 손실](../../07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md#격리-수준으로는-막지-못하는-것--갱신-손실) — Lost Update가 왜 격리 수준으로 안 막히는지
- ★ [낙관적-비관적-락 › 비관적 락 — 미리 잠근다](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#비관적-락--미리-잠근다) — `SELECT ... FOR UPDATE` 동작
- ★ [낙관적-비관적-락 › 비관적 락 — JPA](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#비관적-락--jpa) — `@Lock(PESSIMISTIC_WRITE)` 코드
- ★ [MVCC › 재고·잔액은 스냅숏을 믿지 않는다](../../07-트랜잭션-데이터접근/MVCC/MVCC.md#재고잔액은-스냅숏을-믿지-않는다) — 잔고 확인에 일반 조회를 쓰면 안 되는 이유
- [낙관적-비관적-락 › 정확성 — 락이 없으면 데이터가 깨진다](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#정확성--락이-없으면-데이터가-깨진다) — 재현 실험 설계 참고
- [낙관적-비관적-락 › 낙관적 락 vs 비관적 락](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#낙관적-락-vs-비관적-락) — ADR-005 근거
- [낙관적-비관적-락 › 인덱스 없는 비관적 락의 함정](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#인덱스-없는-비관적-락의-함정) — FOR UPDATE가 PK로 걸리는지 확인

**할 일**

1. [AI] 6번 `ConcurrencyRunner`를 변형한 `OverReservationTest` — 잔고 1,000,000원 계좌에 BUY 80,000 × 10(= 800,000) 동시 2건 / 동시 100건
2. [직접] **Lock 없이 먼저 실행** → 성공 건수, 최종 `reservedBalance`, Σ(열린 BUY 주문 금액)을 출력하게 하고 기록
3. [직접] 현상 해석: 두 트랜잭션이 같은 잔고를 읽고 각자 덮어쓰는 **Lost Update** — `reservedBalance`는 800,000인데 열린 주문은 1,600,000
4. [직접] `AccountRepository.findByIdForUpdate(id)` — `@Lock(PESSIMISTIC_WRITE)`, 예약 · 해제 · 정산이 모두 이 메서드로 계좌를 읽게 변경
5. [직접] Position도 같은 방식 (`findForUpdate(accountId, stockCode)`)
6. [직접] 같은 테스트 재실행 → 정확히 1건 성공
7. [직접] ADR-005 "Pessimistic Lock을 고른 이유" (위 설계 근거 + 2번 수치)

**판단할 것**

- Lock을 거는 범위: 예약 / 해제 / 정산 각각에서 계좌를 어떻게 읽는지 전부 점검
- Lock 없는 버전을 테스트에 남기는 방법 (추천: 6번처럼 test 소스의 별도 구현으로, 실패를 assert, `@Tag("reproduce")`로 기본 빌드에서 제외)

**결과물**

- 코드: `findByIdForUpdate`, Position 동일, 서비스 변경
- 테스트: `OverReservationTest` (Lock 없음 → 위반 assert / Lock 있음 → 1건 성공)
- 기록: devlog에 Lock 없음 수치 원문, ADR-005

**이렇게 나오면 성공**

```text
Lock 없음 (동시 2건)
  성공 2건 / 거절 0건
  account.reservedBalance = 800,000
  Σ 열린 BUY 주문 금액     = 1,600,000   ← 불일치 (Lost Update)

Lock 있음 (동시 100건)
  성공 1건 / INSUFFICIENT_BALANCE 99건
  account.reservedBalance = 800,000 = Σ 열린 BUY 주문 금액

동시 SELL (보유 100주, SELL 60주 × 동시 10건) → 성공 1건
```

**완료 기준**

- [ ] Lock 없음 실패 수치가 devlog에 있다
- [ ] Lock 있음: 잔액 · 보유 초과 불가 테스트 통과
- [ ] ADR-005 작성

[↑ 일정표](#schedule)

<a id="f9-2"></a>

### 9-2. Deadlock 재현 → Lock 순서 `W6-D2 · 1.5h`

**목표**: 두 계좌가 서로 사고파는 정산이 동시에 일어날 때의 Deadlock을 재현하고, Lock 순서 규칙으로 없앤다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [낙관적-비관적-락 › 계좌 이체 — 락 순서를 코드로 강제한다](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#계좌-이체--락-순서를-코드로-강제한다) — **오늘 구현과 거의 같은 코드**
- ★ [낙관적-비관적-락 › 데드락 — 비관적 락의 실패 모드](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#데드락--비관적-락의-실패-모드) — DB가 Deadlock을 감지해 한쪽을 실패시키는 과정
- ★ [Thread-동기화 › 데드락이 만들어지는 조건](../../04-동시성/Thread-동기화/Thread-동기화.md#데드락이-만들어지는-조건) — 4가지 조건 중 Lock 순서가 깨는 것은 무엇인지
- [장애분석-성능개선 › 락을 항상 같은 순서로 잡는다 (데드락 예방)](../../10-테스트-운영/장애분석-성능개선/장애분석-성능개선.md#락을-항상-같은-순서로-잡는다-데드락-예방) — 같은 원리의 Java 코드 버전
- [낙관적-비관적-락 › 데드락과 락 대기를 모니터링한다](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#데드락과-락-대기를-모니터링한다) — `deadlock detected` 로그 읽기
- [그래프-문제해결 › 순환 탐지 — 3색 표시](../../02-알고리즘/그래프-문제해결/그래프-문제해결.md#순환-탐지--3색-표시) — DB의 Deadlock 감지 = 대기 그래프에서 사이클 찾기

**할 일**

1. [AI] `CrossSettlementTest` — 계좌 A, B가 서로 현금 · 주식을 충분히 보유. "A가 사고 B가 판다" Trade와 "B가 사고 A가 판다" Trade를 각 100건씩 동시에 `settle`
2. [직접] 현재 코드(Buyer 먼저, Seller 나중에 Lock)로 실행 → `deadlock detected` 발생 확인, 로그 원문 보관
3. [직접] `findAllForUpdateOrderById(List<Long> ids)` — `@Query("select a from Account a where a.id in :ids order by a.id")` + `@Lock`
4. [직접] Position도 `(accountId, stockCode)` 오름차순으로 한 번에 잠그기
5. [직접] 전역 규칙을 코드 주석과 ADR-005에 추가: **Account(id 순) → Position((account_id, stock_code) 순)**
6. [직접] 같은 테스트 재실행 → 전부 완료

**판단할 것**

- 왜 `id IN (...)`만으로는 부족하고 `ORDER BY`가 필요한가 (DB가 잠그는 순서를 보장하려고)
- PostgreSQL은 Deadlock을 감지하면(기본 1초 뒤) 한쪽을 실패시킨다 → "멈춤"이 아니라 "실패"로 나타난다
- **실제 흐름에서 Deadlock은 어디서 나는가?** 같은 종목의 체결은 Lock / Worker 때문에 어차피 한 줄로 처리돼 서로 엇갈리지 않는다. 엇갈리는 건 **서로 다른 종목**의 체결이 같은 두 계좌를 반대 방향으로 정산할 때다 (A가 삼성전자를 사고 B가 팔 때, 동시에 B가 NAVER를 사고 A가 팔 때). 테스트도 종목 2개로 만든다 — "단위 테스트로만 재현했나요?"라는 꼬리 질문에 답할 수 있게
- 재현 테스트(정렬 전 버전)는 6번 규칙대로 `@Tag("reproduce")`로 기본 빌드에서 뺀다

**결과물**

- 코드: 정렬 Lock 메서드 2개, `SettlementService` 변경
- 테스트: `CrossSettlementTest`
- 기록: devlog에 Deadlock 로그 원문, ADR-005 갱신

**이렇게 나오면 성공**

```text
정렬 전
  ERROR: deadlock detected
  Detail: Process 812 waits for ShareLock on transaction 1204; blocked by process 815.
          Process 815 waits for ShareLock on transaction 1203; blocked by process 812.
  → 200건 중 N건 실패

정렬 후
  CrossSettlementTest > 교차_정산_200건_동시() PASSED   (실패 0건)
  두 계좌 현금 합계 · 005930 수량 합계 정산 전후 동일
```

**완료 기준**

- [ ] Deadlock 로그 원문이 devlog에 있다
- [ ] 정렬 후 `CrossSettlementTest` 통과

[↑ 일정표](#schedule)

<a id="f9-3"></a>

### 9-3. 자산 불변식 · 트랜잭션 범위 `W6-D3 · 1.5h` `🏷 v0.2-account`

**목표**: 주문 · 취소 · 체결 · 정산이 뒤섞인 동시 상황에서도 돈과 주식이 한 원, 한 주도 새지 않는다는 것을 검증하고 Tag를 찍는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [낙관적-비관적-락 › 트랜잭션 안에 외부 호출을 넣지 않는다 — 락을 쓸 때는 더 치명적이다](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#트랜잭션-안에-외부-호출을-넣지-않는다--락을-쓸-때는-더-치명적이다) — 트랜잭션 범위 점검 기준
- [ACID-격리수준 › 긴 트랜잭션을 감시한다](../../07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md#긴-트랜잭션을-감시한다) — Lock 유지 시간 관찰
- [낙관적-비관적-락 › 낙관적 락 — JPA `@Version`](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#낙관적-락--jpa-version) — (선택 D4) Optimistic 버전 구현
- [낙관적-비관적-락 › 재시도 — 반드시 트랜잭션 밖에서](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#재시도--반드시-트랜잭션-밖에서) — (선택 D4) 재시도 위치
- [로그-메트릭-트레이싱 › 로그는 뜨거운 경로에서 비싸다](../../10-테스트-운영/로그-메트릭-트레이싱/로그-메트릭-트레이싱.md#로그는-뜨거운-경로에서-비싸다) — 트랜잭션 안 로그 점검 기준

**할 일**

1. [AI] `InvariantChecker.checkAssets()` — 6번 "자산" 불변식을 SQL로 (정의는 6번대로) → [직접] 검토
2. [AI] `MixedConcurrencyTest` — 계좌 10개, 종목 2개, 2,000건(주문 80% + 취소 20%) 동시, 두 엔진 모드
3. [직접] 실행 → 위반이 나오면 어디서 새는지 추적 (가장 흔한 원인: 가격 개선 차액 미해제, 취소 시 해제 금액 계산)
4. [직접] 트랜잭션 범위 점검 — 트랜잭션 안의 로그 출력, 외부 호출, 불필요한 조회 제거
5. [직접] `git tag v0.2-account` — Kafka에서 막혀도 돌아올 수 있는 지점
6. (선택 · D4) [직접] `@Version` + 재시도로 Optimistic 버전을 짜서 `OverReservationTest` 조건으로 비교 → benchmarks.md "부록"

**판단할 것**

- "모든 정산이 끝난 뒤 예약금 = 열린 주문 합" 불변식은 **동기 정산인 지금은 언제나** 성립해야 한다. Week 7 이후에는 "정산 완료 후"에만 성립 → 그 차이를 devlog에 적어두기

**결과물**

- 코드(test): `InvariantChecker.checkAssets()`, `MixedConcurrencyTest`
- 기록: devlog (발견한 누수와 수정 내역), Tag

**이렇게 나오면 성공**

```text
MixedConcurrencyTest
  ✔ [1] mode=lock          tradingViolations=[] assetViolations=[]
  ✔ [2] mode=single-writer tradingViolations=[] assetViolations=[]

assetViolations가 비어 있다는 것의 의미
  - 모든 계좌 0 <= reserved <= balance
  - 전체 현금 합계 = 시드 합계
  - 종목별 보유 수량 합계 = 시드 합계
  - 계좌별 reservedBalance = Σ(열린 BUY 잔량 × 주문가)
  - 계좌별 reservedQuantity = Σ(열린 SELL 잔량)

$ git tag
v0.1-trading
v0.2-account
```

**완료 기준**

- [ ] `MixedConcurrencyTest` 두 모드 통과
- [ ] `git tag v0.2-account`

[↑ 일정표](#schedule)

---

<a id="f10"></a>

## 10. 이벤트: Kafka · Outbox · Idempotency

**왜**: "DB Commit 후 발행이 실패하면?", "메시지가 중복 전달되면?" — 이벤트 정합성의 두 질문에 답한다.

**설계 — 왜 분리하는가**

```text
Worker가 정산까지 직접 하면 → 체결 처리에 계좌 Lock 대기가 섞이고, 정산 장애가 체결 중단으로 번진다
Trading: 누가 누구와 몇 주 체결했는가 / Settlement: 돈과 주식 반영

대가: Eventual Consistency — 주문 응답 직후 계좌를 조회하면 아직 정산 전일 수 있다
```

**설계 — 이벤트와 Partition**

```json
{ "eventId": "uuid", "tradeId": 10001, "stockCode": "005930",
  "buyerAccountId": 1, "sellerAccountId": 2,
  "buyOrderPrice": 70100, "price": 70000, "quantity": 10,
  "executedAt": "2026-10-07T10:00:00" }
```

```text
Topic: trade-executed / Key: stockCode → 같은 종목은 같은 Partition → 순서 보장 (현재가에 필요)
Trade-off: 정산은 "계좌 단위" 순서가 더 중요하지만 Key는 하나만 고를 수 있다
  → 정산은 순서에 의존하지 않게 (Row Lock + 예약 기반 차감 → 적용 순서가 바뀌어도 결과 동일)
Hot Partition 가능성도 기록

Consumer Group: settlement / market-data 독립 → 한쪽 장애가 다른 쪽을 막지 않는다
```

**설계 — Outbox (발행 신뢰성)**

```text
문제: Trade INSERT 성공 → Kafka Publish 실패 → Trade는 있는데 정산이 안 됨

BEGIN (5번의 Worker 트랜잭션에 추가, 새 트랜잭션 X)
  Order / Trade 저장
  Outbox INSERT (eventId, eventType, aggregateId, payload, status, createdAt)
COMMIT
Publisher: PENDING id 순 조회 → 발행 → 성공 시 PUBLISHED, 실패 시 다음 주기에 재시도

Outbox만으로 중복이 사라지지 않는다 — 재시도로 두 번 발행될 수 있다 → Idempotency 필요
```

**설계 — Idempotency (중복 안전성)**

```text
잘못된 방식: eventId 조회 → 없음 → 정산 → 저장   (동시 처리 시 둘 다 "없음" → 이중 반영)

올바른 방식
BEGIN
  processed_event INSERT (event_id PK)   ← 중복 판정은 DB Unique 제약에 맡긴다
  정산
COMMIT
→ Offset Commit   (At-least-once + Idempotent = Effectively-once)

PostgreSQL 함정: 트랜잭션 안에서 Duplicate Key 예외가 나면 그 트랜잭션은 abort 상태
  → 예외 시 전체 Rollback 후 ACK, 또는 INSERT ... ON CONFLICT DO NOTHING 후 영향 행 0이면 skip
```

<a id="f10-1"></a>

### 10-1. Outbox + Kafka 발행 `W7-D1 · 2h`

**목표**: 체결이 Commit되면 그 사실이 반드시 Kafka 토픽까지 간다. (아직 정산은 동기 그대로, 소비자는 없음)

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [메시지-중복-재시도-Outbox › 4) Outbox 패턴 — 발행을 DB 쓰기로 바꾼다](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#4-outbox-패턴--발행을-db-쓰기로-바꾼다) — Outbox가 푸는 문제
- ★ [메시지-중복-재시도-Outbox › 폴링 릴레이](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#폴링-릴레이) — `OutboxPublisher` 구현 형태
- ★ [Kafka-구조와-동작 › 1) 프로듀서가 파티션을 고른다](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#1-프로듀서가-파티션을-고른다) — Key = stockCode → 같은 Partition
- ★ [Kafka-구조와-동작 › 안전한 프로듀서 설정](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#안전한-프로듀서-설정) — `acks=all` 등 Producer 설정
- [Kafka-구조와-동작 › 5) 복제와 ISR — `acks=all`의 함정](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#5-복제와-isr--acksall의-함정) — 단일 노드에서 acks=all의 의미
- [Kafka-구조와-동작 › 2) 파티션을 늘리면 기존 키가 이사한다](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#2-파티션을-늘리면-기존-키가-이사한다) — partitions 3으로 정할 때
- [동기-비동기와-메시지큐 › 커밋 이후로 발행 미루기](../../11-메시징/동기-비동기와-메시지큐/동기-비동기와-메시지큐.md#커밋-이후로-발행-미루기) — Outbox 대신 After-Commit 발행과 비교

**할 일**

1. [AI] `docker-compose.yml`에 Kafka(KRaft 단일 노드) 추가, spring-kafka 의존성 · Producer 설정(JSON, `acks=all`), Testcontainers Kafka
2. [AI] Flyway `V3__create_outbox_processed_event.sql`
    - `outbox(id, event_id UNIQUE, event_type, aggregate_id, payload jsonb, status, created_at, published_at)`, `INDEX(status, id)`
    - `processed_event(event_id PK, processed_at)` (10-3에서 사용)
3. [AI] `TradeExecutedEvent` record (위 JSON), `NewTopic` 빈 (`trade-executed`, partitions 3)
4. [직접] `MatchResultWriter`에 Trade마다 Outbox INSERT 추가 — **같은 트랜잭션**. payload에 `tradeId`가 들어가므로 Trade INSERT(ID 부여) 뒤에 만든다
5. [직접] `OutboxPublisher` — `@Scheduled(fixedDelay = 200)`: PENDING을 id 순으로 최대 100건 → `kafkaTemplate.send(topic, stockCode, payload).get(3s)` → 성공 건만 PUBLISHED. 실패하면 그 건에서 멈추고 다음 주기에 재시도 (순서 유지)
6. [직접] kafka CLI로 토픽 설명 · 메시지 확인 (아래)

**판단할 것**

- 실패 시 "그 건에서 멈춤" vs "건너뛰고 다음 건": 같은 종목 순서를 지키려면 멈춤
- 다중 인스턴스면 Publisher가 중복 발행 → 이 프로젝트는 단일 인스턴스로 범위를 정하고 README에 기록 (`FOR UPDATE SKIP LOCKED`는 선택)

**결과물**

- 코드: `V3__…sql`, `TradeExecutedEvent`, `OutboxEvent` Entity/Repository, `OutboxPublisher`, Kafka 설정
- 테스트: `OutboxTest` — 체결 → Outbox 1건 → Testcontainers Kafka에서 수신
- 기록: devlog, ai-log (Kafka 설정을 AI에게 맡긴 부분)

**이렇게 나오면 성공**

```text
$ kafka-topics --bootstrap-server localhost:9092 --describe --topic trade-executed
Topic: trade-executed  PartitionCount: 3  ReplicationFactor: 1

데모 체결 1건 후
SELECT event_type, aggregate_id, status FROM outbox;
 TRADE_EXECUTED | 1 | PUBLISHED

$ kafka-console-consumer --bootstrap-server localhost:9092 --topic trade-executed \
    --from-beginning --property print.key=true
005930  {"eventId":"9b1c…","tradeId":1,"stockCode":"005930","buyerAccountId":1, … ,"quantity":10}

OutboxTest
  ✔ 체결 1건 → outbox 1건 (Trade와 같은 트랜잭션)
  ✔ Trade 저장 실패 → outbox도 없음
  ✔ Publisher 실행 후 → Kafka에서 같은 eventId 수신, status PUBLISHED
```

**완료 기준**

- [ ] `OutboxTest` 통과
- [ ] CLI로 Key = stockCode인 메시지를 직접 봤다

[↑ 일정표](#schedule)

<a id="f10-2"></a>

### 10-2. Settlement Consumer `W7-D2 · 1.5h`

**목표**: 정산이 체결 흐름에서 빠져나와 Kafka Consumer가 한다. 체결은 계좌 Lock을 더 이상 기다리지 않는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [Kafka-구조와-동작 › 3) 컨슈머 그룹이 파티션을 나눠 갖는다](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#3-컨슈머-그룹이-파티션을-나눠-갖는다) — settlement / market-data Group 분리
- ★ [Kafka-구조와-동작 › 4) 오프셋은 컨슈머가 커밋한다](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#4-오프셋은-컨슈머가-커밋한다) — Offset Commit 시점
- ★ [Kafka-구조와-동작 › 처리 후에 커밋하는 컨슈머](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#처리-후에-커밋하는-컨슈머) — DB Commit 이후 Offset Commit
- [Kafka-구조와-동작 › 7) 컨슈머가 "죽었다"고 판정되는 두 경로](../../11-메시징/Kafka-구조와-동작/Kafka-구조와-동작.md#7-컨슈머가-죽었다고-판정되는-두-경로) — 정산이 오래 걸릴 때 리밸런싱
- [동기-비동기와-메시지큐 › 동기 · 비동기와 블로킹 · 논블로킹](../../11-메시징/동기-비동기와-메시지큐/동기-비동기와-메시지큐.md#동기--비동기와-블로킹--논블로킹) — Eventual Consistency를 설명할 때

**할 일**

1. [직접] `SettlementConsumer` — `@KafkaListener(topics = "trade-executed", groupId = "settlement")` → 이벤트를 Trade 정보로 바꿔 `SettlementService.settle` 호출
2. [직접] 체결 흐름(8-3에서 연결한 곳)에서 동기 정산 호출 제거
3. [AI] Consumer 설정: JSON 역직렬화, `AckMode` (기본 BATCH / RECORD 중 선택), 에러 핸들러 기본값
4. [AI] Awaitility 기반 테스트 골격 — `await().atMost(5, SECONDS).until(...)`
5. [직접] 8-3 `SettlementTest`, 9-3 `MixedConcurrencyTest`를 "정산 완료까지 기다린 뒤 검증"으로 수정
6. [직접] 수동 확인: 주문 직후 / 1초 뒤 계좌 조회 비교

**판단할 것**

- Offset Commit이 DB Commit **이후**에 일어나는지 (리스너 메서드가 정상 종료된 뒤 커밋되는 설정인지 확인)
- 사용자에게 보이는 변화 — "주문 응답 직후 계좌 조회 시 아직 정산 전일 수 있다" → README에 Eventual Consistency로 기록
- 그 결과 생기는 제약: **방금 산 주식은 정산 전까지 팔 수 없고, 판 돈도 정산 전까지 쓸 수 없다** (Position · balance가 정산 때 바뀌므로). 버그가 아니라 범위를 정한 결정이라고 설명할 수 있어야 한다 — 실제 증권사는 결제(T+2) 전에도 "매도 가능 수량"을 따로 계산해 당일 재매도를 허용하지만, 이 프로젝트는 단순화를 위해 정산 완료 후에만 허용한다

**결과물**

- 코드: `SettlementConsumer`, 체결 흐름에서 정산 제거
- 테스트: 비동기로 바뀐 `SettlementTest`, `MixedConcurrencyTest`
- 기록: devlog (동기 → 비동기로 바뀐 API 동작)

**이렇게 나오면 성공**

```text
POST BUY (체결 발생) → 201
즉시 GET /accounts/1   → reservedBalance 701,000 (아직 정산 전일 수 있음)
~100ms 뒤 GET /accounts/1 → balance 300,000, reservedBalance 0, 005930 10주

로그
  [settlement-0-C-1] settled trade=1 buyer=1 seller=2 qty=10

$ kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group settlement
GROUP       TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
settlement  trade-executed  0          12              12              0

SettlementTest (비동기)              ✔
MixedConcurrencyTest (정산 완료 후)  ✔ assetViolations = []
```

**완료 기준**

- [ ] 체결 흐름 코드에 `SettlementService` 호출이 없다
- [ ] 비동기 기준으로 바꾼 테스트 통과, LAG 0 확인

[↑ 일정표](#schedule)

<a id="f10-3"></a>

### 10-3. Idempotency · Kafka 장애 `W7-D3 · 2h` `🏷 v0.3-event`

**목표**: 같은 이벤트가 몇 번 오든 정산은 한 번, Kafka가 잠시 죽어도 체결은 계속되고 나중에 정산까지 따라잡는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [메시지-중복-재시도-Outbox › 1) 커밋 순서가 배달 보장을 정한다](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#1-커밋-순서가-배달-보장을-정한다) — At-least-once가 되는 이유
- ★ [메시지-중복-재시도-Outbox › 3) 멱등 컨슈머 — 중복을 결과에서 지운다](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#3-멱등-컨슈머--중복을-결과에서-지운다) — processed_event 방식의 원리
- ★ [메시지-중복-재시도-Outbox › 멱등 컨슈머](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#멱등-컨슈머) — 구현 코드
- ★ [분산락-멱등성 › 최종 방어선 — DB 유니크 제약](../../08-캐시-Redis/분산락-멱등성/분산락-멱등성.md#최종-방어선--db-유니크-제약) — 중복 판정을 DB Unique에 맡기는 이유
- [메시지-중복-재시도-Outbox › 2) exactly-once의 현실](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#2-exactly-once의-현실) — "Effectively-once"라고 말하는 근거
- [메시지-중복-재시도-Outbox › 5) 재시도 — 무엇을 다시 할 것인가](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#5-재시도--무엇을-다시-할-것인가) — Publisher 재시도 판단
- [메시지-중복-재시도-Outbox › 오류를 가려서 재시도하고, 넘치면 DLQ로](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#오류를-가려서-재시도하고-넘치면-dlq로) — 범위 밖이지만 면접 꼬리 질문 대비
- [09-장애-대응 › Connection Refused](../../infra/09-장애-대응/09-장애-대응.md#connection-refused) — Kafka를 내렸을 때 보이는 증상 읽기

**할 일**

1. [직접] PostgreSQL 함정 대응 방식 선택 (아래 판단) → ADR-006
2. [직접] Consumer 트랜잭션 — `processed_event` INSERT → (중복이면 skip) → 정산 → Commit. 한 메서드 · 한 `@Transactional`
3. [AI] 테스트 골격
    - 같은 이벤트를 `KafkaTemplate`으로 2번 발행
    - 같은 이벤트로 Consumer 처리 메서드를 2개 스레드에서 동시 호출
    - Publisher가 실패하는 `KafkaTemplate`(Mock)일 때 PENDING 유지 → 정상 복구 후 PUBLISHED
4. [AI] `InvariantChecker.checkEvents()` — 6번 "이벤트" 불변식
5. [직접] 수동 장애 시나리오 (아래 "성공"의 순서대로) 실행하고 결과 기록
6. [직접] `git tag v0.3-event`

**판단할 것** → ADR-006

- 트랜잭션 안에서 Duplicate Key 예외가 나면 PostgreSQL은 그 트랜잭션을 abort 상태로 만든다
    - (a) 예외를 잡지 말고 전체 Rollback → 바깥에서 "이미 처리됨"으로 보고 ACK
    - (b) `INSERT ... ON CONFLICT DO NOTHING` → 영향 행 0이면 정산 건너뛰기 (추천: 흐름이 단순)
- 왜 "eventId 조회 후 없으면 처리"가 안 되는지 동시 테스트로 직접 보여줄 수 있으면 더 좋다

**결과물**

- 코드: Consumer 멱등 처리, `checkEvents()`
- 테스트: `IdempotencyTest`, `OutboxRetryTest`
- 기록: ADR-006, devlog에 장애 시나리오 결과, Tag

**이렇게 나오면 성공**

```text
IdempotencyTest
  ✔ 같은 이벤트 2번 발행 → 계좌 변화 1번, processed_event 1행
  ✔ 같은 이벤트 동시 2스레드 처리 → 계좌 변화 1번
OutboxRetryTest
  ✔ 발행 실패 → status PENDING 유지 → 복구 후 PUBLISHED, 순서 유지

수동 장애 시나리오
  1) docker compose stop kafka
  2) 주문 20건 → 모두 201 (체결은 계속된다)
     SELECT status, count(*) FROM outbox GROUP BY status;   → PENDING | 12
  3) docker compose start kafka
  4) 수 초 뒤                                               → PUBLISHED | 12, PENDING 0
     GET /accounts/*  → 정산 완료,  checkAssets() = [],  checkEvents() = []

$ git tag
v0.1-trading  v0.2-account  v0.3-event
```

**완료 기준**

- [ ] 두 테스트 클래스 통과
- [ ] 수동 장애 시나리오 결과가 devlog에 있다
- [ ] ADR-006, `git tag v0.3-event`

[↑ 일정표](#schedule)

---

<a id="f11"></a>

## 11. 체결 내역 조회: Index · Cursor

**왜**: "데이터가 수백만 건이면 조회를 어떻게 최적화하나요?" — 일부러 평범하게 만들고, 느려지는 조건을 수치로 찾고, 고친다.

**설계**

```sql
-- V1: Offset
SELECT * FROM trade WHERE stock_code = ? ORDER BY id DESC LIMIT 50 OFFSET ?;

-- Index
CREATE INDEX idx_trade_stock_id ON trade (stock_code, id DESC);

-- V2: Cursor
SELECT * FROM trade
WHERE stock_code = ? AND id < ?
ORDER BY id DESC
LIMIT 51;   -- size + 1로 hasNext 판단
```

```json
{ "items": [], "nextCursor": 999950, "hasNext": true }
```

```text
Cursor는 무조건 좋아서가 아니라 "최신 체결부터 순차 조회"라는 요구사항에 맞아서 선택했다고 설명한다
```

<a id="f11-1"></a>

### 11-1. Offset 조회 + 대량 데이터 `W8-D1 · 1.5h`

**목표**: 평범한 페이지 조회 API와, 그것이 느려질 만큼의 데이터.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [조인-페이지네이션 › `OFFSET` 페이지네이션이 느려지는 이유](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#offset-페이지네이션이-느려지는-이유) — 오늘 만드는 API가 왜 느려질지 미리 이해
- ★ [조인-페이지네이션 › `COUNT`의 비용](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#count의-비용) — `Pageable`의 count 쿼리를 끄는 이유
- [대용량-처리-시스템 › 5) 벌크 쓰기와 인덱스 비용](../../12-시스템설계/대용량-처리-시스템/대용량-처리-시스템.md#5-벌크-쓰기와-인덱스-비용) — 100만 건 생성 시
- [인덱스-실행계획 › 선택도 — 인덱스를 타도 안 빨라지는 경우](../../06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md#선택도--인덱스를-타도-안-빨라지는-경우) — 데이터 분포(균등 vs 편중)가 결과를 바꾸는 이유

**할 일**

1. [AI] `GET /stocks/{code}/trades?page=0&size=50` — Offset 쿼리로 구현 (Spring Data `Pageable`이어도 됨, 단 `count` 쿼리는 끄기)
2. [직접] 데이터 분포 결정 (아래 판단)
3. [AI] `scripts/generate-trades.sql` — `generate_series`로 N건 INSERT, 종목 · 가격 · 수량 · 시각 분포를 2번대로. 10만 / 100만 / 500만을 파라미터로
4. [직접] 100만 건 생성 → `VACUUM ANALYZE trade;` → 건수 · 종목별 분포 확인
5. [직접] API 응답 확인, 생성에 걸린 시간 기록

**판단할 것**

- 분포: 종목 10개 균등 vs 인기 종목 1개에 50% 편중 → 결과가 달라진다. 하나 정해서 benchmarks.md에 명시
- 시드 종목은 3개뿐이다 → 생성기가 측정용 종목 7개를 `stock`에 먼저 넣는다 (`trade.stock_code` FK)
- **종목당 건수를 계산해 둔다** — 100만 건 / 10종목 균등이면 종목당 10만 건 = size 50 기준 **2,000페이지**가 끝이다. 11-2의 측정 page는 이 범위 안에서 고른다
- trade의 FK(order id) 때문에 orders도 생성할지, 측정용 DB에서는 FK 없이 갈지 (추천: 측정 전용 스키마에서 FK 해제, 그 사실을 기록)

**결과물**

- 코드: Offset 조회 API, `scripts/generate-trades.sql`
- 기록: benchmarks.md "실험 2" 데이터 조건 섹션, devlog

**이렇게 나오면 성공**

```text
SELECT count(*) FROM trade;                                → 1000000
SELECT stock_code, count(*) FROM trade GROUP BY 1;         → 분포가 의도대로

GET /stocks/005930/trades?page=0&size=50
{ "items":[{"tradeId":999991,"price":70100,"quantity":3,"executedAt":"…"}, …50건],
  "page":0, "size":50 }
```

**완료 기준**

- [ ] 100만 건 적재, `VACUUM ANALYZE` 완료
- [ ] 분포가 benchmarks.md에 적혀 있다

[↑ 일정표](#schedule)

<a id="f11-2"></a>

### 11-2. 측정: EXPLAIN + Index `W8-D2 · 2h`

**목표**: "어떤 조건에서 얼마나 느렸고, Plan에서 원인이 무엇이었는가"를 숫자와 Plan으로 남긴다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [인덱스-실행계획 › 복합 인덱스 — 선두 컬럼 규칙](../../06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md#복합-인덱스--선두-컬럼-규칙) — `(stock_code, id DESC)` 순서의 근거
- ★ [인덱스-실행계획 › 정렬 — 인덱스는 `ORDER BY` 비용도 없앤다](../../06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md#정렬--인덱스는-order-by-비용도-없앤다) — Plan에서 Sort가 사라지는 이유
- ★ [인덱스-실행계획 › 페이징에서 인덱스가 하는 일](../../06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md#페이징에서-인덱스가-하는-일) — Index로도 깊은 OFFSET이 느린 이유
- [인덱스-실행계획 › 실행 계획 읽기 (MySQL `EXPLAIN`)](../../06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md#실행-계획-읽기-mysql-explain) — 노트는 MySQL 기준 — PostgreSQL `EXPLAIN ANALYZE`와 용어 대응하며 읽기
- [인덱스-실행계획 › 인덱스가 쓰기에 물리는 비용](../../06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md#인덱스가-쓰기에-물리는-비용) — (선택 D4) INSERT 비용 측정
- [조인-페이지네이션 › 지연 조인 — `OFFSET`을 줄이는 실무 기법](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#지연-조인--offset을-줄이는-실무-기법) — Cursor 외의 대안으로 언급할 수 있게

**할 일**

1. [AI] `k6/trades-offset.js` — page = 0 / 1,000 / 1,990 각각 p95 측정 (종목당 10만 건 기준 처음 · 중간 · 끝)
2. [직접] **Index 없음** 측정 + 각 page의 `EXPLAIN (ANALYZE, BUFFERS)` 실행
3. [직접] Plan을 **먼저 직접 읽고** 메모 (Seq Scan? Sort? Rows Removed by Filter? 실행 시간?) → 그다음 AI에게 "내 해석이 맞는지"만 검증 요청
4. [AI] Flyway `V4__add_trade_indexes.sql` — 비교용으로 `stock_code` 단일 Index → 측정 → 제거 → `(stock_code, id DESC)` → 측정
5. [직접] 세 경우 × 세 page 결과를 표로, Plan 요약을 한 줄씩
6. [직접] 관찰 정리: 복합 Index로 정렬은 사라졌지만 **깊은 page는 여전히 느리다** — 버릴 행도 Index를 따라 읽어야 하므로 → 11-3의 근거

**판단할 것**

- 최종으로 남길 Index (추천: `(stock_code, id DESC)` 하나. 단일 Index는 제거)
- 측정마다 캐시 상태를 맞출지 (추천: 같은 쿼리 1회 워밍업 후 측정)

**결과물**

- 코드: `V4__…sql`, `k6/trades-offset.js`
- 기록: benchmarks.md "실험 2-1 Offset × Index", Plan 원문은 `docs/plans/`에 파일로

**이렇게 나오면 성공** (benchmarks.md 형식)

```text
## 실험 2-1. Offset × Index
데이터: trade 1,000,000건, 종목 10개 균등, VACUUM ANALYZE 후

| Index              | page=0 p95 | page=1,000 p95 | page=1,990 p95 | Plan 요약 (아래는 예상 — 실제 Plan으로 바꿔 쓴다) |
|--------------------|------------|----------------|----------------|-----------|
| 없음               |            |                |                | Seq Scan + Sort, Rows Removed by Filter ≈ 900,000 |
| stock_code         |            |                |                | Bitmap Index Scan + Sort (또는 Planner가 Seq Scan 선택) |
| (stock_code, id ↓) |            |                |                | Index Scan, Sort 없음, page=1,990에서 99,550행 읽고 버림 |

해석
- Index 없음: 매 요청 전체 스캔 + 정렬 → page와 무관하게 느림
- 복합 Index: 정렬이 사라져 얕은 page는 빨라졌지만, OFFSET만큼 Index를 읽고 버리므로 깊을수록 느려짐
- → Offset 방식 자체의 한계. Cursor로 간다
```

**완료 기준**

- [ ] 3 × 3 수치와 Plan 요약이 표에 있다
- [ ] "Index만으로 해결 안 되는 이유"가 한 줄로 적혀 있다

[↑ 일정표](#schedule)

<a id="f11-3"></a>

### 11-3. Cursor Pagination `W8-D3 · 1.5h`

**목표**: 몇 번째 페이지든 첫 페이지만큼 빠르고, 조회 중 새 체결이 들어와도 중복 · 누락이 없다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [조인-페이지네이션 › 커서(키셋) 페이지네이션](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#커서키셋-페이지네이션) — Cursor 방식 원리
- ★ [조인-페이지네이션 › 커서 페이지네이션 구현](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#커서-페이지네이션-구현) — 구현 코드
- ★ [대용량-처리-시스템 › 4) 처리하면서 대상이 바뀌면 OFFSET은 건너뛴다](../../12-시스템설계/대용량-처리-시스템/대용량-처리-시스템.md#4-처리하면서-대상이-바뀌면-offset은-건너뛴다) — "새 체결이 들어와도 중복·누락 없음" 설명 근거
- [조인-페이지네이션 › 페이지네이션 방식을 고르는 순서](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#페이지네이션-방식을-고르는-순서) — "요구사항에 맞아서 Cursor" 답변 재료
- [REST-API-설계 › 페이지네이션은 규약을 하나로 정한다](../../09-웹-보안/REST-API-설계/REST-API-설계.md#페이지네이션은-규약을-하나로-정한다) — `{items, nextCursor, hasNext}` 응답 형식

**할 일**

1. [직접] Cursor 쿼리 (`id < :cursor ORDER BY id DESC LIMIT size + 1`) — `cursor` 없으면 최신부터
2. [직접] `size + 1`개를 읽어 `hasNext` 판단, 마지막 항목 id를 `nextCursor`로
3. [AI] 응답 DTO `{items, nextCursor, hasNext}`, 테스트 골격
4. [직접] 테스트 기대값: 300건을 size 50으로 끝까지 넘겼을 때 모은 id가 전체와 같고 중복 없음
5. [AI] `k6/trades-cursor.js` — Offset의 page=1,990과 같은 위치(cursor = 그 위치의 id)에서 p95
6. [직접] benchmarks.md에 Offset vs Cursor 추가, Offset API 제거

**판단할 것**

- 조회 도중 새 체결이 들어와도 중복/누락이 없는 이유: 새 체결은 cursor보다 id가 커서 이미 지나간 범위에만 생긴다
- 정렬 키를 `executed_at`이 아니라 `id`로 쓰는 이유: 유일하고 단조 증가

**결과물**

- 코드: Cursor 조회, `k6/trades-cursor.js`, Offset API 제거
- 테스트: `TradeCursorTest`
- 기록: benchmarks.md "실험 2-2 Offset vs Cursor"

**이렇게 나오면 성공**

```text
GET /stocks/005930/trades?size=50
{ "items":[ …50건, id 999,993 · 999,983 · … (10종목이 섞여 있어 id가 띄엄띄엄) ], "nextCursor":999503, "hasNext":true }
GET /stocks/005930/trades?cursor=999503&size=50
{ "items":[ …다음 50건, 모두 id < 999,503 ], "nextCursor":999013, "hasNext":true }

TradeCursorTest
  ✔ 첫 페이지 = 최신 50건
  ✔ 끝까지 넘기면 전체 300건, 중복 0, 누락 0, 마지막 hasNext=false
  ✔ 넘기는 도중 새 체결 10건 추가 → 기존 300건 중 중복 · 누락 없음

## 실험 2-2. Offset vs Cursor (복합 Index 있음)
| 방식   | 위치        | p95 |
|--------|-------------|-----|
| Offset | page=1,990  |     |
| Cursor | 같은 위치   |     |   ← 첫 페이지와 비슷해야 정상
```

**완료 기준**

- [ ] `TradeCursorTest` 통과
- [ ] Offset vs Cursor 비교가 benchmarks.md에 있다
- [ ] Offset API가 코드에서 제거됐다

[↑ 일정표](#schedule)

---

<a id="f12"></a>

## 12. 현재가: Redis

**왜**: "Redis를 왜, 어디에만 썼나요?" — 가장 자주 조회되는 값 하나에만, 이유를 갖고, 장애가 번지지 않게.

**설계**

```text
현재가 = 가장 최근 Trade의 체결 가격. 조회가 가장 잦고 체결마다 바뀐다

TradeExecuted → MarketData Consumer (group: market-data) → SET stock:{code}:price

Cache Aside를 쓰지 않은 이유
  Cache Aside: 요청이 와야 채워짐 → 자주 바뀌는 값은 TTL 동안 stale, TTL을 줄이면 Hit율 하락
  Event Update: 바뀌는 시점에 갱신 → "쓰기가 이미 이벤트로 존재하는" 시세에 적합

재전달된 과거 이벤트가 현재가를 덮어쓸 수 있다
  → tradeId를 함께 저장하고 더 클 때만 갱신(Lua), 또는 곧 다음 이벤트로 덮이니 허용

장애 격리 — Redis 장애로 주문 체결이 멈추면 안 된다
  Trading Core는 Redis에 의존하지 않는다 (Redis는 Consumer 뒤에만)
  현재가 조회: Redis 실패 또는 값 없음 → DB 최신 체결로 Fallback
  함정: Redis 클라이언트 timeout이 길면 장애 시 요청마다 그만큼 기다린다 → 짧게
```

<a id="f12-1"></a>

### 12-1. Redis 현재가 `W9-D1 · 2h`

**목표**: 체결이 일어나면 현재가가 Redis에 반영되고, `GET /stocks/{code}/price`가 Redis에서 읽는다. Redis에 값이 없으면 DB에서 읽는다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [캐시-전략-정합성 › 쓰기 전략 — 여기가 진짜 갈림길이다](../../08-캐시-Redis/캐시-전략-정합성/캐시-전략-정합성.md#쓰기-전략--여기가-진짜-갈림길이다) — Event Update를 고른 근거
- ★ [캐시-전략-정합성 › 읽기 전략 — Cache-Aside가 하는 일](../../08-캐시-Redis/캐시-전략-정합성/캐시-전략-정합성.md#읽기-전략--cache-aside가-하는-일) — Cache Aside를 쓰지 않은 이유 설명
- ★ [Redis-자료구조 › String vs Hash — 객체 하나를 담을 때](../../08-캐시-Redis/Redis-자료구조/Redis-자료구조.md#string-vs-hash--객체-하나를-담을-때) — `{price, tradeId}` 저장 형태 고르기
- [Redis-자료구조 › 키 이름 규칙을 정한다](../../08-캐시-Redis/Redis-자료구조/Redis-자료구조.md#키-이름-규칙을-정한다) — `stock:{code}:price`
- [선착순-쿠폰-시스템 › Redis 방식 — Lua 스크립트로 판정](../../12-시스템설계/선착순-쿠폰-시스템/선착순-쿠폰-시스템.md#redis-방식--lua-스크립트로-판정) — tradeId 비교 후 갱신 Lua
- [Redis-자료구조 › 왜 빠른가 — 세 가지 이유](../../08-캐시-Redis/Redis-자료구조/Redis-자료구조.md#왜-빠른가--세-가지-이유) — "Redis를 왜 썼나" 꼬리 질문
- [실시간-처리-시스템 › 7) Hot Key — 한 키에 몰릴 때](../../12-시스템설계/실시간-처리-시스템/실시간-처리-시스템.md#7-hot-key--한-키에-몰릴-때) — 인기 종목 현재가 키에 조회가 몰릴 때

**할 일**

1. [AI] `docker-compose.yml`에 Redis 추가, Spring Data Redis 의존성 · 설정, Testcontainers Redis
2. [직접] `MarketDataConsumer` — `@KafkaListener(topics = "trade-executed", groupId = "market-data")` → `stock:{code}:price`에 `{price, tradeId, executedAt}` 저장 (Hash 또는 JSON 문자열)
3. [직접] 과거 이벤트 덮어쓰기 대응 결정 → 대응한다면 "저장된 tradeId보다 클 때만 SET" Lua 스크립트
4. [직접] `CurrentPriceService.get(code)` — Redis 조회 → 없거나 실패하면 `SELECT price FROM trade WHERE stock_code=? ORDER BY id DESC LIMIT 1`
5. [AI] `GET /stocks/{code}/price` Controller — 응답에 `source`(REDIS / DB) 포함 (테스트와 데모용)
6. [AI] 테스트 골격 → [직접] 기대값

**판단할 것**

- 과거 이벤트 덮어쓰기: 같은 종목은 같은 Partition이라 보통 순서대로 오지만, 재전달(Rebalance 등) 때 과거 값이 잠깐 덮일 수 있다 → 막을지 허용할지 이유와 함께 기록
- Settlement와 Group을 분리한 이유를 내 말로: 현재가 갱신이 정산 지연 · 장애에 묶이지 않게

**결과물**

- 코드: Redis 설정, `MarketDataConsumer`, `CurrentPriceService`, Controller
- 테스트: `CurrentPriceTest`
- 기록: devlog (덮어쓰기 판단), ai-log

**이렇게 나오면 성공**

```text
체결 70,000 → 체결 70,100 → 체결 70,050

$ redis-cli HGETALL stock:005930:price
1) "price"    2) "70050"
3) "tradeId"  4) "3"

GET /stocks/005930/price  → {"stockCode":"005930","price":70050,"source":"REDIS"}
redis-cli DEL stock:005930:price
GET /stocks/005930/price  → {"stockCode":"005930","price":70050,"source":"DB"}

$ kafka-consumer-groups --describe --group market-data   → LAG 0

CurrentPriceTest
  ✔ 체결 → Redis 현재가 = 마지막 체결가
  ✔ Redis 값 없음 → DB 최신 체결가, source=DB
  ✔ (대응했다면) tradeId 2 이벤트 재전달 → 현재가 변하지 않음
```

**완료 기준**

- [ ] `CurrentPriceTest` 통과
- [ ] `market-data` Group이 `settlement`와 별도로 LAG 0

[↑ 일정표](#schedule)

<a id="f12-2"></a>

### 12-2. Redis 장애 격리 + 측정 `W9-D2 · 1.5h`

**목표**: Redis가 죽어도 주문 · 체결은 아무 영향이 없고, 현재가는 빠르게 DB로 넘어간다. Redis를 쓴 효과를 숫자로 남긴다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [캐시-전략-정합성 › 캐시 장애가 서비스 장애가 되지 않게 한다](../../08-캐시-Redis/캐시-전략-정합성/캐시-전략-정합성.md#캐시-장애가-서비스-장애가-되지-않게-한다) — Fallback 설계
- ★ [장애분석-성능개선 › 외부 호출에는 반드시 타임아웃을 건다](../../10-테스트-운영/장애분석-성능개선/장애분석-성능개선.md#외부-호출에는-반드시-타임아웃을-건다) — Redis timeout 함정
- [HTTP-TCP-네트워크 › 타임아웃을 어디에 거는가](../../09-웹-보안/HTTP-TCP-네트워크/HTTP-TCP-네트워크.md#타임아웃을-어디에-거는가) — connect / command timeout 구분
- [ConnectionPool과-쿼리튜닝 › 쿼리 수를 테스트로 고정하기](../../06-데이터베이스/ConnectionPool과-쿼리튜닝/ConnectionPool과-쿼리튜닝.md#쿼리-수를-테스트로-고정하기) — 측정 구간 DB Query 수 세기
- [Cache-Stampede › 원본 앞에 서킷 브레이커를 둔다](../../08-캐시-Redis/Cache-Stampede/Cache-Stampede.md#원본-앞에-서킷-브레이커를-둔다) — README "다음 단계" 재료
- [09-장애-대응 › Timeout](../../infra/09-장애-대응/09-장애-대응.md#timeout) — Redis를 내렸을 때 어디서 기다리는지 나누기

**할 일**

1. [직접] Redis 클라이언트 timeout 설정 — `spring.data.redis.timeout`, `connect-timeout` (추천: 200ms 안팎)
2. [AI] 장애 테스트 골격 — Testcontainers Redis를 테스트 중간에 `stop()`
3. [직접] 장애 테스트 기대값: Redis 중지 후 현재가는 `source=DB`로 200ms 안에 응답, 주문 API는 201
4. [직접] timeout을 일부러 기본값(길게)으로 두고 같은 테스트 → 현재가 응답이 얼마나 느려지는지 기록 (함정 재현)
5. [AI] `k6/price.js` — VU 100으로 현재가 조회: (a) Redis 사용 (b) Redis 끄고 DB만
6. [직접] DB Query 수 비교 — `pg_stat_statements` 또는 Hibernate 통계로 측정 구간 쿼리 수
7. [직접] benchmarks.md "실험 3" 작성, "Cache Aside를 쓰지 않은 이유"를 내 말로 3줄

**판단할 것**

- timeout 값 — 너무 짧으면 정상 상황에서도 Fallback이 잦다
- Redis가 계속 죽어 있으면 매 요청 timeout만큼 낭비 → Circuit Breaker는 범위 밖으로 두고 README에 "다음 단계"로 기록
- **결과를 미리 각오해 둔다** — 11-2의 `(stock_code, id DESC)` Index 덕분에 DB의 "최신 체결 1건" 쿼리도 이미 빠르다. 응답 시간 차이는 작게 나올 수 있다. 그때 Redis의 근거는 속도가 아니라 **"가장 잦은 조회를 DB에서 떼어냈다"(DB Query 수 ≈ 0, DB CPU)**다. 수치를 근거에 맞춰 꾸미지 말고, 나온 수치로 근거를 고른다

**결과물**

- 코드: timeout 설정, `k6/price.js`
- 테스트: `RedisFailureTest`
- 기록: benchmarks.md "실험 3", devlog (timeout 함정 수치)

**이렇게 나오면 성공**

```text
RedisFailureTest
  ✔ Redis 중지 → GET price: source=DB, 응답 < 300ms
  ✔ Redis 중지 → POST /orders: 201, 체결 · 정산 정상
  ✔ Redis 재시작 → 다음 체결부터 source=REDIS

timeout 함정 (devlog)
  timeout 기본값: Redis 중지 후 현재가 응답 ≈ N초
  timeout 200ms : Redis 중지 후 현재가 응답 ≈ 0.2초

## 실험 3. 현재가 조회: DB vs Redis
| 방식  | TPS | p95(ms) | 측정 구간 DB Query 수 |
|-------|-----|---------|------------------------|
| DB    |     |         |                        |
| Redis |     |         | ≈ 0                    |
```

**완료 기준**

- [ ] `RedisFailureTest` 통과
- [ ] 실험 3 표와 해석이 benchmarks.md에 있다

[↑ 일정표](#schedule)

---

<a id="f13"></a>

## 13. 통합 & 면접 준비

<a id="f13-1"></a>

### 13-1. 통합 테스트 `W9-D3 · 1.5h` `🏷 v1.0`

**목표**: [전체 흐름](#overview)이 실제 PostgreSQL · Kafka · Redis 위에서 처음부터 끝까지 한 번에 돈다. 면접 데모가 이 테스트와 같은 순서다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [단위-통합-테스트 › 컨텍스트 캐시 — 통합 테스트를 살리는 장치](../../10-테스트-운영/단위-통합-테스트/단위-통합-테스트.md#컨텍스트-캐시--통합-테스트를-살리는-장치) — PostgreSQL + Kafka + Redis 통합 테스트를 빠르게
- ★ [Mock-SpringTest-Testcontainers › Testcontainers는 컨테이너를 재사용한다](../../10-테스트-운영/Mock-SpringTest-Testcontainers/Mock-SpringTest-Testcontainers.md#testcontainers는-컨테이너를-재사용한다) — 컨테이너 3개 기동 비용 줄이기
- [단위-통합-테스트 › 그래서 테스트 피라미드다](../../10-테스트-운영/단위-통합-테스트/단위-통합-테스트.md#그래서-테스트-피라미드다) — 단위 / 통합 / E2E 비율 설명

**할 일**

1. [AI] `EndToEndTest` 골격 — Testcontainers PostgreSQL + Kafka + Redis를 함께 띄우는 베이스
2. [직접] 시나리오 작성 (아래 순서 그대로)
3. [직접] 마지막에 `checkTrading()`, `checkAssets()`, `checkEvents()` 모두 호출
4. [AI] `http/demo-full.http` — 같은 시나리오를 수동으로 보여줄 데모 스크립트
5. [직접] 데모를 직접 실행하며 3분 안에 보여줄 순서와 멘트 메모
6. [직접] `git tag v1.0`

**결과물**

- 테스트: `EndToEndTest`
- 기록: `http/demo-full.http`, devlog (데모 순서), Tag

**이렇게 나오면 성공**

```text
EndToEndTest > 주문부터_조회까지() PASSED
  1. 계좌 2: SELL 005930 70,000 × 10                    → 201 OPEN
  2. 계좌 1: BUY  005930 70,100 × 10                    → 201 FILLED, trades 1건 (70,000)
  3. GET /stocks/005930/orderbook                       → asks [], bids []
  4. await: GET /accounts/1 → balance 300,000, 005930 10주, reserved 0
            GET /accounts/2 → balance 700,000, 005930 90주
  5. await: GET /stocks/005930/price                    → 70,000, source REDIS
  6. GET /stocks/005930/trades?size=10                  → 1건, hasNext false
  7. 불변식 trading / assets / events                   → 위반 0

$ git tag
v0.1-trading  v0.2-account  v0.3-event  v1.0
```

**완료 기준**

- [ ] `EndToEndTest` 통과
- [ ] 전체 테스트(`./gradlew test`) 통과
- [ ] `git tag v1.0`

[↑ 일정표](#schedule)

<a id="f13-2"></a>

### 13-2. README `W10-D1 · 2h`

**목표**: 면접관이 5분 안에 "무슨 문제를 어떻게 풀었고 수치로 확인했는지"를 알 수 있는 README.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [시스템설계-답변법 › ⑦ 장애와 정합성 — 무엇이 죽으면 무엇이 되는가](../../12-시스템설계/시스템설계-답변법/시스템설계-답변법.md#⑦-장애와-정합성--무엇이-죽으면-무엇이-되는가) — README "문제와 해결" 구성
- ★ [시스템설계-답변법 › ⑧ 단점 — 먼저 말한다](../../12-시스템설계/시스템설계-답변법/시스템설계-답변법.md#⑧-단점--먼저-말한다) — "만들지 않은 것", 한계 섹션
- [실시간-처리-시스템 › 6) 서버에서 클라이언트로 — 누가 먼저 말하는가](../../12-시스템설계/실시간-처리-시스템/실시간-처리-시스템.md#6-서버에서-클라이언트로--누가-먼저-말하는가) — README "만들지 않은 것"에서 SSE를 뺀 이유 설명

```text
1. 프로젝트 소개 (한 문단)
2. 전체 흐름 (다이어그램)
3. 문제와 해결 — 영역마다: 문제 재현 → 대안 비교 → 선택 → 측정
   체결 자료구조 / Lock → Single Writer / 영속화와 복구
   자산 정합성(예약, Lock, Deadlock) / 이벤트(Outbox, Idempotency) / 조회(Index, Cursor, Redis)
4. 성능 실험 결과 (측정 3종)
5. 만들지 않은 것과 이유 + 설계의 한계 (단일 인스턴스 전제 등 — 면접 준비 > 꼬리 질문 대비 표)
6. AI 활용 방식
7. 실행 방법 (docker compose up → bootRun → demo-full.http)
맨 위에 CI 배지
```

**할 일**

1. [AI] devlog / ADR / benchmarks를 넘겨 위 구조의 뼈대 + Mermaid 흐름도 초안
2. [직접] 3번 "문제와 해결" 각 항목을 직접 쓴다 — 항목마다 **재현 증거(devlog 원문) → 선택(ADR 링크) → 수치(benchmarks 링크)**
3. [직접] 수치가 기대와 달랐던 부분의 설명 (예: Lock vs Single Writer 차이가 작았던 이유)
4. [직접] 5번은 [만들지 않는 것](#overview) 표를 요약, 6번은 [AI 활용 질문](#ai-interview) 답변을 요약
5. [직접] 처음 보는 사람 입장에서 7번대로 실행해본다

**결과물**

- `README.md`, 다이어그램, ADR · benchmarks로 가는 링크

**이렇게 나오면 성공**

```text
README.md
  ✔ 첫 화면(스크롤 전)에 소개 + 흐름도가 보인다
  ✔ "문제와 해결" 6개 항목 모두에 재현 · 선택 · 수치가 있다
  ✔ 측정 3종 표가 있다
  ✔ 실행 방법대로 하면 데모가 돈다
```

**완료 기준**

- [ ] README 완성, 링크가 모두 열린다
- [ ] 실행 방법을 처음부터 따라해서 데모 성공

[↑ 일정표](#schedule)

<a id="f13-3"></a>

### 13-3. 면접 답변 `W10-D2 · 1.5h`

**목표**: [면접 준비](#interview)의 핵심 질문 10개와 AI 활용 질문에 내 프로젝트의 사실과 숫자로 답할 수 있다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- ★ [시스템설계-답변법 › 면접에서 말하는 순서 (단축 URL, 약 5분 분량)](../../12-시스템설계/시스템설계-답변법/시스템설계-답변법.md#면접에서-말하는-순서-단축-url-약-5분-분량) — 프로젝트 설명 순서의 틀
- [낙관적-비관적-락 › 6. 면접 정리](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#6-면접-정리) — Q5 (동시성 · Lock)
- [메시지-중복-재시도-Outbox › 6. 면접 정리](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#6-면접-정리) — Q6 · Q7 (Outbox · Idempotency)
- [조인-페이지네이션 › 6. 면접 정리](../../06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md#6-면접-정리) — Q8 (조회 최적화)
- [캐시-전략-정합성 › 6. 면접 정리](../../08-캐시-Redis/캐시-전략-정합성/캐시-전략-정합성.md#6-면접-정리) — Q9 (Redis)
- [Thread-동기화 › 6. 면접 정리](../../04-동시성/Thread-동기화/Thread-동기화.md#6-면접-정리) — Q2 · Q3 (동시성)
- [해시-트리-비교 › 6. 면접 정리](../../01-복잡도-자료구조/해시-트리-비교/해시-트리-비교.md#6-면접-정리) — Q1 (자료구조)

**할 일**

1. [직접] `docs/interview.md` — 핵심 질문 10개에 각 3~4문장. 각 답에 **숫자 하나 또는 재현 증거 하나**를 넣는다
2. [직접] [꼬리 질문 대비](#interview) 표의 질문마다 "현재 → 이유 → 확장" 3단 답 작성
3. [직접] ai-log에서 "AI가 틀린 점" 중 가장 기술적인 사례 1개 고르기 → AI 활용 답변 완성
4. [직접] 이력서 3줄 요약을 실제 수치로 확정
5. [AI] **면접관 역할**: README + interview.md를 주고 "꼬리 질문 10개 해줘" → 답한 뒤 "약한 답변을 지적해줘"
6. [직접] 약하다고 나온 답변 보강, 소리 내어 답해보며 2분 안에 끝나는지 확인

**결과물**

- `docs/interview.md` (질문 10개 + AI 질문 + 꼬리 질문 답변 + 이력서 3줄)
- ai-log (면접관 역할 결과)

**이렇게 나오면 성공**

```text
docs/interview.md 의 한 항목 예

Q5. 동시 주문에서 잔고가 초과 사용되지 않게 어떻게 막았나요?
A.  Lock 없이 같은 계좌에 80만원 주문 2건을 동시에 넣었더니 둘 다 접수되고
    예약금은 80만원만 기록되는 Lost Update가 재현됐습니다(devlog 날짜).
    계좌 Row에 비관적 락을 걸어 100건 동시 요청 중 정확히 1건만 성공하게 했고,
    교차 정산 Deadlock은 계좌 id 오름차순 Lock 규칙으로 없앴습니다.
```

**완료 기준**

- [ ] 질문 11개(10 + AI) 답변이 문서에 있고, 각각 숫자나 증거가 들어 있다
- [ ] 꼬리 질문 표의 모든 질문에 3단 답이 있다
- [ ] 이력서 3줄에 대괄호가 남아 있지 않다 (전부 실제 수치)
- [ ] 각 답을 소리 내어 2분 안에 말할 수 있다

[↑ 일정표](#schedule)

<a id="f13-4"></a>

### 13-4. 손코딩 · 데모 리허설 `W10-D3 · 1.5h`

**목표**: AI 없이도 핵심 코드를 짤 수 있다는 것을 스스로 확인하고, 데모를 3분 안에 끝낸다.

**학습 노트** (★ = 작업 전에 먼저 읽기)

- [해시-트리-비교 › 범위 검색 — TreeMap이 압도적인 지점](../../01-복잡도-자료구조/해시-트리-비교/해시-트리-비교.md#범위-검색--treemap이-압도적인-지점) — 손코딩 1 전에 TreeMap API 복습
- [낙관적-비관적-락 › 비관적 락 — JPA](../../07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md#비관적-락--jpa) — 손코딩 2 · 정산 Lock 복습
- [메시지-중복-재시도-Outbox › 멱등 컨슈머](../../11-메시징/메시지-중복-재시도-Outbox/메시지-중복-재시도-Outbox.md#멱등-컨슈머) — 손코딩 3 복습

**할 일**

1. [직접] IDE · AI 없이 종이 또는 화이트보드에 각 15분
    - OrderBook `add` / `cancel` + Matching 루프
    - `Account.settleBuy` (가격 개선 차액 해제 포함)
    - Idempotent Consumer의 트랜잭션 순서 (의사 코드)
2. [직접] 짠 것을 실제 코드와 비교 → 틀린 곳 devlog에 기록 후 다시 한 번
3. [직접] `demo-full.http`로 화면 공유하듯 3분 데모 (타이머)
4. [직접] 데모 중 나올 질문 3개를 예상하고 답 준비

**결과물**

- 손코딩 사진 또는 메모, devlog (틀린 곳, 걸린 시간)

**이렇게 나오면 성공**

```text
devlog
  손코딩 1 Matching      12분  가격 비교 방향 1회 실수 → 재작성 OK
  손코딩 2 settleBuy      6분  OK
  손코딩 3 Idempotency    8분  OK
  데모                  2분 50초
```

**완료 기준**

- [ ] 손코딩 3개 각 15분 안에 완료
- [ ] 데모 3분 안에 완료

[↑ 일정표](#schedule)

---

<a id="interview"></a>

# 면접 준비

## 핵심 질문 10개

```text
1.  왜 이 자료구조를 선택했나요?                                    → 2
2.  동시에 주문이 들어오면 순서를 어떻게 보장하나요?                → 4, 7
3.  Lock 방식과 Single Writer 방식의 차이는 무엇인가요?             → 7, 7-3
4.  서버가 죽으면 메모리에 있던 호가창은 어떻게 되나요?             → 5
5.  동시 주문에서 잔고가 초과 사용되지 않게 어떻게 막았나요?        → 9
6.  DB Commit 후 이벤트 발행이 실패하면 어떻게 하나요?              → 10 (Outbox)
7.  Kafka 메시지가 중복 전달되면 어떻게 하나요?                     → 10 (Idempotency)
8.  거래 데이터가 수백만 건 쌓이면 조회를 어떻게 최적화하나요?      → 11
9.  Redis를 왜, 어디에만 사용했나요?                                → 12
10. 개선 전후를 실제로 측정했나요?                                  → 측정 3종
```

## 좋은 설명 방식

```text
OrderBook
  ✗ TreeMap을 사용했습니다.
  ○ 가격 Level 정렬과 같은 가격 FIFO를 동시에 표현해야 해서 TreeMap<Price, Deque<Order>>를 골랐고,
    취소 시 전체 탐색을 피하려고 HashMap Order Index를 두었습니다.

동시성
  ✗ synchronized를 사용했습니다.
  ○ 처음엔 종목별 Lock으로 정합성을 확보했고, Lock을 빼면 불변식 테스트가 실제로 깨지는 걸 확인했습니다.
    이후 처리 순서를 결정적으로 만들고 부하를 Queue 적재량으로 드러내려고 종목별 Single Writer로 바꿨습니다.
    [측정 결과 — 7-3의 실제 수치와 병목 위치로 채운다. 예상과 달랐다면 다른 대로 말한다]

Kafka
  ✗ Kafka를 공부하려고 사용했습니다.
  ○ Worker가 정산까지 하면 계좌 Lock 대기가 체결 지연으로, 정산 장애가 체결 중단으로 번집니다.
    그래서 체결 이벤트로 분리했고, 발행 유실은 Outbox로, 중복 전달은 DB Unique 제약 기반 Idempotency로 막았습니다.

Redis
  ✗ Redis가 빠르기 때문에 사용했습니다.
  ○ 가장 자주 조회되는 현재가를 매번 DB 최신 체결 쿼리로 읽고 있었습니다. 현재가는 체결 이벤트가 이미 있는
    데이터라 Cache Aside 대신 이벤트로 Redis를 갱신했고, 장애 시 DB로 Fallback해 체결로 번지지 않게 했습니다.
    [12-2 수치 — 응답 시간 차이가 작았다면 "DB 쿼리 수를 0에 가깝게 떼어냈다"를 근거로]
```

이 문서의 예시 문장은 **틀**이다. 대괄호와 숫자는 반드시 내가 직접 잰 결과로 바꾼다. 측정하지 않은 결론을 외워 가면 꼬리 질문 한 번에 무너진다.

## 꼬리 질문 대비 — 설계의 한계를 먼저 아는 것

면접관은 잘 만든 부분보다 **한계를 아는지**를 더 깊게 판다. 아래는 이 설계에서 반드시 나오는 질문들이다. 각각 "현재 어떻게 되는가 → 왜 그렇게 뒀는가 → 확장한다면"의 3단으로 답을 준비한다.

| 질문 | 답의 재료 |
|---|---|
| 서버를 2대로 늘리면 어떻게 되나요? | 메모리 OrderBook · 단일 Publisher · (골랐다면) `AtomicLong` ID가 모두 단일 인스턴스 전제. 확장한다면 종목 단위로 인스턴스를 나누는 라우팅(같은 종목 = 같은 인스턴스, 7장 Worker 라우팅과 같은 발상), Publisher는 `FOR UPDATE SKIP LOCKED`. README "한계"에 적어둔다 |
| Queue에 들어간 주문은 서버가 죽으면요? | 사라진다. 클라이언트는 응답을 못 받았으므로 "모름" 상태 → `GET /orders/{id}`로 확인. 예약은 8-2 ADR 시나리오 2의 방법으로 찾아 보정 |
| Worker 스레드가 죽으면요? | 루프는 예외를 잡아 계속 돈다(7-1). 그래도 죽는다면 그 종목만 멈춘다 → 감지 방법(Queue 적재량 증가)과 재기동 |
| timeout 나면 주문은 어떻게 되나요? | 실패가 아니라 "모름" → 202 PENDING, 예약 유지 (7-1, 8-2) |
| 왜 Kafka예요? `@Async`나 Spring 이벤트로는 안 되나요? | 프로세스 안 이벤트는 서버가 죽으면 같이 사라진다. 체결과 정산 사이의 유실을 막으려면 DB(Outbox)에 남기고 밖으로 내보내야 했다. 대신 운영 비용이 늘었다 — 이것도 같이 말한다 |
| Outbox 폴링 지연은요? | 주기(200ms)만큼 정산이 늦다. 줄이려면 CDC(Debezium) — 범위 밖, 대안으로만 언급 |
| Redis가 죽으면요? | 체결은 영향 없음, 현재가는 DB Fallback (12-2 테스트로 증명) |
| 정산이 계속 실패하는 이벤트가 있으면요? | 지금은 재시도만 한다. DLQ로 격리하는 것이 다음 단계 (Study-Note 메시징 노트) |
| 테스트는 어떻게 믿을 수 있나요? | "Lock을 빼면 깨지는" 재현 테스트로 테스트 자체를 검증했다 (6, 9-1, 9-2) |

## 이력서 요약 (3줄)

README와 별개로 이력서에 넣을 문장을 W10-D2에 확정한다. 형식: **무엇을 → 어떻게 → 숫자로**.

```text
- 가격-시간 우선 체결 엔진을 TreeMap+Deque로 구현하고, 종목별 Single Writer로 동시성 처리 (Lock 대비 [측정값])
- 자산 예약 · 정산의 동시성 문제를 직접 재현하고 Pessimistic Lock · Lock 순서로 해결, Outbox + 멱등 Consumer로 이벤트 유실 · 중복 방지
- 체결 100만 건 조회를 복합 Index + Cursor로 개선 (깊은 페이지 p95 [전] → [후] ms), 현재가 조회 DB 쿼리를 Redis로 제거
```

## 프로젝트 소개 예시

> 가상 증권 거래소를 주문부터 체결, 정산, 조회까지 하나의 흐름으로 구현했습니다.
>
> 체결 엔진은 가격-시간 우선 Matching과 종목별 Single Writer로 만들었고, 메모리 호가창은 DB에서 언제든 재구성할 수 있게 해 장애 시 복구되도록 했습니다. 자산은 예약 방식과 Lock 순서 규칙으로 동시 주문과 교차 정산에서도 정합성을 지켰습니다.
>
> 정산은 Kafka로 분리하면서 Outbox와 Idempotency로 유실과 중복을 막았고, 체결 데이터가 쌓이며 생긴 조회 문제는 복합 Index와 Cursor로, 가장 잦은 현재가 조회는 Redis로 개선했습니다.
>
> 각 문제는 먼저 직접 재현했고, 개선 전후를 테스트와 수치로 비교했습니다.

<a id="ai-interview"></a>

## AI 활용 질문 — "AI를 어디에, 어떻게, 왜 썼나요?"

면접관이 확인하려는 것:

```text
1. 핵심 로직을 본인이 이해하고 짰는가
2. AI 결과물을 검증할 능력이 있는가
3. 도구를 합리적인 기준으로 쓰는가
4. 정직한가 — 숨기거나 과장하면 꼬리 질문에서 무너진다
```

답변 재료는 **기억이 아니라 기록**에서 나와야 한다. `docs/ai-log.md` 형식:

```text
| 날짜 | 맡긴 것 | 분류 | 내가 검증/수정한 것 | AI가 틀린 점 |
|---|---|---|---|---|
| W3-D1 | V1 DDL, Entity 매퍼 | 반복 코드 | (stock_code, sequence) Unique 추가 | 없음 |
| W7-D3 | 중복 이벤트 테스트 골격 | 테스트 도구 | 동시 처리 케이스 직접 추가 | Duplicate Key 예외 후 같은 트랜잭션에서 계속 진행 → PostgreSQL에서 실패 |
(형식 예시. 실제 기록으로 채운다)
```

**"AI가 틀린 점" 칸이 가장 중요하다.** 이 문서에서 짚은 함정들(PostgreSQL Duplicate Key 후 abort, `Math.abs(hashCode())`, Lock 밖 Commit, Redis timeout)에서 AI가 뭐라고 했는지 특히 기록한다.

답변 뼈대:

```text
1. 기준   — 무엇을 맡기고 무엇을 직접 했는지 나눈 기준 한 문장
2. 어디에 — 맡긴 것 2~3개, 직접 한 것 2~3개
3. 어떻게 — 테스트 기대값은 직접 계산, 핵심 로직은 리뷰어로만
4. 사례   — AI가 틀렸고 내가 잡아낸 것 1개 (ai-log에서)
5. 결과   — 아낀 시간을 어디에 썼는가
```

예시 답변 (대괄호는 실제로 겪은 일만):

> 기준은 "면접에서 이 코드를 설명하라고 하면 제가 짠 것처럼 말해야 하는가"였습니다.
>
> 설정 파일, DTO, 마이그레이션 SQL 초안, k6 스크립트처럼 정답이 정해진 반복 작업은 AI에게 맡겼고, Matching 루프, 예약/정산 계산, Single Writer Worker, Idempotency 트랜잭션 순서는 직접 짠 뒤 AI는 엣지 케이스를 찾는 리뷰어로만 썼습니다.
>
> 테스트 기대값은 제가 손으로 계산했습니다. AI가 구현과 테스트를 둘 다 쓰면 같은 오해를 공유한 채 통과할 수 있기 때문입니다. 실제로 [ai-log 사례].
>
> 그렇게 아낀 시간을 Lock 없이 실패를 재현하고 성능을 측정하는 데 썼습니다.

| 꼬리 질문 | 답변 방향 |
|---|---|
| 핵심 로직도 AI한테 시키면 더 빠르지 않았나요? | 빠르다. 하지만 목적은 설계 판단을 익히는 것이었다. 실무라면 AI 초안 → 내 검증도 가능하지만, 그 검증 능력이 지금 직접 짜면서 생긴다 |
| AI 없이 지금 다시 짤 수 있나요? | 실제로 짤 수 있어야 한다 → [13-4 손코딩](#f13-4) |
| AI 리뷰를 어떻게 믿었나요? | 믿지 않았다. 지적마다 실패하는 테스트를 먼저 만들어 재현될 때만 반영했다 |
| AI가 틀렸던 사례는? | ai-log에서 가장 기술적인 것 1개 |
| AI 때문에 시간이 더 든 적은? | 있으면 솔직하게 + 그 뒤로 바꾼 습관 |
| 팀 AI 사용 규칙을 만든다면? | 도메인 핵심 로직은 사람이 책임, 반복 코드는 AI + 리뷰, 테스트 기대값은 사람이 |

[↑ 일정표](#schedule)

---

<a id="out-of-scope-notes"></a>

# 부록. 이 프로젝트에서 쓰지 않는 학습 노트

Study-Note 60개 노트 중 이 계획의 어느 단계에도 연결하지 않은 노트다. 이 프로젝트가 **단일 인스턴스 · 인증 없음 · 배포 없음**으로 범위를 정했기 때문이다. 공부할 가치가 없다는 뜻이 아니라, **이 10주 동안은 손대지 않는다**는 뜻이다.

## 인증 · 보안 — "인증 없음"으로 범위를 정했다

이 프로젝트는 `accountId`를 요청 본문으로 받는다. 누가 보낸 요청인지 확인하지 않는다.

| 노트 | 빼는 이유 |
|---|---|
| [인증인가-CORS-CSRF](../../09-웹-보안/인증인가-CORS-CSRF/인증인가-CORS-CSRF.md) | 로그인 · 권한이 없다 |
| [쿠키-세션-JWT](../../09-웹-보안/쿠키-세션-JWT/쿠키-세션-JWT.md) | 세션 · 토큰이 없다 |

**면접 대비로 이것만은 본다** — "남의 `accountId`를 넣으면 남의 돈으로 주문되지 않나요?"는 거의 확실히 나온다.
[인증인가-CORS-CSRF › 인가 누락 — 가장 흔하고 가장 조용한 취약점](../../09-웹-보안/인증인가-CORS-CSRF/인증인가-CORS-CSRF.md#인가-누락--가장-흔하고-가장-조용한-취약점)을 읽고 답을 준비한다: "범위 밖으로 둔 결정이고, 실제라면 인증된 사용자 ID와 계좌 소유자를 조회 조건에 넣어 막는다". README "한계"에도 적는다.

## 배포 인프라 — "로컬 실행 + CI까지"로 범위를 정했다

CI(GitHub Actions에서 테스트)는 1. 셋업에 넣었다. 그 이후의 배포는 다루지 않는다.

| 노트 | 빼는 이유 |
|---|---|
| [01-네트워크](../../infra/01-네트워크/01-네트워크.md) | 외부 공개 서버가 없다 |
| [04-Nginx](../../infra/04-Nginx/04-Nginx.md) | 앞단 프록시가 없다 |
| [05-외부-접속](../../infra/05-외부-접속/05-외부-접속.md) | 외부에서 접속하지 않는다 |
| [06-DNS-HTTPS](../../infra/06-DNS-HTTPS/06-DNS-HTTPS.md) | 도메인 · 인증서가 없다 |
| [10-Kubernetes](../../infra/10-Kubernetes/10-Kubernetes.md) | 단일 인스턴스 전제 (서버를 늘리는 질문은 면접 준비 > 꼬리 질문 대비에서 말로 답한다) |
| [11-전체-연결하기](../../infra/11-전체-연결하기/11-전체-연결하기.md) | 배포 전체 그림 — 위 노트들을 잇는 노트 |

10주를 끝내고 시간이 남으면 가장 먼저 붙일 만한 것: **CD(이미지 빌드 → 서버 배포) + Nginx + HTTPS**로 데모를 공개 URL에 띄우기. 면접관이 링크 하나로 바로 눌러볼 수 있게 된다.

## 알고리즘

| 노트 | 빼는 이유 |
|---|---|
| [구간-처리](../../02-알고리즘/구간-처리/구간-처리.md) | 투 포인터 · 슬라이딩 윈도우를 쓰는 지점이 없다. 코딩 테스트 준비용으로 따로 본다 |

[↑ 일정표](#schedule)
