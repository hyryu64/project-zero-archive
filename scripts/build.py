#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GH 무한상상 아이디어 특별공모 「프로젝트 제로」 응모작 아카이브
정적 사이트 생성 스크립트

사용법:
    python3 scripts/build.py

무엇을 하나요?
  1) data/items.json 을 읽어 content/ 아래에 카테고리별 폴더를 만듭니다.
     (이미 폴더/파일이 있으면 건드리지 않습니다 — 실제 업로드한 이미지·
      응모신청서·유사 응모작 파일을 안전하게 보존합니다.)
  2) 각 우수작 폴더 안에서 이미지·응모신청서·유사 응모작 파일을 자동으로
     찾아서 index.html / items/*.html / categories/*.html 을 다시 생성합니다.

즉, 이 스크립트는 "실제 파일을 폴더에 넣고 다시 실행"하는 것을 전제로
설계되어 있습니다. 파일을 새로 추가했다면 이 스크립트를 다시 실행하세요.
"""
import json
import re
import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "items.json").read_text(encoding="utf-8"))

MEANS = {m["key"]: m for m in DATA["axes"]["means"]}
DOMAINS = {d["key"]: d for d in DATA["axes"]["domains"]}
ITEMS = DATA["items"]
SITE = DATA["site"]

IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
DOC_EXTS = [".pdf", ".hwp", ".hwpx", ".doc", ".docx"]
PLACEHOLDER_IMAGE_NAME = "image.svg"
PLACEHOLDER_DOC_NAME = "응모신청서_업로드필요.txt"

NAV_ORDER = [("AI", "AI"), ("digital", "디지털·기술"), ("system", "제도·방식")]
DOM_ORDER = [("work", "업무혁신"), ("biz", "사업혁신"), ("service", "서비스혁신")]


def slugify(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[·:/\\?!,\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text


def item_folder_name(item):
    return f"{item['id']}_{slugify(item['title'])}"


def content_dir(item) -> Path:
    domain_label = DOMAINS[item["domain"]]["label"]
    means_label = MEANS[item["means"]]["label"]
    return ROOT / "content" / domain_label / means_label / item_folder_name(item)


def ensure_placeholders(item):
    d = content_dir(item)
    similar = d / "similar"
    d.mkdir(parents=True, exist_ok=True)
    similar.mkdir(parents=True, exist_ok=True)

    has_image = any((d / f"image{ext}").exists() for ext in IMAGE_EXTS)
    if not has_image and not (d / PLACEHOLDER_IMAGE_NAME).exists():
        (d / PLACEHOLDER_IMAGE_NAME).write_text(
            _placeholder_svg(item["title"]), encoding="utf-8"
        )

    has_doc = any(p.suffix.lower() in DOC_EXTS for p in d.glob("*") if p.is_file())
    if not has_doc and not (d / PLACEHOLDER_DOC_NAME).exists():
        (d / PLACEHOLDER_DOC_NAME).write_text(
            "이 파일을 지우고, 같은 폴더에 실제 응모신청서 파일(PDF 권장)을 넣어주세요.\n"
            "예) 응모신청서.pdf\n",
            encoding="utf-8",
        )

    readme = similar / "README.txt"
    if not readme.exists() and not any(similar.glob("*")):
        readme.write_text(
            "이 폴더에 이 우수작과 비슷한 다른 응모작 파일(이미지, PDF, 한글파일 등)을 "
            "넣어두면 상세 페이지의 '유사 응모작' 목록에 자동으로 표시됩니다.\n"
            "이 안내 파일(README.txt)은 지워도 됩니다.\n",
            encoding="utf-8",
        )


def _placeholder_svg(title):
    safe = html.escape(title)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
  <rect width="800" height="450" fill="#e4eaee"/>
  <g fill="none" stroke="#c7d2da" stroke-width="1">
    {''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="450"/>' for x in range(0, 800, 40))}
    {''.join(f'<line x1="0" y1="{y}" x2="800" y2="{y}"/>' for y in range(0, 450, 40))}
  </g>
  <rect x="0" y="0" width="800" height="450" fill="none" stroke="#9fb0be" stroke-width="2"/>
  <text x="400" y="215" text-anchor="middle" font-family="monospace" font-size="16" fill="#5b6b7c">이미지를 이 폴더에 추가하세요 (image.jpg)</text>
  <text x="400" y="240" text-anchor="middle" font-family="monospace" font-size="13" fill="#5b6b7c">{safe}</text>
</svg>"""


def find_image(item):
    d = content_dir(item)
    for ext in IMAGE_EXTS:
        p = d / f"image{ext}"
        if p.exists():
            return p, False
    return d / PLACEHOLDER_IMAGE_NAME, True


def find_doc(item):
    d = content_dir(item)
    for p in sorted(d.glob("*")):
        if p.is_file() and p.suffix.lower() in DOC_EXTS:
            return p
    return None


def find_similar(item):
    d = content_dir(item) / "similar"
    out = []
    for p in sorted(d.glob("*")):
        if p.is_file() and p.name != "README.txt":
            out.append(p)
    return out


def rel_from_root(p: Path) -> str:
    return "/".join(quote(part) for part in p.relative_to(ROOT).parts)


# ---------------------------------------------------------------- HTML shell

def page(title, breadcrumb_html, body_html, depth=0, extra_head=""):
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}assets/css/style.css">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="site-header__inner">
    <p class="site-header__eyebrow">GH 무한상상 아이디어 특별공모 · PROJECT ZERO</p>
    <h1 class="site-header__title"><a href="{prefix}index.html">{html.escape(SITE['title'])}</a></h1>
    <div class="site-header__meta">
      <span>전체 응모작 <b>{SITE['totalSubmissions']}건</b></span>
      <span>수록 우수작 <b>{len(ITEMS)}건</b></span>
    </div>
    {breadcrumb_html}
  </div>
</header>
<main class="wrap">
{body_html}
</main>
<footer class="site-footer">
  <div class="wrap">GH 무한상상 아이디어 특별공모 「프로젝트 제로」 응모작 아카이브</div>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- index.html

def build_index():
    counts = {}
    for it in ITEMS:
        counts[(it["means"], it["domain"])] = counts.get((it["means"], it["domain"]), 0) + 1

    header_cells = "".join(f'<th scope="col">{DOMAINS[k]["label"]}</th>' for k, _ in DOM_ORDER)

    rows = []
    for mk, mlabel in NAV_ORDER:
        cells = []
        for dk, dlabel in DOM_ORDER:
            n = counts.get((mk, dk), 0)
            href = f"categories/{mk}-{dk}.html"
            if n > 0:
                cells.append(
                    f'<td class="cell"><a class="cell-link" href="{href}">'
                    f'<span class="cell-count">{n}<sup>건</sup></span>'
                    f'<span class="cell-hint">{MEANS[mk]["label"]} · {dlabel}</span>'
                    f"</a></td>"
                )
            else:
                cells.append(
                    f'<td class="cell"><a class="cell-link is-empty" href="{href}">'
                    f'<span class="cell-count">0<sup>건</sup></span>'
                    f'<span class="cell-hint">등록된 우수작 없음</span>'
                    f"</a></td>"
                )
        rows.append(
            f'<tr><th scope="row" class="axis-label">{MEANS[mk]["label"]}</th>{"".join(cells)}</tr>'
        )

    legend_means = "".join(
        f'<div class="legend-item"><dt>{m["label"]}</dt><dd>{html.escape(m["desc"])}</dd></div>'
        for _, m in MEANS.items()
    )
    legend_domains = "".join(
        f'<div class="legend-item"><dt>{d["label"]}</dt><dd>{html.escape(d["desc"])}</dd></div>'
        for _, d in DOMAINS.items()
    )

    body = f"""
<div class="intro">
  <p>「프로젝트 제로」에 접수된 응모작 {SITE['totalSubmissions']}건 가운데, 심사를 통해 선정된 우수작 {len(ITEMS)}건을
  <b>혁신 수단</b>과 <b>혁신 적용영역</b> 두 기준으로 나눈 표입니다. 칸을 선택하면 해당 우수작 목록으로 이동합니다.</p>
</div>

<h2 class="section-title">우수작 매트릭스</h2>
<div class="matrix-scroll">
<table class="matrix">
  <caption>행 = 혁신 수단, 열 = 혁신 적용영역</caption>
  <thead>
    <tr><th scope="col">&nbsp;</th>{header_cells}</tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
</div>

<details class="legend">
  <summary>분류 판단기준 보기</summary>
  <div class="legend-body">
    <div class="legend-group">
      <h3>혁신 수단</h3>
      {legend_means}
    </div>
    <div class="legend-group">
      <h3>혁신 적용영역</h3>
      {legend_domains}
    </div>
  </div>
</details>
"""
    (ROOT / "index.html").write_text(page(SITE["title"], "", body, depth=0), encoding="utf-8")


# ------------------------------------------------------------- category page

def build_category(mk, dk):
    mlabel, dlabel = MEANS[mk]["label"], DOMAINS[dk]["label"]
    items = [it for it in ITEMS if it["means"] == mk and it["domain"] == dk]

    tabs = []
    for k2, l2 in NAV_ORDER:
        for d2, l2d in DOM_ORDER:
            cur = " is-current" if (k2, d2) == (mk, dk) else ""
            n = len([it for it in ITEMS if it["means"] == k2 and it["domain"] == d2])
            tabs.append(f'<a class="{cur.strip()}" href="{k2}-{d2}.html">{l2} · {l2d} ({n})</a>')

    if items:
        cards = []
        for it in items:
            img_path, _ = find_image(it)
            img_rel = "../" + rel_from_root(img_path)
            cards.append(f"""
<a class="card" href="../items/{it['id']}.html">
  <div class="card__thumb"><img src="{img_rel}" alt="{html.escape(it['title'])} 대표 이미지" loading="lazy"></div>
  <div class="card__body">
    <p class="card__id">No.{it['id']}</p>
    <h3 class="card__title">{html.escape(it['title'])}</h3>
  </div>
</a>""")
        grid = f'<div class="card-grid">{"".join(cards)}</div>'
    else:
        grid = '<div class="empty-state">이 조합에 해당하는 우수작이 아직 없습니다.</div>'

    breadcrumb = f'<p class="breadcrumb"><a href="../index.html">전체 매트릭스</a> / {mlabel} · {dlabel}</p>'
    body = f"""
<h2 class="section-title">{mlabel} · {dlabel} <span style="color:var(--muted); font-weight:400;">({len(items)}건)</span></h2>
<div class="cat-tabs">{''.join(tabs)}</div>
{grid}
"""
    fname = ROOT / "categories" / f"{mk}-{dk}.html"
    fname.write_text(page(f"{mlabel} · {dlabel} — {SITE['title']}", breadcrumb, body, depth=1), encoding="utf-8")


# ------------------------------------------------------------------ item page

def build_item(item, idx):
    mlabel = MEANS[item["means"]]["label"]
    dlabel = DOMAINS[item["domain"]]["label"]
    img_path, is_placeholder = find_image(item)
    img_rel = "../" + rel_from_root(img_path)
    doc_path = find_doc(item)
    similar_files = find_similar(item)

    if doc_path:
        ext = doc_path.suffix.lower().lstrip(".")
        doc_rel = "../" + rel_from_root(doc_path)
        doc_btn = f'<a class="btn btn--primary" href="{doc_rel}" download>응모신청서 다운로드 <span style="opacity:.7">.{ext}</span></a>'
    else:
        doc_btn = '<span class="btn btn--disabled">응모신청서 업로드 예정</span>'

    if similar_files:
        rows = []
        for p in similar_files:
            rel = "../" + rel_from_root(p)
            ext = p.suffix.lower().lstrip(".") or "file"
            rows.append(
                f'<li><a href="{rel}" download>{html.escape(p.name)}</a>'
                f'<span class="file-ext">.{ext}</span></li>'
            )
        similar_html = f'<ul class="file-list">{"".join(rows)}</ul>'
    else:
        similar_html = '<p class="muted-note">등록된 유사 응모작 첨부파일이 아직 없습니다. content 폴더의 해당 우수작 하위 "similar" 폴더에 파일을 넣고 build.py를 다시 실행하면 이 자리에 표시됩니다.</p>'

    prev_item = ITEMS[idx - 1] if idx > 0 else None
    next_item = ITEMS[idx + 1] if idx < len(ITEMS) - 1 else None
    prev_html = f'<a href="{prev_item["id"]}.html">← No.{prev_item["id"]} {html.escape(prev_item["title"])}</a>' if prev_item else '<span class="disabled">← 이전 없음</span>'
    next_html = f'<a href="{next_item["id"]}.html">No.{next_item["id"]} {html.escape(next_item["title"])} →</a>' if next_item else '<span class="disabled">다음 없음 →</span>'

    figure_html = (
        f'<div class="placeholder"><img src="{img_rel}" alt="{html.escape(item["title"])} 이미지 플레이스홀더" style="max-width:60%;"></div>'
        if is_placeholder else
        f'<img src="{img_rel}" alt="{html.escape(item["title"])} 대표 이미지">'
    )

    breadcrumb = (
        f'<p class="breadcrumb"><a href="../index.html">전체 매트릭스</a> / '
        f'<a href="../categories/{item["means"]}-{item["domain"]}.html">{mlabel} · {dlabel}</a> / No.{item["id"]}</p>'
    )

    body = f"""
<article class="sheet">
  <div class="sheet__figure">{figure_html}</div>
  <div class="titleblock">
    <div class="tb-num"><span class="tb-label">도면번호</span><span class="tb-value">No.{item['id']}</span></div>
    <div class="tb-title-cell"><span class="tb-label">우수작명</span><span class="tb-title">{html.escape(item['title'])}</span></div>
    <div><span class="tb-label">혁신 수단</span><span class="tb-value">{mlabel}</span></div>
    <div><span class="tb-label">적용 영역</span><span class="tb-value">{dlabel}</span></div>
  </div>
  <div class="sheet__actions">
    {doc_btn}
  </div>
  <div class="sheet__section">
    <h2>유사 응모작</h2>
    {similar_html}
  </div>
  <div class="sheet__section">
    <h2>의견 · 추천</h2>
    <p class="comments-hint">아래 댓글창에서 누구나 의견을 남기고, 상단 👍 반응으로 이 우수작을 추천할 수 있습니다.</p>
    <div id="giscus-container"></div>
  </div>
</article>
<nav class="pager">{prev_html}{next_html}</nav>
"""
    extra_head = (
        f'<script src="../assets/js/giscus-config.js"></script>\n'
        f'<script src="../assets/js/comments.js" defer></script>'
    )
    fname = ROOT / "items" / f"{item['id']}.html"
    fname.write_text(
        page(f"No.{item['id']} {item['title']} — {SITE['title']}", breadcrumb, body, depth=1, extra_head=extra_head),
        encoding="utf-8",
    )


def main():
    for it in ITEMS:
        ensure_placeholders(it)

    build_index()
    for mk, _ in NAV_ORDER:
        for dk, _ in DOM_ORDER:
            build_category(mk, dk)
    for idx, it in enumerate(ITEMS):
        build_item(it, idx)

    print(f"생성 완료: index.html, categories/*.html ({len(NAV_ORDER)*len(DOM_ORDER)}개), items/*.html ({len(ITEMS)}개)")


if __name__ == "__main__":
    main()
