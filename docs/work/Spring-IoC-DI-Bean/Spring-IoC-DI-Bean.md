# Spring IoC · DI · Bean

> **객체의 생성과 연결을 비즈니스 코드에서 떼어내 Container에 맡기는 것.
> 그리고 `@Component`가 실제 Bean이 되기까지 거치는 단계.**

`Spring Framework 6.1.13` (Spring Boot 3.3.x 계열) · Java 17

**계기** — 1주차 학습 주제. 개념 설명은 읽었지만 `@Component`가 실제로 Bean이 되기까지 무슨 일이
벌어지는지, BeanDefinition이 왜 중간에 끼어드는지가 납득되지 않아 파고들었다.

!!! note "면접용 일반론은 커리큘럼 노트에 있다"
    같은 주제를 6개 섹션 형식으로 정리한 [IoC · DI와 Bean](../../05-Spring/IoC-DI와-Bean/IoC-DI와-Bean.md)이 따로 있다.
    이 노트는 **1주차에 내가 실제로 헷갈렸던 것과 직접 돌려서 확인한 결과**를 남기는 쪽이다.

!!! success "이 노트의 출력은 전부 실측이다"
    아래 나오는 Bean 이름, 예외 메시지, `true`/`false` 판정은 모두
    Spring Framework 6.1.13을 클래스패스에 놓고 실제로 실행해 얻은 것이다.
    검증 방법은 아래 **4. 실측으로 확인한 것**에 있다.

---

## 0. 이번 주 한눈에 보기

### 이번 주 핵심 질문

* Spring은 왜 객체의 생성과 의존관계 관리를 개발자 코드 대신 Container가 담당하는가?
* IoC와 DI는 어떤 관계이며, DI를 사용하면 객체 설계가 어떻게 달라지는가?
* `@Component`, `@Bean`으로 등록한 객체가 실제 Spring Bean이 되기까지 어떤 과정을 거치는가?
* `BeanFactory`, `ApplicationContext`, `BeanDefinition`은 각각 어떤 역할을 담당하는가?

### 핵심 흐름

```text
Spring Boot 실행
    ↓
@SpringBootApplication
    ↓
Component Scan / 설정 정보 처리
    ↓
@Component / @Service / @Bean 등 탐색
    ↓
BeanDefinition 등록
    ↓
BeanFactory가 BeanDefinition을 이용해 객체 생성
    ↓
Dependency Injection
    ↓
초기화
    ↓
ApplicationContext가 Bean 관리
    ↓
애플리케이션에서 Bean 사용
```

조금 더 개념적으로 보면 다음과 같다.

```text
IoC
│
│ 객체 생성/관리의 제어권을 Spring이 가짐
↓
DI
│
│ 필요한 객체를 외부에서 전달
↓
Bean
│
│ Spring Container가 관리하는 객체
↓
BeanDefinition
│
│ Bean을 어떻게 만들지에 대한 메타데이터
↓
BeanFactory
│
│ Bean 생성/조회/관리의 핵심 기능
↓
ApplicationContext
│
└─ BeanFactory 기능 + Spring 애플리케이션 기능
```

---

## 1. 핵심 개념

### 1-1. IoC — Inversion of Control

#### 한 줄 정의

**객체의 생성, 의존관계 설정, 생명주기 관리 등의 제어권을 개발자 코드가 직접 가지지 않고
Framework/Container가 담당하도록 역전시키는 개념이다.**

#### 왜 필요한가?

객체가 자신이 사용할 객체까지 직접 생성하면 구체 구현체와 강하게 결합된다.

```java
public class OrderService {

    private final OrderRepository repository
        = new JdbcOrderRepository();
}
```

이 경우 `OrderService`가 다음 두 가지를 모두 담당한다.

```text
OrderService
├─ 주문 비즈니스 로직
└─ 어떤 OrderRepository를 사용할지 결정
```

`JdbcOrderRepository`를 `JpaOrderRepository`로 변경하려면 `OrderService` 코드까지 수정해야 한다.

객체 사용과 객체 생성/구성을 분리하면 비즈니스 객체는 자신의 역할에 집중할 수 있다.

#### 어떻게 동작하는가?

Spring을 사용하는 경우 개념적으로 다음과 같다.

```text
개발자가 클래스 작성
    ↓
Spring에 Bean 정보 제공
    ↓
Spring Container가 객체 생성
    ↓
필요한 의존 객체 탐색
    ↓
의존성 연결
    ↓
Bean 생명주기 관리
```

즉 제어권이

```text
개발자 코드
    ↓
Spring Container
```

로 이동한다.

#### 핵심 코드

```java
@Service
public class OrderService {

    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

`OrderService`는 `OrderRepository`를 직접 생성하지 않는다.

#### 주의할 점

IoC를 단순히

> 설정 같은 자잘한 작업을 Spring이 대신한다.

라고 이해하면 부족하다.

핵심은 **객체를 누가 생성하고 연결하고 관리할 것인가에 대한 제어권**이다.

---

### 1-2. DI — Dependency Injection

#### 한 줄 정의

**객체가 필요한 의존 객체를 직접 생성하지 않고 외부에서 전달받는 방식이다.**

#### 왜 필요한가?

다음 코드는 구체 구현체에 직접 의존한다.

```java
public class OrderService {

