import pandas
import yaml
import os
import glob
import mkdocs
from pathlib import Path
import yaml
import re
import logging

import requests
log = logging.getLogger('mkdocs')

# MASVS category to CSS color variable mapping
MASVS_CATEGORY_COLORS = {
    'MASVS-STORAGE': 'var(--tag-color-masvs-storage)',
    'MASVS-CRYPTO': 'var(--tag-color-masvs-crypto)',
    'MASVS-AUTH': 'var(--tag-color-masvs-auth)',
    'MASVS-NETWORK': 'var(--tag-color-masvs-network)',
    'MASVS-PLATFORM': 'var(--tag-color-masvs-platform)',
    'MASVS-CODE': 'var(--tag-color-masvs-code)',
    'MASVS-RESILIENCE': 'var(--tag-color-masvs-resilience)',
    'MASVS-PRIVACY': 'var(--tag-color-masvs-privacy)'
}
def natural_id_sort_key(component_id):
    """Sort IDs like MASWE-0006 / MASTG-TEST-0052 numerically on their trailing number."""
    match = re.search(r'(\d+)$', component_id or "")
    if match:
        return (component_id[:match.start()], int(match.group(1)))
    return (component_id or "", 0)

def is_v1_test(test_identifier):
    """Check if a test is v1 (MASTG-TEST-0000 to MASTG-TEST-0199)"""
    match = re.search(r'MASTG-TEST-(\d+)', test_identifier)
    if match:
        try:
            test_number = int(match.group(1))
            return test_number < 200
        except ValueError:
            return False
    return False

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

def get_level_icon(level, value):
    if level == "L1" and value == True:
        return '<span class="mas-dot-blue"></span><span style="display: none;">profile:L1</span>'
    elif level == "L2" and value == True:
        return '<span class="mas-dot-green"></span><span style="display: none;">profile:L2</span>'
    elif level == "R" and value == True:
        return '<span class="mas-dot-orange"></span><span style="display: none;">profile:R</span>'
    elif level == "P" and value == True:
        return '<span class="mas-dot-purple"></span><span style="display: none;">profile:P</span>'

def get_platform_icon(platform):
    if platform == "android":
        return '<span style="font-size: x-large; color: #54b259;" title="Android"> :material-android: </span><span style="display: none;">platform:android</span>'
    elif platform == "ios":
        return '<span style="font-size: x-large; color: #007aff;" title="iOS"> :material-apple: </span><span style="display: none;">platform:ios</span>'
    elif platform == "generic":
        return '<span style="font-size: x-large; color: darkgrey;" title="Generic"> :material-asterisk: </span><span style="display: none;">platform:generic</span>'
    elif platform == "network":
        return '<span style="font-size: x-large; color: #9383e2;" title="Network"> :material-web: </span><span style="display: none;">platform:network</span>'
    else:
        return '<span style="font-size: x-large; color: darkgrey;" title="Unknown"> :material-progress-question: </span><span style="display: none;">platform:unknown</span>'

def get_masvs_category_chip(masvs_category):
    """Generate a styled chip for MASVS category"""
    color = MASVS_CATEGORY_COLORS.get(masvs_category, '#999999')
    
    return f'<span class="md-tag" style="background-color: {color}; color: white;">{masvs_category}</span><span style="display: none;">{masvs_category.lower()}</span>'

def get_maswe_test_counts():
    test_counts = {}

    for file in glob.glob("docs/MASTG/tests/**/*.md", recursive=True):
        if "index.md" in file:
            continue

        with open(file, 'r') as f:
            frontmatter = next(yaml.load_all(f, Loader=yaml.FullLoader))
            weakness = frontmatter.get('weakness')
            if weakness:
                test_counts[weakness] = test_counts.get(weakness, 0) + 1

    return test_counts

