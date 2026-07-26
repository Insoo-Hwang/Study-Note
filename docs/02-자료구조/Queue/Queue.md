# Queue

> **큐(Queue)는 먼저 넣은 데이터를 먼저 꺼내는(FIFO) 규칙으로, 들어온 순서를 보장하며 데이터를 처리하는 자료구조다.**

---

## 1. 핵심 요약

* 큐는 **뒤(rear)로 넣고 앞(front)에서 꺼내는** 구조이며, 이를 **FIFO(First In First Out)** 라고 한다.
* 핵심 연산은 `offer`(넣기), `poll`(꺼내기), `peek`(앞 확인)이며 모두 **O(1)** 이다.
* 큐의 본질적 가치는 **"생산 속도와 소비 속도가 다를 때 그 차이를 흡수하는 완충 장치"** 라는 데 있다.
* Java의 `Queue`는 인터페이스이며, 구현체로 `ArrayDeque`, `LinkedList`, `PriorityQueue`, `LinkedBlockingQueue` 등이 있다.
* **예외를 던지는 메서드(`add`/`remove`/`element`)와 특수값을 반환하는 메서드(`offer`/`poll`/`peek`)** 를 반드시 구분해야 한다.

---

## 2. 등장 배경

### 해결하려는 문제

현실의 처리에는 **순서가 곧 공정성**인 경우가 많다.

* 먼저 주문한 사람이 먼저 배송받아야 한다.
* 먼저 접수된 요청이 먼저 처리되어야 한다.
* 먼저 도착한 패킷이 먼저 전달되어야 한다.

스택(LIFO)으로 처리하면 나중에 온 요청이 먼저 처리되고, 먼저 온 요청은 계속 밀린다. 이를 **기아 상태(starvation)** 라고 한다.

또 하나 더 중요한 문제가 있다. **만드는 쪽과 처리하는 쪽의 속도가 다르다.**

```text
초당 1000건의 요청이 들어옴
       ↓
처리 서버는 초당 200건만 처리 가능
       ↓
큐가 없다면 → 800건은 그냥 실패
큐가 있다면 → 대기열에 쌓아두고 순서대로 처리
```

큐는 이 속도 차이를 흡수하는 **완충 장치(buffer)** 다. 이것이 실무에서 큐가 존재하는 진짜 이유다.

### 이 개념이 없을 때

* 순서를 보장할 수 없어 먼저 온 요청이 영원히 처리되지 않을 수 있다.
* 순간 트래픽이 몰리면 처리하지 못한 요청을 그대로 버려야 한다.
* 생산자와 소비자가 서로의 속도에 강하게 묶여, 한쪽이 느려지면 전체가 멈춘다.
* 무거운 작업(메일 발송, 이미지 변환)을 요청 처리 중에 동기로 실행해야 해서 응답이 느려진다.
* BFS처럼 "가까운 것부터 차례로" 탐색하는 알고리즘을 구현할 수 없다.

---

## 3. 핵심 개념

| 개념                    | 설명                                | 중요한 이유                                    |
| --------------------- | --------------------------------- | ----------------------------------------- |
| **FIFO**              | 먼저 들어온 것이 먼저 나가는 규칙               | 순서 보장과 공정성의 근거다                           |
| **front(head)**       | 다음에 꺼낼 원소가 있는 위치                  | `poll`/`peek`의 대상이다                       |
| **rear(tail)**        | 다음에 넣을 위치                         | `offer`의 대상이다                             |
| **`offer` / `add`**   | 큐에 데이터를 넣는 연산                     | 가득 찼을 때 `offer`는 `false`, `add`는 예외를 던진다  |
| **`poll` / `remove`** | 앞에서 꺼내며 제거하는 연산                   | 비었을 때 `poll`은 `null`, `remove`는 예외를 던진다   |
| **`peek` / `element`** | 앞의 데이터를 제거하지 않고 확인                | 처리 여부를 판단한 뒤 꺼내야 할 때 쓴다                   |
| **순환 배열(원형 큐)**       | 배열의 끝과 시작을 이어 붙인 것처럼 인덱스를 돌려 쓰는 방식 | 배열 큐에서 원소 이동 없이 O(1)을 만드는 핵심 기법이다         |
| **유계 큐(bounded)**     | 최대 크기가 정해진 큐                      | 무한히 쌓여 메모리가 터지는 것을 막는다                    |
| **무계 큐(unbounded)**   | 크기 제한이 없는 큐                       | 편하지만 폭주 시 `OutOfMemoryError` 위험이 있다       |
| **블로킹 큐**             | 비었으면 기다리고 가득 차면 기다리는 큐            | 생산자·소비자 패턴의 표준 도구다                        |
| **백프레셔(backpressure)** | 소비자가 못 따라갈 때 생산자를 늦추는 흐름 제어       | 유계 큐가 있어야 성립하는 안정성 장치다                    |

개념 간 관계는 다음과 같다.

```text
       poll / peek                       offer
            ↑                              ↓
        ┌───────┬───────┬───────┬───────┐
        │   A   │   B   │   C   │       │
        └───────┴───────┴───────┴───────┘
            ↑                       ↑
         front                    rear
      (가장 오래된 것)            (가장 최근 것)
```