    private final OrderRepository repository
        = new JdbcOrderRepository();
}
```

이 구조에서는 구현체를 바꾸기 어렵고 테스트에서도 실제 구현체를 사용해야 한다.

DI를 사용하면:

```java
public class OrderService {

    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

외부에서 원하는 구현체를 넣을 수 있다.

```text
OrderRepository
├─ JdbcOrderRepository
├─ JpaOrderRepository
└─ MockOrderRepository
```

따라서 다음 효과가 생긴다.

```text
구체 구현체에 대한 결합 감소
        ↓
다형성 활용
        ↓
구현체 교체 용이
        ↓
테스트 용이
```

#### 어떻게 동작하는가?

Spring에서는:

```text
OrderService Bean 생성 필요
        ↓
생성자에 OrderRepository 필요
        ↓
Container에서 OrderRepository 타입 Bean 탐색
        ↓
적절한 Bean 선택
        ↓
생성자 호출 시 전달
```

#### 주의할 점

DI를 사용한다고 해서 `OrderService`가 `OrderRepository`에 **의존하지 않는 것**은 아니다.

```text
잘못된 이해
OrderService가 다른 클래스에 의존하지 않는다.

실제
OrderService가 구체 구현체가 아니라
OrderRepository라는 추상화에 의존한다.
```

또한 DI 자체는 Spring 전용 개념이 아니다.

```java
OrderRepository repository = new JdbcOrderRepository();
OrderService service = new OrderService(repository);
```

Spring 없이 이렇게 작성해도 DI다.

Spring은 **Container가 이러한 작업을 자동으로 수행해주는 Framework**다.

---

### 1-3. IoC와 DI의 관계

**IoC가 더 큰 개념이고, DI는 IoC를 구현하기 위한 대표적인 방법이다.**

```text
IoC
└─ 객체 관리의 제어권을 외부로 넘김
       ↓
      DI
└─ 의존 객체를 외부에서 전달
```

DI를 통해 객체가 자기 의존성을 직접 결정하지 않게 만들고, Spring Container가 의존관계를 구성한다.

---

### 1-4. Spring Bean

#### 한 줄 정의

**Spring Container가 생성하고 관리하는 객체다.**

#### 왜 필요한가?

Spring이 객체를 관리해야 다음과 같은 Framework 기능을 적용할 수 있다.

```text
Bean 생성
↓
의존관계 설정
↓
Scope 관리
↓
생명주기 관리
↓
필요한 곳에 주입
```

개발자가 단순히 `new`로 생성한 객체는 자동으로 Spring이 관리하는 Bean이 되는 것이 아니다.

#### 어떻게 동작하는가?

대표적인 Bean 등록 방식은 이번 주에 두 가지를 학습했다.

```text
@Component 계열
→ Component Scan
→ 자동 Bean 등록

@Bean
→ Configuration 정보 처리
→ 메서드 반환 객체를 Bean 등록
```

---

### 1-5. `@Component`

#### 한 줄 정의

**클래스 자체를 Component Scan 대상으로 만들어 자동으로 Bean 등록하도록 하는 애노테이션이다.**

#### 왜 필요한가?

내가 직접 관리하는 Service, Repository 등의 클래스를 일일이 설정 클래스에서 등록하면 설정 코드가 많아진다.

```java
@Bean
public OrderService orderService() {
    return new OrderService();
}
```

대신:

```java
@Service
public class OrderService {
}
```

처럼 선언하고 자동 탐색하게 할 수 있다.

#### 어떻게 동작하는가?

```text
@Component / @Service 등
        ↓
Component Scan
        ↓
클래스 발견
        ↓
BeanDefinition 생성
        ↓
BeanFactory 등록
        ↓
Bean 생성
```

#### 핵심 코드

```java
@Component
public class PaymentClient {
}
```

`@Service`, `@Repository`, `@Controller` 등도 Component Scan 대상이다.
이들은 각각 `@Component`를 메타 애노테이션으로 달고 있다.

```text
@Component
├─ @Service
├─ @Repository
└─ @Controller
```

#### 기본 Bean 이름 (실측)

클래스 이름의 첫 글자를 소문자로 바꾼 이름이 기본이다.

```text
@Service     OrderService          →  orderService
@Repository  JdbcOrderRepository   →  jdbcOrderRepository
@Component("customName") NamedBean →  customName
```

#### 주의할 점

Component Scan 범위 밖에 있는 클래스에는 `@Component`가 붙어 있어도 자동 등록되지 않을 수 있다.

Spring Boot에서는 일반적으로 `@SpringBootApplication`이 위치한 패키지를 기준으로 하위 패키지를 스캔한다.

---

### 1-6. `@Bean`

#### 한 줄 정의

**메서드가 반환한 객체를 Spring Bean으로 등록하는 방식이다.**

#### 왜 필요한가?

외부 라이브러리 클래스는 소스 코드에 직접 다음과 같이 붙일 수 없다.

```java
@Component
public class ObjectMapper {
}
```

따라서 내가 관리하는 설정 코드에서 객체를 생성한 뒤 Bean으로 등록할 수 있다.

또한 객체 생성 과정에 세부 설정이 필요한 경우에도 유용하다.

#### 어떻게 동작하는가?

```text
@Bean 메서드 발견
    ↓
메서드 실행에 필요한 정보 등록
    ↓
반환 객체 생성
    ↓
Spring Bean으로 관리
```

#### 핵심 코드

```java
@Configuration
public class AppConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
```

Bean 이름은 기본적으로 **메서드 이름**이다 (`objectMapper`).

#### 주의할 점

`@Bean`은 **외부 라이브러리 전용이 아니다.**

직접 만든 클래스도 등록할 수 있다.

```java
@Bean
public OrderService orderService() {
    return new OrderService();
}
```

차이의 핵심은:

```text
@Component
→ 클래스 자체를 자동 탐색

@Bean
→ 메서드가 반환하는 객체를 명시적으로 등록
```

---

### 1-7. `@Configuration`

#### 한 줄 정의

**해당 클래스가 Spring Bean 설정을 담당하는 Configuration 클래스임을 나타낸다.**

#### 왜 필요한가?

`@Bean`을 이용한 객체 등록과 Bean 간 구성 정보를 한 곳에서 관리하기 위해 필요하다.

#### 어떻게 동작하는가?

```java
@Configuration
public class AppConfig {

    @Bean
    public OrderRepository orderRepository() {
        return new OrderRepository();
    }

    @Bean
    public OrderService orderService(OrderRepository repository) {
        return new OrderService(repository);
    }
}
```

```text
@Configuration 처리
       ↓
@Bean 정보 확인
       ↓
BeanDefinition 등록
       ↓
필요한 Bean 생성
       ↓
의존관계 연결
```

#### 주의할 점

이번 주 가장 헷갈렸던 부분 중 하나다.

```text
@Bean
≠
@Configuration
```

역할이 다르다.

```text
@Bean
→ 객체 하나를 Bean으로 등록하는 정보

@Configuration
→ Bean 구성을 담당하는 설정 클래스
```

#### `proxyBeanMethods` — "특별하게 처리"의 정체 (실측)

처음에는 "Spring이 설정 클래스를 특별하게 처리할 수 있다"는 정도로만 알고 넘어갔는데,
실제로 무엇을 하는지 확인해 봤다. **Spring이 설정 클래스를 CGLIB으로 상속한 프록시로 바꿔치기한다.**

```java
@Configuration                       // 기본값 proxyBeanMethods = true
public class BeanConfig {
    @Bean public Plain plainOne() { return new Plain(); }
    @Bean public Plain user() { return plainOne(); }   // Bean 메서드 직접 호출
}
```

```text
기본(true)  설정 클래스 실제 타입   =>  com.example.app.BeanConfig$$SpringCGLIB$$0
기본(true)  user() == plainOne()   =>  true

false      설정 클래스 실제 타입   =>  com.example.app.LiteConfig
false      user() == plainOne()   =>  false
```

`plainOne()`을 코드에서 직접 호출했는데도 새 객체가 생기지 않고 Container의 Bean이 돌아온다.
프록시가 그 호출을 가로채 Container 조회로 바꾸기 때문이다.

`proxyBeanMethods = false`로 두면 프록시를 만들지 않아 **평범한 메서드 호출**이 되고,
`user()`는 `plainOne()`이 만든 새 인스턴스를 들고 있게 된다. Bean은 두 개가 되고 서로 다른 객체다.

---

### 1-8. Component Scan

#### 한 줄 정의

**지정된 패키지 범위에서 `@Component` 계열 클래스를 탐색하여 Bean 등록 대상으로 만드는 과정이다.**

#### 왜 필요한가?

모든 애플리케이션 클래스를 개발자가 직접 Bean으로 등록해야 한다면 설정 코드가 매우 많아진다.

Component Scan을 사용하면 관례에 따라 클래스를 배치하고 애노테이션만 붙여도 자동으로 등록할 수 있다.

#### 어떻게 동작하는가?

Spring Boot 기준:

```text
@SpringBootApplication
        ↓
@ComponentScan 기능
        ↓
메인 클래스 패키지 기준 탐색
        ↓
@Component 계열 발견
        ↓
BeanDefinition 생성
```

#### 주의할 점

`@SpringBootApplication`과 `@ComponentScan`을 완전히 별개의 실행 과정이라고 생각하지 않는다.

`@SpringBootApplication`에는 Component Scan 역할이 포함되어 있다.

---

### 1-9. BeanDefinition

#### 한 줄 정의

**Spring이 Bean을 생성하고 관리하는 데 필요한 메타데이터를 표현하는 Bean의 명세서다.**

#### 왜 필요한가?

Spring에는 Bean 정보를 제공하는 방식이 여러 가지다.

```text
@Component
@Bean
XML
...
```

각 방식의 표현은 완전히 다르다.

BeanFactory가 모든 설정 형식을 각각 이해하게 만들면 Container가 설정 방식에 강하게 결합된다.

그래서 중간 표현을 사용한다.

```text
@Component ─┐
@Bean ──────┼──→ BeanDefinition → BeanFactory
XML ────────┘
```

Container는 원래 설정 정보가 어디에서 왔는지 몰라도 `BeanDefinition`만 보고 Bean을 관리할 수 있다.

#### 어떻게 동작하는가?

```text
Spring 설정 정보
        ↓
설정 방식에 맞는 Parser/Scanner 처리
        ↓
BeanDefinition 생성
        ↓
BeanDefinition Registry 등록
        ↓
BeanFactory가 정보 사용
        ↓
실제 Bean 생성
```

#### 담기는 대표 정보

```text
Bean 클래스/타입 정보
Scope
Lazy 여부
생성 방식
초기화 정보
Destroy 정보
의존성 관련 메타데이터
```

#### 주의할 점

BeanDefinition을 처음에는

> Bean 타입들이 서로 달라서 필요한 것

으로 생각했지만 핵심은 아니다.

정확한 이유는:

> **여러 Bean 설정 방식을 Spring 내부에서 하나의 공통 메타데이터 형태로 추상화하기 위해서다.**

또한 Bean이 한 번 만들어졌다고 BeanDefinition이 바로 없어지는 것도 아니다. **실제로 확인했다.**

```text
Bean을 다 만든 뒤 ctx.getBeanDefinition("orderService")

생성 후 getBeanDefinition("orderService")  =>  com.example.app.OrderService
getScope() 원본 값                         =>  'singleton'
isSingleton()                              =>  true
BeanDefinition 구현 클래스                 =>  ScannedGenericBeanDefinition
```

Component Scan으로 등록된 것이라 구현체가 `ScannedGenericBeanDefinition`이다.
등록 경로에 따라 구현 클래스가 달라진다는 것도 여기서 눈으로 확인된다.

---

### 1-10. BeanFactory

#### 한 줄 정의

**Spring의 Bean 생성, 조회, 의존관계 관리 등의 핵심 기능을 정의하는 기본 IoC Container 인터페이스다.**

#### 왜 필요한가?

Spring이 객체 관리를 담당하려면 Bean을 찾고 만들고 의존관계를 구성하는 중심 역할이 필요하다.

#### 어떻게 동작하는가?

개념적으로:

```text
BeanDefinition
    ↓
BeanFactory
    ↓
Bean 생성
    ↓
의존성 주입
    ↓
Bean 관리
```

#### 주의할 점

BeanFactory를 단순히:

> Bean을 만드는 클래스

라고만 이해하면 부족하다.

**클래스가 아니라 인터페이스다.** 리플렉션으로 확인하면 `BeanFactory.class.isInterface()`가 `true`다.
정확하게는 **Bean 생성·조회·관리의 핵심 계약을 제공하는 IoC Container 인터페이스**다.

---

### 1-11. ApplicationContext

#### 한 줄 정의

**BeanFactory의 IoC 기능을 기반으로 실제 Spring 애플리케이션에 필요한 다양한 기능을
추가로 제공하는 Container다.**

#### 왜 필요한가?

실제 Spring 애플리케이션에는 단순 객체 생성만 필요한 것이 아니다.

예를 들어:

```text
Bean 관리
Event
Resource Loading
Environment / Property
Message / 국제화
...
```

같은 기능이 함께 필요하다.

그래서 일반적인 Spring 애플리케이션에서는 BeanFactory를 직접 사용하기보다 `ApplicationContext`를 사용한다.

#### 어떤 관계인가 (실측)

"BeanFactory 기능을 **포함**한다"고 적어 뒀는데, 정확히는 **인터페이스 상속**이다.
`ApplicationContext`가 직접 상속한 인터페이스를 뽑아 보면 이렇다.

```text
ApplicationContext.class.getInterfaces()

[EnvironmentCapable, ListableBeanFactory, HierarchicalBeanFactory,
 MessageSource, ApplicationEventPublisher, ResourcePatternResolver]
```

`ListableBeanFactory`와 `HierarchicalBeanFactory`가 각각 `BeanFactory`를 상속하므로
`ApplicationContext`는 `BeanFactory`의 하위 타입이다. 실제로 `ctx instanceof BeanFactory`가 `true`다.

나머지 인터페이스가 그대로 "부가 기능"의 목록이 된다.

```text
ListableBeanFactory / HierarchicalBeanFactory  → Bean 조회·계층 (IoC 핵심)
EnvironmentCapable                             → Environment / Property
MessageSource                                  → 메시지·국제화
ApplicationEventPublisher                      → 이벤트
ResourcePatternResolver                        → 리소스 로딩
```

#### 핵심 코드

```java
ApplicationContext context =
    new AnnotationConfigApplicationContext(AppConfig.class);

OrderService service =
    context.getBean(OrderService.class);
```

---

### 1-12. `getBean()`

#### 한 줄 정의

**Spring Container에 등록된 Bean을 직접 조회하는 API다.**

#### 어떻게 동작하는가?

이름 기준 조회:

```java
context.getBean("orderService");
```

타입 기준 조회:

```java
context.getBean(OrderService.class);
```

이름 + 타입:

```java
context.getBean("orderService", OrderService.class);
```

#### 주의할 점

```java
context.getBean("orderService");
```

는 **클래스 이름 조회가 아니라 Bean 이름 조회**다.

또한 타입으로 조회할 때 동일 타입의 Bean이 여러 개 존재하면 하나를 결정할 수 없어 예외가 발생한다.
실제 예외와 메시지는 이렇다.

```text
org.springframework.beans.factory.NoUniqueBeanDefinitionException:
No qualifying bean of type 'com.example.app.PaymentClient' available:
expected single matching bean but found 2: kakaoPaymentClient,naverPaymentClient
```

메시지가 **후보 Bean 이름을 그대로 나열해 준다.** 실무에서 이 예외를 만나면
어떤 구현체들이 부딪혔는지 메시지만 보고 바로 알 수 있다.

---

### 1-13. 생성자 주입

#### 한 줄 정의

**객체 생성 시점에 필요한 의존 객체를 생성자 인자로 전달받는 DI 방식이다.**

#### 왜 필요한가?

핵심 이유는 세 가지로 정리할 수 있다.

```text
필수 의존성 보장
+
불변성
+
테스트 용이성
```

#### 어떻게 동작하는가?

```java
@Service
public class OrderService {

    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

`OrderService`를 정상적으로 생성하려면 `OrderRepository`가 필요하다.

따라서 객체 생성 시점부터 필요한 의존관계를 갖게 된다.

`final`을 사용할 수 있어 생성 이후 참조 변경도 방지할 수 있다.

테스트에서는 Spring 없이 직접 구현체나 Mock을 넣을 수 있다.

```java
OrderRepository mockRepository = mock(OrderRepository.class);

OrderService service =
    new OrderService(mockRepository);
```

#### `@Autowired` 생략

생성자가 하나만 있다면 Spring이 사용할 생성자를 명확하게 판단할 수 있기 때문에 `@Autowired`를 생략할 수 있다.
위 코드에 `@Autowired`가 없는데도 `JdbcOrderRepository`가 주입되는 것을 실제로 확인했다.

!!! danger "생성자가 둘 이상이면 예외가 아니라 '조용히' 넘어간다 (실측)"
    생성자를 두 개 두고 `@Autowired`를 붙이지 않으면 **에러가 나지 않는다.**
    Spring이 **기본 생성자를 골라 버리고 주입은 그냥 일어나지 않는다.**

    ```java
    @Component
    public static class TwoCtors {
        public final PaymentClient c;
        public TwoCtors() { this.c = null; }              // ← 이쪽이 선택된다
        public TwoCtors(PaymentClient c) { this.c = c; }
    }
    ```

    ```text
    생성자 2개 + @Autowired 없음  =>  기본 생성자 선택됨 (주입 안 됨)
    ```

    애플리케이션은 정상 기동하고, 나중에 그 필드를 쓰는 순간 `NullPointerException`으로 터진다.
    **"생성자 1개면 생략 가능"을 뒤집으면 "2개부터는 반드시 `@Autowired`로 지목"** 이다.
    기동 시점에 안 잡히는 종류의 실수라 특히 위험하다.

#### 주의할 점

생성자 주입의 장점은 **메모리 절약이 아니다.**

Bean이 생성되어 Container에서 관리되고 있다면 생성자/Setter/필드 주입 방식 때문에
사용하지 않을 때 자동으로 메모리에서 사라지는 구조가 아니다.

---

### 1-14. 동일 타입 Bean이 여러 개 존재하는 경우

**주입하려는 타입에 후보 Bean이 여러 개 있으면 Spring이 어느 Bean을 사용할지 결정할 기준이 필요하다.**

예:

```java
public interface PaymentClient {
}
```

```java
@Component
public class KakaoPaymentClient implements PaymentClient {
}
```

```java
@Component
public class NaverPaymentClient implements PaymentClient {
}
```

그리고:

```java
public PaymentService(PaymentClient paymentClient) {
    this.paymentClient = paymentClient;
}
```

후보가 두 개다.

```text
PaymentClient
├─ kakaoPaymentClient
└─ naverPaymentClient
```

Spring이 하나를 결정할 수 없으면 `NoUniqueBeanDefinitionException`이 발생한다.

#### 해결 방법

기본 Bean 지정:

```java
@Primary
@Component
public class KakaoPaymentClient implements PaymentClient {
}
```

특정 Bean 지정:

```java
public PaymentService(
    @Qualifier("naverPaymentClient")
    PaymentClient paymentClient
) {
    this.paymentClient = paymentClient;
}
```

정리:

```text
@Primary
→ 기본 후보

@Qualifier
→ 특정 후보 명시
```

#### 둘을 같이 쓰면 누가 이기는가 (실측)

`Kakao`에 `@Primary`를 붙여 두고, 주입 지점에서 `@Qualifier("naver")`로 다른 쪽을 지목해 봤다.

```text
@Primary만 있을 때 주입된 것             =>  Kakao
@Primary + @Qualifier("naver") 주입된 것 =>  Naver
타입 조회 getBean(PaymentClient.class)   =>  Kakao
```

**`@Qualifier`가 `@Primary`를 이긴다.** 이해하기 쉬운 규칙이다.

```text
@Primary   → "따로 말 안 하면 이걸 써라"  (기본값)
@Qualifier → "여기서는 이걸 써라"          (지역에서의 명시적 지정)
```

그리고 `@Primary`가 있으면 `getBean(타입)` 같은 **타입 조회도 예외 없이 통과한다.**
후보가 둘이어도 대표가 정해져 있기 때문이다.

---

### 1-15. Spring Singleton Bean

#### 한 줄 정의

**하나의 Spring Container가 특정 BeanDefinition에 대해 기본적으로 하나의 Bean 인스턴스를
생성해 공유하는 Scope다.**

#### 왜 필요한가?

Service나 Repository처럼 상태를 가질 필요가 없는 객체를 요청마다 새로 만드는 것은
불필요한 객체 생성 비용을 발생시킬 수 있다.

Spring은 기본적으로 하나의 인스턴스를 생성해 재사용한다.

```java
OrderService a = context.getBean(OrderService.class);
OrderService b = context.getBean(OrderService.class);

a == b; // true
```

#### "ApplicationContext 단위"라는 말의 확인 (실측)

같은 설정으로 Context를 **두 개** 띄우고 비교하면 서로 다른 객체다.

```text
같은 Context에서 a == b            =>  true
다른 Context끼리 같은 인스턴스인가  =>  false
```

Spring Singleton이 JVM 전체에서 하나라는 뜻이 아니라
**ApplicationContext 하나당 하나**라는 것이 이 두 줄로 확정된다.
(일반적인 애플리케이션은 Context가 하나라서 결과적으로 하나처럼 보일 뿐이다.)

#### 일반 Singleton Pattern과 차이

일반 Singleton:

```java
public class Singleton {

