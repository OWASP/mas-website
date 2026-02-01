import re
import yaml
from pathlib import Path

FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def split_frontmatter(text: str):
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return meta, body


def inject_methods(test_dir: Path):
    main_files = list(test_dir.glob("MASTG-TEST-*.md"))
    if not main_files:
        return

    main_file = main_files[0]
    main_text = main_file.read_text(encoding="utf-8")
    main_meta, main_body = split_frontmatter(main_text)

    method_files = sorted(test_dir.glob("method-*.md"))
    if not method_files:
        return

    merged_types = set()
    method_blocks = []

    for idx, mf in enumerate(method_files, 1):
        meta, body = split_frontmatter(mf.read_text(encoding="utf-8"))

        title = meta.get("title", f"Method {idx}")
        mtype = meta.get("type")

        if mtype:
            if isinstance(mtype, list):
                merged_types.update(mtype)
            else:
                merged_types.add(mtype)

        block = f"""
## Method {idx} - {title}

{body.strip()}
"""
        method_blocks.append(block)

    # Merge types
    existing = main_meta.get("type", [])
    if isinstance(existing, str):
        existing = [existing]

    main_meta["type"] = sorted(set(existing) | merged_types)

    # Inject before Evaluation
    injection = "\n".join(method_blocks)

    if "## Evaluation" in main_body:
        main_body = main_body.replace(
            "## Evaluation",
            f"{injection}\n## Evaluation",
            1
        )
    else:
        main_body += "\n\n" + injection

    final = f"---\n{yaml.safe_dump(main_meta)}---\n{main_body}"
    main_file.write_text(final, encoding="utf-8")


def on_pre_build(config):
    root = Path("OWASP/mastg/tests-beta")

    if not root.exists():
        return

    for folder in root.rglob("MASTG-TEST-*"):
        if folder.is_dir():
            inject_methods(folder)