**핵심 관계**: 큐의 크기 제한(유계/무계)이 백프레셔 가능 여부를 결정하고, 그것이 시스템 안정성을 결정한다.

---

## 4. 구조와 동작 원리

### 단순 배열로 만들면 생기는 문제

```text
[A][B][C][D]
 front=0        rear=4

poll() → A 반환
[ ][B][C][D]
    front=1

이제 offer(E)를 하려면?
→ rear가 이미 배열 끝 → 공간이 앞에 남았는데 못 쓴다
→ 전부 앞으로 당기면 O(n)
```

### 순환 배열이 해결책

배열의 끝에서 다시 0번으로 돌아오게 만든다.

```text
capacity = 5

초기        [ ][ ][ ][ ][ ]     front=0, rear=0
offer(A~D)  [A][B][C][D][ ]     front=0, rear=4
poll() ×2   [ ][ ][C][D][ ]     front=2, rear=4
offer(E)    [ ][ ][C][D][E]     front=2, rear=0  ← 끝에서 0으로 순환
offer(F)    [F][ ][C][D][E]     front=2, rear=1  ← 앞의 빈 공간 재사용
```

인덱스 순환은 나머지 연산으로 계산한다.

```text
다음 위치 = (현재 위치 + 1) % capacity
```

원형으로 그리면 다음과 같다.

```text
             0
          ┌─────┐
      4  │   F   │  1
    ┌────┴───────┴────┐
    │  E           C  │
    │       큐        │
    └────┬───────┬────┘
      3  │   D   │  2
          └─────┘

front → C 방향으로 진행,  rear → F 다음 칸
```

![단순 배열의 문제와 순환 배열의 해결 방식 비교](queue-circular.svg)

*인덱스를 배열 길이로 나눈 나머지로 이동시키면 원소를 하나도 옮기지 않고 앞의 빈 공간을 재사용한다.*

### 동작 순서

1. `offer(값)`을 호출한다.
2. 큐가 가득 찼는지 확인한다. 유계 큐라면 `false` 반환(또는 대기), 무계 큐라면 확장한다.
3. `elements[rear] = 값`으로 저장한다.
4. `rear = (rear + 1) % capacity`로 다음 위치를 계산한다. → **O(1)**
5. `poll()`을 호출하면 큐가 비었는지 확인한다. 비었으면 `null`을 반환한다.
6. `값 = elements[front]`를 읽고 `elements[front] = null`로 참조를 끊는다.
7. `front = (front + 1) % capacity`로 이동한다. → **O(1)**

**어떤 경우에도 원소를 이동시키지 않는다.** 이것이 큐가 O(1)인 이유다.

### BFS에서의 큐 동작

그래프 `1 - 2`, `1 - 3`, `2 - 4`에서 1부터 탐색한다.

```text
초기       큐: [1]              방문: {1}
poll 1  →  1의 이웃 2, 3 추가
           큐: [2, 3]           방문: {1,2,3}
poll 2  →  2의 이웃 4 추가
           큐: [3, 4]           방문: {1,2,3,4}
poll 3  →  새 이웃 없음
           큐: [4]
poll 4  →  새 이웃 없음
           큐: []               탐색 종료
```

방문 순서는 `1 → 2 → 3 → 4`로, **시작점에서 가까운 순서**가 된다. 큐가 FIFO이기 때문에 자동으로 얻어지는 성질이다.

---

## 5. 코드 또는 사용 예시

### 직접 만들어 보는 순환 배열 큐

```java
public class CircularQueue {

    private final Object[] elements;
    private int front;
    private int rear;
    private int size;

    public CircularQueue(int capacity) {
        this.elements = new Object[capacity];
        this.front = 0;
        this.rear = 0;
        this.size = 0;
    }

    public boolean offer(Object value) {
        if (size == elements.length) {
            return false;
        }
        elements[rear] = value;
        rear = (rear + 1) % elements.length;
        size++;
        return true;
    }

    public Object poll() {
        if (size == 0) {
            return null;
        }
        Object value = elements[front];
        elements[front] = null;
        front = (front + 1) % elements.length;
        size--;
        return value;
    }

    public Object peek() {
        if (size == 0) {
            return null;
        }
        return elements[front];
    }

    public int size() {
        return size;
    }

    public static void main(String[] args) {
        CircularQueue queue = new CircularQueue(3);

        System.out.println(queue.offer("A"));   // true
        System.out.println(queue.offer("B"));   // true
        System.out.println(queue.offer("C"));   // true
        System.out.println(queue.offer("D"));   // false (가득 참)

        System.out.println(queue.poll());       // A
        System.out.println(queue.offer("D"));   // true (빈 자리 재사용)
        System.out.println(queue.peek());       // B
    }
}
```

각 부분의 역할은 다음과 같다.

```java
rear = (rear + 1) % elements.length;
```

배열 끝에 도달하면 0으로 돌아간다. 순환 큐의 핵심 한 줄이다.

```java
private int size;
```

`front == rear`만으로는 "비어 있음"과 "가득 참"을 구분할 수 없다. `size`를 따로 세면 이 문제가 사라진다.

```java
elements[front] = null;
```

꺼낸 자리의 참조를 끊어 GC가 회수할 수 있게 한다.

