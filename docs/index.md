# 목차

**링크가 걸린 항목은 작성 완료**, 링크 없는 항목은 아직 쓰지 않은 노트다.
`/study-section <번호>`를 실행하면 그 섹션에서 링크 없는 항목을 찾아 작성한다.

**섹션 제목을 누르면 그 섹션의 「한 페이지 요약」이 열린다** — 그 섹션 노트 전체의 핵심 · 치트시트 ·
자주 틀리는 것을 한 페이지에 모은 문서다 (좌측 메뉴에서 섹션 이름을 눌러도 같은 페이지로 간다).

모든 노트는 같은 6개 섹션으로 되어 있다.

```text
1. 핵심 요약 → 2. 동작 원리 → 3. 특징과 비교 → 4. 실무 주의사항 → 5. 예제 → 6. 면접 정리
```

---

### [01. 복잡도 · 자료구조](01-복잡도-자료구조/index.md)

- [시간 복잡도와 공간 복잡도](01-복잡도-자료구조/시간-공간-복잡도/시간-공간-복잡도.md)
- [Amortized Analysis (상각 분석)](01-복잡도-자료구조/Amortized-Analysis/Amortized-Analysis.md)
- [선형 자료구조 비교](01-복잡도-자료구조/선형-자료구조-비교/선형-자료구조-비교.md)
- [해시와 트리 비교](01-복잡도-자료구조/해시-트리-비교/해시-트리-비교.md)
- [Heap과 PriorityQueue](01-복잡도-자료구조/Heap-PriorityQueue/Heap-PriorityQueue.md)
- [Collection 선택 기준](01-복잡도-자료구조/Collection-선택-기준/Collection-선택-기준.md)

### [02. 알고리즘](02-알고리즘/index.md)

- [탐색과 정렬](02-알고리즘/탐색-정렬/탐색-정렬.md)
- [구간 처리](02-알고리즘/구간-처리/구간-처리.md)
- [그래프 문제 해결](02-알고리즘/그래프-문제해결/그래프-문제해결.md)

### [03. Java](03-Java/index.md)

- [Java Collection](03-Java/Java-Collection/Java-Collection.md)
- [equals · hashCode](03-Java/equals-hashCode/equals-hashCode.md)
- [객체지향과 SOLID](03-Java/객체지향-SOLID/객체지향-SOLID.md)
- [Generic · Exception · Stream](03-Java/Generic-Exception-Stream/Generic-Exception-Stream.md)
- [JVM 메모리와 GC](03-Java/JVM-메모리-GC/JVM-메모리-GC.md)

### 04. 동시성

- [Thread와 동기화](04-동시성/Thread-동기화/Thread-동기화.md)
- [Atomic과 Concurrent Collection](04-동시성/Atomic-Concurrent-Collection/Atomic-Concurrent-Collection.md)
- [ThreadPool과 Deadlock](04-동시성/ThreadPool-Deadlock/ThreadPool-Deadlock.md)

### 05. Spring

- [IoC · DI와 Bean](05-Spring/IoC-DI와-Bean/IoC-DI와-Bean.md)
- [AOP · Proxy와 Transactional](05-Spring/AOP-Proxy-Transactional/AOP-Proxy-Transactional.md)
- [Spring MVC 요청 흐름](05-Spring/Spring-MVC-요청흐름/Spring-MVC-요청흐름.md)
- [Spring Boot와 예외 처리](05-Spring/Spring-Boot와-예외처리/Spring-Boot와-예외처리.md)

### 06. 데이터베이스

- [인덱스와 실행 계획](06-데이터베이스/인덱스-실행계획/인덱스-실행계획.md)
- [조인과 페이지네이션](06-데이터베이스/조인-페이지네이션/조인-페이지네이션.md)
- [대용량 데이터 분할](06-데이터베이스/대용량-데이터-분할/대용량-데이터-분할.md)
- [Connection Pool과 쿼리 튜닝](06-데이터베이스/ConnectionPool과-쿼리튜닝/ConnectionPool과-쿼리튜닝.md)

### 07. 트랜잭션 · 데이터 접근

- [ACID와 격리 수준](07-트랜잭션-데이터접근/ACID-격리수준/ACID-격리수준.md)
- [MVCC](07-트랜잭션-데이터접근/MVCC/MVCC.md)
- [낙관적 락 · 비관적 락](07-트랜잭션-데이터접근/낙관적-비관적-락/낙관적-비관적-락.md)
- [JDBC · MyBatis · JPA](07-트랜잭션-데이터접근/JDBC-MyBatis-JPA/JDBC-MyBatis-JPA.md)

### [08. 캐시 · Redis](08-캐시-Redis/index.md)

- [캐시 전략과 정합성](08-캐시-Redis/캐시-전략-정합성/캐시-전략-정합성.md)
- [Cache Stampede와 Request Collapsing](08-캐시-Redis/Cache-Stampede/Cache-Stampede.md)
- [Redis 자료구조와 활용](08-캐시-Redis/Redis-자료구조/Redis-자료구조.md)
- [분산 락과 멱등성](08-캐시-Redis/분산락-멱등성/분산락-멱등성.md)

### [09. 웹 · 보안](09-웹-보안/index.md)

- [HTTP · TCP 네트워크](09-웹-보안/HTTP-TCP-네트워크/HTTP-TCP-네트워크.md)
- [REST와 API 설계](09-웹-보안/REST-API-설계/REST-API-설계.md)
- [쿠키 · 세션 · JWT](09-웹-보안/쿠키-세션-JWT/쿠키-세션-JWT.md)
- [인증 · 인가 · CORS · CSRF](09-웹-보안/인증인가-CORS-CSRF/인증인가-CORS-CSRF.md)

### 10. 테스트 · 운영

- 단위 테스트와 통합 테스트
- Mock · Spring Test · Testcontainers
- 로그 · 메트릭 · 트레이싱
- 장애 분석과 성능 개선

### 11. 메시징 · 시스템 설계

- 동기 · 비동기와 메시지 큐
- 메시지 중복 · 재시도 · Outbox
- 시스템 설계 답변법
- 선착순 쿠폰 시스템
- 주문 · 결제 시스템

### 12. 경험 기반 면접

- 프로젝트 · 경력 소개
- 장애 대응 경험
- 성능 개선 경험
- 기술 선택과 트레이드오프
- 예상 질문과 답변
