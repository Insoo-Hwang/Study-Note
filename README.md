# Study Note — 백엔드 면접 학습 노트

자료구조부터 시스템 설계까지, **"어떤 상황에서 무엇을 선택하고 왜 선택했는지 설명할 수 있는 수준"** 을 목표로 정리한 학습 저장소입니다.

> 📖 **학습 사이트**: <https://Insoo-Hwang.github.io/Study-Note/>
> 각 주제 페이지에 **알아볼 내용 · GPT 질문 · 면접 질문 · 완료 체크리스트**가 정리되어 있습니다.

---

## 학습 목표

모든 문제를 푸는 것이 아니라, 주어진 상황에서 **적절한 자료구조와 저장 방식을 선택하고, 조건이 달라질 때 어떻게 바꿀지 설명하는 능력**을 기르는 것이 목적입니다.

핵심 흐름은 다음과 같습니다.

```
복잡도 → 자료구조 → 알고리즘 → Java 컬렉션 → 동시성
      → DB 인덱스·설계 → 트랜잭션 → 캐시·Redis → 시스템 설계
```

---

## 커리큘럼 (항목별)

| 단계  | 주제           | 핵심 목표             |
| --- | ------------ | ----------------- |
| 1   | **복잡도**      | 성능을 비교하는 공통 기준 이해 |
| 2   | **자료구조**     | 상황별 저장 구조 선택      |
| 3   | **알고리즘**     | 탐색·집계·구간 처리       |
| 4   | **Java 컬렉션** | 구현체 내부 원리 이해      |
| 5   | **동시성**      | 여러 요청의 안전한 처리     |
| 6   | **데이터베이스**   | 대용량 조회·저장 최적화     |
| 7   | **트랜잭션**     | 데이터 정합성 유지        |
| 8   | **캐시·Redis** | 빠른 조회와 분산 데이터     |
| 9   | **시스템 설계**   | 전체 지식을 연결해 설명     |

### 세부 학습 항목

```text
docs/
├─ README.md
│
├─ 01-복잡도/
│  ├─ README.md
│  ├─ 시간-공간-복잡도.md
│  └─ Amortized-Analysis.md
│
├─ 02-자료구조/
│  ├─ README.md
│  ├─ 선형-자료구조-비교.md
│  ├─ 해시-트리-비교.md
│  └─ Heap-PriorityQueue.md
│
├─ 03-알고리즘/
│  ├─ README.md
│  ├─ 탐색-정렬.md
│  ├─ 구간-처리.md
│  └─ 그래프-문제해결.md
│
├─ 04-Java/
│  ├─ README.md
│  ├─ Java-Collection.md
│  ├─ equals-hashCode.md
│  └─ Collection-선택기준.md
│
├─ 05-동시성/
│  ├─ README.md
│  ├─ Thread와-동기화.md
│  ├─ Atomic과-ConcurrentCollection.md
│  └─ ThreadPool과-Deadlock.md
│
├─ 06-데이터베이스/
│  ├─ README.md
│  ├─ 인덱스와-실행계획.md
│  ├─ 조인과-페이지네이션.md
│  └─ 대용량-데이터-분할.md
│
├─ 07-트랜잭션/
│  ├─ README.md
│  ├─ ACID와-격리수준.md
│  ├─ MVCC.md
│  └─ 낙관적락-비관적락.md
│
├─ 08-캐시-Redis/
│  ├─ README.md
│  ├─ 캐시-전략.md
│  ├─ Redis-자료구조.md
│  └─ 분산락과-멱등성.md
│
└─ 09-시스템설계/
   ├─ README.md
   ├─ 시스템설계-답변법.md
   ├─ 조회수-쿠폰-시스템.md
   └─ 주문-결제-시스템.md
```