```java
if (size == elements.length) { return false; }
```

유계 큐의 특징이다. 가득 차면 실패를 알린다. 이 신호가 백프레셔의 출발점이다.

### Java `Queue` 사용

```java
import java.util.ArrayDeque;
import java.util.Queue;

public class QueueUsage {

    public static void main(String[] args) {
        Queue<String> queue = new ArrayDeque<>();

        queue.offer("주문1");
        queue.offer("주문2");
        queue.offer("주문3");

        System.out.println("다음 처리 대상: " + queue.peek());

        while (!queue.isEmpty()) {
            String order = queue.poll();
            System.out.println("처리: " + order);
        }

        System.out.println("비었을 때 poll: " + queue.poll());   // null
    }
}
```

### 반드시 구분해야 하는 두 계열의 메서드

| 목적    | 예외를 던지는 메서드    | 특수값을 반환하는 메서드      |
| ----- | -------------- | ------------------ |
| 넣기    | `add(e)` → 예외  | `offer(e)` → `false` |
| 꺼내기   | `remove()` → 예외 | `poll()` → `null`  |
| 앞 확인  | `element()` → 예외 | `peek()` → `null`  |

```java
Queue<String> queue = new ArrayDeque<>();

System.out.println(queue.poll());     // null  — 흐름 제어에 유리
System.out.println(queue.remove());   // NoSuchElementException
```

일반적으로는 **`offer`/`poll`/`peek`** 을 쓴다. 예외로 흐름을 제어하는 것보다 반환값으로 판단하는 편이 명확하기 때문이다. 단, `null`을 저장할 수 있는 큐라면 `poll()`의 `null`이 "비어있음"인지 "저장된 값"인지 헷갈릴 수 있어 주의해야 한다. (`ArrayDeque`는 아예 `null` 저장을 금지해 이 모호함을 없앴다.)

### 생산자·소비자 패턴

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class ProducerConsumer {

    public static void main(String[] args) throws InterruptedException {
        final BlockingQueue<String> queue = new ArrayBlockingQueue<>(5);

        Thread producer = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    for (int i = 1; i <= 10; i++) {
                        queue.put("작업" + i);      // 가득 차면 여기서 대기
                        System.out.println("생산: 작업" + i);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });

        Thread consumer = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    for (int i = 1; i <= 10; i++) {
                        String task = queue.take();   // 비었으면 여기서 대기
                        System.out.println("소비: " + task);
                        Thread.sleep(100);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });

        producer.start();
        consumer.start();

        producer.join();
        consumer.join();
    }
}
```

`put`과 `take`가 핵심이다.

```text
큐가 가득 참  →  producer.put()이 블로킹  →  생산 속도가 자동으로 늦춰짐 (백프레셔)
큐가 빔      →  consumer.take()가 블로킹  →  바쁜 대기(busy wait) 없이 효율적으로 기다림
```

큐 크기를 5로 제한했기 때문에 생산자가 아무리 빨라도 메모리가 무한정 늘지 않는다. **유계 큐가 시스템을 보호한다.**

---

## 6. 성능 특성

| 연산                 | 평균 시간 복잡도 | 최악 시간 복잡도 | 설명                          |
| ------------------ | -------: | -------: | --------------------------- |
| `offer` / `add`    |     O(1) |     O(n) | 무계 배열 큐에서 확장이 일어나는 순간만 O(n) |
| `poll` / `remove`  |     O(1) |     O(1) | front 인덱스만 이동한다             |
| `peek` / `element` |     O(1) |     O(1) | front 위치를 읽기만 한다            |
| `size` / `isEmpty` |     O(1) |     O(1) | 카운터로 즉시 판단한다                |
| `contains`         |     O(n) |     O(n) | 큐는 검색용 구조가 아니다              |
| 임의 위치 접근           |      미지원 |      미지원 | 인덱스 접근 개념이 없다               |

공간 복잡도는 **O(n)** 이다.

시간 복잡도로 표현하기 어려운 **시스템 관점의 비용**도 함께 봐야 한다.

| 기준         | 설명                                     |
| ---------- | -------------------------------------- |
| 메모리 사용량    | 무계 큐는 소비가 느리면 무한히 쌓여 OOM 위험이 있다        |
| 대기 시간(지연)  | 큐가 길수록 마지막에 들어온 작업의 대기 시간이 길어진다        |
| 처리량        | 큐가 완충 역할을 해 순간 부하를 평탄화한다               |
| 락 경합       | 여러 스레드가 같은 큐를 쓰면 락 경합이 병목이 될 수 있다      |
| 네트워크·직렬화 비용 | 분산 메시지 큐(Kafka 등)는 직렬화와 네트워크 왕복 비용이 붙는다 |

데이터가 많아질 때의 변화는 다음과 같다.

* `offer`/`poll` 비용은 개수와 무관하게 O(1)로 유지된다.
* **큐 길이가 곧 지연 시간**이 된다. 처리량이 초당 200건인데 10,000건이 쌓이면 마지막 작업은 50초를 기다린다.
* 무계 큐는 소비 속도가 생산 속도보다 느린 순간부터 계속 자란다. 결국 메모리가 터진다.

```text
생산 속도 > 소비 속도가 지속되면

