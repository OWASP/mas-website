"""
MkDocs hook to inject test methods into MASTG test files.

This hook supports folder-based test structure where a test can have multiple
testing methods defined in separate method-*.md files.

Structure examples:
  - Flat (backward compatible): tests-beta/android/MASVS-STORAGE/MASTG-TEST-0202.md
  - Folder-based (new): tests-beta/android/MASVS-STORAGE/MASTG-TEST-0202/
                           ├── MASTG-TEST-0202.md
                           ├── method-1.md
                           ├── method-2.md
                           └── method-3.md

Each method-*.md file should have frontmatter with 'type' (static, dynamic, network, etc.)
and markdown content with ## Steps and ## Observation sections.

The hook injects all methods before the "## Evaluation" section in the main test file
and updates the page metadata with the unique types from all methods.
"""

import logging
import re
import os
from pathlib import Path
import mkdocs.plugins
import yaml
import textwrap

log = logging.getLogger('mkdocs')

# Type mappings from the method types to display names
TYPE_DISPLAY_NAMES = {
    "static": "Static Analysis",
    "dynamic": "Dynamic Analysis",
    "network": "Network Analysis",
}

@mkdocs.plugins.event_priority(-35)
def on_page_markdown(markdown, page, **kwargs):
    path = page.file.src_uri
    filename = os.path.basename(path)
    
    # Only apply the transformation if the page is a test file
    if "MASTG-TEST-" not in filename:
        return markdown
    
    # Get the directory of the test file
    page_dir = Path(page.file.abs_src_path).parent
    
    # Look for method-*.md files in the same directory
    method_files = sorted(page_dir.glob("method-*.md"))
    
    if not method_files:
        # No methods to inject, return original markdown
        return markdown
    
    log.info(f"Found {len(method_files)} method files for {filename}")
    
    # Parse and inject methods
    method_contents = []
    obs_lines = []
    all_types = set()
    
    for i, method_file in enumerate(method_files, start=1):
        try:
            # Read file with specific error handling for common issues
            content = method_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            log.error(f"Encoding error reading {method_file.name}. File must be UTF-8 encoded.")
            continue
        except PermissionError:
            log.error(f"Permission denied reading {method_file.name}")
            continue
        except OSError as e:
            log.error(f"OS error reading {method_file.name}: {e}")
            continue
        
        # Extract frontmatter and content
        frontmatter, method_body = extract_frontmatter(content)
        
        if not frontmatter:
            log.warning(f"No frontmatter found in {method_file.name}")
            continue
        
        # Get the type from frontmatter
        method_type = frontmatter.get('type', 'static')
        all_types.add(method_type)
        
        # Get the display name for the type
        type_display = TYPE_DISPLAY_NAMES.get(method_type, method_type.title())

        # Compute the method title (matches the title used in the tab)
        method_title = f"Method {i} - {type_display}"

        method_section = get_method_section(method_title, method_body)

        method_contents.append(method_section)

        # Collect observations from the method frontmatter, if any
        for o in frontmatter.get('observations', []) or []:
            obs_lines.append(f"- [{method_title}: {o}](#steps-{method_title.lower().replace(' ', '-')})")
    
    if not method_contents:
        return markdown
    
    # Update the page metadata with the types from methods
    # Note: This replaces any existing 'type' metadata as method types should be authoritative
    if all_types:
        page.meta['type'] = sorted(list(all_types))
    
    # Find the "## Evaluation" section and inject methods before it
    evaluation_pattern = r'^## Evaluation'
    
    if re.search(evaluation_pattern, markdown, re.MULTILINE):
        # Inject methods before the Evaluation section
        injected_methods = '\n'.join(method_contents)
        steps_heading = '## Steps\n\n'

        # Build Observations block if we collected any
        observations_block = ''
        if obs_lines:
            observations_block = '\n## Observations\n\n' + '\n'.join(obs_lines) + '\n\n'

        updated_markdown = re.sub(
            evaluation_pattern,
            f"{steps_heading}{injected_methods}{observations_block}## Evaluation",
            markdown,
            flags=re.MULTILINE
        )
        log.info(f"Injected {len(method_contents)} methods into {filename}")
        return updated_markdown
    else:
        # If no Evaluation section found, raise an exception
        raise ValueError(f"No '## Evaluation' section found in {filename}")



def extract_frontmatter(content):
    """Extract YAML frontmatter and body from markdown content."""
    # Match YAML frontmatter pattern with support for Windows line endings and optional whitespace
    frontmatter_pattern = r'^---\s*(?:\r?\n)(.*?)(?:\r?\n)---\s*(?:\r?\n)(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if match:
        try:
            frontmatter_text = match.group(1)
            body = match.group(2)
            # Use safe_load which is consistent with other hooks in the project
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter or {}, body
        except yaml.YAMLError as e:
            log.error(f"Error parsing YAML frontmatter: {e}")
            return {}, content
    
    return {}, content
