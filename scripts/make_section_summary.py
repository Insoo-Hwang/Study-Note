# -*- coding: utf-8 -*-
"""섹션별 '한 장 요약' 도식을 만든다.

    python scripts/make_section_summary.py

각 섹션의 노트를 카드 하나씩으로 압축해 `docs/<NN-섹션>/<NN>-요약.svg`에 저장한다.
카드의 문구는 각 노트의 `1. 핵심 요약 > 한눈에 보기`에서 뽑아 줄인 것이므로,
노트를 고치면 여기 문구도 같이 고쳐야 한다.

새 섹션을 추가할 때는 build_04() 같은 함수를 만들어 아래 SECTIONS에 등록한다.
카드는 (색, 제목, 한 줄 핵심, 불릿 목록, 단계 표시) 다섯 값으로 쓴다.
"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from svg_kit import *  # noqa: E402,F403

W = 880
MARGIN = 32
GAP = 12
CARD_W = (W - MARGIN * 2 - GAP) // 2          # 402
FULL_W = W - MARGIN * 2                        # 816

CARD_BG = "#ffffff"
CARD_BORDER = "rgba(11,11,11,0.13)"
RULE = "rgba(11,11,11,0.09)"


def measure(s, size):
    """대략적인 텍스트 폭. 라벨이 카드를 넘치는지 확인하는 용도."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x1100:            # 한글·CJK
            w += size * 1.0
        elif ch == " ":
            w += size * 0.28
        elif ch.isupper() or ch.isdigit():
            w += size * 0.60
        elif ch.isalpha():
            w += size * 0.52
        else:
            w += size * 0.36
    return w


OVERFLOW = []


def fit(s, size, limit, where):
    if measure(s, size) > limit:
        OVERFLOW.append(f"{where}: {measure(s, size):.0f}>{limit} | {s}")
    return s


def card(x, y, w, color, title, core, bullets, tag=None):
    """왼쪽 색 띠 + 제목 + 한 줄 핵심 + 불릿 목록으로 된 카드."""
    h = card_h(len(bullets))
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
           f'fill="{CARD_BG}" stroke="{CARD_BORDER}" stroke-width="1.2"/>\n')
    out += (f'<path d="M{x} {y+10} a10,10 0 0 1 10,-10 h0 v{h} h0 '
            f'a10,10 0 0 1 -10,-10 Z" fill="{color}"/>\n')
    inner = x + 20
    lim = w - 34
    out += txt(inner, y + 26, fit(title, 15, lim - 60, "title"), size=15,
               fill=color, weight="700")
    if tag:
        out += txt(x + w - 16, y + 26, tag, size=14, fill=GRAY,
                   weight="700", anchor="end")
    out += txt(inner, y + 47, fit(core, 12.5, lim, "core"), size=12.5,
               fill=INK, weight="600")
    out += line(inner, y + 58, x + w - 14, y + 58, color=RULE, width=1)
    by = y + 79
    for b in bullets:
        out += f'<circle cx="{inner + 3}" cy="{by - 4}" r="2.4" fill="{color}" fill-opacity="0.65"/>\n'
        out += txt(inner + 13, by, fit(b, 12, lim - 13, "bullet"), size=12, fill=MUTED)
        by += 19.5
    return out


def card_h(n):
    return int(79 + (n - 1) * 19.5 + 18)


def spine(y, steps, colors):
    """상단 흐름 띠 — 이 섹션을 관통하는 질문의 순서."""
    out = ""
    n = len(steps)
    aw = 26                                  # 화살표 간격
    total = FULL_W - aw * (n - 1)
    pw = total / n
    x = MARGIN
    for i, (s, c) in enumerate(zip(steps, colors)):
        out += (f'<rect x="{x}" y="{y}" width="{pw:.1f}" height="34" rx="8" '
                f'fill="{c}" fill-opacity="0.09" stroke="{c}" '
                f'stroke-opacity="0.35" stroke-width="1.1"/>\n')
        out += txt(x + pw / 2, y + 22, fit(s, 12.5, pw - 16, "spine"),
                   size=12.5, fill=c, weight="700", anchor="middle")
        x += pw
        if i < n - 1:
            out += arrow(x + 5, y + 17, x + aw - 6, y + 17, color=GRAY, width=1.3)
            x += aw
    return out