def get_all_weaknessess():

    weaknesses = []
    test_counts = get_maswe_test_counts()

    for file in glob.glob("docs/MASWE/**/MASWE-*.md", recursive=True):
        with open(file, 'r') as f:
            content = f.read()

            frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))
            frontmatter['path'] = f"/MASWE/{os.path.splitext(os.path.relpath(file, 'docs/MASWE'))[0]}"
            weaknesses_id = frontmatter['id']
            frontmatter['id'] = weaknesses_id
            frontmatter['title'] = f"@{frontmatter['id']}"
            frontmatter['masvs_v2_id'] = frontmatter['mappings']['masvs-v2'][0]
            frontmatter['masvs_category'] = frontmatter['masvs_v2_id'][:frontmatter['masvs_v2_id'].rfind('-')]
            # Apply chip styling to masvs_v2_id column with full control ID inside the chip
            masvs_v2_control_id = frontmatter['masvs_v2_id']
            color = MASVS_CATEGORY_COLORS.get(frontmatter['masvs_category'], '#999999')
            frontmatter['masvs_v2_id'] = f'<span class="md-tag" style="background-color: {color}; color: white;">{masvs_v2_control_id}</span><span style="display: none;">{masvs_v2_control_id.lower()}</span>'
            frontmatter['L1'] = get_level_icon('L1', "L1" in frontmatter['profiles'])
            frontmatter['L2'] = get_level_icon('L2', "L2" in frontmatter['profiles'])
            frontmatter['R'] = get_level_icon('R', "R" in frontmatter['profiles'])
            frontmatter['P'] = get_level_icon('P', "P" in frontmatter['profiles'])
            frontmatter['tests'] = test_counts.get(weaknesses_id, 0)
            frontmatter['status'] = frontmatter.get('status', 'current')
            status = frontmatter['status']
            if status == 'new':
                status = 'current'
            if status == 'current':
                frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--current">current</span><span style="display: none;">status:current</span>'
            elif status == 'placeholder':
                frontmatter['status'] = f'<a href="https://github.com/OWASP/maswe/issues?q=is%3Aopen+in%3Atitle+%22{weaknesses_id}%22" target="_blank"><span class="md-tag md-tag-icon md-tag--placeholder" style="min-width: 4em">placeholder</span></a><span style="display: none;">status:placeholder</span>'
            elif status == 'deprecated':
                frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--deprecated">deprecated</span><span style="display: none;">status:deprecated</span>'
            frontmatter['platform'] = "".join([get_platform_icon(platform) for platform in frontmatter['platform']])
            weaknesses.append(frontmatter)

    weaknesses.sort(key=lambda weakness: natural_id_sort_key(weakness['id']))
    return weaknesses

def retrieve_masvs(version="latest"):
    try:
        url = f"https://github.com/OWASP/masvs/releases/{version}/download/OWASP_MASVS.yaml"
        response = requests.get(url)
        content = response.content
    except Exception as e:
        log.warning("⚠️ Connection failed when retrieving OWASP_MASVS.yaml")
        masvs_yaml_file = Path("OWASP_MASVS.yaml")
        if masvs_yaml_file.exists():
            log.warning("⚠️ Reading OWASP_MASVS.yaml from file")
            content = masvs_yaml_file.read_text()
        else:
            raise Exception("ERROR Failed reading OWASP_MASVS.yaml from file")
    return yaml.safe_load(content)

def get_masvs_groups():
    masvs = retrieve_masvs()
    groups = {}
    for group in masvs['groups']:
        group_id = group['id']
        groups[group_id] = {'id': group_id, 'title': group['title']}
        groups[group_id]['controls'] = [{"id" : control["id"], "statement": control["statement"]} for control in group["controls"]]
    return groups

def list_of_dicts_to_md_table(data, column_titles=None, column_align=None):

    if column_titles is None:
        column_titles = {key:key.title() for (key,_) in data[0].items()}

    df = pandas.DataFrame.from_dict(data).rename(columns=column_titles)
    return df.to_markdown(index=False, colalign=column_align)

def append_to_page(markdown, new_content, tableid=""):

    return markdown + f"\n<div id='{tableid}' markdown='1'>\n"+ new_content + "</div>\n\n<br>\n\n"


