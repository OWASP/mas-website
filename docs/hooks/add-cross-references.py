import logging
import yaml
import mkdocs.plugins
import os
import glob
import re

log = logging.getLogger('mkdocs')


def is_v2_test(test_identifier):
    """Check if a test is v2 (MASTG-TEST-0200 and above)"""
    match = re.search(r'MASTG-TEST-(\d+)', test_identifier)
    if match:
        try:
            test_number = int(match.group(1))
            return test_number >= 200
        except ValueError:
            return False
    return False


def gather_metadata(directory, id_key, component_type):
    metadata = {}
    for file in glob.glob(f"./docs/{directory}/**/MASTG-{component_type}-*.md", recursive=True):
        try:
            if file.endswith("index.md"):
                continue

            with open(file, 'r') as f:
                content = f.read()
                frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))

                # Extract ID from filename if not in frontmatter (for techniques, tools, apps, etc.)
                if not id_key in frontmatter:
                    # Extract ID from filename (e.g., MASTG-TECH-0001.md -> MASTG-TECH-0001)
                    filename = os.path.basename(file)
                    id_match = re.search(rf'(MASTG-{component_type}-\d+)', filename)
                    if id_match:
                        frontmatter[id_key] = id_match.group(1)
                    elif is_v2_test(file):
                        log.error(f"Missing frontmatter ID in {file}")
                        continue
                    else:
                        # Skip if no ID found and it's not a critical component
                        continue

                frontmatter["path"] = os.path.relpath(file, "./docs")

                metadata[frontmatter[id_key]] = frontmatter
        
        except Exception as e:
            raise Exception(f"Missing frontmatter in {file}: {e}")
    return metadata

def gather_tool_references_from_content(content, file_path):
    """Extract all @MASTG-TOOL-XXXX references from file content"""
    tool_pattern = r'@(MASTG-TOOL-\d+)'
    return list(set(re.findall(tool_pattern, content)))

def gather_technique_references_from_content(content, file_path):
    """Extract all @MASTG-TECH-XXXX references from file content"""
    technique_pattern = r'@(MASTG-TECH-\d+)'
    return list(set(re.findall(technique_pattern, content)))

