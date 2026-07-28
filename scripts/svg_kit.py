"""노트 도식용 SVG 생성 키트.

저장소의 도식은 모두 이 키트로 그린다. 스타일을 한곳에 모아 두면
노트마다 색·폰트·여백이 달라지지 않는다.

사용법 — 임시 스크립트를 스크래치패드에 만들고 결과 .svg만 노트 폴더에 저장한다.

    import sys
    sys.path.insert(0, r"c:\\Work\\Git\\Study Note\\scripts")
    from svg_kit import *

    s = head(760, 300, "제목", "한 줄 부제")
    s += cell(40, 100, 60, 36, "A", stroke=BLUE)
    s += arrow(110, 118, 160, 118, color=ORANGE, marker="aho")
    s += txt(40, 200, "설명", fill=MUTED)
    save(r"docs/02-자료구조/Array/foo.svg", s)

규칙
  - 텍스트에 &, <, > 를 넣을 때는 esc()를 쓴다. 안 그러면 XML 파싱이 깨진다.
  - 색은 아래 상수만 쓰고, 색만으로 구분하지 말고 라벨을 함께 붙인다 (색약 대응).
  - 만든 뒤 scripts/preview_svg.py 로 PNG를 뽑아 반드시 눈으로 확인한다.
"""

from pathlib import Path

FONT = "system-ui, -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif"
MONO = "ui-monospace, Consolas, monospace"

# 계열별 고정 색 순서 — 새 도식도 이 순서대로 배정한다
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GREEN = "#008300"
PURPLE = "#7a3ba7"
RED = "#e34948"

GRAY = "#898781"     # 보조선·화살표
INK = "#0b0b0b"      # 본문 강조 텍스트
MUTED = "#52514e"    # 설명 텍스트
CARD = "#fcfcfb"     # 카드 배경 (다크/라이트 양쪽에서 안정적)
BORDER = "rgba(11,11,11,0.10)"

# arrow(marker=...) 에 넣을 수 있는 화살촉 — 선 색과 맞춰 쓴다
MARKERS = {GRAY: "ah", BLUE: "ahb", RED: "ahr", ORANGE: "aho", GREEN: "ahg", PURPLE: "ahp"}


def esc(s: object) -> str:
    """XML 특수문자를 이스케이프한다. 텍스트를 넣을 때 반드시 거친다."""
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;"))


def head(w: int, h: int, title: str, subtitle: str = "") -> str:
    """카드 배경 + 제목 + 부제 + 화살촉 정의까지 담은 SVG 머리말."""
    defs = "".join(
        f'<marker id="{mid}" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">'
        f'<path d="M0,0 L6,3 L0,6 Z" fill="{color}"/></marker>'
        for color, mid in MARKERS.items()
    )
    out = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" font-family="{FONT}">\n'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" '
        f'fill="{CARD}" stroke="{BORDER}"/>\n'
        f'<defs>{defs}</defs>\n'
        f'<text x="34" y="40" font-size="20" font-weight="700" fill="{INK}">{esc(title)}</text>\n'
    )
    if subtitle:
        out += f'<text x="34" y="61" font-size="12.5" fill="{MUTED}">{esc(subtitle)}</text>\n'
    return out


def txt(x, y, s, size=12.5, fill=MUTED, weight="400", anchor="start", mono=False) -> str:
    extra = f' font-family="{MONO}"' if mono else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{extra}>{esc(s)}</text>\n')


def cell(x, y, w, h, label="", fill="#ffffff", stroke=GRAY, tcolor=INK,
         size=13, weight="600", dash=None) -> str:
    """배열 칸·노드 상자 하나."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="1.3"{d}/>\n')
    if label != "":
        out += txt(x + w / 2, y + h / 2 + size * 0.36, label,
                   size=size, fill=tcolor, weight=weight, anchor="middle")
    return out


def circle(x, y, label, fill_color, r=20, tcolor="#ffffff", size=13.5) -> str:
    """트리 노드처럼 원형으로 그릴 때."""
    out = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill_color}" stroke="{fill_color}"/>\n'
    out += txt(x, y + size * 0.36, label, size=size, fill=tcolor, weight="700", anchor="middle")
    return out


def arrow(x1, y1, x2, y2, color=GRAY, marker=None, width=1.4, dash=None) -> str:
    """화살표. marker를 생략하면 선 색에 맞는 화살촉을 자동으로 고른다."""
    if marker is None:
        marker = MARKERS.get(color, "ah")
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{width}" marker-end="url(#{marker})"{d}/>\n')


def line(x1, y1, x2, y2, color=GRAY, width=1.4, dash=None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}"{d}/>\n')


def band(x, y, w, h, color, label="", sub="") -> str:
    """옅은 배경으로 묶은 구역 + 제목/부제."""
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{color}" '
           f'fill-opacity="0.07" stroke="{color}" stroke-opacity="0.30" stroke-width="1.2"/>\n')
    if label:
        out += txt(x + 14, y + 21, label, size=13, fill=color, weight="700")
    if sub:
        out += txt(x + 14, y + 38, sub, size=11.5, fill=MUTED)
    return out


def save(path, body: str) -> Path:
    """SVG를 저장하고, 저장 직후 XML로 파싱해 유효성을 확인한다."""
    import xml.etree.ElementTree as ET

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = body + "</svg>"
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(
            f"{p}: XML이 유효하지 않다 ({e}). "
            f"텍스트에 &, <, > 를 직접 넣었다면 esc()를 거쳐야 한다."
        ) from e
    p.write_text(content, encoding="utf-8")
    print("saved:", p)
    return p