def get_mastg_components_dict(name):

        components = []

        for file in glob.glob(f"{name}/**/*.md", recursive=True):
            if "index.md" not in file:
                with open(file, 'r') as f:
                    content = f.read()

                    frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))
                    component_id = os.path.splitext(os.path.basename(file))[0]
                    component_path = os.path.splitext(os.path.relpath(file, "docs/"))[0]
                    frontmatter['id'] = component_id
                    frontmatter['title'] = f"@{component_id}"
                    if frontmatter.get('platform') and type(frontmatter['platform']) == list:
                        frontmatter['platform'] = "".join([get_platform_icon(platform) for platform in frontmatter['platform']])
                    else:
                        frontmatter['platform'] = get_platform_icon(frontmatter.get('platform'))

                    profiles = frontmatter.get('profiles', [])
                    frontmatter['L1'] = get_level_icon('L1', "L1" in profiles)
                    frontmatter['L2'] = get_level_icon('L2', "L2" in profiles)
                    frontmatter['R'] = get_level_icon('R', "R" in profiles)
                    frontmatter['P'] = get_level_icon('P', "P" in profiles)

                    # Handle status for all component types
                    if is_v1_test(component_id):
                        frontmatter['status'] = frontmatter.get('status', 'update-pending')
                        if frontmatter['status'] == 'update-pending':
                            frontmatter['status'] = f'<a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+in%3Atitle+%22{component_id}%22" target="_blank"><span class="md-tag md-tag-icon md-tag--update-pending" style="min-width: 4em">update-pending</span></a><span style="display: none;">status:update-pending</span>'
                        elif frontmatter['status'] == 'deprecated':
                            frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--deprecated">deprecated</span><span style="display: none;">status:deprecated</span>'
                    elif is_v2_test(component_id):
                        frontmatter['status'] = frontmatter.get('status', 'current')
                        status = frontmatter['status']
                        if status == 'new':
                            status = 'current'
                        if status == 'current':
                            frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--current">current</span><span style="display: none;">status:current</span>'
                        elif frontmatter['status'] == 'placeholder':
                            frontmatter['status'] = f'<a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+in%3Atitle+%22{component_id}%22" target="_blank"><span class="md-tag md-tag-icon md-tag--placeholder" style="min-width: 4em">placeholder</span></a><span style="display: none;">status:placeholder</span>'
                        elif frontmatter['status'] == 'deprecated':
                            frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--deprecated">deprecated</span><span style="display: none;">status:deprecated</span>'
                    else:
                        # For non-test components (tools, apps, techniques, knowledge)
                        frontmatter['status'] = frontmatter.get('status', 'current')
                        status = frontmatter['status']
                        if status == 'new':
                            status = 'current'
                        if status == 'current':
                            frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--current">current</span><span style="display: none;">status:current</span>'
                        elif status == 'placeholder':
                            frontmatter['status'] = f'<a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+in%3Atitle+%22{component_id}%22" target="_blank"><span class="md-tag md-tag-icon md-tag--placeholder" style="min-width: 4em">placeholder</span></a><span style="display: none;">status:placeholder</span>'
                        elif status == 'deprecated':
                            frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--deprecated">deprecated</span><span style="display: none;">status:deprecated</span>'
                    
                    # Add MASVS category chip for knowledge articles
                    if 'masvs_category' in frontmatter and frontmatter['masvs_category']:
                        frontmatter['category'] = get_masvs_category_chip(frontmatter['masvs_category'])

                    components.append(frontmatter)
        components.sort(key=lambda component: natural_id_sort_key(component['id']))
        return components



def get_all_demos_beta():

    demos = []

    for file in glob.glob("docs/MASTG/demos/**/MASTG-DEMO-*.md", recursive=True):
        with open(file, 'r') as f:
            content = f.read()

            frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))

            frontmatter['path'] = f"/MASTG/demos/{os.path.splitext(os.path.relpath(file, 'docs/MASTG/demos'))[0]}"
            demo_id = frontmatter['id']
            frontmatter['id'] = demo_id
            frontmatter['title'] = f"@{demo_id}"
            frontmatter['platform'] = get_platform_icon(frontmatter['platform'])
            frontmatter['status'] = frontmatter.get('status', 'current')
            status = frontmatter['status']
            if status == 'new':
                status = 'current'
            if status == 'current':
                frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--current">current</span><span style="display: none;">status:current</span>'
            elif status == 'placeholder':
                frontmatter['status'] = f'<a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+in%3Atitle+%22{demo_id}%22" target="_blank"><span class="md-tag md-tag-icon md-tag--placeholder" style="min-width: 4em">placeholder</span></a><span style="display: none;">status:placeholder</span>'
            elif status == 'deprecated':
                frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--deprecated">deprecated</span><span style="display: none;">status:deprecated</span>'

            demos.append(frontmatter)
    demos.sort(key=lambda demo: natural_id_sort_key(demo['id']))
    return demos