def footer(y, title, lines, color):
    h = 30 + len(lines) * 20
    out = band(MARGIN, y, FULL_W, h, color, label=title)
    ly = y + 44
    for s in lines:
        out += txt(MARGIN + 16, ly, fit(s, 12, FULL_W - 34, "footer"),
                   size=12, fill=MUTED)
        ly += 20
    return out, h


# ─────────────────────────────────────────────────────────────
# 01. 복잡도 · 자료구조
# ─────────────────────────────────────────────────────────────
def build_01():
    cards = [
        (BLUE, "시간 복잡도와 공간 복잡도", "실행 시간이 아니라 입력이 커질 때의 증가율을 본다", [
            "O(1) < O(log n) < O(n) < O(n log n) < O(n²)",
            "시간은 연산 횟수 · 공간은 추가 메모리, 항상 같이 본다",
            "같은 알고리즘도 최선 · 평균 · 최악이 다르다",
            "메모리를 더 써서 시간을 줄이는 트레이드오프가 핵심",
        ], "①"),
        (BLUE, "Amortized Analysis", "한 번의 최악이 아니라 연속 n번의 총합으로 나눈다", [
            "ArrayList.add는 최악 O(n)이지만 상각 O(1)",
            "용량을 일정 배율로 늘리면 복사 비용이 분산된다",
            "입력 확률을 가정하는 평균 분석과는 다르다",
            "상각 O(1)이 매 연산이 빠르다는 뜻은 아니다",
        ], "①"),
        (ORANGE, "선형 자료구조 비교", "연속된 배열이거나, 흩어진 노드를 연결한 것이거나", [
            "배열 계열은 인덱스 조회 O(1) · 중간 삽입은 밀기 O(n)",
            "노드 계열은 양 끝 조작 O(1) · 인덱스 접근은 O(n)",
            "Stack · Queue · Deque는 저장 구조가 아닌 접근 규칙",
            "Java 표준은 ArrayDeque (Stack · LinkedList는 비권장)",
        ], "②"),
        (ORANGE, "해시와 트리 비교", "정확히 찾기만 하면 Hash, 순서와 범위가 필요하면 Tree", [
            "HashMap은 위치를 계산 → 평균 O(1), 대신 순서가 없다",
            "TreeMap은 정렬 유지 → O(log n), 범위 · 순회에 강하다",
            "LinkedHashMap은 해시 속도 + 삽입(접근) 순서 기억",
            "Set은 값을 키 자리에 넣은 Map일 뿐이다",
        ], "②"),
        (PURPLE, "Heap과 PriorityQueue", "전체 정렬이 아니라 가장 급한 하나만 앞에 두는 부분 정렬", [
            "부모-자식 순서만 지키고 형제끼리는 순서가 없다",
            "조회 O(1) · 삽입/삭제 O(log n) · 배열 하나로 구현",
            "Top-K에서 O(n log n)을 O(n log K)로 줄인다",
            "PriorityQueue는 최소 힙 기본, 순회 순서 ≠ 정렬 순서",
        ], "②"),
        (GREEN, "Collection 선택 기준", "인터페이스를 먼저 정하고, 그다음 구현체를 고른다", [
            "중복 · 순서 · 접근 방식 · 동시성 네 질문으로 좁힌다",
            "기본값 4개 — ArrayList · HashSet · HashMap · ArrayDeque",
            "잘못 고르면 대가가 크다 (contains 실측 2,000배 차이)",
            "순서와 null 허용 여부는 반드시 명시적으로 확인한다",
        ], "③"),
    ]
    steps = ["① 비용을 재는 자를 갖고", "② 구조의 성질을 알고", "③ 네 질문으로 고른다"]
    concl = [
        "복잡도는 순위표가 아니라 판단 기준이다 — 데이터 크기 · 조회 횟수 · 동시 요청 수를 먼저 확인한다.",
        "구조는 결국 넷이다 — 연속(배열) · 연결(노드) · 계산(해시) · 정렬(트리), 여기에 부분 정렬(힙)이 붙는다.",
        "선택은 기본값 4개로 시작하고, 그것으로 안 되는 이유를 측정으로 증명한 뒤에만 바꾼다.",
    ]
    return render("01. 복잡도 · 자료구조",
                  "노트 6개의 핵심을 한 장으로 — 무엇으로 재고, 무엇을 고르고, 왜 그렇게 고르는가",
                  steps, [BLUE, ORANGE, GREEN], cards, "이 섹션의 결론", concl, GREEN)


