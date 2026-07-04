#!/usr/bin/env python3
"""Extract base64-embedded images from a Google-Docs-exported markdown file.

Google Docs markdown exports embed images as base64 data URIs, either as
reference-style definitions:

    ![][image1]
    ...
    [image1]: <data:image/png;base64,iVBORw0KG...>

or as inline data URIs:

    ![alt text](data:image/png;base64,iVBORw0KG...)

This script pulls every embedded image out into an assets/ folder (keeping
the markdown's own image1, image2, ... names) and rewrites the markdown to
reference the extracted files instead of the inline base64 data.

Usage:
    python3 extract_md_images.py input.md [output_dir]

Writes:
    <output_dir>/<input_name>.md   -- edited markdown
    <output_dir>/assets/imageN.ext -- extracted images

If output_dir is omitted, files are written next to the input markdown.
"""
import base64
import re
import sys
from pathlib import Path

REF_DEF_RE = re.compile(r'^\[(image\d+)\]:\s*<data:image/(\w+);base64,([A-Za-z0-9+/=]+)>\s*$')
REF_USE_RE = re.compile(r'!\[([^\]]*)\]\[(image\d+)\]')
INLINE_RE = re.compile(r'!\[([^\]]*)\]\(data:image/(\w+);base64,([A-Za-z0-9+/=]+)\)')

# Adjust this to change how extracted images are referenced in the output
# markdown, e.g. '<center>\n<img style="width: 80%;" src="assets/{name}.{ext}"/>\n</center>'
IMG_TEMPLATE = "![{alt}](assets/{name}.{ext})"


def _save(assets_dir: Path, name: str, ext: str, data: str) -> None:
    (assets_dir / f"{name}.{ext}").write_bytes(base64.b64decode(data))


def extract(md_path: Path, out_dir: Path) -> tuple[Path, Path]:
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    images: dict[str, str] = {}  # name -> ext
    kept_lines = []

    # Pass 1 (streamed): pull reference-style image definitions out of the
    # file line by line, since each one can be several MB of base64 text.
    with md_path.open("r", encoding="utf-8") as f:
        for line in f:
            m = REF_DEF_RE.match(line.strip())
            if m:
                name, ext, data = m.groups()
                _save(assets_dir, name, ext, data)
                images[name] = ext
                continue
            kept_lines.append(line.rstrip("\n"))

    text = "\n".join(kept_lines)

    # Pass 2: rewrite ![alt][imageN] usages that pointed at those definitions
    def ref_sub(m: re.Match) -> str:
        alt, name = m.groups()
        ext = images.get(name, "png")
        return IMG_TEMPLATE.format(alt=alt, name=name, ext=ext)

    text = REF_USE_RE.sub(ref_sub, text)

    # Pass 3: rewrite any inline data-URI images, numbering them after
    # whatever reference-style images were already found.
    counter = [len(images)]

    def inline_sub(m: re.Match) -> str:
        alt, ext, data = m.groups()
        counter[0] += 1
        name = f"image{counter[0]}"
        _save(assets_dir, name, ext, data)
        return IMG_TEMPLATE.format(alt=alt, name=name, ext=ext)

    text = INLINE_RE.sub(inline_sub, text)

    # Collapse blank-line runs left behind by removed definitions.
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

    out_md = out_dir / md_path.name
    out_md.write_text(text, encoding="utf-8")
    return out_md, assets_dir


def main() -> None:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} input.md [output_dir]", file=sys.stderr)
        sys.exit(1)

    md_path = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else md_path.parent

    out_md, assets_dir = extract(md_path, out_dir)
    print(f"wrote {out_md}")
    print(f"images in {assets_dir}")


if __name__ == "__main__":
    main()