### 각 내용 세부 내용
```text
# 01. 복잡도

## `시간-공간-복잡도.md`

### 포함할 내용

- Big-O
- O(1)
- O(log n)
- O(n)
- O(n log n)
- O(n²)
- 최선·평균·최악 복잡도
- 시간 복잡도
- 공간 복잡도
- 시간과 메모리의 Trade-off
- 반복문 복잡도 계산

### 학습 목적

Big-O와 공간 복잡도는 모두 알고리즘의 효율을 판단하기 위한 기준이다.  
따라서 각각 따로 공부하기보다 한 문서에서 함께 비교하는 편이 이해하기 쉽다.

### 핵심 질문

- 입력 데이터가 커지면 실행 시간은 어떻게 증가하는가?
- 더 빠른 처리를 위해 메모리를 더 사용해도 되는가?
- 같은 문제를 여러 방식으로 풀었을 때 어떤 풀이가 더 효율적인가?
- 코드의 반복문만 보고 대략적인 복잡도를 계산할 수 있는가?

---

## `Amortized-Analysis.md`

### 포함할 내용

- Amortized Analysis
- ArrayList Resize
- HashMap Resize
- 평균적으로 O(1)인 이유
- 가끔 발생하는 비싼 연산
- 최악 연산과 전체 평균 비용

### 학습 목적

ArrayList나 HashMap은 가끔 배열 확장과 복사 때문에 큰 비용이 발생한다.  
하지만 매 연산마다 확장이 일어나는 것은 아니므로, 전체 연산 비용을 평균내면 대부분 O(1)에 가깝게 볼 수 있다.

### 운영 기준

처음에는 `시간-공간-복잡도.md` 안의 한 섹션으로 넣어도 된다.  
내용이 길어지거나 이해가 어려울 때만 별도 문서로 분리한다.

---

# 02. 자료구조

## `선형-자료구조-비교.md`

### 포함할 자료구조

| 자료구조 | 핵심 특징 |
|---|---|
| Array | 고정 크기, 인덱스 접근 |
| ArrayList | 크기가 동적으로 늘어나는 배열 |
| LinkedList | 노드를 연결해 데이터를 저장 |
| Stack | LIFO |
| Queue | FIFO |
| Deque | 양쪽에서 삽입·삭제 |

### 비교 기준

- 인덱스 조회
- 순차 탐색
- 앞쪽 삽입·삭제
- 뒤쪽 삽입·삭제
- 중간 삽입·삭제
- 메모리 구조
- 메모리 사용량
- 순차 접근 성능
- Java 구현체
- 실무 사용 사례

### 핵심 질문

> 선형 데이터를 저장할 때 어떤 자료구조를 선택할 것인가?

### 학습 방향

각 자료구조를 독립적으로 외우기보다, 동일한 상황에서 어떤 구조를 선택할지 비교한다.

예시:

- 인덱스 조회가 많다면?
- 앞뒤 삽입·삭제가 많다면?
- 최근 작업부터 처리해야 한다면?
- 먼저 들어온 요청부터 처리해야 한다면?
- Stack과 Queue를 Java에서 어떤 구현체로 사용할 것인가?

---

## `해시-트리-비교.md`

### 포함할 내용

- HashMap
- HashSet
- TreeMap
- TreeSet
- LinkedHashMap
- 해시 함수
- Bucket
- 해시 충돌
- 정렬 여부
- 범위 검색
- 삽입 순서 유지
- equals()
- hashCode()

### 비교 기준

| 기준 | Hash 계열 | Tree 계열 |
|---|---|---|
| 조회 | 평균 O(1) | O(log n) |
| 정렬 | 일반적으로 보장 안 됨 | 정렬 유지 |
| 범위 검색 | 부적합 | 적합 |
| 중복 제거 | HashSet | TreeSet |
| 순서 유지 | LinkedHashMap | TreeMap은 정렬 순서 |
| 주요 목적 | 정확한 Key 조회 | 정렬·범위 조회 |

### 핵심 질문

- 빠른 Key 조회가 중요한가?
- 정렬된 상태가 필요한가?
- 특정 값 이상·이하의 범위 검색이 필요한가?
- 삽입 순서를 유지해야 하는가?
- 중복을 제거하면서 정렬도 유지해야 하는가?

### 학습 목적

HashMap, HashSet, TreeMap을 따로 공부하면 해싱과 트리 구조에 관한 설명이 반복된다.  
실제 면접에서는 각각의 정의보다 어떤 상황에 무엇을 선택하는지 비교하는 질문이 자주 나온다.

---

## `Heap-PriorityQueue.md`

### 포함할 내용

- Heap
- Min Heap
- Max Heap
- PriorityQueue
- 완전 이진 트리
- 삽입과 삭제
- Heapify
- Top-K
- 전체 정렬과 차이
- 스케줄링
- 최댓값·최솟값 반복 조회

### 핵심 질문

- 전체 데이터를 정렬해야 하는가?
- 가장 작은 값 또는 큰 값만 반복해서 꺼내면 되는가?
- 상위 K개만 필요하다면 전체 정렬이 필요한가?
- 작업 우선순위에 따라 처리 순서를 정해야 하는가?

### 학습 목적

Heap은 내부 자료구조이고 PriorityQueue는 우선순위 기반 처리를 제공하는 추상 자료형이다.  
Java의 PriorityQueue가 보통 Heap으로 구현되므로 함께 학습한다.

---

# 03. 알고리즘

알고리즘은 종류별 정의를 암기하기보다, 어떤 문제 패턴에서 사용하는지를 중심으로 본다.

---

## `탐색-정렬.md`

### 포함할 내용

- 선형 탐색
- 이진 탐색
- 정렬
- Comparable
- Comparator
- 정렬 후 탐색
- 검색 횟수에 따른 전략
- DB 인덱스와 이진 탐색의 연결

### 핵심 질문

- 데이터를 한 번만 찾을 것인가?
- 같은 데이터를 반복해서 찾을 것인가?
- 정렬 비용을 미리 지불할 가치가 있는가?
- 데이터 정렬 상태를 유지할 필요가 있는가?
- 정렬 기준이 하나인가, 여러 개인가?

### 학습 포인트

한 번만 탐색한다면 정렬 비용이 더 클 수 있다.  
하지만 같은 데이터에서 반복 검색한다면 정렬 후 이진 탐색이 더 유리할 수 있다.

---

## `구간-처리.md`

### 포함할 내용

- 투 포인터
- 슬라이딩 윈도우
- 누적합
- 최근 N개 데이터
- 최근 5분 요청
- 연속 구간
- 구간 합
- 중복 제거
- 시간 기반 데이터 처리

### 핵심 질문

- 연속된 구간을 다루는 문제인가?
- 구간이 한 칸씩 이동하는가?
- 매번 전체 구간을 다시 계산하고 있는가?
- 두 위치를 이동시키며 조건을 만족할 수 있는가?
- 구간 합을 반복해서 계산해야 하는가?

### 학습 범위

고난도 문제 풀이보다 세 패턴의 차이와 적용 상황을 구분하는 데 집중한다.

| 패턴 | 적합한 상황 |
|---|---|
| 투 포인터 | 두 위치를 조절하며 조건 탐색 |
| 슬라이딩 윈도우 | 연속된 구간이 이동 |
| 누적합 | 여러 번의 구간 합 조회 |

---

## `그래프-문제해결.md`

### 포함할 내용

- Graph
- Vertex
- Edge
- DFS
- BFS
- 재귀
- Stack
- Queue
- 방문 처리
- 순환 구조
- 최단 거리
- 관계 탐색
- Greedy 개념
- DP 개념

### 학습 목적

초기에는 DFS, BFS, Greedy, DP를 각각 깊게 분리하기보다 문제를 해결하는 대표적인 방식으로 이해한다.

### 핵심 질문

- 관계 데이터를 탐색하는 문제인가?
- 깊게 탐색해야 하는가?
- 가까운 노드부터 탐색해야 하는가?
- 최단 거리를 구해야 하는가?
- 동일한 계산이 반복되는가?
- 현재 선택이 이후 결과에 어떤 영향을 미치는가?

### 분리 기준

코딩 테스트 비중이 높은 회사를 준비하거나 내용이 커지면 다음처럼 분리한다.

```text
그래프-탐색.md
Greedy-DP.md
```

---

# 04. Java

자료구조 문서에서는 구조와 복잡도를 다루고, Java 문서에서는 실제 구현체와 API를 다룬다.

```text
자료구조 문서
→ 구조, 동작 원리, 복잡도, 선택 기준

