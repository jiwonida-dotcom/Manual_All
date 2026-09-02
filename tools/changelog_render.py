#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/changelog.json -> index.html 「변경이력」 표 재생성.

    python tools/changelog_render.py

index.html 의 CHANGELOG:START ~ CHANGELOG:END 마커 사이만 교체하고
docs/index.html 로 동일 사본을 복사한다.
네트워크·Airtable 토큰 불필요 — 순수 로컬 렌더링.
"""
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "changelog.json"
PAGE = ROOT / "index.html"
MIRROR = ROOT / "docs" / "index.html"

START = "<!-- CHANGELOG:START -->"
END = "<!-- CHANGELOG:END -->"
IND = " " * 14

CHIP = {
    "제정": '<span class="vchip s" style="background:var(--indigo-100); '
            'color:var(--indigo); border-color:transparent">제정</span>',
    "개정": '<span class="vchip n s">개정</span>',
    "폐지": '<span class="vchip d s">폐지</span>',
}


def die(msg):
    print("[ERROR] " + msg, file=sys.stderr)
    raise SystemExit(1)


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def render_row(r):
    kind = (r.get("kind") or "").strip()
    chip = CHIP.get(kind) or '<span class="vchip s">%s</span>' % esc(kind)
    out = [
        '%s<tr data-at="%s" data-by="%s">' % (IND, esc(r.get("at")), esc(r.get("by"))),
        '%s  <td class="vr">%s</td>' % (IND, esc(r.get("version"))),
        '%s  <td class="dt">%s</td>' % (IND, esc(r.get("date"))),
        '%s  <td>%s</td>' % (IND, chip),
        '%s  <td>' % IND,
        '%s    <span class="np">%s</span>' % (IND, esc(r.get("summary"))),
    ]
    for note in r.get("notes") or []:
        note = str(note).strip().lstrip("※").strip()
        if note:
            out.append('%s    <span class="mm">※ %s</span>' % (IND, esc(note)))
    out += ['%s  </td>' % IND, '%s</tr>' % IND]
    return "\n".join(out)


def main():
    if not SRC.exists():
        die("%s 없음 — 먼저 tools/changelog_fetch.py 실행" % SRC)

    data = json.loads(SRC.read_text(encoding="utf-8"))
    rows = [r for r in data.get("rows", []) if r.get("version") and r.get("summary")]
    if not rows:
        die("게시 대상 레코드 0건 — 빈 표로 덮어쓰지 않고 중단")

    # 작성일시 내림차순 — 최상단 행이 「최근 업데이트」 배지에 노출됨
    rows.sort(key=lambda r: (r.get("at") or "", r.get("date") or ""), reverse=True)

    page = PAGE.read_text(encoding="utf-8")
    i, j = page.find(START), page.find(END)
    if i < 0 or j < 0 or j < i:
        die("index.html 에 CHANGELOG 마커 없음")

    body = "\n".join(render_row(r) for r in rows)
    updated = page[: i + len(START)] + "\n" + body + "\n" + IND + page[j:]

    if updated == page:
        print("변경 없음 — %d건" % len(rows))
    else:
        PAGE.write_text(updated, encoding="utf-8")
        print("index.html 갱신 — %d건 (최신 %s %s)" % (len(rows), rows[0]["version"], rows[0].get("at", "")))

    MIRROR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PAGE, MIRROR)
    print("docs/index.html 동기화 완료")


if __name__ == "__main__":
    main()
