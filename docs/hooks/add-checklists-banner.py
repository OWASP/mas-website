import logging
import mkdocs.plugins

log = logging.getLogger('mkdocs')

checklists_banner = """
!!! info "Checklists Updated (June 2025)"
    The checklists now include **all MASTG tests**, as well as updated mappings to the new [MAS profiles](https://mas.owasp.org/MASTG/0x03b-Testing-Profiles/).
"""

# https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
@mkdocs.plugins.event_priority(-40)
def on_page_markdown(markdown, page, **kwargs):
    path = page.file.src_uri

    if "checklists/MASVS-" in path:
        markdown = "\n" + checklists_banner + "\n\n" + markdown

    return markdown