Java 문서
→ Java 인터페이스, 구현체, API, 내부 구현 특징
```

---

## `Java-Collection.md`

### 포함할 내용

- Collection Framework
- List
- Set
- Map
- Queue
- ArrayList
- LinkedList
- HashMap
- HashSet
- TreeMap
- PriorityQueue
- ArrayDeque
- Collections
- Iterator
- fail-fast
- 불변 컬렉션
- List.of()
- Set.of()
- Map.of()

### 핵심 질문

- 인터페이스와 구현체를 왜 분리하는가?
- List, Set, Map, Queue는 각각 어떤 계약을 가지는가?
- Java에서 Stack 대신 ArrayDeque를 권장하는 이유는 무엇인가?
- Iterator 동작 중 컬렉션을 수정하면 왜 문제가 발생하는가?
- 불변 컬렉션은 언제 필요한가?

---

## `equals-hashCode.md`

### 포함할 내용

- ==
- equals()
- hashCode()
- 동일성과 동등성
- equals와 hashCode 계약
- HashMap Key
- HashSet 중복 판단
- 불변 Key
- Mutable Key 문제
- record
- Lombok
- JPA Entity 주의점

### 핵심 질문

- `==`와 `equals()`는 무엇이 다른가?
- equals가 같으면 hashCode도 같아야 하는 이유는 무엇인가?
- hashCode가 같으면 equals도 반드시 같은가?
- HashMap에 넣은 Key 객체의 값을 변경하면 왜 문제가 생기는가?
- JPA Entity에서 equals와 hashCode 구현이 어려운 이유는 무엇인가?

### 분리 이유

HashMap과 연결되는 주제지만, Java 객체의 동등성 계약 자체가 중요하므로 별도 문서로 관리한다.

---

## `Collection-선택기준.md`

### 목적

새로운 개념을 배우는 문서가 아니라 면접 직전 빠르게 비교하는 복습 문서다.

### 포함할 비교

- ArrayList vs LinkedList
- HashMap vs TreeMap
- HashSet vs List
- ArrayDeque vs Stack
- PriorityQueue vs 전체 정렬
- HashMap vs ConcurrentHashMap
- mutable collection vs immutable collection

### 추천 구성

| 요구사항 | 후보 | 선택 기준 |
|---|---|---|
| 빠른 인덱스 조회 | ArrayList | 순차 데이터, 조회 중심 |
| 정렬된 Key | TreeMap | 범위 검색·정렬 필요 |
| 중복 제거 | HashSet | 존재 확인 중심 |
| 동시 접근 | ConcurrentHashMap | 단일 JVM 내 동시 접근 |
| Top-K | PriorityQueue | 전체 정렬 불필요 |

---

# 05. 동시성

## `Thread와-동기화.md`

### 포함할 내용

- Process
- Thread
- 공유 자원
- Race Condition
- Critical Section
- synchronized
- Lock
- ReentrantLock
- 가시성
- 원자성
- 순서 보장
- 상호 배제

### 핵심 질문

- 여러 스레드가 같은 데이터를 수정하면 어떤 문제가 생기는가?
- synchronized는 어떤 범위에 락을 거는가?
- synchronized와 Lock의 차이는 무엇인가?
- 락 범위를 크게 잡으면 왜 성능이 떨어지는가?
- 원자성, 가시성, 순서 보장은 각각 무엇인가?

---

## `Atomic과-ConcurrentCollection.md`

### 포함할 내용

- volatile
- AtomicInteger
- AtomicLong
- CAS
- Compare And Set
- ConcurrentHashMap
- putIfAbsent
- compute
- computeIfAbsent
- 복합 연산
- 단일 JVM 한계

### 핵심 질문

- volatile은 원자성을 보장하는가?
- count++가 원자적이지 않은 이유는 무엇인가?
- AtomicInteger는 어떻게 락 없이 값을 변경하는가?
- ConcurrentHashMap이면 모든 연산이 자동으로 안전한가?
- 여러 서버에서 ConcurrentHashMap을 공유할 수 있는가?

### 학습 목적

volatile, Atomic, ConcurrentHashMap은 모두 여러 스레드가 공유 상태를 다루는 방법이다.  
따라서 가시성, 원자성, 동시 컬렉션이라는 하나의 흐름으로 학습한다.

---

## `ThreadPool과-Deadlock.md`

### 포함할 내용

- ThreadPool
- ExecutorService
- 작업 Queue
- Core Pool Size
- Maximum Pool Size
- Keep Alive Time
- Reject Policy
- CPU Bound
- I/O Bound
- Deadlock
- 락 순서
- Spring @Async
- 웹 서버 Thread Pool

### 핵심 질문

- 요청마다 Thread를 새로 만들면 왜 문제가 생기는가?
- ThreadPool의 Queue가 가득 차면 어떻게 되는가?
- CPU 작업과 I/O 작업의 적절한 Thread 수는 어떻게 다른가?
- Deadlock은 어떤 조건에서 발생하는가?
- 여러 락을 사용할 때 순서를 통일해야 하는 이유는 무엇인가?
- Spring @Async의 ThreadPool은 어떻게 설정하는가?

---

# 06. 데이터베이스

## `인덱스와-실행계획.md`

### 포함할 내용

- Index
- B-Tree
- B+Tree
- Root
- Branch
- Leaf
- 단일 인덱스
- 복합 인덱스
- Leftmost Prefix
- 커버링 인덱스
- Cardinality
- Selectivity
- 실행 계획
- Full Table Scan
- Index Scan
- Index Range Scan
- 정렬과 인덱스
- 인덱스 관리 비용

### 학습 흐름

```text
인덱스가 필요한 이유
        ↓
