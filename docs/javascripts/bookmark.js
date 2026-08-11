/*
 * 책갈피(이어읽기)
 *
 * 읽던 위치에 책갈피를 꽂아 두고, 나중에 어느 페이지에서든 그 자리로 돌아온다.
 *
 * GitHub Pages는 정적 호스팅이라 서버에 저장할 곳이 없다. 그래서 브라우저의
 * localStorage에 저장한다 — 쿠키와 달리 요청마다 실려 나가지 않고, 만료를
 * 관리할 필요도 없다. 대신 저장 위치가 브라우저이므로 기기나 브라우저가
 * 바뀌면 책갈피는 따라가지 않는다(시크릿 창도 마찬가지).
 *
 * 테마의 navigation.instant(SPA 방식 이동) 때문에 페이지가 바뀌어도 이 스크립트는
 * 다시 실행되지 않는다. 그래서 위젯은 body에 한 번만 만들고, Material이 문서를
 * 갈아끼울 때마다 내보내는 document$ 신호에 맞춰 상태만 다시 그린다.
 */
(function () {
  "use strict";

  var KEY = "study-note:bookmark";           // localStorage — 책갈피 본체
  var PENDING = "study-note:bookmark-jump";  // sessionStorage — 이동 직후 스크롤 복원용
  var HEADER_OFFSET = 100;                   // 상단 고정 헤더에 가려지는 높이(px)

  var ICON_FILLED = "M17,3H7A2,2 0 0,0 5,5V21L12,18L19,21V5C19,3.89 18.1,3 17,3Z";
  var ICON_OUTLINE = "M17,18L12,15.82L7,18V5H17M17,3H7A2,2 0 0,0 5,5V21L12,18L19,21V5C19,3.89 18.1,3 17,3Z";
  var ICON_CLOSE = "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";

  // ── 저장소 ────────────────────────────────────────────────────────────────
  // 저장소 접근은 브라우저 설정(쿠키·사이트 데이터 차단)에 따라 던질 수 있어서
  // 전부 감싼다. 실패하면 책갈피만 동작하지 않고 문서 읽기는 그대로다.

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "null");
    } catch (e) {
      return null;
    }
  }

  function save(value) {
    try {
      localStorage.setItem(KEY, JSON.stringify(value));
      return true;
    } catch (e) {
      return false;
    }
  }

  function remove() {
    try {
      localStorage.removeItem(KEY);
    } catch (e) {
      /* 무시 */
    }
  }

  // ── 현재 읽고 있는 위치 ───────────────────────────────────────────────────

  function article() {
    return document.querySelector("article.md-content__inner") || document.querySelector("article");
  }

  /** 화면 상단을 이미 지나간 마지막 제목 = 지금 읽고 있는 절 */
  function currentHeading() {
    var root = article();
    if (!root) return null;
    var headings = root.querySelectorAll("h1[id], h2[id], h3[id], h4[id]");
    var found = null;
    for (var i = 0; i < headings.length; i++) {
      if (headings[i].getBoundingClientRect().top > HEADER_OFFSET) break;
      found = headings[i];
    }
    return found;
  }

  /** 제목 텍스트 — Material이 붙이는 퍼머링크(¶)는 빼고 읽는다 */
  function headingText(el) {
    if (!el) return "";
    var copy = el.cloneNode(true);
    var link = copy.querySelector(".headerlink");
    if (link) link.remove();
    return copy.textContent.trim();
  }

  function pageTitle() {
    var root = article();
    var h1 = root && root.querySelector("h1");
    return headingText(h1) || document.title.split(/\s+[-–—]\s+/)[0].trim() || "이 문서";
  }

  // ── 위젯 ──────────────────────────────────────────────────────────────────

  var ui = null;

  function icon(path, size) {
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", size);
    svg.setAttribute("height", size);
    svg.setAttribute("aria-hidden", "true");
    var p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("fill", "currentColor");
    p.setAttribute("d", path);
    svg.appendChild(p);
    return svg;
  }

  function buildUI() {
    var root = document.createElement("div");
    root.className = "bm";

    // 저장해 둔 책갈피로 이동하는 칩. <a>로 두어야 테마의 즉시 이동이 그대로 먹는다.
    var resume = document.createElement("a");
    resume.className = "bm__resume";
    resume.appendChild(icon(ICON_FILLED, 16));
    var label = document.createElement("span");
    label.className = "bm__label";
    resume.appendChild(label);

    var drop = document.createElement("button");
    drop.type = "button";
    drop.className = "bm__drop";
    drop.setAttribute("aria-label", "책갈피 삭제");
    drop.title = "책갈피 삭제";
    drop.appendChild(icon(ICON_CLOSE, 14));

    var chip = document.createElement("div");
    chip.className = "bm__chip";
    chip.appendChild(resume);
    chip.appendChild(drop);

    // 지금 위치에 책갈피를 꽂는 버튼
    var setBtn = document.createElement("button");
    setBtn.type = "button";
    setBtn.className = "bm__set";
    setBtn.setAttribute("aria-label", "이 위치에 책갈피 꽂기");
    setBtn.title = "이 위치에 책갈피 꽂기";
    var setIcon = icon(ICON_OUTLINE, 22);
    setBtn.appendChild(setIcon);

    var toast = document.createElement("div");
    toast.className = "bm__toast";

    root.appendChild(toast);
    root.appendChild(chip);
    root.appendChild(setBtn);
    document.body.appendChild(root);

    ui = {
      root: root,
      chip: chip,
      resume: resume,
      label: label,
      setBtn: setBtn,
      setIcon: setIcon.querySelector("path"),
      toast: toast,
      toastTimer: 0
    };

    setBtn.addEventListener("click", dropBookmark);
    drop.addEventListener("click", function () {
      remove();
      render();
      flash("책갈피를 지웠습니다");
    });
    resume.addEventListener("click", onResumeClick);

    return ui;
  }

  function flash(message) {
    if (!ui) return;
    ui.toast.textContent = message;
    ui.toast.classList.add("bm__toast--on");
    clearTimeout(ui.toastTimer);
    ui.toastTimer = setTimeout(function () {
      ui.toast.classList.remove("bm__toast--on");
    }, 2000);
  }

  // ── 동작 ──────────────────────────────────────────────────────────────────

  function dropBookmark() {
    var heading = currentHeading();
    var title = pageTitle();
    var section = headingText(heading);

    save({
      url: location.pathname,
      hash: heading ? heading.id : "",
      title: title,
      // 문서 맨 위(h1)에 꽂았다면 절 이름을 따로 붙일 게 없다
      section: section && section !== title ? section : "",
      scrollY: Math.round(window.scrollY),
      at: Date.now()
    });

    render();
    flash("여기에 책갈피를 꽂았습니다");
  }

  function onResumeClick(event) {
    var bm = load();
    if (!bm) return;

    // 같은 문서 안이라면 이동 없이 그 자리로 스크롤만 한다
    if (bm.url === location.pathname) {
      event.preventDefault();
      scrollTo(bm.scrollY);
      if (bm.hash) history.replaceState(null, "", "#" + bm.hash);
      return;
    }

    // 다른 문서라면 이동 후에 정확한 위치를 맞추도록 표시만 남긴다.
    // (링크의 #앵커가 절 앞까지는 데려다주고, 나머지 오차를 여기서 보정한다)
    try {
      sessionStorage.setItem(PENDING, JSON.stringify({ url: bm.url, scrollY: bm.scrollY }));
    } catch (e) {
      /* 무시 — 앵커까지만 이동한다 */
    }
  }

  function scrollTo(y) {
    window.scrollTo({ top: y, behavior: "smooth" });
  }

  /** 이동 직후, 남겨둔 표시가 있으면 저장된 높이로 맞춘다 */
  function applyPendingJump() {
    var raw = null;
    try {
      raw = sessionStorage.getItem(PENDING);
      if (raw) sessionStorage.removeItem(PENDING);
    } catch (e) {
      return;
    }
    if (!raw) return;

    var pending;
    try {
      pending = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (!pending || pending.url !== location.pathname) return;

    // 본문이 그려지고 높이가 확정된 뒤라야 좌표가 맞는다
    requestAnimationFrame(function () {
      setTimeout(function () {
        window.scrollTo(0, pending.scrollY);
      }, 80);
    });
  }

  function render() {
    if (!ui) return;
    var bm = load();

    if (!bm) {
      ui.chip.classList.remove("bm__chip--on");
      ui.setIcon.setAttribute("d", ICON_OUTLINE);
      ui.setBtn.title = "이 위치에 책갈피 꽂기";
      return;
    }

    ui.chip.classList.add("bm__chip--on");
    ui.resume.href = bm.url + (bm.hash ? "#" + bm.hash : "");
    ui.label.textContent = bm.section ? bm.title + " · " + bm.section : bm.title;
    ui.resume.title = "책갈피로 이동 — " + ui.label.textContent;

    var here = bm.url === location.pathname;
    ui.setIcon.setAttribute("d", here ? ICON_FILLED : ICON_OUTLINE);
    ui.setBtn.title = here ? "이 위치로 책갈피 옮기기" : "이 위치에 책갈피 꽂기";
  }

  // ── 시작 ──────────────────────────────────────────────────────────────────

  function onDocument() {
    if (!ui) buildUI();
    render();
    applyPendingJump();
  }

  // 다른 탭에서 책갈피를 바꾸면 이 탭에도 반영한다
  window.addEventListener("storage", function (event) {
    if (event.key === KEY) render();
  });

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(onDocument);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onDocument);
  } else {
    onDocument();
  }
})();