# ─────────────────────────────────────────────────────────────
# 02. 알고리즘
# ─────────────────────────────────────────────────────────────
def build_02():
    cards = [
        (BLUE, "탐색과 정렬", "이 데이터에서 몇 번 찾을 것인가 — 그 답이 전부를 결정한다", [
            "선형 탐색은 준비 비용이 0이라, 데이터가 작거나 1회 탐색이면 가장 빠르다",
            "이진 탐색은 O(log n)이지만 정렬이 전제 — 전제가 깨지면 예외 없이 조용히 틀린 답을 준다",
            "정렬 한 번의 비용은 선형 탐색 약 52회와 맞먹는다 (그보다 적게 찾으면 정렬하지 않는 편이 빠르다)",
            "Java는 기본형에 Dual-Pivot Quicksort, 객체에 TimSort(안정 정렬)를 쓴다 — 같은 Arrays.sort라도 다른 알고리즘",
            "compareTo · compare의 반환값은 크기가 아니라 부호만 의미가 있다 — a - b는 오버플로로 조용히 틀린다",
        ], "①"),
        (ORANGE, "구간 처리", "이미 계산한 것을 버리지 않는다 — 세 패턴 모두 같은 아이디어다", [
            "투 포인터 — 두 위치를 조절하며 조건을 탐색한다. 전제는 단조성(정렬 등)이다",
            "슬라이딩 윈도우 — 창이 한 칸 움직일 때 나간 값을 빼고 들어온 값을 더한다. 창 크기 k와 무관하게 이동 한 번이 O(1)",
            "누적합 — 미리 O(n)을 선불로 지불해 임의 구간 합을 O(1)로 만든다",
            "for 안에 while이 있어도 left가 되돌아가지 않으면 전체는 O(n)이다 — 상환 분석으로 세야 한다",
        ], "②"),
        (PURPLE, "그래프 문제 해결", "최단 거리가 필요한가로 DFS · BFS가, 지금의 최선을 증명할 수 있는가로 Greedy · DP가 갈린다", [
            "DFS와 BFS는 자료구조만 스택 ↔ 큐로 바꾼 같은 코드인데, 보장하는 성질이 완전히 달라진다",
            "BFS만 최단 경로를 보장하고, 그것도 간선 가중치가 모두 같을 때만이다",
            "방문 표시는 큐에 넣을 때 해야 한다 — 꺼낼 때 하면 같은 정점이 여러 번 들어간다 (실측 6회 → 16회)",
            "재귀 DFS는 JVM 호출 스택을 써서 약 1만 깊이에서 터진다. 명시적 스택은 힙을 써서 1000만도 견딘다",
            "Greedy는 지금 최선을 고르고, DP는 겹치는 계산을 저장한다 — 확신이 없으면 각각 BFS와 DP가 안전한 답이다",
        ], "③"),
    ]
    steps = ["① 몇 번 찾는가", "② 계산을 이어 쓰는가", "③ 최단을 보장하는가"]
    concl = [
        "탐색은 손익분기점 문제다 — 반복 조회가 충분히 많을 때만 정렬이라는 선불 비용이 회수된다.",
        "구간은 매번 다시 세지 말고 이어서 갱신한다 — 한 방향이면 슬라이딩 윈도우, 임의 구간이면 누적합, 짝을 찾으면 투 포인터.",
        "탐색 알고리즘의 선택은 취향이 아니라 보장의 문제다 — 최단이 필요하면 BFS, 증명할 수 없으면 Greedy 대신 DP.",
    ]
    return render("02. 알고리즘",
                  "노트 3개의 핵심을 한 장으로 — 어떤 질문이 어떤 알고리즘으로 이어지는가",
                  steps, [BLUE, ORANGE, PURPLE], cards, "이 섹션의 결론", concl, PURPLE,
                  single_column=True)