    private static final Singleton INSTANCE = new Singleton();

    private Singleton() {}

    public static Singleton getInstance() {
        return INSTANCE;
    }
}
```

클래스 자체가 Singleton을 구현한다.

Spring Singleton:

```java
@Service
public class OrderService {
}
```

클래스는 Singleton 구현을 몰라도 된다.

```text
일반 Singleton
→ 클래스가 하나의 객체를 보장

Spring Singleton
→ Spring Container가 하나의 Bean을 관리
```

---

### 1-16. Singleton Bean과 Stateless

#### 한 줄 정의

**여러 Thread가 하나의 Singleton Bean을 공유하므로 요청별 변경 상태를 Bean 필드에
저장하지 않는 것이 기본적인 설계 원칙이다.**

#### 왜 필요한가?

Spring Web 애플리케이션에서는:

```text
Thread A ─┐
Thread B ─┼──→ OrderService Bean 하나
Thread C ─┘
```

여러 요청이 같은 인스턴스를 동시에 사용할 수 있다.

따라서:

```java
@Service
public class OrderService {

    private Long currentUserId;
}
```

처럼 요청별 값을 공유 필드에 보관하면 다른 요청이 값을 덮어쓸 수 있다.

#### 안전한 형태

```java
public Order findOrder(Long userId) {
    String message = "user=" + userId;

    // ...
}
```

`userId`, `message`처럼 메서드 파라미터와 지역 변수로 처리한다.

#### Mutable / Immutable

판단 기준은 단순히:

```text
자주 바뀌는가?
```

가 아니다.

더 정확하게는:

```text
여러 Thread가 공유하는 Mutable State인가?
```

가 중요하다.

#### `AtomicInteger`

```java
private final AtomicInteger count = new AtomicInteger();

public int increase() {
    return count.incrementAndGet();
}
```

`AtomicInteger.incrementAndGet()`은 별도의 `Lock`을 직접 작성하지 않아도 원자적 증가 연산을 제공한다.

따라서 해당 단일 연산 자체는 Thread-safe하다.

하지만:

```text
Thread-safe
≠
Stateless
≠
무조건 좋은 설계
```

다.

전역 요청 카운터처럼 의도적으로 프로세스 내부에서 공유해야 하는 상태일 수 있지만,
사용자 잔액·주문 상태처럼 중요한 비즈니스 데이터를 Singleton Bean 메모리에 보관하는 것은 적절하지 않다.

멀티 서버가 되면:

```text
Server A → count = 10
Server B → count = 14
Server C → count = 8
```

각 JVM마다 값이 분리되기 때문이다.

---

## 2. 개념 간 연결

이번 주 개념은 독립적인 용어들이 아니다.

전체 구조를 하나로 연결하면 다음과 같다.

```text
IoC
│
│ 객체 관리의 제어권을 Framework로 이동
↓
DI
│
│ 객체가 직접 의존 객체를 생성하지 않음
↓
Bean
│
│ Spring이 관리할 객체
↓
@Component / @Bean
│
│ Spring에 Bean 등록 정보 제공
↓
Component Scan / Configuration 처리
│
↓
BeanDefinition
│
│ 서로 다른 설정 방식을 공통 메타데이터로 변환
↓
BeanFactory
│
│ BeanDefinition을 이용해 Bean 생성/관리
↓
Dependency Injection
│
↓
Singleton Bean 등 Scope에 맞게 관리
│
↓
ApplicationContext
│
└─ 실제 애플리케이션에서 Bean과 Spring 기능 제공
```

왜 이 개념들이 같이 등장하는지가 중요하다.

Spring의 핵심 문제는:

> 애플리케이션에서 사용하는 객체들을 누가 생성하고, 어떻게 연결하고, 어떻게 관리할 것인가?

이다.

Spring은 이를 다음 방식으로 해결한다.

```text
개발자는
"어떤 객체가 필요한가"
"어떤 객체끼리 의존하는가"
를 표현

Spring은
"언제 만들 것인가"
"어떤 구현체를 넣을 것인가"
"얼마나 유지할 것인가"
를 관리
```

그 결과 개발자는 객체 생성 코드보다 비즈니스 로직과 객체 간 역할에 집중할 수 있다.

---

## 3. 내부 동작 Deep Dive

### 3-1. `@Component`가 실제 Bean이 되기까지

```text
Spring Boot Application 실행
        ↓
@SpringBootApplication 처리
        ↓
Component Scan
        ↓
@Component / @Service / @Repository 등 탐색
        ↓
BeanDefinition 생성
        ↓
BeanDefinition Registry 등록
        ↓
BeanFactory가 BeanDefinition 확인
        ↓
객체 생성
        ↓
생성자 의존성 탐색
        ↓
해당 타입 Bean 주입
        ↓
초기화
        ↓
Singleton Bean 관리
```

#### 왜 이런 과정이 필요한가?

`@Component` 자체가 Bean 객체는 아니다.

`@Component`는:

> 이 클래스를 Spring 관리 대상으로 고려하라.

는 메타정보다.

Spring은 먼저 이를 `BeanDefinition`이라는 내부 표현으로 바꾸고, BeanFactory가 이후 실제 객체를 만든다.

따라서:

```text
@Component
→ Bean
```

이 바로 일어나는 것이 아니라:

```text
@Component
→ BeanDefinition
→ BeanFactory
→ Bean
```

이라는 중간 단계가 존재한다.

`ScannedGenericBeanDefinition`이라는 실제 구현 클래스 이름이 이 단계를 그대로 보여준다.
"스캔해서 만들어진 BeanDefinition"이라는 뜻이다.

---

### 3-2. 생성자 DI 내부 흐름

```text
OrderService 생성 필요
        ↓
생성자 분석
        ↓
OrderRepository 파라미터 발견
        ↓
Container에서 OrderRepository 타입 검색
        ↓
후보 1개
        ↓
해당 Bean 준비
        ↓
new OrderService(orderRepository)
        ↓
OrderService Bean 등록
```

후보가 여러 개라면:

```text
OrderRepository 타입 검색
        ↓
후보 2개 이상
        ↓
@Qualifier 확인      ← 있으면 여기서 결정 (가장 우선)
        ↓
@Primary 확인        ← 대표가 있으면 여기서 결정
        ↓
그래도 결정 불가능
        ↓
NoUniqueBeanDefinitionException
```

DI에서 Spring이 단순히 아무 객체나 넣는 것이 아니라
**타입과 Bean 메타정보를 기준으로 적절한 후보를 결정하는 과정**이 존재한다.

---

### 3-3. BeanDefinition을 사용하는 이유

```text
@Component
       ┐
@Bean  ├──→ 서로 다른 설정 표현
XML    ┘
        ↓
BeanDefinition
        ↓
BeanFactory
        ↓
Bean
```

이 중간 계층 덕분에 BeanFactory는 설정 방식이 추가되더라도 핵심 Bean 생성 로직을 크게 변경할 필요가 없다.

즉 `BeanDefinition`은 단순 명세서 이상의 의미가 있다.

**Spring의 외부 설정 표현과 내부 객체 생성 엔진 사이를 분리하는 추상화 계층이다.**

---

### 3-4. Singleton Bean과 Multi Thread

```text
HTTP Request A → Thread A ─┐
HTTP Request B → Thread B ─┼→ Singleton Service
HTTP Request C → Thread C ─┘
```

Service 내부가 다음과 같다면:

```java
private Long currentUserId;
```

모든 요청이 동일 필드를 공유한다.

```text
Thread A
currentUserId = 10

