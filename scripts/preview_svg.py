"""SVG 파일을 PNG로 렌더링해서 눈으로 확인하기 위한 헬퍼.

사용법:
    python scripts/preview_svg.py <svg경로> [출력png경로]

출력을 지정하지 않으면 "<svg파일명>.preview.png"로 저장한다.
(.gitignore가 *.preview.png를 제외하므로 확인용 파일이 실수로 커밋되지 않는다.)
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> str:
    for name in ("google-chrome", "chromium", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    raise SystemExit("Chrome/Edge를 찾을 수 없습니다. 경로를 CHROME_CANDIDATES에 추가하세요.")


def svg_size(svg_path: Path) -> tuple[int, int]:
    text = svg_path.read_text(encoding="utf-8")
    m = re.search(r'viewBox="[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', text)
    if m:
        return int(float(m.group(1))), int(float(m.group(2)))
    w = re.search(r'width="(\d+)"', text)
    h = re.search(r'height="(\d+)"', text)
    if w and h:
        return int(w.group(1)), int(h.group(1))
    return 800, 600


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    svg_path = Path(sys.argv[1]).resolve()
    if not svg_path.exists():
        raise SystemExit(f"파일이 없습니다: {svg_path}")

    out_path = (
        Path(sys.argv[2]).resolve()
        if len(sys.argv) > 2
        else svg_path.with_suffix("").with_suffix(".preview.png")
    )

    width, height = svg_size(svg_path)
    # 카드 여백을 감안해 약간 여유 있게 창 크기를 잡는다.
    win_w, win_h = width + 20, height + 20

    browser = find_browser()
    file_url = "file:///" + str(svg_path).replace("\\", "/")

    subprocess.run(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--force-device-scale-factor=2",
            "--hide-scrollbars",
            f"--screenshot={out_path}",
            f"--window-size={win_w},{win_h}",
            file_url,
        ],
        check=True,
    )
    print(f"저장됨: {out_path}")


if __name__ == "__main__":
    main()