def get_all_mitigations_beta():

        mitigations = []

        for file in glob.glob("docs/MASTG/best-practices/**/MASTG-BEST-*.md", recursive=True):
            with open(file, 'r') as f:
                content = f.read()

                frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))

                frontmatter['path'] = f"/MASTG/best-practices/{os.path.splitext(os.path.relpath(file, 'docs/MASTG/best-practices'))[0]}"
                mitigation_id = frontmatter['id']
                frontmatter['id'] = mitigation_id
                frontmatter['title'] = f"@{mitigation_id}"
                frontmatter['platform'] = get_platform_icon(frontmatter['platform'])
                frontmatter['status'] = frontmatter.get('status', 'current')
                status = frontmatter['status']
                if status == 'new':
                    status = 'current'
                if status == 'current':
                    frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--current">current</span><span style="display: none;">status:current</span>'
                elif status == 'placeholder':
                    frontmatter['status'] = f'<a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+in%3Atitle+%22{mitigation_id}%22" target="_blank"><span class="md-tag md-tag-icon md-tag--placeholder" style="min-width: 4em">placeholder</span></a><span style="display: none;">status:placeholder</span>'
                elif status == 'deprecated':
                    frontmatter['status'] = '<span class="md-tag md-tag-icon md-tag--deprecated">deprecated</span><span style="display: none;">status:deprecated</span>'

                mitigations.append(frontmatter)
        mitigations.sort(key=lambda mitigation: natural_id_sort_key(mitigation['id']))
        return mitigations

def reorder_dict_keys(original_dict, key_order):
    return {key: original_dict.get(key, "N/A") for key in key_order}