        ↓ Context Switch

Thread B
currentUserId = 20

        ↓

Thread A가 다시 읽음
→ 20
```

따라서 일반적인 Service Bean은 요청 데이터를 필드에 저장하지 않고 메서드 인자와 지역 변수로 처리한다.

---

## 4. 실측으로 확인한 것

### 검증 환경

Spring Boot 프로젝트를 만들지 않고 **Spring Framework jar만 클래스패스에 놓고** 확인했다.
IoC/DI/Bean은 `spring-context` 수준에서 전부 재현되기 때문에 이 정도면 충분하다.

```text
Spring Framework 6.1.13   (Spring Boot 3.3.x가 쓰는 버전대)
Java 17

spring-core · spring-beans · spring-context · spring-aop · spring-expression · spring-jcl
```

```java
var ctx = new AnnotationConfigApplicationContext(ScanConfig.class);
```

`@SpringBootApplication` 대신 `@ComponentScan`을 직접 단 설정 클래스를 썼다.
Spring Boot가 하는 일이 결국 이 스캔이라 결과는 같다.

---

### 실측 1. Component Scan · 기본 Bean 이름 · `@Autowired` 생략

#### 확인하려던 것

`@Service` / `@Repository`를 붙인 클래스가 Bean이 되는가, 기본 Bean 이름은 무엇인가,
`@Autowired` 없이 생성자 주입이 되는가.

#### 코드

```java
@Repository
public class JdbcOrderRepository implements OrderRepository {}

@Service
public class OrderService {
    public final OrderRepository repository;
    // @Autowired 없음
    public OrderService(OrderRepository repository) { this.repository = repository; }
}

@Component("customName")
public class NamedBean {}
```

#### 결과

```text
생성자에 @Autowired 없이 주입됐나        =>  JdbcOrderRepository
@Service OrderService 기본 이름          =>  orderService
@Repository JdbcOrderRepository 기본 이름 =>  jdbcOrderRepository
@Component("customName") 이름            =>  customName
```

#### 해석

- 생성자가 하나면 `@Autowired` 없이 주입된다 — 예상대로다.
- 기본 이름은 **클래스 이름의 첫 글자만 소문자**다. `JdbcOrderRepository` → `jdbcOrderRepository`처럼
  뒤쪽 대문자는 그대로 남는다.
- `@Component("...")`로 준 이름이 그대로 Bean 이름이 된다.

---

### 실측 2. Singleton — "ApplicationContext 단위"의 의미

#### 확인하려던 것

`a == b`가 `true`인 것과, 그 "하나"의 범위가 어디까지인지.

#### 코드

```java
var ctx  = new AnnotationConfigApplicationContext(ScanConfig.class);
var ctx2 = new AnnotationConfigApplicationContext(ScanConfig.class);   // 같은 설정, 다른 Context

ctx.getBean(OrderService.class) == ctx.getBean(OrderService.class);
ctx.getBean(OrderService.class) == ctx2.getBean(OrderService.class);
```

#### 결과

```text
같은 Context에서 a == b             =>  true
다른 Context끼리 같은 인스턴스인가   =>  false
```

#### 해석

두 번째 줄이 이 실측의 요점이다. Singleton의 범위는 **JVM이 아니라 ApplicationContext**다.
"Spring Singleton은 JVM 전체에서 정확히 하나인가?"라는 질문에 이제 근거를 갖고 아니라고 답할 수 있다.

---

### 실측 3. BeanDefinition은 Bean 생성 후에도 남는가

#### 확인하려던 것

"Bean을 만들었으면 BeanDefinition은 역할이 끝난다"고 생각했던 것을 뒤집을 근거.

#### 코드

```java
ctx.getBean(OrderService.class);                        // Bean을 먼저 다 만든 뒤
BeanDefinition bd = ctx.getBeanDefinition("orderService");
```

#### 결과

```text
생성 후 getBeanDefinition("orderService")  =>  com.example.app.OrderService
getScope() 원본 값                         =>  'singleton'
isSingleton()                              =>  true
BeanDefinition 구현 클래스                 =>  ScannedGenericBeanDefinition
```

#### 해석

Bean이 만들어진 뒤에도 조회된다. Container는 Bean 인스턴스와 그 명세를 **둘 다** 들고 있다.
Scope, lazy, 생명주기 같은 정보는 Bean을 만든 뒤에도 계속 필요하기 때문이다.

---

### 실측 4. 동일 타입 Bean 2개 · `@Primary` · `@Qualifier`

#### 확인하려던 것

예외의 정확한 타입과 메시지, 그리고 `@Primary`와 `@Qualifier`가 같이 있을 때의 우선순위.

#### 결과

```text
[후보 2개, 기준 없음 — 타입으로 조회]
org.springframework.beans.factory.NoUniqueBeanDefinitionException:
No qualifying bean of type 'com.example.app.PaymentClient' available:
expected single matching bean but found 2: kakaoPaymentClient,naverPaymentClient

[Kakao에 @Primary를 붙인 뒤]
@Primary만 있을 때 주입된 것             =>  Kakao
@Primary + @Qualifier("naver") 주입된 것 =>  Naver
타입 조회 getBean(PaymentClient.class)   =>  Kakao
```

#### 해석

- 예외 메시지가 **충돌한 Bean 이름을 그대로 나열**해 준다.
- `@Qualifier`가 `@Primary`보다 우선한다.
- `@Primary`가 있으면 타입 조회(`getBean(타입)`)도 예외 없이 대표를 돌려준다.

---

### 실측 5. `@Configuration`의 `proxyBeanMethods`

#### 확인하려던 것

"Spring이 설정 클래스를 특별하게 처리한다"의 실체.

#### 코드

```java
@Configuration                       // 기본값 proxyBeanMethods = true
public class BeanConfig {
    @Bean public Plain plainOne() { return new Plain(); }
    @Bean public Plain user() { return plainOne(); }
}

@Configuration(proxyBeanMethods = false)
public class LiteConfig {
    @Bean public Plain plainOne() { return new Plain(); }
    @Bean public Plain user() { return plainOne(); }
}
```

#### 결과

```text
기본(true)  설정 클래스 실제 타입   =>  com.example.app.BeanConfig$$SpringCGLIB$$0
기본(true)  user() == plainOne()   =>  true

false      설정 클래스 실제 타입   =>  com.example.app.LiteConfig
false      user() == plainOne()   =>  false
```

#### 해석

클래스 이름에 `$$SpringCGLIB$$0`이 붙은 것이 결정적이다.
Container에 들어간 설정 클래스는 내가 쓴 그 클래스가 아니라 **CGLIB이 상속해 만든 프록시**다.
그래서 `plainOne()`을 코드에서 직접 호출해도 새 객체가 생기지 않고 Container 조회로 바뀐다.

`proxyBeanMethods = false`면 프록시가 없으니 그냥 평범한 자바 메서드 호출이고, 새 객체가 생긴다.
`@Bean` 메서드끼리 호출하지 않는 설정 클래스라면 프록시 생성 비용을 아낄 수 있다는 뜻이기도 하다.

---

### 실측 6. 생성자가 둘일 때

#### 확인하려던 것

"생성자 1개면 `@Autowired` 생략 가능"의 반대편. 2개면 어떻게 되는가.

#### 코드

```java
@Component
public static class TwoCtors {
    public final PaymentClient c;
    public TwoCtors() { this.c = null; }
    public TwoCtors(PaymentClient c) { this.c = c; }
}
```

#### 결과

```text
생성자 2개 + @Autowired 없음  =>  기본 생성자 선택됨 (주입 안 됨)
```

#### 해석

**예상과 달랐다.** 애매하니까 예외가 날 거라고 생각했는데, 예외는커녕 애플리케이션이 정상 기동한다.
Spring이 기본 생성자를 골라 버리고, 의존성은 조용히 `null`로 남는다.

이번 주 실측 중 가장 값진 결과다. 기동 시점에 안 걸리고 **런타임에 `NullPointerException`으로**
나타나는 종류의 실수라, 규칙을 "생성자 1개면 생략 가능"이 아니라
**"생성자가 2개 이상이면 반드시 `@Autowired`로 지목"** 으로 기억해야 한다.

---

## 5. 내가 헷갈렸던 부분 / 틀린 부분

### 착각 1. IoC는 Spring이 설정 같은 자잘한 일을 대신하는 것

**내가 생각했던 것** — IoC는 제어의 역전이고 설정 등 자잘한 컨트롤은 Framework에서 하는 것이다.

**실제로는** 핵심이 단순 설정 편의가 아니다.

```text
객체 생성
의존관계 설정
생명주기 관리
```

와 같은 **객체 제어권 자체가 Framework로 넘어가는 것**이다.

**왜 헷갈렸는가** — Spring이 실제로 많은 설정과 객체 관리를 자동으로 처리하기 때문에
"편의 기능"으로 보이기 쉽지만, IoC는 더 근본적인 객체 설계 원칙이다.

---

### 착각 2. DI를 하면 다른 클래스에 의존하지 않는다

**내가 생각했던 것** — 외부에서 주입하므로 한 클래스가 다른 클래스에 의존적이지 않다.

**실제로는** 의존성은 여전히 존재한다.

```text
OrderService
    ↓
OrderRepository
```

다만:

```text
JdbcOrderRepository라는 구체 구현체 의존
```

에서

```text
OrderRepository라는 추상화 의존
```

으로 바꾸는 것이 핵심이다.

---

### 착각 3. DI 때문에 Spring이 객체 생명주기를 관리한다

**내가 생각했던 것** — 외부에서 주입하기 때문에 Spring이 객체의 생명주기를 관리할 수 있다.

**실제로는** 인과관계가 반대다.

```text
Spring Container가 Bean을 관리
├─ Bean 생성
├─ 생명주기 관리
└─ DI 수행
```

DI와 생명주기 관리는 모두 Container가 Bean을 관리하기 때문에 가능한 기능이다.

---

### 착각 4. 생성자 주입은 메모리 측면에서 유리하다

**내가 생각했던 것** — 생성자가 호출될 때만 메모리 공간을 차지하므로 생성자 주입이 좋다.

**실제로는** 생성자 주입을 권장하는 주요 이유와 메모리는 관계가 없다.

핵심은:

```text
필수 의존성 보장
+
final을 통한 불변성
+
단위 테스트 용이성
```

이다.

---

### 착각 5. `@Autowired`를 굳이 사용할 필요가 없다는 것만 기억함

**내가 생각했던 것** — `@Autowired` 없이도 생성자 주입을 할 수 있다는 사실은 알고 있었지만
조건을 명확히 설명하지 못했다.

**실제로는** **생성자가 하나라면** Spring이 사용할 생성자를 명확하게 판단할 수 있어 생략할 수 있다.

그리고 **실측 6**에서 반대편을 확인했다. 생성자가 둘이면 **예외가 아니라
기본 생성자가 조용히 선택되고 주입이 일어나지 않는다.**

```text
생성자 1개      → @Autowired 생략 가능
생성자 2개 이상 → @Autowired로 지목하지 않으면 조용히 주입 안 됨
```

---

### 착각 6. `@Configuration`이 필요한 이유는 외부 클래스에 `@Component`를 못 붙여서다

**내가 생각했던 것** — 외부 클래스에 직접 `@Component`를 붙이지 못하므로 설정할 장소가 필요하다.

**실제로는** 그 설명은 주로 **왜 `@Bean`을 사용하는가**와 연결된다.

`@Configuration`의 핵심은:

> 이 클래스가 Spring의 Bean 구성을 담당하는 설정 클래스라는 것을 표현하는 것

이다.

```text
@Bean
→ 등록할 객체

@Configuration
→ Bean 설정을 담당하는 클래스
```

여기에 더해 **실측 5**에서 `@Configuration`만의 실제 기능도 확인했다.
**CGLIB 프록시를 씌워 `@Bean` 메서드 직접 호출을 Container 조회로 바꾸는 것**이다.
이건 `@Bean`이 아니라 `@Configuration`이 하는 일이다.

---

### 착각 7. Spring Singleton과 일반 Singleton의 차이를 멀티스레드 문제로 설명함

**내가 생각했던 것** — Spring Singleton은 멀티스레드 환경에 취약하다.

**실제로는** 그것은 Spring Singleton 사용 시의 **주의점**이지 둘의 핵심 차이는 아니다.

```text
일반 Singleton Pattern
→ 클래스가 Singleton 보장

Spring Singleton
→ Container가 Bean Singleton 관리
```

---

### 착각 8. 변하는 필드라면 모두 Thread-unsafe하다

**내가 생각했던 것** — `AtomicInteger`도 Lock 코드가 없으므로 안전하지 않다.

**실제로는**

```java
count.incrementAndGet();
```

같은 `AtomicInteger`의 원자적 연산은 별도의 Lock 코드를 직접 작성하지 않아도 Thread-safe하다.

핵심 구분:

```text
Mutable
≠
반드시 Thread-unsafe

Thread-safe
≠
Stateless

Thread-safe
≠
항상 좋은 상태 관리 설계
```

---

### 착각 9. BeanFactory는 단순히 Bean을 만드는 클래스다

**내가 생각했던 것** — BeanFactory는 이름 그대로 Bean을 만드는 클래스다.

**실제로는** 클래스가 아니라 **인터페이스**다 (`BeanFactory.class.isInterface()` → `true`).
**Bean 생성·조회·의존관계 관리의 핵심 기능을 정의하는 IoC Container 인터페이스**다.

---

### 착각 10. BeanDefinition은 Bean 생성 후 필요 없다

**내가 생각했던 것** — BeanDefinition은 Bean을 만들었으면 역할이 끝나므로 필요 없어지는 정보다.

**실제로는** **실측 3**에서 Bean을 다 만든 뒤에도 `getBeanDefinition()`으로 조회된다.

```text
BeanDefinition
→ Bean을 어떻게 관리할 것인가

Bean
→ 실제 실행 객체
```

둘은 다른 목적을 가지고 Container 안에 공존한다.

---

### 착각 11. BeanDefinition이 필요한 이유는 Bean마다 타입이 달라서다

**실제로는** 더 중요한 이유는 Spring의 다양한 설정 방법을 공통 표현으로 통일하기 위해서다.

```text
@Component
@Bean
XML
 ↓
BeanDefinition
```

실측에서 나온 구현 클래스 이름 `ScannedGenericBeanDefinition`이 이 구조를 그대로 보여준다.
스캔 경로로 들어오면 이 구현체, `@Bean` 경로로 들어오면 또 다른 구현체를 쓰되
**BeanFactory가 보는 타입은 `BeanDefinition` 하나**다.

---

### 착각 12. `getBean("orderService")`는 클래스 이름으로 조회한다

**실제로는** 문자열 인자는 **Bean 이름**이다.

```text
getBean("orderService")
→ 이름

getBean(OrderService.class)
→ 타입
```

---

### 착각 13. ApplicationContext가 BeanFactory를 "포함"한다

**내가 생각했던 것** — ApplicationContext 안에 BeanFactory가 들어 있다 (합성 관계).

**실제로는** **인터페이스 상속**이다. `ApplicationContext`는 `ListableBeanFactory`와
`HierarchicalBeanFactory`를 상속하고, 이들이 `BeanFactory`를 상속한다.

```text
ApplicationContext.class.getInterfaces()
[EnvironmentCapable, ListableBeanFactory, HierarchicalBeanFactory,
 MessageSource, ApplicationEventPublisher, ResourcePatternResolver]
```

그래서 `ctx instanceof BeanFactory`가 `true`다.
"BeanFactory의 기능을 그대로 쓰면서 인터페이스를 더 얹은 것"이라고 말하는 편이 정확하다.

(구현 내부에서는 `GenericApplicationContext`가 `DefaultListableBeanFactory`를 들고 있는
합성 구조이기도 하다. 다만 **타입 관계는 상속**이라는 것이 요점이다.)

---

## 6. 비교 정리

### IoC vs DI

| 구분       | IoC              | DI                  |
| -------- | ---------------- | ------------------- |
| 의미       | 제어의 역전           | 의존성 주입              |
| 범위       | 더 큰 설계 개념        | IoC 구현 방법 중 하나      |
| 핵심       | 객체 제어권을 외부로 이동   | 의존 객체를 외부에서 전달      |
| Spring에서 | Container가 객체 관리 | Container가 Bean을 연결 |

---

### `@Component` vs `@Bean`

| 구분        | `@Component`                | `@Bean`          |
| --------- | --------------------------- | ---------------- |
| 선언 위치     | 클래스                         | 메서드              |
| 등록 방식     | Component Scan 자동 탐색        | 설정 메서드 반환 객체 등록  |
| 기본 Bean 이름 | 클래스명 첫 글자 소문자 (`orderService`) | 메서드 이름 (`plainOne`) |
| 주 사용      | 직접 작성한 Service/Repository 등 | 외부 객체, 세밀한 생성 설정 |
| 생성 제어     | 비교적 Convention 중심           | 생성 코드를 직접 작성 가능  |
| 직접 만든 클래스 | 가능                          | 가능               |
| 외부 라이브러리  | 직접 붙이기 어려움                  | 적합               |

선택 기준:

```text
내가 작성한 일반적인 애플리케이션 클래스
→ @Component / @Service 등

외부 클래스 또는 생성 설정 직접 제어
→ @Bean
```

---

### BeanFactory vs ApplicationContext

| 구분          | BeanFactory   | ApplicationContext      |
| ----------- | ------------- | ----------------------- |
| 정체          | 인터페이스         | 인터페이스 (BeanFactory 하위 타입) |
| 핵심 역할       | Bean 생성·조회·관리 | Spring 애플리케이션 Container |
| IoC/DI      | 제공            | 제공 (상속)                 |
| Event       | 핵심 역할 아님      | `ApplicationEventPublisher` |
| Resource    | 핵심 역할 아님      | `ResourcePatternResolver` |
| Environment | 핵심 역할 아님      | `EnvironmentCapable`    |
| 메시지·국제화     | 핵심 역할 아님      | `MessageSource`         |
| 일반 개발에서     | 직접 사용할 일 적음   | 주로 사용                   |

---

### BeanDefinition vs Bean

| 구분 | BeanDefinition | Bean                |
| -- | -------------- | ------------------- |
| 의미 | Bean 메타정보/명세   | 실제 객체               |
| 역할 | 어떻게 생성·관리할지 표현 | 비즈니스 로직 실행          |
| 예  | Scope, 생성 정보 등 | `OrderService` 인스턴스 |
| 생성 후 | Container에 그대로 남음 | Container가 참조 보관 |

---

### 일반 Singleton vs Spring Singleton

| 구분                         | 일반 Singleton Pattern    | Spring Singleton      |
| -------------------------- | ----------------------- | --------------------- |
| 관리 주체                      | 클래스                     | Spring Container      |
| 구현                         | `static`, private 생성자 등 | 일반 POJO 가능            |
| 범위                         | 일반적으로 클래스/JVM 관점        | ApplicationContext 기준 |
| 비즈니스 클래스가 Singleton을 인식하는가 | 인식                      | 몰라도 됨                 |

---

### `@Primary` vs `@Qualifier`

| 구분    | `@Primary`   | `@Qualifier`     |
| ----- | ------------ | ---------------- |
| 목적    | 기본 Bean 지정   | 특정 Bean 지정       |
| 선언 위치 | Bean 쪽       | 주입 지점 쪽          |
| 의미    | "보통 이걸 사용"   | "여기서는 정확히 이것 사용" |
| 사용 상황 | 대표 구현체가 있을 때 | 특정 구현체를 명확하게 선택  |
| 둘이 겹치면 | 진다           | **이긴다**          |

---

## 7. 실무에서는 어떻게 사용되는가?

### IoC / DI

```text
Service
↓
Repository / Client 필요
↓
생성자 DI
↓
구현체 교체 가능
```

비즈니스 Service가 Repository나 외부 Client를 직접 `new`하지 않도록 구성하면
구현 변경과 테스트가 쉬워진다.

---

### `@Service`, `@Repository`

실제 Spring Backend 프로젝트에서는 대부분의 애플리케이션 계층을 Component Scan 기반 Bean으로 관리한다.

```text
Controller
    ↓
Service
    ↓
Repository
```

각 계층의 객체 생성 코드를 직접 작성하지 않고 Container가 연결한다.

---

### `@Bean`

외부 라이브러리 객체나 세부 설정이 필요한 객체를 애플리케이션 설정에 맞게 등록할 때 사용한다.

```text
외부 Library 객체
↓
@Configuration
↓
@Bean
↓
Spring 관리 객체
```

---

### Singleton Service

Spring Service는 기본적으로 Singleton Bean이기 때문에 웹 요청 데이터를 필드에 저장하는 설계는 피해야 한다.

```java
@Service
public class OrderService {

