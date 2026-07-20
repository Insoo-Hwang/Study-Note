# Study Note

백엔드 면접을 위한 개인 학습 노트입니다. **"어떤 상황에서 무엇을 선택하고 왜 그렇게 했는지 설명할 수 있는 수준"** 을 목표로 합니다.

!!! tip "사용법"
    상단 🔍 **검색창**에 키워드(`인덱스`, `낙관적 락`, `Cache Aside` 등)를 입력하면 바로 이동합니다.

```
복잡도 → 자료구조 → 알고리즘 → Java 컬렉션 → 동시성
      → 데이터베이스 → 트랜잭션 → 캐시·Redis → 시스템 설계
```

---

## 📚 목차

### 1. 복잡도

- [Big-O](01-시간 복잡도/Big-O/Big-O.md)
- 공간 복잡도
- Amortized 분석

### 2. 자료구조

- Array
- ArrayList
- LinkedList
- Stack
- Queue
- Deque
- HashMap
- HashSet
- TreeMap
- Heap
- PriorityQueue

### 3. 알고리즘

- 선형 탐색
- 이진 탐색
- 정렬
- Comparable · Comparator
- 투 포인터
- 슬라이딩 윈도우
- DFS
- BFS
- 그리디
- DP

### 4. Java 컬렉션

- ArrayList 내부 구조
- HashMap 내부 구조
- TreeMap · PriorityQueue 내부 구조
- equals · hashCode
- 구현체 선택 기준

### 5. 동시성

- Thread · Race Condition
- synchronized · Lock
- volatile · Atomic
- ConcurrentHashMap
- ThreadPool · Deadlock

### 6. 데이터베이스

- B-Tree · B+Tree
- 단일 인덱스
- 복합 인덱스
- 실행 계획
- 커버링 인덱스
- 정규화
- 조인
- 페이지네이션
- 파티셔닝
- 샤딩

### 7. 트랜잭션

- ACID
- 격리 수준
- MVCC
- 비관적 락
- 낙관적 락

### 8. 캐시 · Redis

- Local Cache
- Cache Aside · TTL
- Redis 자료구조
- Cache Stampede
- 분산 락 · 멱등성

### 9. 시스템 설계

- 요구사항 분석
- 조회수 시스템
- 쿠폰 시스템
- 결제 시스템
- 모의 면접