무계 큐  →  메모리 계속 증가  →  OutOfMemoryError (전체 서버 다운)
유계 큐  →  가득 참  →  거절 또는 생산자 대기 (일부 실패, 서버는 생존)
```

**"큐가 있으니 괜찮다"가 아니라 "큐가 계속 자라면 결국 터진다"** 가 정확한 이해다. 큐 길이는 반드시 모니터링해야 하는 지표다.

---

## 7. 장점과 단점

| 장점                  | 이유                                       |
| ------------------- | ---------------------------------------- |
| 순서를 보장한다            | FIFO 규칙으로 먼저 들어온 요청이 밀리지 않는다             |
| 모든 핵심 연산이 O(1)이다    | 순환 배열이나 연결 노드로 원소 이동 없이 양 끝만 조작한다        |
| 생산자와 소비자를 분리한다      | 서로의 속도에 직접 묶이지 않아 한쪽이 느려도 전체가 멈추지 않는다    |
| 순간 부하를 평탄화한다        | 트래픽 폭주를 대기열에 쌓아 두고 처리 속도에 맞춰 소화한다        |
| 응답 시간을 줄일 수 있다      | 무거운 작업을 큐에 넣고 즉시 응답한 뒤 비동기로 처리한다         |
| 재시도와 장애 격리가 쉬워진다    | 실패한 작업을 다시 큐에 넣거나 별도 큐로 보낼 수 있다          |

| 단점                    | 이유 및 주의점                                       |
| --------------------- | ---------------------------------------------- |
| 중간 원소에 접근할 수 없다       | 앞에서만 꺼낼 수 있어 특정 작업을 골라 처리할 수 없다                |
| 무계 큐는 메모리 위험이 있다      | 소비가 느리면 무한히 쌓여 `OutOfMemoryError`가 발생한다        |
| 큐 길이가 곧 지연이 된다        | 쌓일수록 마지막 작업의 대기 시간이 길어져 사실상 실패와 같아진다           |
| 우선순위를 표현할 수 없다        | 급한 작업도 순서를 기다려야 한다. 필요하면 `PriorityQueue`를 쓴다   |
| 비동기 처리는 복잡도를 올린다      | 실패 처리, 중복 처리, 순서 보장, 모니터링을 모두 설계해야 한다          |
| 결과를 즉시 알 수 없다         | 큐에 넣은 시점에는 성공/실패를 모른다. 상태 조회 수단이 별도로 필요하다      |

---

## 8. 사용 기준

### 사용하기 좋은 상황

* 들어온 순서대로 처리해야 하는 경우 (주문 처리, 요청 접수)
* 생산 속도와 소비 속도가 다른 경우 (트래픽 폭주 흡수)
* 무거운 작업을 응답 후에 처리하고 싶은 경우 (메일 발송, 이미지 리사이징, 정산)
* BFS처럼 가까운 것부터 차례로 탐색해야 하는 경우
* 여러 소비자에게 작업을 나눠 주고 싶은 경우
* 서비스 간 결합을 느슨하게 만들고 싶은 경우 (메시지 큐)

### 사용하지 않는 것이 좋은 상황

* 마지막 것부터 처리해야 하는 경우 → **스택**
* 중요도에 따라 처리 순서를 바꿔야 하는 경우 → **`PriorityQueue`**
* 즉시 결과를 반환해야 하는 경우 (로그인 검증, 잔액 조회 등 동기 응답)
* 인덱스나 키로 임의 접근이 필요한 경우 → `List`, `Map`
* 소비자가 생산자보다 구조적으로 느린데 무계 큐를 쓰려는 경우

### 선택 기준

1. 처리 순서가 **먼저 온 것 먼저**인가?
2. 생산·소비 속도 차이를 흡수해야 하는가?
3. 크기 제한이 필요한가? → **거의 항상 필요하다** (유계 큐)
4. 가득 찼을 때 어떻게 할 것인가? (거절 / 대기 / 버리기)
5. 여러 스레드가 공유하는가? → `BlockingQueue` 계열
6. 서버 재시작에도 작업이 살아남아야 하는가? → 인메모리 큐가 아니라 **메시지 브로커**

```text
단일 JVM · 단일 스레드      →  ArrayDeque
단일 JVM · 여러 스레드      →  LinkedBlockingQueue / ArrayBlockingQueue
우선순위 필요               →  PriorityQueue
서버 재시작에도 유실 금지    →  Kafka / RabbitMQ / Redis Stream
```

---

## 9. 비슷한 개념 비교

### Queue와 Stack

| 비교 항목  | Queue        | Stack           | 선택 기준        |
| ------ | ------------ | --------------- | ------------ |
| 목적     | 먼저 온 것 먼저 처리 | 마지막 것 먼저 처리     | 처리 순서 요구사항   |
| 규칙     | FIFO         | LIFO            | 공정성 vs 되돌아가기 |
| 접근 지점  | 양 끝(넣기·꺼내기)  | 한쪽 끝(top)       | 구조 차이        |
| 대표 알고리즘 | BFS          | DFS             | 탐색 방식        |
| 성능     | 모든 연산 O(1)   | 모든 연산 O(1)      | 차이 없음        |
| 적합한 상황 | 작업 대기열, 버퍼   | 괄호 검사, Undo, 재귀 | 문제 성격        |

### Queue 구현체 비교

| 비교 항목  | `ArrayDeque`   | `LinkedList`  | `LinkedBlockingQueue`  | 선택 기준       |
| ------ | -------------- | ------------- | ---------------------- | ----------- |
| 내부 구조  | 순환 배열          | 양방향 연결 노드     | 연결 노드 + 락              | 메모리·속도      |
| 스레드 안전 | 아니오            | 아니오           | 예                      | 동시 접근 여부    |
| 블로킹 지원 | 아니오            | 아니오           | 예 (`put`/`take`)       | 생산자·소비자 패턴  |
| 크기 제한  | 무계(자동 확장)      | 무계            | 유계 지정 가능               | 메모리 보호 필요 여부 |
| `null` 저장 | 불가             | 가능            | 불가                     | `null` 의미 모호성 |
| 속도     | 가장 빠름          | 느림            | 락 비용 있음                | 단일 스레드면 ArrayDeque |
| 적합한 상황 | 단일 스레드 큐·스택·덱  | 특별한 이유 없으면 비추천 | 스레드 풀 작업 대기열           | 상황별         |

### 인메모리 큐와 메시지 큐(Kafka·RabbitMQ)

| 비교 항목  | 인메모리 큐 (`ArrayDeque` 등)  | 메시지 큐 (Kafka, RabbitMQ) | 선택 기준         |
| ------ | ----------------------- | ----------------------- | ------------- |
| 목적     | 한 프로세스 안의 작업 버퍼         | 서버 간 비동기 통신과 작업 분산      | 범위(프로세스 vs 시스템) |
| 영속성    | 없음 (재시작 시 유실)           | 디스크에 저장, 재시작에도 생존       | 유실 허용 여부      |
| 성능     | 매우 빠름 (메모리 접근)          | 네트워크·직렬화 비용 발생          | 지연 허용 범위      |
| 확장성    | 서버 1대 안에서만              | 여러 소비자·파티션으로 수평 확장      | 처리량 요구        |
| 운영 부담  | 없음                      | 브로커 운영, 모니터링, 장애 대응 필요  | 팀 역량과 규모      |
| 장점     | 단순하고 빠름                 | 유실 방지, 재시도, 서비스 분리      | 요구사항          |
| 단점     | 서버 죽으면 작업 전부 유실         | 인프라 복잡도 증가              | 트레이드오프       |
| 적합한 상황 | 유실돼도 되는 가벼운 작업          | 결제·정산·알림 등 유실이 치명적인 작업  | **유실 허용 여부가 핵심** |

> **실무 판단 기준**: "이 작업이 사라져도 괜찮은가?"를 먼저 묻는다. 사라지면 안 되는 작업(결제 후속 처리, 정산)은 절대 인메모리 큐에 넣지 않는다. 서버가 재배포되는 순간 그대로 증발한다.

---

## 10. 백엔드 실무 적용

### Spring·Java

큐는 Spring 애플리케이션 내부에 이미 곳곳에 들어 있다.

* **스레드 풀의 작업 대기열**: `ThreadPoolExecutor`는 내부에 `BlockingQueue`를 갖는다.

```java
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.LinkedBlockingQueue;

