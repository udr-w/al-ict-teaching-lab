"""Render lesson slide Markdown into deterministic standalone HTML."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def render_markdown(source: str, title: str) -> str:
    """Render the repository's deliberately small slide Markdown subset."""
    sections: list[list[str]] = []
    current: list[str] = []
    in_list = False
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            if in_list:
                current.append("</ul>")
                in_list = False
            if current:
                sections.append(current)
            current = [f"<h2>{escape(line[3:])}</h2>"]
        elif line.startswith("# "):
            current.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                current.append("<ul>")
                in_list = True
            current.append(f"<li>{escape(line[2:])}</li>")
        elif line:
            if in_list:
                current.append("</ul>")
                in_list = False
            current.append(f"<p>{escape(line)}</p>")
    if in_list:
        current.append("</ul>")
    if current:
        sections.append(current)

    rendered_sections = []
    total = len(sections)
    for index, section in enumerate(sections, start=1):
        rendered_sections.append(
            f'<section class="slide" id="slide-{index}" aria-label="Slide {index} of {total}">'
            f'<div class="eyebrow">GCE A/L ICT · Competency lesson</div>{"".join(section)}'
            f'<footer><span>{escape(title)}</span><span>{index} / {total}</span></footer></section>'
        )
    slides = "\n".join(rendered_sections)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><style>
:root{{--ink:#14213d;--navy:#17365d;--blue:#2563a6;--teal:#087f8c;--gold:#f2b134;--paper:#f8fafc;--muted:#526174}}
*{{box-sizing:border-box}}html{{scroll-snap-type:y mandatory}}body{{margin:0;font:clamp(18px,2vw,31px)/1.42 Inter,Aptos,"Segoe UI",sans-serif;background:#dce5ef;color:var(--ink)}}
.slide{{position:relative;min-height:100vh;padding:11vh 10vw 13vh;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(135deg,var(--paper) 0 78%,#e6f3f4 78%);border-top:10px solid var(--teal);scroll-snap-align:start}}
.slide:first-child{{background:linear-gradient(135deg,var(--navy),#0c6873);color:white;border-color:var(--gold)}}
.eyebrow{{position:absolute;top:5vh;left:10vw;color:var(--teal);font-size:.48em;font-weight:750;letter-spacing:.12em;text-transform:uppercase}}
.slide:first-child .eyebrow{{color:#bcebf0}}h1{{font-size:2.25em;line-height:1.05;max-width:18ch}}h2{{font-size:1.65em;line-height:1.15;color:var(--navy);margin:.15em 0 .55em;max-width:22ch}}
p{{max-width:42ch}}ul{{max-width:38ch;padding-left:1.2em}}li{{margin:.4em 0}}code{{font-family:"Cascadia Mono",monospace;background:#e5edf5;border-radius:.25em;padding:.08em .3em}}
footer{{position:absolute;left:10vw;right:8vw;bottom:4vh;display:flex;justify-content:space-between;color:var(--muted);font-size:.42em}}.slide:first-child footer{{color:#cbdbe8}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}@media print{{@page{{size:16in 9in;margin:0}}html{{scroll-snap-type:none}}.slide{{width:16in;height:9in;min-height:0;break-after:page}}}}
</style></head><body>{slides}<script>document.addEventListener('keydown',e=>{{if(!['ArrowDown','ArrowRight','PageDown','ArrowUp','ArrowLeft','PageUp'].includes(e.key))return;const d=['ArrowDown','ArrowRight','PageDown'].includes(e.key)?1:-1;const n=Math.max(1,Math.min({total},Math.round(scrollY/innerHeight)+1+d));document.getElementById('slide-'+n).scrollIntoView();}});</script></body></html>\n"""


def render_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    title = source.parent.name.replace("-", " ").title()
    destination.write_text(render_markdown(source.read_text(encoding="utf-8"), title), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "slides")
    args = parser.parse_args(argv)
    sources = args.sources or sorted((ROOT / "content" / "lessons").glob("unit-*/competency-*/slides.md"))
    for source in sources:
        unit, competency = source.parent.parent.name, source.parent.name
        render_file(source, args.output / unit / f"{competency}.html")
    print(f"Rendered {len(sources)} slide deck(s) to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