B+Tree 구조
        ↓
단일·복합 인덱스
        ↓
컬럼 순서와 조회 조건
        ↓
커버링 인덱스
        ↓
실행 계획으로 확인
```

### 핵심 질문

- 인덱스가 왜 조회를 빠르게 하는가?
- 복합 인덱스의 컬럼 순서는 어떻게 정하는가?
- 인덱스가 많으면 왜 쓰기 성능이 떨어지는가?
- Cardinality와 Selectivity가 왜 중요한가?
- 커버링 인덱스는 왜 빠른가?
- 실행 계획에서 인덱스 사용 여부를 어떻게 확인하는가?

---

## `조인과-페이지네이션.md`

### 포함할 내용

- Join
- Nested Loop Join
- Hash Join
- Sort Merge Join
- Offset Pagination
- Cursor Pagination
- No Offset
- 정렬 기준
- 복합 Cursor
- created_at과 id
- 대용량 목록 조회
- 페이지 중복과 누락

### 핵심 질문

- 조인은 어떤 방식으로 실행되는가?
- 작은 테이블과 큰 테이블의 조인 순서는 왜 중요한가?
- Offset이 뒤 페이지에서 느려지는 이유는 무엇인가?
- Cursor Pagination이 빠른 이유는 무엇인가?
- created_at이 같은 행이 여러 개라면 Cursor를 어떻게 구성하는가?
- 임의 페이지 이동과 성능 중 무엇이 더 중요한가?

### 분리 기준

조인과 페이지네이션 내용이 커지면 다음처럼 나눈다.

```text
조인-알고리즘.md
페이지네이션.md
```

---

## `대용량-데이터-분할.md`

### 포함할 내용

- 정규화
- 반정규화
- 파티셔닝
- 샤딩
- Scale Up
- Scale Out
- 분산 저장
- 데이터 재배치
- 분할 기준
- Hot Partition
- Cross-Shard Query

### 핵심 질문

- 정규화는 어떤 문제를 해결하는가?
- 반정규화는 왜 사용하는가?
- 파티셔닝과 샤딩의 차이는 무엇인가?
- 데이터 분할 기준은 어떻게 정하는가?
- 특정 파티션에 트래픽이 몰리면 어떻게 되는가?
- 샤딩 후 조인과 트랜잭션은 어떻게 어려워지는가?

### 학습 범위

초기에는 구현 세부사항보다 목적과 Trade-off를 이해한다.

---

# 07. 트랜잭션

## `ACID와-격리수준.md`

### 포함할 내용

- Transaction
- ACID
- Atomicity
- Consistency
- Isolation
- Durability
- Dirty Read
- Non-repeatable Read
- Phantom Read
- Read Uncommitted
- Read Committed
- Repeatable Read
- Serializable

### 학습 흐름

```text
트랜잭션이 왜 필요한가
        ↓