public class ThreadPoolExample {

    public static void main(String[] args) {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
                5,                                     // corePoolSize
                10,                                    // maximumPoolSize
                60L, TimeUnit.SECONDS,                 // 유휴 스레드 유지 시간
                new LinkedBlockingQueue<Runnable>(100) // 유계 작업 대기열
        );

        executor.execute(new Runnable() {
            @Override
            public void run() {
                System.out.println("작업 실행: " + Thread.currentThread().getName());
            }
        });

        executor.shutdown();
    }
}
```

동작 순서를 정확히 알아야 한다.

```text
작업 도착
   ↓
현재 스레드 수 < corePoolSize ?  →  예: 새 스레드 생성
   ↓ 아니오
큐에 여유가 있는가?             →  예: 큐에 넣고 대기
   ↓ 아니오
현재 스레드 수 < maximumPoolSize ? → 예: 새 스레드 생성
   ↓ 아니오
거부 정책(RejectedExecutionHandler) 실행
```

여기서 흔한 함정: **큐를 무계로 두면 `maximumPoolSize`가 영원히 쓰이지 않는다.** 큐가 절대 가득 차지 않으므로 스레드는 `corePoolSize`를 넘어 늘어나지 않고, 대신 큐만 계속 자라다 OOM이 난다. `Executors.newFixedThreadPool()`이 정확히 이 구조라서 실무에서 위험하다고 이야기된다.

* **`@Async` 비동기 처리**: 내부적으로 `ThreadPoolTaskExecutor`의 큐를 쓴다.
* **`@Scheduled` 작업**: 스케줄러도 작업 큐를 갖는다.
* **톰캣의 요청 처리**: `acceptCount` 설정이 곧 OS 수준 대기 큐의 크기다.

```text
클라이언트 요청
      ↓
톰캣 accept 큐 (acceptCount)
      ↓
워커 스레드 풀 (maxThreads)
      ↓
