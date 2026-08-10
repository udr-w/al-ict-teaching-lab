from pathlib import Path

from scripts.render_slides import render_file, render_markdown


ROOT = Path(__file__).resolve().parents[1]


def test_renderer_creates_accessible_standalone_html(tmp_path: Path) -> None:
    source = ROOT / "content" / "lessons" / "unit-01" / "competency-1.1" / "slides.md"
    destination = tmp_path / "deck.html"
    render_file(source, destination)
    html = destination.read_text(encoding="utf-8")
    assert '<html lang="en">' in html
    assert '<meta name="viewport"' in html
    assert html.count('<section class="slide"') >= 2
    assert 'aria-label="Slide 1 of ' in html
    assert "From Data to Useful Information" in html


def test_renderer_escapes_untrusted_markup() -> None:
    html = render_markdown("# Test\n\n<script>alert(1)</script>", "Unsafe <title>")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "Unsafe &lt;title&gt;" in html
