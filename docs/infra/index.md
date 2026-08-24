# 인프라 노트

> **면접 커리큘럼(01~12)과 분리된, 인프라를 직접 만지며 남기는 기록.**

01~12 섹션은 "면접에서 설명할 수 있는가"를 목표로 6개 섹션 형식을 맞춰 쓴 노트다.
이 트리는 목적이 다르다. **직접 설치하고 설정하고 깨뜨려 본 것을 남기는 곳**이라
형식을 강제하지 않는다.

목적이 다르니 화면도 나눠 뒀다. 헤더의 **CS 노트 / 인프라 노트 / 실무 노트** 탭이 그 경계다.
지금은 인프라 모드라 좌측 메뉴에 이 트리만 보이고 헤더도 틸색이다.
커리큘럼으로 돌아가려면 **[CS 노트](../index.md)** 탭을 누른다.

| 구분 | 01~12 커리큘럼 | 인프라 노트 | 실무 노트 |
| -- | -- | -- | -- |
| **목적** | 면접에서 설명하기 | 직접 돌려 보고 다시 찾아보기 | 쓰고 있는 기술을 깊게 이해하기 |
| **주인공** | 개념 일반론 | 설치 · 설정 · 환경 | 코드 · API · 라이브러리 |
| **형식** | 6개 섹션 고정 (검사기가 강제) | 자유 | 자유 |
| **작성 명령** | `/study-section <번호>` | `/study-infra` | `/study-work` |
| **완결성** | 이 문서 하나로 이해되어야 함 | 메모·명령어 모음도 괜찮음 | 파다 만 것도 괜찮음 |

**인프라와 실무를 가르는 기준은 주인공이다.** Redis 컨테이너를 올리고 AOF를 설정한 기록은
여기, 그 Redis를 Redisson으로 어떻게 쓰는지는 **[실무 노트](../work/index.md)** 다.

---

## 노트 목록

**요청 하나가 브라우저에서 DB까지 가는 길**을 따라 1번부터 순서대로 읽으면 이어진다.
앞 장의 IP · Port · localhost 규칙이 뒤 장에서 이름만 바꿔 계속 다시 나오기 때문에,
건너뛰기보다 순서대로 보는 편이 빠르다.

| # | 노트 | 무엇을 잡는가 |
| -- | -- | -- |
| 1 | [네트워크](01-네트워크/01-네트워크.md) | Client · Server · IP · Port · localhost · DNS · NAT — 나머지 전부의 바탕 |
| 2 | [Docker](02-Docker/02-Docker.md) | Image · Container · Dockerfile · Port Mapping · Volume · 컨테이너 네트워크 |
| 3 | [Docker Compose](03-Docker-Compose/03-Docker-Compose.md) | 여러 컨테이너를 YAML 하나로, Service 이름으로 통신하기 |
| 4 | [Nginx](04-Nginx/04-Nginx.md) | Web Server · Reverse Proxy · Load Balancing · `proxy_pass` · 502 |
| 5 | [외부 접속](05-외부-접속/05-외부-접속.md) | 공유기 · NAT · Port Forwarding · Firewall · Tunnel |
| 6 | [DNS / HTTPS](06-DNS-HTTPS/06-DNS-HTTPS.md) | Domain · A · CNAME · TLS · 인증서 · HTTPS 동작 순서 |
| 7 | [CI/CD](07-CI-CD/07-CI-CD.md) | GitHub Actions · Workflow · Runner · Registry · Tag · Secret · Rollback |
| 8 | [모니터링](08-모니터링/08-모니터링.md) | Log · Metric · Actuator · Micrometer · Prometheus · Grafana |
| 9 | [장애 대응](09-장애-대응/09-장애-대응.md) | Status Code · 각종 로그 · Connection Refused · Timeout · 추적 순서 |
| 10 | [Kubernetes](10-Kubernetes/10-Kubernetes.md) | Cluster · Pod · Deployment · Service · Ingress · Desired State |
| 11 | [전체 연결하기](11-전체-연결하기/11-전체-연결하기.md) | 사용자 요청 흐름과 배포 흐름, 두 개를 하나로 겹쳐 보기 |

---

## 노트 추가하는 법

정리한 내용을 `/study-infra` 뒤에 그대로 붙여넣으면 아래 규칙에 맞춰 노트로 만들고 등록까지 한다.
같은 주제 노트가 이미 있으면 새로 만들지 않고 그 노트에 합친다.

```text
/study-infra
오늘 nginx 리버스 프록시 세팅함. proxy_pass로 8080 넘겼고
502 뜨길래 보니 upstream이 127.0.0.1이어야 하는데 localhost로 써서...
```

아래는 그 명령이 지키는 규칙이고, 직접 쓸 때도 같다.

### 1. 경로

커리큘럼과 **물리 구조만 같다.** 노트마다 폴더를 하나 만들고, 파일명은 폴더명과 같게 한다.
도식(`.svg`)은 노트와 같은 폴더에 둔다.

```text
docs/infra/<노트명>/<노트명>.md
docs/infra/<노트명>/<도식>.svg
```

이 트리는 지금 1~11번이 하나의 흐름을 이루고 있어서 폴더명 앞에 번호를 붙여 두었다.
**커리큘럼(01~12)의 번호와는 아무 관계가 없다.** 읽는 순서를 표시하는 용도일 뿐이다.
흐름과 무관한 단발성 기록이라면 번호 없이 주제명만 써도 된다.

카테고리(컨테이너 · 네트워크 · CI/CD …)는 **폴더를 더 파지 않고** `mkdocs.yml`의 `nav`에서
묶는다. 폴더를 한 단계 더 파면 검사기(`docs/*/*/*.md`)와 도식 경로 규칙에서 벗어난다.

### 2. 지켜야 하는 것 (검사기가 잡는 것)

자유 형식이지만 아래 네 가지는 커리큘럼 노트와 똑같이 검사한다.

- **파일명 == 폴더명**
- **번호 목록 아래 하위 불릿은 4칸 들여쓰기** — 3칸이면 mkdocs에서 목록이 끊긴다
- **참조한 이미지가 같은 폴더에 실제로 있을 것**, 외부 이미지(`https://…`) 금지
- **SVG는 XML로 파싱될 것**, 외부 리소스 참조 금지

6개 섹션 · 요약표는 **검사하지 않는다.**

### 3. 등록

두 곳에 추가한다.

1. 이 파일(`docs/infra/index.md`)의 노트 목록
2. `mkdocs.yml`의 `nav` → 최상위 `인프라 노트` 그룹
   (최상위 항목은 `CS 노트` · `인프라 노트` · `실무 노트` 셋뿐이고, 이 셋이 곧 헤더의 탭이다.
   여기에 항목을 더 만들면 탭이 늘어나 모드 구분이 깨진다.)

`docs/index.md`(커리큘럼 목차)와 `README.md`의 커리큘럼 트리에는 **넣지 않는다.**
그게 두 트리를 분리해 두는 이유다.

### 4. 검사

```bash
python scripts/check_notes.py infra    # 인프라 노트만 검사
python -m mkdocs build --strict        # 링크·nav 검증
```
