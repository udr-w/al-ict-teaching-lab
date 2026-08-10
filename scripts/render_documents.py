"""Render lesson Markdown documents to styled HTML and PDF publication candidates."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ["teacher-notes.md", "delivery-guide.md", "accessibility.md", "worksheet.md", "practical.md", "homework.md", "answers.md"]


def inline(text: str) -> str:
    value = escape(text)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def markdown_body(source: str) -> str:
    lines = source.splitlines()
    result: list[str] = []
    index = 0
    list_tag: str | None = None
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("|") and index + 1 < len(lines) and set(lines[index + 1].replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            headers = [inline(cell.strip()) for cell in line.strip("|").split("|")]
            index += 2
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append([inline(cell.strip()) for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            result.append("<table><thead><tr>" + "".join(f"<th>{cell}</th>" for cell in headers) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows) + "</tbody></table>")
            continue
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if match:
            if list_tag:
                result.append(f"</{list_tag}>")
                list_tag = None
            level = len(match.group(1))
            result.append(f"<h{level}>{inline(match.group(2))}</h{level}>")
        elif re.match(r"^-\s+", line):
            if list_tag != "ul":
                if list_tag:
                    result.append(f"</{list_tag}>")
                result.append("<ul>")
                list_tag = "ul"
            result.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\.\s+", line):
            if list_tag != "ol":
                if list_tag:
                    result.append(f"</{list_tag}>")
                result.append("<ol>")
                list_tag = "ol"
            result.append(f"<li>{inline(re.sub(r'^\d+\.\s+', '', line))}</li>")
        elif line:
            if list_tag:
                result.append(f"</{list_tag}>")
                list_tag = None
            result.append(f"<p>{inline(line)}</p>")
        index += 1
    if list_tag:
        result.append(f"</{list_tag}>")
    return "\n".join(result)


def render_document(source: Path, html_path: Path, pdf_path: Path, chrome: str = "google-chrome") -> None:
    body = markdown_body(source.read_text(encoding="utf-8"))
    title = source.stem.replace("-", " ").title()
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>
@page{{size:A4;margin:18mm 16mm 20mm}}:root{{--navy:#17365d;--teal:#087f8c;--line:#cbd5e1;--paper:#fff;--ink:#172033}}*{{box-sizing:border-box}}body{{margin:0 auto;max-width:190mm;font:11.5pt/1.5 Aptos,"Segoe UI",sans-serif;color:var(--ink);background:var(--paper)}}h1{{font-size:25pt;color:var(--navy);border-bottom:4px solid var(--teal);padding-bottom:8mm}}h2{{font-size:17pt;color:var(--navy);margin-top:8mm;break-after:avoid}}h3{{font-size:13pt;color:var(--teal);break-after:avoid}}p,li{{orphans:3;widows:3}}code{{background:#edf2f7;padding:1px 4px;border-radius:3px}}table{{width:100%;border-collapse:collapse;margin:5mm 0;break-inside:avoid}}th,td{{border:1px solid var(--line);padding:2.5mm;text-align:left}}th{{background:#e8f3f4}}@media screen{{body{{padding:12mm;box-shadow:0 0 24px #94a3b8}}}}
</style></head><body>{body}</body></html>'''
    html_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], check=True, capture_output=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "publication-candidates")
    args = parser.parse_args(argv)
    destination = args.output / args.package.parent.name / args.package.name
    for name in DOCUMENTS:
        source = args.package / name
        stem = source.stem
        render_document(source, destination / f"{stem}.html", destination / f"{stem}.pdf")
    print(f"Rendered {len(DOCUMENTS)} documents to {destination}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