    // 요청별 값 저장 X
    // private Long currentUserId;

    public Order getOrder(Long userId) {
        // parameter/local variable 사용
    }
}
```

이는 실제 서버의 멀티스레드 요청 처리와 직접 연결되는 중요한 실무 포인트다.

---

## 8. 장애 / 문제 상황으로 이해하기

### Case 1. 같은 인터페이스 구현체가 두 개라 애플리케이션 실행 실패

**상황**

```text
PaymentClient
├─ KakaoPaymentClient
└─ NaverPaymentClient
```

```java
public PaymentService(PaymentClient paymentClient) {
}
```

**원인** — `PaymentClient` 타입으로 주입할 후보 Bean이 여러 개라 Spring이 하나를 선택할 수 없다.

**실제 예외**

```text
org.springframework.beans.factory.NoUniqueBeanDefinitionException:
No qualifying bean of type 'com.example.app.PaymentClient' available:
expected single matching bean but found 2: kakaoPaymentClient,naverPaymentClient
```

**해결** — 대표를 정하려면 `@Primary`, 이 자리에서만 다른 걸 쓰려면 `@Qualifier`.
둘이 겹치면 `@Qualifier`가 이긴다.

**핵심 개념** — DI / Bean 후보 선택

---

### Case 2. `@Service`를 붙였는데 Bean을 찾을 수 없음

**상황**

```java
@Service
public class PaymentService {
}
```

인데 주입 또는 `getBean()`에서 Bean을 찾지 못한다.

**원인** — Component Scan 범위 밖에 클래스가 존재할 수 있다.

```text
com.example.app
└─ Application

com.other.payment
└─ PaymentService
```

**해결** — 패키지 구조를 Component Scan 범위 안에 배치하거나 Scan 범위를 명시적으로 조정한다.

**핵심 개념** — Component Scan

---

### Case 3. Singleton Service의 사용자 정보가 다른 요청과 섞임

**상황**

```java
@Service
public class UserService {

