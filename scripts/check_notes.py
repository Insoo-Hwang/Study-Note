"""학습 노트와 도식이 저장소 규칙을 지키는지 검사한다.

사용법:
    python scripts/check_notes.py                 # 전체 검사
    python scripts/check_notes.py 02-자료구조      # 특정 섹션만 검사

ERROR가 하나라도 있으면 종료 코드 1을 반환한다 (CI/커밋 전 게이트로 사용).
WARN은 참고용이며 종료 코드에 영향을 주지 않는다.

검사 항목은 실제로 겪었던 문제에서 나왔다.
  - 3칸 들여쓰기로 mkdocs 순서 목록이 끊긴 문제 (`들여쓰기 수정` 커밋)
  - `답변 구조`에 복잡도/대안/실무가 빠져 면접 대비가 부족했던 문제
  - SVG에 이스케이프 안 된 `&`가 들어가 브라우저에서 XML 파싱 에러가 난 문제
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# 노트가 공통으로 쓰는 16개 섹션 (순서 포함)
SECTIONS = [
    "핵심 요약", "등장 배경", "핵심 개념", "구조와 동작 원리",
    "코드 또는 사용 예시", "성능 특성", "장점과 단점", "사용 기준",
    "비슷한 개념 비교", "백엔드 실무 적용", "자주 하는 오해", "면접 답변",
    "예상 면접 질문", "추가 학습 방향", "최종 체크리스트", "한 줄 결론",
]

# `면접 답변 > 답변 구조`가 반드시 이 순서로 담아야 하는 8개 항목
ANSWER_PARTS = [
    "정의", "내부 원리", "복잡도", "장점",
    "단점", "사용 기준", "대안과 비교", "실무 적용 사례",
]

errors: list[str] = []
warns: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"  [ERROR] {where}\n          {msg}")


def warn(where: str, msg: str) -> None:
    warns.append(f"  [WARN ] {where}\n          {msg}")


def strip_code_fences(text: str) -> str:
    """```로 감싼 블록을 지운다 (본문 규칙 검사에서 코드 내용을 제외하기 위해)."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


# ─────────────────────────────────────────────────────────────
# 노트(.md) 검사
# ─────────────────────────────────────────────────────────────
def check_note(md: Path) -> None:
    rel = md.relative_to(ROOT).as_posix()
    text = md.read_text(encoding="utf-8")
    body = strip_code_fences(text)

    # 1) 파일명 == 폴더명  (Obsidian 빠른 전환에서 구분하기 위한 규칙)
    if md.stem != md.parent.name:
        err(rel, f"파일명이 폴더명과 다르다 (폴더 '{md.parent.name}' / 파일 '{md.stem}')")

    # 2) 16개 섹션이 순서대로 있는지
    found = re.findall(r"^## \d+\.\s*(.+?)\s*$", text, flags=re.MULTILINE)
    missing = [s for s in SECTIONS if s not in found]
    if missing:
        warn(rel, f"빠진 섹션: {', '.join(missing)}")
    else:
        order = [found.index(s) for s in SECTIONS]
        if order != sorted(order):
            warn(rel, "섹션 순서가 표준 순서와 다르다")

    # 3) 번호 목록 하위 불릿은 반드시 4칸 들여쓰기
    #    3칸이면 Python-Markdown이 순서 목록의 하위 항목으로 인식하지 못한다.
    for i, line in enumerate(body.split("\n"), start=1):
        if re.match(r"^ {1,3}\* ", line):
            err(rel, f"{i}행: 하위 불릿 들여쓰기가 4칸 미만이다 → mkdocs에서 목록이 끊긴다\n"
                     f"          {line.strip()[:60]}")

    # 4) `답변 구조` 8개 항목이 고정 순서로 있는지
    m = re.search(r"^### 답변 구조\s*$(.*?)^---", text, flags=re.MULTILINE | re.DOTALL)
    if not m:
        if "## 12. 면접 답변" in text:
            err(rel, "`### 답변 구조` 절이 없다")
    else:
        # 불릿(`* **정의**`)과 번호 목록(`1. **정의**`) 양쪽을 인정한다.
        # 노트가 번호 목록으로 바뀌었는데 검사기가 불릿만 보고 전부 오류로 잡던 문제.
        parts = re.findall(r"^(?:\*|\d+\.)\s+\*\*(.+?)\*\*",
                           m.group(1), flags=re.MULTILINE)
        if parts != ANSWER_PARTS:
            err(rel, f"`답변 구조` 항목이 규칙과 다르다\n"
                     f"          기대: {' → '.join(ANSWER_PARTS)}\n"
                     f"          실제: {' → '.join(parts) if parts else '(없음)'}")

    # 5) 코드 블록에 언어 태그가 있는지
    for fence in re.findall(r"^```(\w*)", text, flags=re.MULTILINE)[::2]:
        if fence == "":
            warn(rel, "언어 태그가 없는 코드 블록이 있다 (```java, ```text 등을 붙인다)")
            break

    # 6) 참조한 이미지가 같은 폴더에 실제로 있는지 + 캡션이 붙었는지
    for img in re.finditer(r"^!\[(.*?)\]\((.+?)\)\s*$", text, flags=re.MULTILINE):
        alt, src = img.group(1), img.group(2)
        if src.startswith(("http://", "https://")):
            err(rel, f"외부 이미지 참조는 금지다: {src}")
            continue
        if not (md.parent / src).exists():
            err(rel, f"이미지 파일이 없다: {src}")
        if not alt.strip():
            warn(rel, f"이미지에 설명(alt)이 없다: {src}")
        after = text[img.end():].lstrip("\n").split("\n", 1)[0]
        if not (after.startswith("*") and after.endswith("*")):
            warn(rel, f"이미지 아래 이탤릭 캡션이 없다: {src}")