def generate_cross_references():
    tests = gather_metadata("MASTG/tests", "id", "TEST")
    demos = gather_metadata("MASTG/demos", "id", "DEMO")
    best_practices_metadata = gather_metadata("MASTG/best-practices", "id", "BEST")
    techniques = gather_metadata("MASTG/techniques", "id", "TECH")
    knowledge = gather_metadata("MASTG/knowledge", "id", "KNOW")

    cross_references = {
        "weaknesses": {},
        "tests": {},
        "best-practices": {},
        "tools": {},  # Tools cross-references
        "techniques": {}  # Techniques cross-references
    }

    for test_id, test_meta in tests.items():
        weakness_id = test_meta.get("weakness")
        test_path = test_meta.get("path")
        test_title = test_meta.get("title")
        test_platform = test_meta.get("platform")
        best_practices_ids = test_meta.get("best-practices")

        # Create cross-references for weaknesses listing all tests and best practices that reference each weakness ID
        if weakness_id:
            if weakness_id not in cross_references["weaknesses"]:
                cross_references["weaknesses"][weakness_id] = {"tests": [], "best_practices": {}}
            cross_references["weaknesses"][weakness_id]["tests"].append({"id": test_id, "path": test_path, "title": test_title, "platform": test_platform})
            
            # Collect best-practices from tests that reference each weakness
            if best_practices_ids:
                for best_practice_id in best_practices_ids:
                    if best_practice_id not in cross_references["weaknesses"][weakness_id]["best_practices"]:
                        # Get the best-practice metadata if available
                        best_practice_meta = best_practices_metadata.get(best_practice_id, {})
                        best_practice_path = best_practice_meta.get("path", f"MASTG/best-practices/{best_practice_id}.md")
                        best_practice_title = best_practice_meta.get("title", best_practice_id)
                        best_practice_platform = best_practice_meta.get("platform", test_platform)
                        cross_references["weaknesses"][weakness_id]["best_practices"][best_practice_id] = {
                            "id": best_practice_id,
                            "path": best_practice_path,
                            "title": best_practice_title,
                            "platform": best_practice_platform
                        }

        # Create cross-references for best_practices listing all tests that reference each best_practice ID
        if best_practices_ids:
            for best_practice_id in best_practices_ids:
                if best_practice_id not in cross_references["best-practices"]:
                    cross_references["best-practices"][best_practice_id] = []
                cross_references["best-practices"][best_practice_id].append({"id": test_id, "path": test_path, "title": test_title, "platform": test_platform})

    for demo_id, demo_meta in demos.items():
        test_id = demo_meta.get("test")
        demo_path = demo_meta.get("path")
        demo_title = demo_meta.get("title")
        demo_platform = demo_meta.get("platform")

        # Create cross-references for tests listing all demos that reference each test ID
        if test_id:
            if test_id not in cross_references["tests"]:
                cross_references["tests"][test_id] = []
            cross_references["tests"][test_id].append({"id": demo_id, "path": demo_path, "title": demo_title, "platform": demo_platform})

    # Create cross-references for tools
    # Scan techniques for tool references
    for technique_id, technique_meta in techniques.items():
        technique_path = technique_meta.get("path")
        technique_title = technique_meta.get("title")
        technique_platform = technique_meta.get("platform")
        
        # Read the full content of the technique file to find @MASTG-TOOL-XXXX references
        technique_file_path = os.path.join("./docs", technique_path)
        try:
            with open(technique_file_path, 'r') as f:
                content = f.read()
                tool_refs = gather_tool_references_from_content(content, technique_file_path)
                
                for tool_id in tool_refs:
                    if tool_id not in cross_references["tools"]:
                        cross_references["tools"][tool_id] = {"techniques": [], "tests": [], "demos": [], "knowledge": []}
                    cross_references["tools"][tool_id]["techniques"].append({
                        "id": technique_id,
                        "path": technique_path,
                        "title": technique_title,
                        "platform": technique_platform
                    })
        except Exception as e:
            log.warning(f"Error reading technique file {technique_file_path}: {e}")
    
    # Scan tests for tool references
    for test_id, test_meta in tests.items():
        test_path = test_meta.get("path")
        test_title = test_meta.get("title")
        test_platform = test_meta.get("platform")
        
        # Read the full content of the test file to find @MASTG-TOOL-XXXX references
        test_file_path = os.path.join("./docs", test_path)
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
                tool_refs = gather_tool_references_from_content(content, test_file_path)
                
                for tool_id in tool_refs:
                    if tool_id not in cross_references["tools"]:
                        cross_references["tools"][tool_id] = {"techniques": [], "tests": [], "demos": [], "knowledge": []}
                    cross_references["tools"][tool_id]["tests"].append({
                        "id": test_id,
                        "path": test_path,
                        "title": test_title,
                        "platform": test_platform
                    })
        except Exception as e:
            log.warning(f"Error reading test file {test_file_path}: {e}")
    
    # Scan demos for tool references
    for demo_id, demo_meta in demos.items():
        demo_path = demo_meta.get("path")
        demo_title = demo_meta.get("title")
        demo_platform = demo_meta.get("platform")
        
        # Read the full content of the demo file to find @MASTG-TOOL-XXXX references
        demo_file_path = os.path.join("./docs", demo_path)
        try:
            with open(demo_file_path, 'r') as f:
                content = f.read()
                tool_refs = gather_tool_references_from_content(content, demo_file_path)
                
                for tool_id in tool_refs:
                    if tool_id not in cross_references["tools"]:
                        cross_references["tools"][tool_id] = {"techniques": [], "tests": [], "demos": [], "knowledge": []}
                    cross_references["tools"][tool_id]["demos"].append({
                        "id": demo_id,
                        "path": demo_path,
                        "title": demo_title,
                        "platform": demo_platform
                    })
        except Exception as e:
            log.warning(f"Error reading demo file {demo_file_path}: {e}")
    
    # Scan knowledge articles for tool references
    for knowledge_id, knowledge_meta in knowledge.items():
        knowledge_path = knowledge_meta.get("path")
        knowledge_title = knowledge_meta.get("title")
        knowledge_platform = knowledge_meta.get("platform")
        
        # Read the full content of the knowledge file to find @MASTG-TOOL-XXXX references
        knowledge_file_path = os.path.join("./docs", knowledge_path)
        try:
            with open(knowledge_file_path, 'r') as f:
                content = f.read()
                tool_refs = gather_tool_references_from_content(content, knowledge_file_path)
                
                for tool_id in tool_refs:
                    if tool_id not in cross_references["tools"]:
                        cross_references["tools"][tool_id] = {"techniques": [], "tests": [], "demos": [], "knowledge": []}
                    cross_references["tools"][tool_id]["knowledge"].append({
                        "id": knowledge_id,
                        "path": knowledge_path,
                        "title": knowledge_title,
                        "platform": knowledge_platform
                    })
        except Exception as e:
            log.warning(f"Error reading knowledge file {knowledge_file_path}: {e}")
    
    # Create cross-references for techniques
    # Scan tests for technique references
    for test_id, test_meta in tests.items():
        test_path = test_meta.get("path")
        test_title = test_meta.get("title")
        test_platform = test_meta.get("platform")
        
        # Read the full content of the test file to find @MASTG-TECH-XXXX references
        test_file_path = os.path.join("./docs", test_path)
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
                technique_refs = gather_technique_references_from_content(content, test_file_path)
                
                for technique_id in technique_refs:
                    if technique_id not in cross_references["techniques"]:
                        cross_references["techniques"][technique_id] = {"tests": [], "demos": []}
                    cross_references["techniques"][technique_id]["tests"].append({
                        "id": test_id,
                        "path": test_path,
                        "title": test_title,
                        "platform": test_platform
                    })
        except Exception as e:
            log.warning(f"Error reading test file {test_file_path} for technique references: {e}")
    
    # Scan demos for technique references
    for demo_id, demo_meta in demos.items():
        demo_path = demo_meta.get("path")
        demo_title = demo_meta.get("title")
        demo_platform = demo_meta.get("platform")
        
        # Read the full content of the demo file to find @MASTG-TECH-XXXX references
        demo_file_path = os.path.join("./docs", demo_path)
        try:
            with open(demo_file_path, 'r') as f:
                content = f.read()
                technique_refs = gather_technique_references_from_content(content, demo_file_path)
                
                for technique_id in technique_refs:
                    if technique_id not in cross_references["techniques"]:
                        cross_references["techniques"][technique_id] = {"tests": [], "demos": []}
                    cross_references["techniques"][technique_id]["demos"].append({
                        "id": demo_id,
                        "path": demo_path,
                        "title": demo_title,
                        "platform": demo_platform
                    })
        except Exception as e:
            log.warning(f"Error reading demo file {demo_file_path} for technique references: {e}")

    with open("cross_references.yaml", 'w') as f:
        yaml.dump(cross_references, f)

    return cross_references, best_practices_metadata