# ─────────────────────────────────────────────────────────────
# 03. Java
# ─────────────────────────────────────────────────────────────
def build_03():
    cards = [
        (BLUE, "객체지향과 SOLID", "목적은 현실 흉내가 아니라 변경이 퍼지지 않게 막는 것", [
            "네 기둥 중 실제 이득을 만드는 것은 다형성 하나다",
            "메서드는 오버라이딩되지만 필드는 되지 않는다 (실측 확인)",
            "SOLID 다섯은 결국 변할 것과 변하지 않을 것을 분리하라는 한 말",
            "상속은 기본 선택지가 아니다 — 이유가 없으면 합성을 쓴다",
            "DIP가 Spring 의존성 주입의 이론적 근거다",
        ], "①"),
        (ORANGE, "Java Collection", "무엇을 보장하는가와 어떻게 만들었는가의 분리", [
            "Iterable → Collection → List · Set · Queue (Map은 별개다)",
            "ArrayList는 0 → 10에서 1.5배씩, HashMap은 table 16 · 임계 12",
            "subList · keySet · Arrays.asList는 복사본이 아니라 뷰다",
            "fail-fast는 보장이 아니다 — 끝에서 두 번째 삭제만 조용히 통과",
            "구현체 선택은 곧 내부 자료구조 선택이다",
        ], "②"),
        (ORANGE, "equals · hashCode", "hashCode는 어디를 뒤질까, equals는 그중 진짜인가", [
            "버킷을 찾고 최종 확인하는 두 단계라 둘 다 필요하다",
            "equals만 재정의 → 못 찾고, hashCode만 → 중복이 그대로 쌓인다",
            "해시가 같아도 같은 객체가 아니다 (\"Aa\"와 \"BB\" 모두 2112)",
            "키 필드를 바꾸면 미아가 된다 — 못 찾는데 size엔 잡힌다",
            "상수 hashCode면 HashSet 삽입이 2,408배 느려진다 (실측)",
        ], "②"),
        (PURPLE, "Generic · Exception · Stream", "직접 하지 말고 맡겨라 — 대신 각각 함정이 하나씩 있다", [
            "타입 소거 — List<String>과 List<Integer>는 실행 중 같은 클래스",
            "그래서 넣을 때는 조용하고, 꺼낼 때 ClassCastException이 난다",
            "와일드카드는 PECS — 읽기만 ? extends, 쓰기만 ? super",
            "finally에서 return하면 예외가 통째로 사라진다 (실측 확인)",
            "스트림은 지연 평가 — 최종 연산이 없으면 아무 일도 없다",
            "진짜 비용은 스트림이 아니라 박싱이다 (100만 건 5.1배 차이)",
        ], "③"),
        (GREEN, "JVM 메모리와 GC", "GC는 메모리가 부족할 때가 아니라 Eden이 찰 때마다 수시로 돈다", [
            "스레드마다 갖는 곳(스택 · PC)과 모두가 공유하는 곳(힙 · 메타스페이스)으로 나뉜다 — 객체는 힙에, 참조 변수는 스택에 있다",
            "GC의 기준은 참조 횟수가 아니라 GC Root에서 따라갈 수 있는가(도달 가능성)다",
            "힙은 Young(Eden + Survivor 2개)과 Old로 나뉘고, 근거는 대부분의 객체는 금방 죽는다는 약한 세대 가설이다",
            "JDK 9부터 기본은 G1 — 실측에서 약 1GB 할당에 GC 8회 · 누적 18 ms로 자주, 그리고 짧게 돌았다",
            "메모리 누수는 쓰지 않지만 참조가 남은 객체다. GC는 참조가 있으면 절대 치우지 않는다 — 응답 시간의 주범은 STW다",
        ], "④"),
    ]
    steps = ["① 변경을 가두고(OOP)", "② 자료를 규약 위에 담고", "③ 도구에 맡기고", "④ JVM이 떠받친다"]
    concl = [
        "객체지향은 다형성으로 변경의 파급을 가두는 일이고, SOLID는 그 방법을 다섯 문장으로 정리한 것이다.",
        "컬렉션은 인터페이스라는 계약과 equals · hashCode라는 규약 위에서만 정확하게 동작한다 — 키는 반드시 불변이어야 한다.",
        "제네릭 · 예외 · 스트림은 편의를 주는 대신 각각 소거 · 예외 삼킴 · 지연 평가라는 함정을 남긴다.",
        "그 모든 것 아래에서 JVM이 메모리를 나누고 GC가 돈다 — 튜닝의 목표는 GC를 없애는 것이 아니라 짧게 만드는 것이다.",
    ]
    return render("03. Java",
                  "노트 5개의 핵심을 한 장으로 — 언어의 원칙에서 실행 기반까지",
                  steps, [BLUE, ORANGE, PURPLE, GREEN], cards, "이 섹션의 결론", concl, BLUE)