애플리케이션 처리
```

### 데이터베이스·캐시

* **커넥션 풀 대기 큐**: HikariCP는 커넥션이 모두 사용 중이면 요청 스레드를 대기시킨다. `connectionTimeout`을 넘기면 예외가 난다. 이 대기열이 길어지는 것이 DB 병목의 대표 신호다.
* **Redis List로 만드는 간단한 큐**: `LPUSH`로 넣고 `BRPOP`으로 꺼낸다. `BRPOP`은 데이터가 올 때까지 블로킹한다.

```text
LPUSH task:queue "작업1"     ← 생산자
BRPOP task:queue 0          ← 소비자 (데이터 올 때까지 대기)
```

다만 Redis List 큐는 **소비자가 꺼낸 직후 죽으면 작업이 사라진다.** 유실이 문제라면 `RPOPLPUSH`로 처리 중 목록에 옮겨 두거나, Redis Stream(소비자 그룹 + ACK)이나 Kafka를 쓴다.

* **아웃박스 패턴**: DB 트랜잭션 안에서 "보낼 메시지"를 테이블에 저장하고, 별도 프로세스가 그 테이블을 큐처럼 읽어 발송한다. DB 커밋과 메시지 발송의 원자성을 확보하는 표준 기법이다.

```sql
CREATE TABLE outbox (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type  VARCHAR(50)  NOT NULL,
    payload     TEXT         NOT NULL,
    published   BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  DATETIME     NOT NULL,
    INDEX idx_published_created (published, created_at)
);
```

### 동시성·분산 환경

* `ArrayDeque`, `LinkedList`는 **스레드 안전하지 않다.** 여러 스레드가 쓰면 `BlockingQueue` 계열이나 `ConcurrentLinkedQueue`를 쓴다.
* 분산 환경에서 서버마다 인메모리 큐를 두면 **큐가 서버 수만큼 쪼개진다.** 순서 보장도, 전체 길이 파악도 불가능하다. 공유 큐가 필요하면 Redis, Kafka 같은 외부 저장소를 쓴다.
* Kafka는 **파티션 안에서만 순서를 보장한다.** 전역 순서가 필요하면 파티션을 1개로 두어야 하는데, 그러면 병렬성이 사라진다. 보통은 "같은 사용자 ID는 같은 파티션으로" 처럼 **키 기반 분배**로 필요한 범위의 순서만 보장한다.
* 소비자가 여러 대면 **같은 메시지가 두 번 처리될 수 있다.** (네트워크 재시도, ACK 유실) 그래서 소비자는 **멱등성**을 갖도록 설계해야 한다.

```text
메시지 "결제 완료 알림" 을 두 번 받았다면?
   ↓
처리 이력 테이블에서 message_id 확인
   ↓
