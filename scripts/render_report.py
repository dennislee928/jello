#!/usr/bin/env python3
"""Render a daily report as Markdown. Titles are untrusted and flattened."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def plain(value):
    """Flatten untrusted text so it cannot break Markdown or look executable."""
    text = "".join(char if char.isprintable() else " " for char in str(value))
    for char in ("`", "<", ">", "$"):
        text = text.replace(char, " ")
    return " ".join(text.split())


def _bullet_items(items):
    if not items:
        return ["沒有。"]
    lines = []
    for item in items:
        signals = ", ".join(plain(signal) for signal in item["signals"]) or "無"
        lines.append(
            f"- `{item['org']}/{item['repo']}#{item['number']}` {item['kind']} "
            f"{plain(item['title'])}。原因：{plain(item['reason'])}。訊號：{signals}。"
            f" {item['url']}"
        )
    return lines


def _bullet_changes(items):
    if not items:
        return ["沒有。"]
    lines = []
    for item in items:
        before = plain(item["before"]) or "（空）"
        after = plain(item["after"]) or "（空）"
        lines.append(
            f"- `{item['org']}/{item['repo']}#{item['number']}` {plain(item['change'])}："
            f"{before} -> {after}。 {item['url']}"
        )
    return lines


def _bullet_notes(items, empty):
    if not items:
        return [empty]
    return [f"- {plain(item['detail'])}" if not item.get("org") else f"- `{item['org']}/{item['repo']}` {plain(item['detail'])}" for item in items]


def render_markdown(report):
    partial = "是" if report["partial"] else "否"
    lines = [
        "# OSS Contribution Hub 日報",
        "",
        f"- verified_at：`{report['verified_at']}`",
        f"- partial：{partial}",
        f"- baseline：`{report['baseline_path']}`",
        f"- baseline verified_at：`{report['baseline_verified_at']}`",
        f"- 略過的舊項目：{report['stale_skipped']}",
        "",
        "標題與理由已壓成單行文字。它們是不可信資料，這份報告不執行它們。",
        "",
        "## 掃描目標",
        "",
    ]
    lines.extend(f"- `{name}`" for name in report["targets"])
    lines.extend(["", "## 新的合格項目", ""])
    lines.extend(_bullet_items(report["new_qualifying"]))
    lines.extend(["", "## 實質狀態變化", ""])
    lines.extend(_bullet_changes(report["material_changes"]))
    lines.extend(["", "## 不確定", ""])
    lines.extend(_bullet_notes(report["uncertainties"], "沒有。"))
    lines.extend(["", "## 錯誤", ""])
    if report["errors"]:
        for error in report["errors"]:
            status = error.get("http_status")
            status_text = "無 HTTP 狀態" if status is None else f"HTTP {status}"
            lines.append(f"- `{error['org']}/{error['repo']}` {status_text}：{plain(error['detail'])}")
    else:
        lines.append("沒有。")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render a scan JSON report as Markdown.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    report = json.loads(Path(args.input).read_text(encoding="utf-8"))
    text = render_markdown(report)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