# ─────────────────────────────────────────────────────────────
def render(title, subtitle, steps, step_colors, cards, ftitle, flines,
           fcolor, single_column=False):
    spine_y = 84
    top = spine_y + 34 + 22

    # 배치 계산 (2단 또는 1단)
    placed = []
    y = top
    if single_column:
        for c in cards:
            h = card_h(len(c[3]))
            placed.append((MARGIN, y, FULL_W, c))
            y += h + GAP
    else:
        i = 0
        while i < len(cards):
            pair = cards[i:i + 2]
            if len(pair) == 2:
                h = max(card_h(len(pair[0][3])), card_h(len(pair[1][3])))
                placed.append((MARGIN, y, CARD_W, pair[0]))
                placed.append((MARGIN + CARD_W + GAP, y, CARD_W, pair[1]))
            else:
                h = card_h(len(pair[0][3]))
                placed.append((MARGIN, y, FULL_W, pair[0]))
            y += h + GAP
            i += 2

    fy = y + 10
    fh = 30 + len(flines) * 20
    H = int(fy + fh + 26)

    s = head(W, H, title + " — 한 장 요약", subtitle)
    s += spine(spine_y, steps, step_colors)
    for x, cy, w, (color, t, core, bullets, tag) in placed:
        s += card(x, cy, w, color, t, core, bullets, tag)
    f, _ = footer(fy, ftitle, flines, fcolor)
    s += f
    return s


# 섹션 폴더명 → (출력 파일명, 생성 함수)
SECTIONS = [
    ("01-복잡도-자료구조", "01-요약.svg", build_01),
    ("02-알고리즘", "02-요약.svg", build_02),
    ("03-Java", "03-요약.svg", build_03),
]


if __name__ == "__main__":
    docs = ROOT / "docs"
    for folder, name, build in SECTIONS:
        save(docs / folder / name, build())
    if OVERFLOW:
        # measure()는 어림값이라 몇 px 넘는 것은 실제로는 문제없을 때가 많다.
        # 그래도 눈으로 확인하라는 신호로 남긴다.
        print("\n── 카드 폭을 넘칠 수 있는 문구 ──")
        for o in OVERFLOW:
            print(" ", o)
    else:
        print("\n텍스트 폭 문제 없음")