이미 처리했으면 무시, 아니면 처리 후 기록
```

* **모니터링**: 큐 길이(lag)는 반드시 지표로 뽑아야 한다. 큐가 계속 자라면 소비자가 못 따라가고 있다는 뜻이며, 그대로 두면 메모리 폭발 또는 지연 폭증으로 이어진다.

---

## 11. 자주 하는 오해

| 잘못된 이해                             | 올바른 이해                                                              |
| ---------------------------------- | ------------------------------------------------------------------- |
| 큐를 쓰면 처리 속도가 빨라진다                  | 전체 처리량은 그대로다. 순간 부하를 시간에 걸쳐 분산할 뿐이다                                 |
| 큐가 있으면 트래픽이 몰려도 안전하다               | 소비가 계속 느리면 큐가 무한히 자라 결국 터진다. 유계 큐와 모니터링이 필요하다                       |
| 큐는 무한히 넣을 수 있다                     | 무계 큐도 힙 메모리 한계까지다. 유계 큐로 명시적으로 제한하는 것이 안전하다                         |
| `add`와 `offer`는 같다                 | 가득 찼을 때 `add`는 예외, `offer`는 `false`를 반환한다                           |
| `poll()`이 `null`이면 항상 큐가 빈 것이다     | `null` 저장이 가능한 큐라면 저장된 `null`일 수도 있다. `ArrayDeque`는 그래서 `null`을 금지한다 |
| 큐로 만들 때는 `LinkedList`가 정석이다        | `ArrayDeque`가 더 빠르고 메모리도 적게 쓴다                                      |
| 메시지 큐를 쓰면 메시지가 한 번만 처리된다           | 재시도·ACK 유실로 중복 처리가 발생한다. 소비자를 멱등하게 설계해야 한다                          |
| Kafka는 전체 메시지의 순서를 보장한다            | **파티션 단위**로만 순서를 보장한다. 전역 순서를 원하면 파티션 1개여야 한다                       |
| 인메모리 큐에 중요한 작업을 넣어도 된다             | 서버 재시작·배포·장애 시 그대로 유실된다. 유실되면 안 되는 작업은 브로커나 DB를 쓴다                  |
| 스레드 풀 큐를 크게 잡으면 안정성이 올라간다          | 오히려 지연만 길어지고 `maximumPoolSize`가 무력화된다. 큐 크기는 신중히 정해야 한다             |
| 비동기로 큐에 넣었으니 처리는 보장된다              | 큐에 넣은 것과 처리 완료는 다르다. 처리 결과를 확인할 수단(상태 저장, 실패 큐)이 필요하다              |

---

## 12. 면접 답변

### 기본 답변

큐는 먼저 넣은 데이터를 먼저 꺼내는 FIFO 자료구조입니다. 뒤에서 넣고 앞에서 꺼내며, `offer`, `poll`, `peek` 모두 O(1)입니다.

배열로 구현할 때는 원소를 앞으로 당기지 않도록 **순환 배열**을 씁니다. `front`와 `rear` 인덱스를 배열 길이로 나눈 나머지로 이동시켜, 배열 끝에 도달하면 0번으로 돌아가 앞의 빈 공간을 재사용합니다. 그래서 어떤 경우에도 원소 이동 없이 O(1)이 보장됩니다.

큐의 실무적 가치는 순서 보장보다 **생산 속도와 소비 속도의 차이를 흡수하는 완충 장치**라는 점입니다. 초당 1000건이 들어오는데 200건만 처리할 수 있어도, 큐에 쌓아 두고 순서대로 소화할 수 있습니다.

다만 소비가 계속 느리면 큐는 무한히 자랍니다. 그래서 실무에서는 **유계 큐**를 써서 가득 찼을 때 거절하거나 생산자를 대기시키는 백프레셔를 걸고, 큐 길이를 반드시 모니터링합니다.

Java에서는 단일 스레드면 `ArrayDeque`, 여러 스레드의 생산자·소비자 패턴이면 `LinkedBlockingQueue` 같은 `BlockingQueue`를 씁니다. 서버 재시작에도 작업이 살아남아야 한다면 인메모리 큐가 아니라 Kafka나 RabbitMQ 같은 메시지 브로커를 사용합니다.

### 답변 구조

* **정의**

    * 먼저 들어온 것이 먼저 나가는 FIFO 자료구조
    * `offer`(뒤로 넣기), `poll`(앞에서 꺼내기), `peek`(앞 확인)

* **내부 원리**

    * 순환 배열: `(index + 1) % capacity`로 인덱스를 돌려 재사용
    * 또는 연결 리스트의 head/tail 조작
    * 원소 이동이 전혀 없어 O(1) 보장

* **복잡도**

    * `O(1)`: `offer`, `poll`, `peek`, `size` (무계 배열 큐의 확장 순간만 O(n))
    * `O(n)`: `contains` (큐는 검색용이 아님)
    * 공간 `O(n)`, 단 **큐 길이 = 지연 시간**이라는 시스템 비용이 더 중요

* **장점**

    * 순서 보장, 모든 연산 O(1)
    * 생산자·소비자 분리, 순간 부하 평탄화, 응답 시간 단축

* **단점**

    * 중간 접근 불가, 우선순위 표현 불가
    * 무계 큐는 OOM 위험, 큐가 길어지면 지연이 곧 실패가 됨
    * 비동기 처리의 복잡도(중복·실패·모니터링) 증가

* **사용 기준**

    * 순서 보장이 필요하고, 생산·소비 속도 차를 흡수해야 할 때
    * 크기 제한과 가득 찼을 때의 정책을 반드시 함께 결정

* **대안과 비교**

    * 마지막 것 먼저 → `Stack`, 중요한 것 먼저 → `PriorityQueue`
    * 단일 스레드 → `ArrayDeque`, 멀티 스레드 → `BlockingQueue`
    * 유실 금지 → Kafka·RabbitMQ (인메모리 큐는 재시작 시 증발)

* **실무 적용 사례**

    * `ThreadPoolExecutor`의 작업 대기열, `@Async` 처리
    * HikariCP 커넥션 대기, 톰캣 `acceptCount`
    * 아웃박스 패턴, Redis List/Stream 기반 작업 큐

---

## 13. 예상 면접 질문

### 기본 질문

1. **큐란 무엇이고 스택과 어떻게 다른가요?**

    * 핵심 키워드: FIFO vs LIFO, 양 끝 vs 한쪽 끝, BFS vs DFS

2. **배열로 큐를 만들 때 순환 배열을 쓰는 이유는 무엇인가요?**

    * 핵심 키워드: 앞쪽 빈 공간 재사용, 원소 이동 회피, `% capacity`, O(1) 유지

3. **`offer`와 `add`, `poll`과 `remove`의 차이는 무엇인가요?**

    * 핵심 키워드: 특수값 반환 vs 예외, 흐름 제어, `null`/`false`

4. **Java에서 큐를 만들 때 어떤 구현체를 쓰나요?**

    * 핵심 키워드: `ArrayDeque`(단일 스레드), `BlockingQueue`(멀티 스레드), `LinkedList` 비권장

5. **큐를 실무에서 쓰는 대표적인 이유는 무엇인가요?**

    * 핵심 키워드: 생산·소비 속도 차 흡수, 비동기 처리, 응답 시간 단축, 서비스 분리

6. **BFS에 큐를 쓰는 이유는 무엇인가요?**

    * 핵심 키워드: FIFO, 가까운 노드부터 방문, 최단 경로(가중치 없는 그래프)

7. **유계 큐와 무계 큐의 차이는 무엇인가요?**

    * 핵심 키워드: 크기 제한, 백프레셔, OOM 위험, 거절 정책

### 꼬리 질문

1. **큐가 계속 쌓이면 어떤 문제가 생기고 어떻게 대응하나요?**

    * 핵심 키워드: 메모리 증가, 지연 폭증, 유계 큐, 거절 정책, 소비자 증설, lag 모니터링

2. **`Executors.newFixedThreadPool()`이 위험하다고 하는 이유는 무엇인가요?**

    * 핵심 키워드: 무계 `LinkedBlockingQueue`, `maximumPoolSize` 무력화, 큐 무한 증가, OOM

3. **`ThreadPoolExecutor`에서 큐와 `maximumPoolSize` 중 무엇이 먼저 쓰이나요?**

    * 핵심 키워드: core → 큐 → max → 거부 정책 순서, 무계 큐면 max 미사용

4. **인메모리 큐와 Kafka 중 어떤 기준으로 선택하나요?**

    * 핵심 키워드: 유실 허용 여부, 영속성, 서버 간 공유, 운영 복잡도

5. **메시지가 중복 처리되는 상황을 어떻게 막나요?**

    * 핵심 키워드: 멱등성, 메시지 ID 기록, 유니크 제약, at-least-once 전제

6. **Kafka에서 순서 보장은 어디까지 되나요?**

    * 핵심 키워드: 파티션 단위 보장, 키 기반 분배, 전역 순서와 병렬성의 트레이드오프

7. **큐에 넣은 작업이 실패하면 어떻게 처리하나요?**

    * 핵심 키워드: 재시도, 백오프, DLQ(Dead Letter Queue), 실패 이력 저장

8. **비동기 큐 처리에서 사용자에게 결과를 어떻게 알려주나요?**

    * 핵심 키워드: 작업 상태 테이블, 폴링, 웹소켓/SSE, 콜백, 상태 조회 API

9. **아웃박스 패턴은 어떤 문제를 해결하나요?**

    * 핵심 키워드: DB 커밋과 메시지 발송의 원자성, 이중 쓰기 문제, 별도 발행 프로세스

---

## 14. 추가 학습 방향

### 바로 이어서 공부

| 키워드                | 연결되는 이유                                |
| ------------------ | -------------------------------------- |
| **Deque**          | 큐와 스택을 하나로 합친 구조이며 `ArrayDeque`의 정체다   |
| **ArrayDeque**     | Java에서 큐를 만드는 실질적인 기본 선택지다             |
| **PriorityQueue**  | 순서가 아니라 우선순위로 꺼내는 변형 큐다                |
| **BFS**            | 큐의 FIFO 성질을 그대로 활용하는 대표 알고리즘이다         |
| **Stack**          | 정반대 규칙과 비교하면 큐의 성질이 선명해진다              |

### 실무 확장

| 키워드                     | 연결되는 이유                                    |
| ----------------------- | ------------------------------------------ |
| **BlockingQueue**       | 생산자·소비자 패턴과 백프레셔의 표준 도구다                   |
| **ThreadPoolExecutor**  | 큐 크기와 스레드 수의 상호작용을 이해해야 안전하게 설정할 수 있다      |
| **Spring `@Async`**     | 애플리케이션 레벨 비동기 처리의 큐 설정을 배운다                |
| **Redis List / Stream** | 간단한 분산 큐와 소비자 그룹·ACK 개념을 익힌다               |
| **Kafka 기초**            | 파티션, 오프셋, 소비자 그룹으로 큐를 수평 확장하는 방식을 배운다      |
| **아웃박스 패턴**             | DB 트랜잭션과 메시지 발행의 정합성 문제를 해결한다              |

### 심화 학습

| 키워드                      | 연결되는 이유                              |
| ------------------------ | ------------------------------------ |
| **백프레셔와 흐름 제어**          | 시스템이 과부하에서 무너지지 않게 만드는 설계 원리다        |
| **멱등성 설계**               | 중복 메시지가 전제인 분산 환경에서 필수 개념이다          |
| **DLQ와 재시도 전략**          | 실패한 작업을 잃지 않고 처리하는 운영 패턴이다           |
| **`ConcurrentLinkedQueue`** | CAS 기반 논블로킹 큐의 동작 원리를 배운다            |
| **Exactly-once 시맨틱**     | at-most / at-least / exactly-once 차이를 이해한다 |
| **큐 기반 시스템 용량 산정**       | 도착률·처리율·대기 시간의 관계(대기 행렬 이론)를 계산한다    |

---

## 15. 최종 체크리스트

* [ ] 개념을 한 문장으로 설명할 수 있다
* [ ] 등장 배경을 설명할 수 있다
* [ ] 내부 동작 과정을 설명할 수 있다
* [ ] 성능 특성을 설명할 수 있다
* [ ] 장점과 단점을 설명할 수 있다
* [ ] 사용할 상황과 사용하지 않을 상황을 구분할 수 있다
* [ ] 비슷한 기술과 비교할 수 있다
* [ ] Spring 백엔드 실무 사례를 설명할 수 있다
* [ ] 기본 면접 질문에 답할 수 있다
* [ ] 조건이 달라졌을 때 대안을 제시할 수 있다

---

## 16. 한 줄 결론

**들어온 순서대로 처리해야 하고 생산·소비 속도 차이를 흡수해야 한다면 큐를 쓰되, 반드시 크기를 제한하고 큐 길이를 모니터링한다.**
