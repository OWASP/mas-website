import glob
import mkdocs
import yaml
import re
import os
import logging

log = logging.getLogger('mkdocs')


def get_terms():
    terms = {}

    for file in glob.glob("docs/MASTG/terms/MASTG-TERM-*.md", recursive=True):
        with open(file, 'r') as f:
            id = os.path.splitext(os.path.basename(file))[0]
            content = f.read()
            frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))

            # Build a normalized relative path (from docs/) and a mkdocs-friendly URL
            rel_path = os.path.relpath(file, "docs")
            rel_path_no_ext, _ = os.path.splitext(rel_path)
            # mkdocs pages usually resolve to "/<path-without-ext>/"
            url = "/" + rel_path_no_ext.replace(os.sep, "/") + "/"

            terms[id] = {
                "url": url,
                "title": frontmatter.get("title"),
                "nist_url": frontmatter.get("nist"),
                "cwe_url": frontmatter.get("cwe"),
            }

    return terms


@mkdocs.plugins.event_priority(-10)
def on_pre_build(config):
    config["terms"] = get_terms()


@mkdocs.plugins.event_priority(-40)
def on_page_markdown(markdown, page, config, **kwargs):
    path = page.file.src_uri

    if path.endswith("terms/index.md"):
        # glossary terms index
        terms = config.get("terms", {}).values()
        # Sort by title (case-insensitive)
        terms_sorted = sorted(terms, key=lambda term: (term.get("title") or "").lower())
        # Format as markdown links
        terms_formatted = [f"[{term['title']}]({term['url']})" for term in terms_sorted if
                           term.get("title") and term.get("url")]

        return markdown + "<br/>" + "<br/>".join(terms_formatted)
    elif path and re.compile(r"^.*terms/MASTG-TERM-\d{4}.md").match(path):
        # append NIST and CWE link to the term

        terms = config.get("terms", {})
        term_id = os.path.splitext(os.path.basename(path))[0]
        term = terms.get(term_id)

        if term:
            nist_url = term.get("nist_url")
            cwe_url = term.get("cwe_url")
            if nist_url or cwe_url:
                references = f"## Other Framework References"
                if nist_url:
                    references += f"\n\n[NIST]({nist_url})"
                if cwe_url:
                    references += f"\n\n[CWE]({cwe_url})"

                return markdown + f"\n\n\n{references}"

    return markdown