동시에 실행되면 어떤 문제가 생기는가
        ↓
격리 수준으로 무엇을 조절하는가
        ↓
성능과 정합성 사이에서 무엇을 선택하는가
```

### 핵심 질문

- ACID의 각 요소는 무엇을 보장하는가?
- 격리 수준이 높아지면 왜 성능이 떨어질 수 있는가?
- Dirty Read, Non-repeatable Read, Phantom Read는 어떻게 다른가?
- DB마다 기본 격리 수준이 다른 이유는 무엇인가?
- Spring @Transactional과 DB Transaction은 어떤 관계인가?

---

## `MVCC.md`

### 포함할 내용

- MVCC
- Version
- Snapshot
- Undo
- Read View
- Consistent Read
- 현재 읽기
- 읽기와 쓰기 충돌 완화
- 격리 수준과의 관계
- 오래된 트랜잭션 문제

### 핵심 질문

- MVCC가 왜 필요한가?
- 읽기와 쓰기를 동시에 처리할 수 있는 이유는 무엇인가?
- Snapshot은 무엇인가?
- 오래 실행되는 트랜잭션은 어떤 문제를 만드는가?
- MVCC와 Lock은 서로 완전히 대체 관계인가?

### 분리 이유

MVCC는 트랜잭션과 격리 수준을 이해하는 핵심이면서 개념 난도가 높기 때문에 별도 문서로 유지한다.

---

## `낙관적락-비관적락.md`

### 포함할 내용

- 낙관적 락
- 비관적 락
- Version
- SELECT FOR UPDATE
- 충돌률
- 재시도
- Lock Wait
- Deadlock
- 재고 차감
- 쿠폰 발급
- 금융 거래

### 비교 기준

| 기준 | 낙관적 락 | 비관적 락 |
|---|---|---|
| 가정 | 충돌이 적음 | 충돌이 많음 |
| 방식 | Version 검증 | DB Lock 선점 |
| 충돌 시 | 실패 후 재시도 | 다른 트랜잭션 대기 |
| 장점 | 락 대기 감소 | 높은 충돌에서 단순 |
| 단점 | 재시도 비용 | 대기·Deadlock 가능 |

### 핵심 질문

- 충돌 가능성이 높은가?
- 실패 후 재시도가 가능한가?
- 정확한 순차 처리가 필요한가?
- 트랜잭션이 오래 유지되는가?
- 외부 API가 트랜잭션 안에 포함되는가?

---

# 08. 캐시·Redis

## `캐시-전략.md`

### 포함할 내용

- Local Cache
- Distributed Cache
- Cache Aside
- TTL
- Cache Hit
- Cache Miss
- Hit Ratio
- Eviction
- Cache Stampede
- Cache Penetration
- Cache Avalanche
- Request Collapsing
- Hot Key
- 캐시 일관성
- 캐시 장애 시 Fallback

### 핵심 질문

- 어떤 데이터를 캐시해야 하는가?
- 데이터 변경 빈도는 어느 정도인가?
- 오래된 데이터를 어느 정도 허용할 수 있는가?
- TTL은 어떻게 정하는가?
- 캐시와 DB가 불일치하면 어떻게 하는가?
- 캐시가 장애 나면 DB로 바로 요청이 몰리지 않는가?

### 학습 목적

캐시 전략과 캐시 장애 문제는 분리하기보다 함께 봐야 한다.  
전략을 선택하면 어떤 장애와 정합성 문제가 생기는지까지 연결해서 이해한다.

---

## `Redis-자료구조.md`

### 포함할 내용

- String
- Hash
- List
- Set
- Sorted Set
- Stream
- Bitmap
- HyperLogLog
- TTL
- 세션
- 카운터
- 랭킹
- 중복 제거
- 메시지 처리

### 학습 우선순위

```text
String
→ Hash
→ Set
→ Sorted Set
→ Stream
→ Bitmap·HyperLogLog은 용도 중심
```

### 주요 활용

| 요구사항 | Redis 자료구조 |
|---|---|
| 단순 캐시 | String |
| 객체 속성 | Hash |
| 중복 없는 집합 | Set |
| 랭킹 | Sorted Set |
| 메시지 처리 | Stream |
| 출석·상태 기록 | Bitmap |
| 대략적인 방문자 수 | HyperLogLog |

### 핵심 질문

- Redis 자료구조를 어떤 기준으로 선택하는가?
- List와 Stream은 어떻게 다른가?
- Sorted Set으로 랭킹을 어떻게 구현하는가?
- Redis 데이터는 원본 데이터로 사용해도 되는가?
- Redis 장애와 데이터 유실에 어떻게 대비하는가?

---

## `분산락과-멱등성.md`

### 포함할 내용

- Local Lock
- Distributed Lock
- Lock Key
- Lock TTL
- 락 소유권
- 락 해제
- Redisson
- Watchdog
- Idempotency Key
- 중복 요청
- Unique Constraint
- 재시도
- 결제 중복 방지
- 메시지 중복 소비
- 처리 상태 저장

### 학습 목적

분산 락과 멱등성은 같은 개념은 아니다.

- 분산 락: 동시에 실행되는 작업 수를 통제
- 멱등성: 동일 요청이 여러 번 들어와도 결과를 한 번 처리한 것처럼 유지

하지만 둘 다 중복 실행과 동시 요청 제어라는 실무 문제에서 함께 등장하므로 한 문서에서 비교한다.

### 핵심 질문

- 단일 JVM Lock으로 해결할 수 없는 이유는 무엇인가?
- 락을 획득한 서버가 죽으면 어떻게 되는가?
- 작업이 Lock TTL보다 오래 걸리면 어떻게 되는가?
- 결제 성공 후 응답이 유실되면 어떻게 처리하는가?
- Unique Constraint만으로 멱등성을 완전히 보장할 수 있는가?

---

# 09. 시스템 설계

시스템 사례마다 DB, Redis, 동시성, 장애 대응 설명이 반복될 수 있다.  
따라서 설계 원칙과 사례 문서를 분리한다.

---

## `시스템설계-답변법.md`

### 포함할 내용

- 기능 요구사항
- 비기능 요구사항
- 트래픽
- 데이터 규모
- 읽기·쓰기 비율
- 응답 시간
- 정합성
- 가용성
- 데이터 유실 허용 여부
- 단순한 초기 설계
- 병목 분석
- 확장 전략
- 장애 대응
- 면접 답변 순서

### 권장 답변 순서

```text
1. 요구사항 확인
2. 데이터 규모와 트래픽 확인
3. 가장 단순한 설계 제시
4. 저장 구조와 조회 구조 설명
5. 병목 지점 설명
6. 확장 방법 제시
7. 장애와 정합성 설명
8. 선택한 방식의 단점 설명
```

### 핵심 질문

- 정확성이 중요한가, 가용성이 중요한가?
- 데이터 유실이나 지연을 허용할 수 있는가?
- 읽기가 많은가, 쓰기가 많은가?
- 동기 처리가 필요한가?
- 서버가 여러 대일 때 공유 상태를 어떻게 관리할 것인가?
- 일부 컴포넌트가 장애 나면 전체 서비스는 어떻게 동작해야 하는가?

---

## `조회수-쿠폰-시스템.md`

### 비교 목적

두 시스템은 데이터 성격이 크게 다르므로 함께 비교하면 설계 선택 기준을 이해하기 좋다.

| 시스템 | 핵심 문제 |
|---|---|
| 조회수 | 높은 쓰기량, 일부 지연·오차 허용 가능 |
| 쿠폰 | 정확한 수량, 동시성, 중복 발급 방지 |

### 조회수 시스템 학습 내용

- 높은 쓰기량
- DB 직접 UPDATE의 문제
- Redis INCR
- 배치 반영
- Write Behind
- 데이터 유실 허용 범위
- 중복 조회 처리
- Hot Key

### 쿠폰 시스템 학습 내용

- 재고 수량
- 선착순 처리
- 중복 발급 방지
- 동시성 제어
- DB Lock
- Redis Atomic Operation
- 분산 락
- Queue
- 실패 복구
- 정확성

### 핵심 질문

- 조회수는 어느 정도의 오차를 허용할 수 있는가?
- 쿠폰 수량은 왜 정확해야 하는가?
- 동일한 Redis를 사용해도 두 시스템의 설계가 달라지는 이유는 무엇인가?
- 트래픽을 순차 처리하기 위해 Queue를 사용할 수 있는가?
- Redis 장애 시 어떻게 복구할 것인가?

---

## `주문-결제-시스템.md`

### 포함할 내용

- 주문 상태
- 결제 상태
- 트랜잭션
- 멱등성
- 외부 결제 API
- 네트워크 타임아웃
- 재시도
- 중복 결제
- 보상 처리
- 이벤트
- 메시지 큐
- Outbox Pattern 개념
- 장애 복구
- 감사 로그

### 핵심 질문

- 결제는 성공했지만 응답을 받지 못했다면 어떻게 하는가?
- 외부 API 호출을 DB 트랜잭션 안에 넣어도 되는가?
- 주문과 결제 상태가 다르면 어떻게 복구하는가?
- 중복 결제를 어떻게 방지하는가?
- 재시도 가능한 오류와 재시도하면 안 되는 오류를 어떻게 구분하는가?
- 메시지가 중복 소비되면 어떻게 처리하는가?

### 중요도

은행·금융권 백엔드 면접을 준비한다면 다음 내용을 특히 중요하게 본다.

- 데이터 정합성
- 멱등성
- 트랜잭션
- 장애 복구
- 감사 가능성
- 중복 처리 방지
- 상태 전이
- 외부 시스템 연동 실패
```

## 최종 결과물

| 결과물 | 수량 | 내용 |
| --- | --- | --- |
| 개념 노트 | 주제별 1개 | 정의 · 원리 · 복잡도 |
| 비교표 | 10개 이상 | ArrayList vs LinkedList 등 |
| 실무 문제 | 주 2개 | 저장 · 조회 · 동시성 |
| 코드 구현 | 주 1개 | 자료구조 · 동시성 예제 |
| 모의 면접 | 주 1회 | 꼬리 질문 연습 |
| 시스템 설계 | 최종 4개 | 조회수 · 쿠폰 · 주문 · 결제 |

### 면접 직전 반복용 핵심 비교표

- ArrayList vs LinkedList
- HashMap vs TreeMap
- HashMap vs ConcurrentHashMap
- Queue vs Message Queue
- Heap vs 전체 정렬
- Offset vs Cursor Pagination
- 낙관적 락 vs 비관적 락
- Local Cache vs Redis
- DB Lock vs Distributed Lock
- 동기 처리 vs 비동기 처리