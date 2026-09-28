#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

repository_root = Path(__file__).resolve().parents[1]
mermaid_output = Path(
    os.environ.get("MERMAID_OUTPUT", "/tmp/projectmanagementweb-mermaid")
)

markdown_link_pattern = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
ignored_schemes = (
    "http://",
    "https://",
    "mailto:",
    "data:",
    "javascript:",
)

errors: list[str] = []
mermaid_blocks: list[tuple[Path, int, str]] = []


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in repository_root.rglob("*.md")
        if ".git" not in path.parts
    )


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()

    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]

    # 移除頁面內 anchor。
    target = target.split("#", 1)[0]

    return unquote(target.strip())


def validate_local_links(markdown_path: Path, content: str) -> None:
    for match in markdown_link_pattern.finditer(content):
        raw_target = match.group(1)
        target = normalize_link_target(raw_target)

        if not target:
            continue

        if target.startswith("#") or target.lower().startswith(ignored_schemes):
            continue

        resolved_target = (markdown_path.parent / target).resolve()

        if not resolved_target.exists():
            relative_markdown = markdown_path.relative_to(repository_root)
            errors.append(
                f"{relative_markdown}: 找不到相對連結或圖片：{raw_target}"
            )


def extract_mermaid_blocks(markdown_path: Path, lines: list[str]) -> None:
    active_fence_language: str | None = None
    fence_start_line = 0
    mermaid_lines: list[str] = []

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if stripped.startswith("```"):
            if active_fence_language is None:
                active_fence_language = stripped[3:].strip().lower()
                fence_start_line = line_number
                mermaid_lines = []
                continue

            if active_fence_language == "mermaid":
                mermaid_blocks.append(
                    (
                        markdown_path,
                        fence_start_line,
                        "\n".join(mermaid_lines) + "\n",
                    )
                )

            active_fence_language = None
            fence_start_line = 0
            mermaid_lines = []
            continue

        if active_fence_language == "mermaid":
            mermaid_lines.append(line)

    if active_fence_language is not None:
        relative_markdown = markdown_path.relative_to(repository_root)
        errors.append(
            f"{relative_markdown}:{fence_start_line}: "
            "Markdown code fence 沒有關閉"
        )


def write_mermaid_blocks() -> None:
    mermaid_output.mkdir(parents=True, exist_ok=True)

    for index, (source, line_number, content) in enumerate(
        mermaid_blocks,
        start=1,
    ):
        safe_name = re.sub(
            r"[^A-Za-z0-9._-]+",
            "-",
            str(source.relative_to(repository_root)),
        )

        output_path = mermaid_output / (
            f"{index:03d}-{safe_name}-line-{line_number}.mmd"
        )
        output_path.write_text(content, encoding="utf-8")


def main() -> int:
    files = markdown_files()

    if not files:
        print("找不到 Markdown 文件。", file=sys.stderr)
        return 1

    for markdown_path in files:
        content = markdown_path.read_text(encoding="utf-8")
        validate_local_links(markdown_path, content)
        extract_mermaid_blocks(markdown_path, content.splitlines())

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    write_mermaid_blocks()

    print(f"已檢查 Markdown 文件：{len(files)}")
    print(f"已擷取 Mermaid 區塊：{len(mermaid_blocks)}")
    print(f"Mermaid 暫存目錄：{mermaid_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())