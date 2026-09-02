#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Airtable 「변경이력」 테이블 -> data/changelog.json

    set AIRTABLE_PAT=patXXXXXXXX      (Windows CMD)
    python tools/changelog_fetch.py

토큰은 환경변수로만 전달 — 저장소·HTML 에 기록하지 않는다.
PAT 발급: Airtable > Builder hub > Personal access tokens
  스코프 data.records:read / 대상 base = Manual_All
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_ID = "appIDWrezBNzJXqhv"
TABLE_ID = "tbl8AFUUVhgwC27Id"
KST = timezone(timedelta(hours=9))

OUT = Path(__file__).resolve().parent.parent / "data" / "changelog.json"

F = {
    "version": "버전",
    "date": "적용일",
    "at": "작성일시",
    "by": "작성자",
    "kind": "구분",
    "summary": "변경내용",
    "notes": "단서",
    "publish": "게시",
}


def die(msg):
    print("[ERROR] " + msg, file=sys.stderr)
    raise SystemExit(1)


def fetch(pat):
    records, offset = [], None
    while True:
        params = {"pageSize": "100"}
        if offset:
            params["offset"] = offset
        url = "https://api.airtable.com/v0/%s/%s?%s" % (
            BASE_ID, TABLE_ID, urllib.parse.urlencode(params))
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + pat})
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                payload = json.load(res)
        except urllib.error.HTTPError as e:
            die("Airtable %s — %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
        records += payload.get("records", [])
        offset = payload.get("offset")
        if not offset:
            return records


def to_kst(value):
    """2026-09-01T08:20:00.000Z -> 2026-09-01 17:20"""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return dt.astimezone(KST).strftime("%Y-%m-%d %H:%M")


def main():
    pat = os.environ.get("AIRTABLE_PAT", "").strip()
    if not pat:
        die("환경변수 AIRTABLE_PAT 미설정")

    rows = []
    for rec in fetch(pat):
        f = rec.get("fields", {})
        if not f.get(F["publish"]):
            continue
        notes = [n.strip().lstrip("※").strip()
                 for n in str(f.get(F["notes"], "")).splitlines()]
        rows.append({
            "version": f.get(F["version"], ""),
            "date": f.get(F["date"], ""),
            "at": to_kst(f.get(F["at"], "")),
            "by": f.get(F["by"], ""),
            "kind": f.get(F["kind"], ""),
            "summary": f.get(F["summary"], ""),
            "notes": [n for n in notes if n],
        })

    if not rows:
        die("게시 체크된 레코드 0건 — 기존 data/changelog.json 유지")

    rows.sort(key=lambda r: (r["at"], r["date"]), reverse=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "generated": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S%z"),
        "source": {"baseId": BASE_ID, "tableId": TABLE_ID, "table": "변경이력"},
        "rows": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("data/changelog.json — %d건 저장 (최신 %s)" % (len(rows), rows[0]["version"]))


if __name__ == "__main__":
    main()