    private Long currentUserId;
}
```

여러 요청이 동시에 처리된다.

**원인** — 하나의 Singleton Bean을 여러 Thread가 공유하면서 동일한 mutable field를 변경한다.

**해결** — 요청별 값을 필드에 보관하지 않는다.

```java
public User findUser(Long userId) {
}
```

메서드 파라미터/지역 변수 등을 사용한다.

**핵심 개념** — Singleton / Stateless / Multi Thread

---

### Case 4. 타입으로 `getBean()` 했더니 예외 발생

**상황**

```java
context.getBean(PaymentClient.class);
```

그런데 해당 타입 Bean이 두 개 존재한다.

**원인** — 타입만으로 하나를 특정할 수 없다.

**해결** — Bean 이름으로 조회하거나, `@Primary`로 대표를 정한다.
실측에서 `@Primary`를 붙이자 타입 조회도 예외 없이 통과했다.

**핵심 개념** — Bean 이름 / 타입 조회 / Bean 후보

---

### Case 5. 기동은 되는데 런타임에 NPE — 생성자가 둘이었다

**상황**

```java
@Component
public class ReportService {
    private final PaymentClient client;

    public ReportService() { this.client = null; }          // 테스트용으로 추가했던 것
    public ReportService(PaymentClient client) { this.client = client; }
}
```

애플리케이션은 정상 기동하는데 해당 기능을 호출하는 순간 `NullPointerException`.

**원인** — 생성자가 둘인데 `@Autowired`가 없어 Spring이 **기본 생성자를 골랐다.**
후보가 애매하면 예외가 날 거라고 예상했지만, 예외 없이 조용히 넘어간다 (**실측 6**).

**해결** — 주입받을 생성자에 `@Autowired`를 명시하거나, 불필요한 생성자를 없앤다.

**핵심 개념** — 생성자 주입 / `@Autowired` 생략 조건

---

## 9. 기술면접 핵심 질문

### Q1. IoC와 DI의 차이는 무엇인가요?

**답변 핵심 키워드** — 제어권 → Container → 외부 주입 → IoC 구현 방식

**좋은 답변**

IoC는 객체의 생성이나 의존관계 설정 같은 제어권을 개발자가 직접 가지는 것이 아니라
Framework가 담당하도록 하는 개념입니다. DI는 객체가 필요한 의존 객체를 직접 생성하지 않고
외부에서 전달받는 방식이고, Spring에서는 Container가 Bean을 생성하면서 의존 Bean을 주입합니다.
따라서 IoC가 더 큰 개념이고 DI는 IoC를 구현하는 대표적인 방식이라고 이해하고 있습니다.

**꼬리질문**

* DI를 사용하면 어떤 장점이 있나요?
* Spring을 사용하지 않고도 DI가 가능한가요?

---

### Q2. 생성자 주입을 권장하는 이유는 무엇인가요?

**답변 핵심 키워드** — 필수 의존성 → `final` → 불변성 → 테스트

**좋은 답변**

생성자 주입은 객체가 만들어지는 시점에 필수 의존성을 전달받기 때문에 정상적으로 생성된 객체가
필요한 의존성을 갖도록 만들 수 있습니다. 또한 의존 필드를 `final`로 선언해 변경 가능성을 줄일 수 있고,
테스트에서도 Spring Container 없이 생성자를 통해 Mock이나 Fake 구현체를 전달하기 쉽습니다.
그래서 필수 의존성에는 생성자 주입을 사용하는 편이 좋습니다.

**꼬리질문**

* `@Autowired`는 언제 생략할 수 있나요?
    * 생성자가 하나일 때. 둘 이상이면 명시하지 않는 한 기본 생성자가 선택되고 주입이 일어나지 않는다.
* Setter 주입은 언제 사용할 수 있나요?

---

### Q3. `@Component`와 `@Bean`의 차이는 무엇인가요?

**답변 핵심 키워드** — 클래스 → Component Scan / 메서드 → 명시적 객체 생성

**좋은 답변**

`@Component`는 클래스에 직접 선언하고 Component Scan을 통해 자동으로 Bean 등록하는 방식이라
제가 작성한 Service나 Repository 등에 주로 사용합니다. `@Bean`은 메서드가 반환하는 객체를
Bean으로 등록하기 때문에 외부 라이브러리처럼 클래스에 애노테이션을 직접 붙일 수 없거나
객체 생성 과정을 직접 제어해야 할 때 유용합니다. 다만 `@Bean`도 제가 작성한 클래스에 사용할 수 있습니다.

**꼬리질문**

* `@Service`와 `@Component`는 어떤 관계인가요?
* `@Configuration`은 왜 필요한가요?
    * `@Bean` 메서드 직접 호출을 Container 조회로 바꾸는 CGLIB 프록시가 여기서 나온다.

---

### Q4. BeanDefinition은 무엇이고 왜 필요한가요?

**답변 핵심 키워드** — Bean 메타데이터 → 공통 표현 → 설정 방식 추상화 → BeanFactory

**좋은 답변**

BeanDefinition은 Bean 클래스나 Scope, 생성 방식 등 Spring이 Bean을 생성하고 관리하기 위한
메타데이터입니다. Spring은 `@Component`, `@Bean`, XML처럼 여러 방식으로 Bean 설정을 받을 수 있는데
이를 내부에서 BeanDefinition이라는 공통 형태로 표현합니다. 덕분에 BeanFactory는 설정 정보가
어떤 방식으로 작성됐는지 몰라도 BeanDefinition을 기준으로 일관되게 Bean을 생성하고 관리할 수 있습니다.

**꼬리질문**

* Bean과 BeanDefinition의 차이는 무엇인가요?
* Bean을 생성하고 나면 BeanDefinition은 없어지나요?
    * 없어지지 않는다. Scope·생명주기 정보가 계속 필요하다.

---

### Q5. BeanFactory와 ApplicationContext의 차이는 무엇인가요?

**답변 핵심 키워드** — IoC Container → BeanFactory → 확장 기능 → ApplicationContext

**좋은 답변**

BeanFactory는 Bean의 생성, 조회, 의존관계 관리 같은 Spring IoC의 핵심 기능을 정의하는
기본 Container 인터페이스입니다. ApplicationContext는 이 BeanFactory를 상속하면서
이벤트 처리, 리소스 로딩, Environment, 메시지 소스 등 실제 애플리케이션에 필요한 기능을
추가로 제공합니다. 그래서 일반적인 Spring 애플리케이션에서는 ApplicationContext를 사용합니다.

**꼬리질문**

* ApplicationContext 안에는 Bean만 존재하나요?
* BeanDefinition은 어디에서 사용되나요?

---

### Q6. Spring Singleton과 Singleton Pattern은 어떻게 다른가요?

**답변 핵심 키워드** — 클래스 관리 → Container 관리 → ApplicationContext

**좋은 답변**

일반 Singleton Pattern은 클래스 자체가 static 인스턴스나 private 생성자 등을 이용해
객체 하나를 유지하도록 구현합니다. 반면 Spring Singleton은 클래스가 Singleton을 직접 구현하지 않아도
Spring Container가 특정 Bean 인스턴스를 하나 생성해서 재사용하는 방식입니다.
따라서 Spring Singleton은 Container, 정확히는 ApplicationContext 관점에서 관리된다는 차이가 있습니다.

**꼬리질문**

* Singleton Bean에서 상태를 가지면 어떤 문제가 발생하나요?
* Spring Singleton은 JVM 전체에서 정확히 하나인가요?
    * 아니다. Context를 두 개 띄우면 서로 다른 인스턴스다 (**실측 2**).

---

### Q7. Singleton Bean을 Stateless하게 설계해야 하는 이유는 무엇인가요?

**답변 핵심 키워드** — 공유 객체 → 여러 Thread → Mutable State → Race Condition

**좋은 답변**

Spring의 기본 Singleton Bean은 여러 요청 Thread가 동일한 객체를 공유할 수 있습니다.
그래서 사용자 ID나 현재 주문 같은 요청별 데이터를 인스턴스 필드에 저장하면
다른 Thread가 값을 변경해 요청 간 데이터가 섞일 수 있습니다.
따라서 일반적인 Service는 요청 상태를 필드에 두지 않고 파라미터나 지역 변수로 처리해
Stateless하게 만드는 것이 안전합니다.

**꼬리질문**

* `AtomicInteger`를 필드에 사용하면 Thread-safe한가요?
* Thread-safe와 Stateless는 같은 의미인가요?

---

### Q8. 같은 타입의 Bean이 여러 개라면 Spring은 어떻게 동작하나요?

**답변 핵심 키워드** — 후보 여러 개 → 결정 불가 → `@Primary` / `@Qualifier`

**좋은 답변**

주입하려는 타입에 해당하는 Bean이 여러 개 존재하면 Spring이 어떤 Bean을 사용할지
하나로 결정해야 합니다. 명확한 선택 기준이 없다면 `NoUniqueBeanDefinitionException`이 발생하고,
기본 구현체를 지정하려면 `@Primary`, 특정 위치에서 사용할 Bean을 지정하려면 `@Qualifier`를 사용할 수 있습니다.

**꼬리질문**

* `@Primary`와 `@Qualifier`를 같이 사용하면 어떻게 생각해야 하나요?
    * `@Qualifier`가 이긴다. `@Primary`는 기본값, `@Qualifier`는 지역에서의 명시적 지정.
* Bean 이름으로도 후보를 구분할 수 있나요?

---

### Q9. `@Component` 클래스가 Bean이 되는 과정을 설명해 주세요.

**답변 핵심 키워드** — Component Scan → BeanDefinition → BeanFactory → 생성 → DI

**좋은 답변**

Spring Boot가 시작되면 `@SpringBootApplication`에 포함된 Component Scan 기능을 통해
지정된 패키지에서 `@Component` 계열 클래스를 찾습니다. 탐색된 클래스 정보는 BeanDefinition 형태로
Container에 등록되고, BeanFactory가 해당 정보를 기준으로 실제 객체를 생성합니다.
생성 과정에서 필요한 다른 Bean을 찾아 의존성을 주입하고 최종적으로 Container가 Bean을 관리합니다.

**꼬리질문**

* Component Scan의 기본 범위는 어디인가요?
* `@Bean`은 같은 과정을 어떻게 다르게 시작하나요?

---

## 10. 이번 주 최고의 면접 질문 3개

### ⭐ Q1. IoC와 DI는 무엇이며 두 개념은 어떤 관계인가요?

반드시 들어가야 하는 키워드:

```text
제어권
Spring Container
객체 생성/관리
외부 의존성 주입
IoC > DI
```

---

### ⭐ Q2. `@Component` 클래스가 실제 Spring Bean이 되기까지의 과정을 설명해 주세요.

반드시 들어가야 하는 키워드:

```text
@SpringBootApplication
Component Scan
BeanDefinition
BeanFactory
Bean 생성
DI
ApplicationContext
```

---

### ⭐ Q3. Spring Singleton Bean을 왜 Stateless하게 설계해야 하나요?

반드시 들어가야 하는 키워드:

```text
Singleton 공유
멀티스레드
Mutable State
요청 데이터
지역 변수 / 파라미터
Thread-safe ≠ Stateless
```

---

## 11. 1분 설명 연습

Spring의 IoC는 애플리케이션에서 사용하는 객체의 생성과 의존관계 관리에 대한 제어권을
개발자 코드가 아니라 Spring Container가 담당하도록 하는 개념입니다.

이렇게 하는 이유는 Service 같은 객체가 자신이 사용할 Repository 구현체까지 직접 생성하면
구체 구현에 강하게 결합되고 구현 교체나 테스트가 어려워지기 때문입니다.

Spring에서는 `@Component`나 `@Bean` 등을 통해 관리할 객체 정보를 제공하면 이를 BeanDefinition 같은
내부 메타데이터로 표현하고, BeanFactory가 이 정보를 이용해 실제 Bean을 생성합니다.
생성 과정에서 필요한 다른 Bean을 찾아 생성자 등을 통해 DI하고 ApplicationContext가 이를 관리합니다.

또한 기본 Bean Scope가 Singleton이기 때문에 하나의 Service 객체가 여러 요청 Thread에서 공유될 수 있습니다.
따라서 일반적인 Service에서는 요청별 상태를 필드에 저장하지 않고 Stateless하게 설계하는 것이 중요합니다.

결국 Spring IoC Container를 사용하는 핵심 의미는 단순히 객체 생성을 자동화하는 것이 아니라
**객체 생성과 연결을 비즈니스 코드에서 분리해 결합도를 낮추고 Framework가 일관되게
객체를 관리하도록 만드는 것**입니다.

---

## 12. 이번 주 최종 요약

### 꼭 기억할 것

1. **IoC는 객체의 생성·의존관계·관리 제어권을 Framework로 넘기는 개념이다.**
2. **DI는 필요한 의존 객체를 외부에서 전달받는 방식이며 IoC를 구현하는 대표적인 방법이다.**
3. DI는 의존성을 없애는 것이 아니라 **구체 구현체에 대한 결합을 줄이는 것**이다.
4. `@Component`는 Component Scan 기반 자동 등록, `@Bean`은 메서드 반환 객체의 명시적 등록이다.
5. `BeanDefinition`은 Bean 자체가 아니라 **Bean 생성·관리 메타데이터**이며 여러 설정 방식을
   공통 형태로 추상화한다. **Bean을 만든 뒤에도 사라지지 않는다.**
6. `BeanFactory`는 **인터페이스**이고 `ApplicationContext`는 이를 **상속해** 애플리케이션 기능을
   추가로 제공한다.
7. 생성자 주입의 핵심 장점은 **필수 의존성 보장 + 불변성 + 테스트 용이성**이다.
   **생성자가 둘 이상이면 `@Autowired`를 붙이지 않는 한 조용히 주입되지 않는다.**
8. 같은 타입 Bean이 여러 개라면 `@Primary`, `@Qualifier` 등으로 선택 기준을 제공해야 하고,
   **둘이 겹치면 `@Qualifier`가 이긴다.**
9. Spring Singleton은 Singleton Pattern과 달리 **Container가 객체 하나를 관리**하며
   그 범위는 **ApplicationContext 하나당 하나**다.
10. Singleton Bean은 여러 Thread가 공유하므로 **요청별 Mutable State를 필드에 저장하지 않는 것이 기본**이다.

### 한 줄 결론

> **Spring IoC/DI의 핵심은 객체 생성과 의존관계 구성을 비즈니스 코드에서 분리하고,
> BeanDefinition과 Container를 통해 Spring이 객체의 생성·연결·관리를 일관되게 담당하도록 만드는 것이다.**

---

## 13. 다음에 복습할 때

### 5분 복습

다음 다섯 개만 빠르게 본다.

1. IoC와 DI의 관계
2. `@Component → Component Scan → BeanDefinition → Bean`
3. `@Component` vs `@Bean`
4. BeanFactory vs ApplicationContext
5. Singleton Bean과 Stateless

특히 다음 그림을 머릿속에서 바로 그릴 수 있어야 한다.

```text
@Component
    ↓
Component Scan
    ↓
BeanDefinition
    ↓
BeanFactory
    ↓
Bean 생성
    ↓
DI
    ↓
ApplicationContext 관리
```

---

### 15분 복습

아무것도 보지 않고 다음 질문을 직접 설명한다.

1. IoC와 DI의 차이는 무엇인가?
2. 생성자 주입은 왜 권장되는가?
3. `@Component`와 `@Bean`은 어떻게 다른가?
4. BeanDefinition은 왜 존재하는가?
5. BeanFactory와 ApplicationContext는 어떻게 다른가?
6. Singleton Bean을 왜 Stateless하게 설계해야 하는가?

답을 외우기보다는 항상:

```text
무엇인가?
↓
왜 필요한가?
↓
Spring에서는 어떻게 동작하는가?
```

순서로 설명한다.

---

### 직접 다시 해볼 실습

#### 실습 1. Bean 등록 방식 비교

다음 두 방식으로 각각 Bean을 등록한다.

```text
@Component
vs
@Bean + @Configuration
```

그리고 `ApplicationContext#getBean()`으로 직접 조회한다.

확인할 것:

```text
Bean 이름
Bean 타입
동일 객체 여부
```

#### 실습 2. 같은 인터페이스 구현체 두 개 등록

```text
PaymentClient
├─ KakaoPaymentClient
└─ NaverPaymentClient
```

두 Bean을 등록한 뒤:

```java
public PaymentService(PaymentClient paymentClient)
```

로 주입을 시도한다.

그 후:

```text
1. 선택 기준이 없을 때
2. @Primary 추가
3. @Qualifier 추가
4. @Primary와 @Qualifier를 동시에
```

순서로 결과가 왜 달라지는지 직접 확인한다.
