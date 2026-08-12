#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMITTED = ROOT / "submitted-posters"
THEME_DIRS = sorted(SUBMITTED.glob("poster-theme-*"))


def split_name_tokens(name: str) -> list[str]:
    tokens = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", name)
    return [t for t in tokens if t]


def format_display_name(file_stem: str) -> str:
    # Example: PosterTheme1_TanzSandra -> TanzSandra -> "Sandra Tanz"
    # We assume the final token block before a final underscore is SurnameFirstname.
    # If the name already contains an underscore, use the segment after the last underscore.
    name_segment = file_stem.split("_")[-1]
    tokens = split_name_tokens(name_segment)
    if len(tokens) >= 2:
        surname = tokens[0]
        first_name = " ".join(tokens[1:])
        return f"{first_name} {surname}"
    if len(tokens) == 1:
        return tokens[0]
    return file_stem


def convert_pdf_to_image(pdf_path: Path, image_dir: Path) -> Path:
    image_dir.mkdir(parents=True, exist_ok=True)
    output_path = image_dir / f"{pdf_path.stem}.png"
    if output_path.exists():
        return output_path

    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-r",
            "200",
            "-singlefile",
            str(pdf_path),
            str(image_dir / pdf_path.stem),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return output_path


def page_template(theme_num: int, poster_blocks: str) -> str:
    return f'''---
title: "Posters Theme {theme_num}"
---

## Posters

{poster_blocks}
'''


def build_poster_block(pdf_path: Path, theme_dir: Path) -> str:
    stem = pdf_path.stem
    image_dir = theme_dir / "generated-images"
    image_path = convert_pdf_to_image(pdf_path, image_dir)
    rel_image = image_path.relative_to(ROOT).as_posix()
    display_name = format_display_name(stem)
    return f'''<div class="poster-card">
  <img src="{rel_image}" alt="Poster by {display_name}" />
  <p>{display_name}</p>
</div>'''


def build_theme_page(theme_dir: Path) -> str:
    theme_num = int(theme_dir.name.rsplit("-", 1)[-1])
    pdfs = sorted(theme_dir.glob("*.pdf"))

    if not pdfs:
        return page_template(theme_num, "No posters have been submitted for this theme yet.")

    blocks = "\n".join(build_poster_block(pdf, theme_dir) for pdf in pdfs)
    return page_template(theme_num, f'<div class="poster-gallery">\n{blocks}\n</div>')


def main() -> None:
    if not SUBMITTED.exists():
        raise FileNotFoundError(f"Poster folder does not exist: {SUBMITTED}")

    for theme_dir in THEME_DIRS:
        page_path = ROOT / f"posters-theme-{theme_dir.name.rsplit('-', 1)[-1]}.qmd"
        content = build_theme_page(theme_dir)
        page_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