def get_platform_icon(platform):
    if platform == "ios":
        return ":material-apple:"
    if platform == "android":
        return ":material-android:"
    return ":material-asterisk:"

def on_pre_build(config):
    cross_references, best_practices_metadata = generate_cross_references()
    config.cross_references = cross_references
    config.best_practices_metadata = best_practices_metadata

@mkdocs.plugins.event_priority(-40)
def on_page_markdown(markdown, page, config, **kwargs):
    path = page.file.src_uri
    filename = os.path.basename(path)
    meta = page.meta

    cross_references = config.cross_references

    if "MASWE-" in filename:
        weakness_id = meta.get('id')

        # Add Tests and Best Practices sections to weaknesses as buttons
        # ORIGIN: Cross-references from this script

        if weakness_id in cross_references["weaknesses"]:
            weakness_refs = cross_references["weaknesses"][weakness_id]
            
            tests = weakness_refs.get("tests", [])
            meta['tests'] = tests
            if tests:
                tests_section =  "## Tests\n\n"
                for test in tests:
                    relPath = os.path.relpath(test['path'], os.path.dirname(path))
                    tests_section += f"[{get_platform_icon(test['platform'])} {test['id']}: {test['title']}]({relPath}){{: .mas-test-button}} "
                markdown += f"\n\n{tests_section}"
            
            best_practices = weakness_refs.get("best_practices", {})
            meta['best-practices'] = list(best_practices.values())
            if best_practices:
                best_practices_section = "## Best Practices\n\n"
                for best_practice_id, best_practice in best_practices.items():
                    relPath = os.path.relpath(best_practice['path'], os.path.dirname(path))
                    best_practices_section += f"[{get_platform_icon(best_practice['platform'])} {best_practice['id']}: {best_practice['title']}]({relPath}){{: .mas-best-button}} "
                markdown += f"\n\n{best_practices_section}"

    if "MASTG-TEST-" in filename:

        # Add best_practices section to tests as buttons (same style as weaknesses)
        # ORIGIN: Test metadata + best practices metadata from config

        best_practices_ids = meta.get('best-practices')
        if best_practices_ids:
            best_practices_section = "## Best Practices\n\n"
            best_practices_metadata = config.best_practices_metadata
            for best_practice_id in best_practices_ids:
                best_practice = best_practices_metadata.get(best_practice_id, {})
                relPath = os.path.relpath(best_practice.get("path", f"MASTG/best-practices/{best_practice_id}.md"), os.path.dirname(path))
                best_practices_section += f"[{get_platform_icon(best_practice.get('platform', 'generic'))} {best_practice_id}: {best_practice.get('title', best_practice_id)}]({relPath}){{: .mas-best-button}} "

            markdown += f"\n\n{best_practices_section}"

        test_id = meta.get('id')

        # Add Demos section to tests as buttons
        # ORIGIN: Cross-references from this script

        if test_id in cross_references["tests"]:
            demos = cross_references["tests"][test_id]
            meta['demos'] = demos
            if demos:
                demos_section = "## Demos\n\n"
                for demo in demos:
                    relPath = os.path.relpath(demo['path'], os.path.dirname(path))
                    demos_section += f"[{get_platform_icon(demo['platform'])} {demo['id']}: {demo['title']}]({relPath}){{: .mas-demo-button}} "

                markdown += f"\n\n{demos_section}"

    if "MASTG-TECH-" in filename:
        technique_id = meta.get('id')
        
        # If no id in meta, try to extract from filename
        if not technique_id:
            tech_match = re.search(r'(MASTG-TECH-\d+)', filename)
            if tech_match:
                technique_id = tech_match.group(1)

        # Add Tests section to techniques as buttons
        # ORIGIN: Cross-references from this script

        if technique_id and technique_id in cross_references.get("techniques", {}):
            refs = cross_references["techniques"][technique_id]
            
            tests = refs.get("tests", [])
            if tests:
                tests_section = "## Tests\n\n"
                for test in tests:
                    relPath = os.path.relpath(test['path'], os.path.dirname(path))
                    tests_section += f"[{get_platform_icon(test['platform'])} {test['id']}: {test['title']}]({relPath}){{: .mas-test-button}} "
                markdown += f"\n\n{tests_section}"
            
            demos = refs.get("demos", [])
            if demos:
                demos_section = "## Demos\n\n"
                for demo in demos:
                    relPath = os.path.relpath(demo['path'], os.path.dirname(path))
                    demos_section += f"[{get_platform_icon(demo['platform'])} {demo['id']}: {demo['title']}]({relPath}){{: .mas-demo-button}} "
                markdown += f"\n\n{demos_section}"

    if "MASTG-TOOL-" in filename:
        tool_id = meta.get('id')
        
        # If no id in meta, try to extract from filename
        if not tool_id:
            tool_match = re.search(r'(MASTG-TOOL-\d+)', filename)
            if tool_match:
                tool_id = tool_match.group(1)

        # Add Techniques, Tests, and Demos sections to tools as buttons
        # ORIGIN: Cross-references from this script

        if tool_id and tool_id in cross_references.get("tools", {}):
            refs = cross_references["tools"][tool_id]
            
            techniques = refs.get("techniques", [])
            if techniques:
                techniques_section = "## Techniques\n\n"
                for technique in techniques:
                    relPath = os.path.relpath(technique['path'], os.path.dirname(path))
                    techniques_section += f"[{get_platform_icon(technique['platform'])} {technique['id']}: {technique['title']}]({relPath}){{: .mas-tech-button}} "
                markdown += f"\n\n{techniques_section}"
            
            tests = refs.get("tests", [])
            if tests:
                tests_section = "## Tests\n\n"
                for test in tests:
                    relPath = os.path.relpath(test['path'], os.path.dirname(path))
                    tests_section += f"[{get_platform_icon(test['platform'])} {test['id']}: {test['title']}]({relPath}){{: .mas-test-button}} "
                markdown += f"\n\n{tests_section}"
            
            demos = refs.get("demos", [])
            if demos:
                demos_section = "## Demos\n\n"
                for demo in demos:
                    relPath = os.path.relpath(demo['path'], os.path.dirname(path))
                    demos_section += f"[{get_platform_icon(demo['platform'])} {demo['id']}: {demo['title']}]({relPath}){{: .mas-demo-button}} "
                markdown += f"\n\n{demos_section}"

    if "MASTG-BEST" in filename:
        best_practice_id = meta.get('id')

        # Add Tests section to best_practices as buttons
        # ORIGIN: Cross-references from this script

        if best_practice_id in cross_references["best-practices"]:
            best_practices = cross_references["best-practices"].get(best_practice_id)
            meta['best-practices'] = best_practices
            if best_practices:
                best_practices_section = "## Tests\n\n"
                for best_practice in best_practices:
                    relPath = os.path.relpath(best_practice['path'], os.path.dirname(path))
                    best_practices_section += f"[{get_platform_icon(best_practice['platform'])} {best_practice['id']}: {best_practice['title']}]({relPath}){{: .mas-test-button}} "

                markdown += f"\n\n{best_practices_section}"

    return markdown