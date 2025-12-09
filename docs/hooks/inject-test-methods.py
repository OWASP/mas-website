import logging
import re
import os
from pathlib import Path
import mkdocs.plugins
import yaml

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
    all_types = set()
    
    for i, method_file in enumerate(method_files, start=1):
        try:
            content = method_file.read_text(encoding="utf-8")
            
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
            
            # Create the method section with proper heading
            method_section = f"\n## Method {i} - {type_display}\n\n{method_body.strip()}\n"
            method_contents.append(method_section)
            
        except Exception as e:
            log.error(f"Error processing {method_file.name}: {e}")
            continue
    
    if not method_contents:
        return markdown
    
    # Update the page metadata with the types
    if all_types:
        page.meta['type'] = sorted(list(all_types))
    
    # Find the "## Evaluation" section and inject methods before it
    evaluation_pattern = r'^## Evaluation'
    
    if re.search(evaluation_pattern, markdown, re.MULTILINE):
        # Inject methods before the Evaluation section
        injected_methods = '\n'.join(method_contents)
        updated_markdown = re.sub(
            evaluation_pattern,
            f"{injected_methods}\n## Evaluation",
            markdown,
            flags=re.MULTILINE
        )
        log.info(f"Injected {len(method_contents)} methods into {filename}")
        return updated_markdown
    else:
        # If no Evaluation section found, append methods at the end
        log.warning(f"No '## Evaluation' section found in {filename}, appending methods at the end")
        injected_methods = '\n'.join(method_contents)
        return markdown + '\n' + injected_methods


def extract_frontmatter(content):
    """Extract YAML frontmatter and body from markdown content."""
    # Match YAML frontmatter pattern
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if match:
        try:
            frontmatter_text = match.group(1)
            body = match.group(2)
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter or {}, body
        except yaml.YAMLError as e:
            log.error(f"Error parsing YAML frontmatter: {e}")
            return {}, content
    
    return {}, content
