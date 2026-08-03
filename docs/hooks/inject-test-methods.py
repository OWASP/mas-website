"""
MkDocs hook to inject test methods into MASTG test files.

This hook supports a folder-based test structure where a test can have
multiple testing methods defined in separate `method-*.md` files.

Structure examples:
    - Flat (backward compatible): tests-beta/android/MASVS-STORAGE/MASTG-TEST-0202.md
    - Folder-based (new): tests-beta/android/MASVS-STORAGE/MASTG-TEST-0202/
                                                     ├── MASTG-TEST-0202.md
                                                     ├── method-1.md
                                                     ├── method-2.md
                                                     └── method-3.md

Method frontmatter
    - `type`: the method category (e.g. `static`, `dynamic`, `network`).
    - `title` (optional): explicit title used for the method tab. If omitted,
        a title like ``Method N - <Type Display>`` is generated.
    - `steps`: either a custom value (any string or markdown) or the literal
        string `default` which tells the hook to resolve platform-specific
        default steps (see below).
    - `observations`: an optional list of observation strings.

Behavior
    - The hook collects all `method-*.md` files next to the main MASTG test
        file and renders each method as a MkDocs Material content tab (the
        `=== "Title"` syntax) under a consolidated `## Steps` section.
    - If the page already contains a `## Steps` heading, the hook will not
        duplicate it; otherwise it inserts one before the injected tabs.
    - Observations from each method's `observations` frontmatter are collected
        and rendered as an `## Observations` list after the injected methods.
    - The hook updates `page.meta['type']` with the unique set of method
        types found.

Default steps
    - If a method sets `steps: default`, the hook resolves the platform from
        the main test page metadata (`page.meta['platform']`) and selects the
        appropriate default steps mapping (`ANDROID_DEFAULT_STEPS` or
        `IOS_DEFAULT_STEPS`). If no platform is present or unrecognised, Android
        defaults are used.
    - Resolved default steps are appended to the end of the method body as a
        `## Steps` block (the hook does not remove any existing method content).

Rendering details
    - Each method becomes a tab using the MkDocs Material content-tabs syntax
        and the method content is indented to satisfy the tab block requirements.
    - Observations are rendered as bullet items of the form
        ``- Method N - <Type Display>: <observation>``.

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

ANDROID_DEFAULT_STATIC_STEPS = """
1. Reverse engineer the app (@MASTG-TECH-0017).
2. Run a static analysis (@MASTG-TECH-0014) tool on the reverse engineered app targeting calls to the relevant APIs.
"""

IOS_DEFAULT_STATIC_STEPS = """
1. Use @MASTG-TECH-0065 to reverse engineer the app.
2. Use @MASTG-TECH-0072 to look for references to the relevant APIs in the reverse engineered app.
3. Use @MASTG-TECH-0076 to analyze the relevant code paths and obtain relevant values.
"""

ANDROID_DEFAULT_DYNAMIC_STEPS = """
1. Use @MASTG-TECH-0005 to install the app.
2. Use @MASTG-TECH-0033 to trace runtime calls to the relevant APIs.
3. Exercise the app thoroughly.
"""

IOS_DEFAULT_DYNAMIC_STEPS = """
1. Use @MASTG-TECH-0056 to install the app.
2. Use @MASTG-TECH-0067 to trace runtime calls to the relevant APIs.
3. Exercise the app thoroughly.
"""

DEFAULT_NETWORK_STEPS = """
1. Set up a proxy tool as per @MASTG-TECH-0043 to capture network traffic from the app.
2. Install the app on a test device or emulator as per @MASTG-TECH-0056.
3. Use the app normally, ensuring to perform actions that would trigger network communications (e.g., logging in, data synchronization).
"""

ANDROID_DEFAULT_STEPS = {
    "static": ANDROID_DEFAULT_STATIC_STEPS,
    "dynamic": ANDROID_DEFAULT_DYNAMIC_STEPS,
    "network": DEFAULT_NETWORK_STEPS,
}

IOS_DEFAULT_STEPS = {
    "static": IOS_DEFAULT_STATIC_STEPS,
    "dynamic": IOS_DEFAULT_DYNAMIC_STEPS,
    "network": DEFAULT_NETWORK_STEPS,
}

def get_method_section(method_title, method_body):
        
        # Create the method section with proper heading
        # method_section = f"\n## Method {i} - {type_display}\n\n{method_body.strip()}\n"

        # MkDocs Material content tabs require the tab content to be indented.
        # Indent all lines of the method body by four spaces.
        body_text = method_body.strip()
        indented_body = textwrap.indent(body_text, '    ')

        # Create a tab for this method using the content-tabs syntax
        method_section = f"\n=== \"{method_title}\"\n\n{indented_body}\n"

        return method_section

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

        # Handle default steps: if frontmatter sets steps: default, resolve
        # the platform from the main test page metadata and inject the
        # appropriate default steps for the method type.
        method_steps_value = frontmatter.get('steps')
        if isinstance(method_steps_value, str) and method_steps_value.lower() == 'default':
            # Resolve platform from the parent MASTG test file metadata
            platform = ''
            try:
                platform = (page.meta.get('platform') or '') if isinstance(page.meta, dict) else ''
            except Exception:
                platform = ''
            platform = str(platform).lower()

            if platform == 'ios':
                default_map = IOS_DEFAULT_STEPS
            else:
                # default to Android steps if unspecified or unknown
                default_map = ANDROID_DEFAULT_STEPS

            default_steps = default_map.get(method_type, '') or ''

            # Append the resolved default steps at the end of the method body.
            method_body = method_body.rstrip() + "\n\n**Steps:**\n\n" + default_steps.strip() + "\n"
        
        # Get the display name for the type
        type_display = TYPE_DISPLAY_NAMES.get(method_type, method_type.title())

        # Compute the method title (matches the title used in the tab)
        method_title = f"Method {i} - {type_display}"

        method_section = get_method_section(method_title, method_body)

        method_contents.append(method_section)

        # Collect observations from the method frontmatter, if any
        for o in frontmatter.get('observations', []) or []:
            obs_lines.append(f"- [{method_title}: {o}](#methods-{method_title.lower().replace(' ', '-')})")
    
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
        methods_heading = '## Methods\n\n'

        # Build Observations block if we collected any
        observations_block = ''
        if obs_lines:
            observations_block = '\n## Observations\n\n' + '\n'.join(obs_lines) + '\n\n'

        updated_markdown = re.sub(
            evaluation_pattern,
            f"{methods_heading}{injected_methods}{observations_block}## Evaluation",
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