# ─────────────────────────────────────────────────────────────
# 도식(.svg) 검사
# ─────────────────────────────────────────────────────────────
def check_svg(svg: Path) -> None:
    rel = svg.relative_to(ROOT).as_posix()
    raw = svg.read_text(encoding="utf-8")

    # 1) XML로 파싱되는지 (이스케이프 안 된 & 가 가장 흔한 원인)
    try:
        ET.fromstring(raw)
    except ET.ParseError as e:
        hint = ""
        if re.search(r"&(?!(amp|lt|gt|quot|apos|#)\w*;)", raw):
            hint = "  ← 이스케이프 안 된 '&' 가 있다. '&amp;' 로 바꾼다."
        err(rel, f"XML 파싱 실패: {e}{hint}")
        return

    # 2) 외부 리소스 참조 금지 (오프라인·GitHub Pages 양쪽에서 깨지지 않게)
    if re.search(r'(href|src|url)\s*=?\s*\(?["\']?https?://', raw):
        err(rel, "외부 리소스를 참조한다 (폰트·이미지는 인라인이어야 한다)")

    # 3) 시스템 폰트를 쓰는지
    if "font-family" not in raw:
        warn(rel, "font-family 지정이 없다")
    elif "Malgun Gothic" not in raw:
        warn(rel, "한글 폰트 폴백('Malgun Gothic')이 없다 — Windows에서 깨질 수 있다")

    # 4) 밝은 카드 배경을 쓰는지 (다크 테마에서도 안정적으로 보이게)
    if "#fcfcfb" not in raw:
        warn(rel, "카드 배경(#fcfcfb)이 없다 — 다크 테마에서 글자가 안 보일 수 있다")

    # 5) viewBox 가 있는지 (반응형 축소에 필요)
    if "viewBox" not in raw:
        warn(rel, "viewBox가 없다 — 좁은 화면에서 잘릴 수 있다")


# ─────────────────────────────────────────────────────────────
# 등록 여부 검사 (nav / 목차)
# ─────────────────────────────────────────────────────────────
def check_registration(notes: list[Path]) -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    index = (DOCS / "index.md").read_text(encoding="utf-8")

    for md in notes:
        rel_docs = md.relative_to(DOCS).as_posix()
        if rel_docs not in nav:
            err("mkdocs.yml", f"nav에 등록되지 않았다: {rel_docs}")
        if rel_docs not in index:
            err("docs/index.md", f"목차에 링크가 없다: {rel_docs}")


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else None

    notes = sorted(
        p for p in DOCS.glob("*/*/*.md")
        if target is None or p.relative_to(DOCS).parts[0] == target
    )
    svgs = sorted(
        p for p in DOCS.glob("*/*/*.svg")
        if target is None or p.relative_to(DOCS).parts[0] == target
    )

    if not notes:
        print(f"검사할 노트가 없다: {target or 'docs/'}")
        return 1

    for md in notes:
        check_note(md)
    for svg in svgs:
        check_svg(svg)
    check_registration(notes)

    scope = target or "전체"
    print(f"검사 대상: 노트 {len(notes)}개, 도식 {len(svgs)}개  ({scope})\n")

    if warns:
        print(f"── 경고 {len(warns)}건 ──")
        print("\n".join(warns), "\n")
    if errors:
        print(f"── 오류 {len(errors)}건 ──")
        print("\n".join(errors))
        print(f"\n실패: 오류 {len(errors)}건을 고쳐야 한다.")
        return 1

    print("통과: 규칙 위반 없음.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