# Higher priority, so that tables are parsed by the other hooks too
@mkdocs.plugins.event_priority(-40)
def on_page_markdown(markdown, page, config, **kwargs):

    path = page.file.src_uri
    metadata = page.meta

    if path.startswith(("MASTG/0x04", "MASTG/0x05", "MASTG/0x06")):
        column_titles = {'id': 'ID', 'title': 'Name', 'platform': "Platform"}
        header = "## Knowledge Articles\n\n"
        knowledge = get_mastg_components_dict("docs/MASTG/knowledge")

        knowledge_filtered = [know for know in knowledge if f'platform:{metadata.get("platform")}' in know.get('platform') and know.get('masvs_category') == metadata.get('masvs_category')]
        if knowledge_filtered:
            knowledge_of_type = [reorder_dict_keys(know, column_titles.keys()) for know in knowledge_filtered]
            return append_to_page(markdown, header + list_of_dicts_to_md_table(knowledge_of_type, column_titles))


    if path.endswith("knowledge/index.md"):
        # knowledge/index.md

        column_titles = {'id': 'ID', 'title': 'Name', 'platform': "Platform", 'category': 'Category', 'status': 'Status'}

        knowledge = get_mastg_components_dict("docs/MASTG/knowledge")
        knowledge_of_type = [reorder_dict_keys(know, column_titles.keys()) for know in knowledge]
        return append_to_page(markdown, list_of_dicts_to_md_table(knowledge_of_type, column_titles))

    elif path.endswith('/tests/index.md'):

        # tests/index.md

        column_titles = {'id': 'ID', 'title': 'Title', 'platform': "Platform", 'L1': 'L1', 'L2': 'L2', 'R': 'R', 'P': 'P', 'status': 'Status'} # 'masvs_v2_id': "MASVS v2 ID", 'masvs_v1_id': "MASVS v1 IDs",
        tests = get_mastg_components_dict("docs/MASTG/tests")
        tests_of_type = [reorder_dict_keys(test, column_titles.keys()) for test in tests]
        for test in tests_of_type:
            if test.get("masvs_v2_id"):
                test['masvs_v2_id'] = test['masvs_v2_id'][0]
            if test.get("masvs_v1_id"):
                test['masvs_v1_id'] = "<br>".join([f"{v1_id}" for v1_id in test['masvs_v1_id']])
        return append_to_page(markdown, list_of_dicts_to_md_table(tests_of_type, column_titles), "table_tests")

    elif path.endswith("demos/index.md"):
        # demos/index.md

        column_titles = {'id': 'ID', 'title': 'Title', 'platform': "Platform", 'test': "Test", 'status': "Status"} # TODO , 'tools': "Tools"

        demos_beta = config["demos_beta"]
        demos_beta_columns_reordered = [reorder_dict_keys(demo, column_titles.keys()) for demo in demos_beta]

        return append_to_page(markdown, list_of_dicts_to_md_table(demos_beta_columns_reordered, column_titles))

    elif path.endswith("best-practices/index.md"):
        # mitigations/index.md

        column_titles = {'id': 'ID', 'title': 'Title', 'platform': "Platform", 'status': 'Status'}

        mitigations_beta = config["mitigations_beta"]
        mitigations_beta_columns_reordered = [reorder_dict_keys(mitigation, column_titles.keys()) for mitigation in mitigations_beta]

        return append_to_page(markdown, list_of_dicts_to_md_table(mitigations_beta_columns_reordered, column_titles))

    elif path.endswith("tools/index.md"):

        # tools/index.md

        column_titles = {'id': 'ID', 'title': 'Name', 'platform': "Platform", 'used_in': "Used in", 'used_in_demos': "Used in Demos", 'status': 'Status'}

        tools = get_mastg_components_dict("docs/MASTG/tools")
        
        # Add "Used in" information from cross-references
        cross_references = getattr(config, 'cross_references', {})
        tool_refs = cross_references.get("tools", {})
        
        def create_used_in_link(base_path, ids, count, icon, label):
            """Helper to generate a 'Used in' link with icon and count"""
            ids_str = ",".join([item["id"] for item in ids])
            return f'<a href="/MASTG/{base_path}/#q:{ids_str.lower()}" title="Used in {count} {label}(s)"><span style="display: inline-flex; align-items: center; gap: 0.25rem;">{icon} {count} MASTG-{label.upper()}</span></a>'
        
        for tool in tools:
            tool_id = tool['id']
            refs = tool_refs.get(tool_id, {"techniques": [], "tests": [], "demos": [], "knowledge": []})
            
            tech_count = len(refs.get("techniques", []))
            test_count = len(refs.get("tests", []))
            demo_count = len(refs.get("demos", []))
            know_count = len(refs.get("knowledge", []))
            
            # Create links with counts and icons
            used_in_parts = []
            
            if tech_count > 0:
                used_in_parts.append(create_used_in_link("techniques", refs["techniques"], tech_count, ":material-magic-staff:", "tech"))
            
            if know_count > 0:
                used_in_parts.append(create_used_in_link("knowledge", refs["knowledge"], know_count, ":material-book-open-variant:", "know"))
            
            if demo_count > 0:
                used_in_parts.append(create_used_in_link("demos", refs["demos"], demo_count, ":material-flask-outline:", "demo"))
            
            if test_count > 0:
                used_in_parts.append(create_used_in_link("tests", refs["tests"], test_count, ":octicons-codescan-checkmark-24:", "test"))
            
            # Add "unused" marker if no references
            if tech_count == 0 and demo_count == 0 and test_count == 0 and know_count == 0:
                tool['used_in'] = '<span style="display: none;">unused</span><span style="color: #999; font-style: italic;">Unused</span>'
            else:
                tool['used_in'] = "<br>".join(used_in_parts)
            
            # Add separate "Used in Demos" column
            if demo_count > 0:
                tool['used_in_demos'] = str(demo_count)
            else:
                tool['used_in_demos'] = '0'
        
        tools_of_type = [reorder_dict_keys(tool, column_titles.keys()) for tool in tools]
        return append_to_page(markdown, "\n" + list_of_dicts_to_md_table(tools_of_type, column_titles))

    elif path.endswith("techniques/index.md"):
        # techniques/index.md

        column_titles = {'id': 'ID', 'title': 'Name', 'platform': "Platform", 'used_in': "Used in", 'used_in_tests': "Used in Tests", 'status': 'Status'}

        techniques = get_mastg_components_dict("docs/MASTG/techniques")
        
        # Add "Used in" information from cross-references
        cross_references = getattr(config, 'cross_references', {})
        technique_refs = cross_references.get("techniques", {})
        
        def create_used_in_link(base_path, ids, count, icon, label):
            """Helper to generate a 'Used in' link with icon and count"""
            ids_str = ",".join([item["id"] for item in ids])
            return f'<a href="/MASTG/{base_path}/#q:{ids_str.lower()}" title="Used in {count} {label}(s)"><span style="display: inline-flex; align-items: center; gap: 0.25rem;">{icon} {count} MASTG-{label.upper()}</span></a>'
        
        for technique in techniques:
            technique_id = technique['id']
            refs = technique_refs.get(technique_id, {"tests": [], "demos": []})
            
            test_count = len(refs.get("tests", []))
            demo_count = len(refs.get("demos", []))
            
            # Create links with counts and icons
            used_in_parts = []
            
            if demo_count > 0:
                used_in_parts.append(create_used_in_link("demos", refs["demos"], demo_count, ":material-flask-outline:", "demo"))
            
            if test_count > 0:
                used_in_parts.append(create_used_in_link("tests", refs["tests"], test_count, ":octicons-codescan-checkmark-24:", "test"))
            
            # Add "unused" marker if no references
            if test_count == 0 and demo_count == 0:
                technique['used_in'] = '<span style="display: none;">unused</span><span style="color: #999; font-style: italic;">Unused</span>'
            else:
                technique['used_in'] = "<br>".join(used_in_parts)
            
            # Add separate "Used in Tests" column
            if test_count > 0:
                technique['used_in_tests'] = str(test_count)
            else:
                technique['used_in_tests'] = '0'
        
        techniques_of_type = [reorder_dict_keys(technique, column_titles.keys()) for technique in techniques]
        return append_to_page(markdown, "\n" + list_of_dicts_to_md_table(techniques_of_type, column_titles))

    elif path.endswith("apps/index.md"):
        # apps/index.md

        column_titles = {'id': 'ID', 'title': 'Name', 'platform': "Platform", 'status': 'Status'}

        apps = get_mastg_components_dict("docs/MASTG/apps")
        apps_of_type = [reorder_dict_keys(app, column_titles.keys()) for app in apps]
        return append_to_page(markdown, list_of_dicts_to_md_table(apps_of_type, column_titles) )

    elif path.endswith("MASWE/index.md"):
        # weaknesses/index.md

        column_titles = {'id': 'ID', 'title': 'Title', 'platform': "Platform", 'masvs_v2_id': "MASVS v2 ID", 'L1': 'L1', 'L2': 'L2', 'R': 'R', 'P': 'P', 'tests': 'Tests', 'status': 'Status'}

        weaknesses = get_all_weaknessess()
        weaknesses_columns_reordered = [reorder_dict_keys(weakness, column_titles.keys()) for weakness in weaknesses]

        return append_to_page(markdown, list_of_dicts_to_md_table(weaknesses_columns_reordered, column_titles) )

    elif path.endswith("talks.md"):
        # talks.md

        data = yaml.safe_load(open("docs/assets/data/talks.yaml"))

        for element in data:
            if element['video'].startswith("http"):
                element['video'] = f"[:octicons-play-24: Video]({element['video']})"
            if element['slides'].startswith("http"):
                element['slides'] = f"[:material-file-presentation-box: Slides]({element['slides']})"

        return append_to_page(markdown, list_of_dicts_to_md_table(data))

    elif match := re.compile(r"MASVS/\d{2}-(MASVS-.*)\.md").match(path):

        column_titles = {'id': 'ID', 'title': 'Control'}
        masvs_controls = config["masvs_groups"][match.group(1)]['controls']
        for control in masvs_controls:
            control['id'] = f'[{control["id"]}](/MASVS/controls/{control["id"]})'

        table = list_of_dicts_to_md_table(masvs_controls, column_titles)
        page_with_table = append_to_page(markdown, table)
        return page_with_table


    return markdown


# Lower priority because it needs to run after collecting docs/MASTG, docs/MASWE, and docs/MASVS in combine-repos.py
@mkdocs.plugins.event_priority(-10)
def on_pre_build(config):
    config["mitigations_beta"] = get_all_mitigations_beta()
    config["demos_beta"] = get_all_demos_beta()
    config["masvs_groups"] = get_masvs_groups()