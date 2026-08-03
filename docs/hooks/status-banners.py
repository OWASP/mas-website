import logging
import yaml
import mkdocs.plugins
import glob
from io import BytesIO
from collections import defaultdict
from zipfile import BadZipFile, ZipFile
import github_api
import requests
from html import escape
from lxml import etree
log = logging.getLogger('mkdocs')

CWE_CATALOG_URL = 'https://cwe.mitre.org/data/xml/cwec_latest.xml.zip'

def get_cwe_titles():
    try:
        response = requests.get(CWE_CATALOG_URL, timeout=30)
        response.raise_for_status()
        with ZipFile(BytesIO(response.content)) as archive:
            catalog_file = next(
                name for name in archive.namelist() if name.endswith('.xml')
            )
            root = etree.fromstring(archive.read(catalog_file))
    except (requests.RequestException, BadZipFile, StopIteration, etree.XMLSyntaxError) as error:
        log.warning('Unable to retrieve the CWE catalog: %s', error)
        return {}

    return {
        weakness.get('ID'): weakness.get('Name')
        for weakness in root.iter()
        if weakness.tag.rsplit('}', 1)[-1] == 'Weakness'
        and weakness.get('ID')
        and weakness.get('Name')
    }

def get_v1_tests_data():

    masvs_v1_tests_metadata = {}
    # Each test has an ID which is the filename
    for file in glob.glob("./tests/**/*.md", recursive=True):
        if "index.md" not in file:
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    frontmatter = next(yaml.load_all(content, Loader=yaml.FullLoader))
                    # masvs category is frontmatter['masvs_v2_id'][0] without the final number. Example: MASVS-STORAGE-2 -> MASVS-STORAGE
                    masvs_category = frontmatter['masvs_v2_id'][0][:-2]
                    platform = frontmatter['platform']
                    # get id from filename without extension
                    id = file.split('/')[-1].split('.')[0]
                    link = f"https://mas.owasp.org/MASTG/tests/{platform}/{masvs_category}/{id}/"
                    frontmatter['link'] = link

                    masvs_v1_tests_metadata[id] = frontmatter
            except:
                log.warning("No frontmatter in " + file)

    # Populate the defaultdict with MASVS v1 IDs and corresponding MASTG-TEST IDs
    masvs_v1_mapping = defaultdict(list)
    for test_id, test_info in masvs_v1_tests_metadata.items():
        for masvs_id in test_info["masvs_v1_id"]:
            masvs_v1_mapping[masvs_id].append(f"[{test_id}]({test_info['link']})")

    return masvs_v1_tests_metadata, masvs_v1_mapping


def get_mastg_v1_coverage(meta, config):
    mappings = meta.get('mappings', '')

    if mappings:
        mastg_v1_tests_metadata, mastg_v1_mapping = config["v1_tests_data"]

        masvs_v1_ids = mappings.get('masvs-v1', []) or []
        mastg_v1_tests_map = []
        for masvs_v1_id in masvs_v1_ids:
            mastg_v1_tests_map.extend(mastg_v1_mapping.get(masvs_v1_id, []))

        mastg_v1_tests_map_list = list(dict.fromkeys(f"{test.split(']')[0].split('[')[1]}" for test in mastg_v1_tests_map))
        mappings['mastg-v1'] = mastg_v1_tests_map_list

        mastg_v1_tests = "\n".join([f"    - [{test} - {mastg_v1_tests_metadata[test]['title']} ({mastg_v1_tests_metadata[test]['platform']})]({mastg_v1_tests_metadata[test]['link']})" for test in mastg_v1_tests_map_list])
        if mastg_v1_tests == "":
            mastg_v1_tests = "    No MASTG v1 tests are related to this weakness."
    return mastg_v1_tests

def get_maswe_placeholder_banner(meta, config):

    id = meta.get('id')

    refs = meta.get('refs', None)
    refs_section = ""
    if refs:
        refs_section = "    ## References\n\n"
        refs_section += "\n".join([f"    - <{ref}>" for ref in refs])

    placeholder_info = meta.get('draft', None)

    description = placeholder_info.get('description', '')
    description = "\n".join(
        f"    {line}" if line else "    " for line in description.splitlines()
    )

    if placeholder_info.get('note', None):
        description += "\n\n    > Note: " + placeholder_info.get('note', None) + "\n"

    topics = placeholder_info.get('topics', None)
    topics_section = ""
    if topics:
        topics_section = "    ## Relevant Topics\n\n"
        topics_section += "\n".join([f"    - {topic}" for topic in topics])

    mastg_v1_tests = get_mastg_v1_coverage(meta, config)

    banner = f"""
!!! warning "Placeholder Weakness"

    This weakness hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that weakness by following our [guidelines](https://docs.google.com/document/d/1EMsVdfrDBAu0gmjWAUEs60q-fWaOmDB5oecY9d9pOlg/edit?usp=sharing).

    <a href="https://github.com/OWASP/maswe/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    ## Initial Description or Hints

{description}

{topics_section}

{refs_section}

    ## MASTG v1 Coverage

{mastg_v1_tests}
"""
    return banner

def get_tests_placeholder_banner(meta):
    id = meta.get('id')
    note = meta.get('note', None)
    weakness = meta.get('weakness', None)

    banner = f"""
!!! warning "Placeholder MASTG-TEST"

    This test hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that test by following our [guidelines](https://mas.owasp.org/contributing/writing-content/).

    <a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    If an issue doesn't exist yet, please create one and request to be assigned to it.

## Draft Description

{note}

For more details, check the associated weakness: @{weakness}

"""
    return banner

def get_v1_deprecated_tests_banner(meta):
    id = meta.get('id')
    covered_by = meta.get('covered_by', [])
    deprecation_note = meta.get('deprecation_note', "")

    if covered_by:
        covered_by = "\n".join([f"    - @{test}" for test in covered_by])
    else:
        covered_by = "    No tests are covering this weakness."

    banner = f"""
!!! danger "Deprecated Test"

    This test is **deprecated** and should not be used anymore. **Reason**: {deprecation_note}

    Please check the following MASTG v2 tests that cover this v1 test:

{covered_by}
"""
    return banner

def get_v1_refactor_tests_banner(meta, url, title):

    banner = f"""
!!! tip "This test will be updated soon"

    The test can be used in its current form, but it will receive a complete overhaul as part of the new <a href="https://docs.google.com/document/d/1veyzE4cVTSnIsKB1DOPUSMhjXow_MtJOtgHeo5HVoho/edit?tab=t.0#heading=h.ue8tn3i2ff0">OWASP MASTG v2 guidelines</a>.

    Help us out by submitting a PR for: <a href='{url}'>{title}</a>

    [:fontawesome-regular-paper-plane: Send Feedback](https://github.com/OWASP/mastg/discussions/categories/maswe-mastg-v2-beta-feedback)
"""
    return banner

def get_deprecated_tools_banner(meta):

    deprecation_note = meta.get('deprecation_note', "The tool is no longer relevant or was replaced by other tools.")

    deprecation_note = f"**Reason**: {deprecation_note}"

    banner = f"""
!!! warning "Deprecated Tool"

    This tool is **deprecated** and should not be used anymore.

    {deprecation_note}

    **Use instead**:

    - {", ".join([f"@{id}" for id in meta.get('covered_by', [])])}
"""

    return banner

def get_deprecated_knowledge_banner(meta):
    deprecation_note = meta.get('deprecation_note', "The knowledge article is no longer relevant or was replaced by other knowledge articles.")

    deprecation_note = f"**Reason**: {deprecation_note}"

    banner = f"""
!!! warning "Deprecated"

    {deprecation_note}

    **Use instead**:

    - {", ".join([f"@{id}" for id in meta.get('covered_by', [])])}
"""

    return banner

def get_demos_placeholder_banner(meta):
    id = meta.get('id')
    note = meta.get('note', None)
    test = meta.get('test', None)

    banner = f"""
!!! warning "Placeholder MASTG-DEMO"

    This demo hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that demo by following our [guidelines](https://mas.owasp.org/contributing/writing-content/).

    <a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    If an issue doesn't exist yet, please create one and request to be assigned to it.

## Draft Description

{note}

For more details, check the associated test: @{test}

"""
    return banner

def get_demos_deprecated_banner(meta):
    id = meta.get('id')
    deprecation_note = meta.get('deprecation_note', "The demo is no longer relevant or was replaced by other demos.")
    covered_by = meta.get('covered_by', [])

    if covered_by:
        covered_by_section = "\n".join([f"    - @{demo}" for demo in covered_by])
    else:
        covered_by_section = "    No demos are covering this demo."

    banner = f"""
!!! danger "Deprecated Demo"

    This demo is **deprecated** and should not be used anymore. **Reason**: {deprecation_note}

    Please check the following demos that cover this demo:

{covered_by_section}
"""
    return banner

def get_best_practices_placeholder_banner(meta):
    id = meta.get('id')
    note = meta.get('note', "This best practice is a placeholder and will be created soon.")

    banner = f"""
!!! warning "Placeholder Best Practice"

    This best practice hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that best practice by following our [guidelines](https://docs.google.com/document/d/1EMsVdfrDBAu0gmjWAUEs60q-fWaOmDB5oecY9d9pOlg/edit?usp=sharing).

    <a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    If an issue doesn't exist yet, please create one and request to be assigned to it.

## Draft Description

{note}

"""
    return banner

def get_best_practices_deprecated_banner(meta):
    id = meta.get('id')
    deprecation_note = meta.get('deprecation_note', "The best practice is no longer relevant or was replaced by other best practices.")
    covered_by = meta.get('covered_by', [])

    if covered_by:
        covered_by_section = "\n".join([f"    - @{bp}" for bp in covered_by])
    else:
        covered_by_section = "    No best practices are covering this best practice."

    banner = f"""
!!! danger "Deprecated Best Practice"

    This best practice is **deprecated** and should not be used anymore. **Reason**: {deprecation_note}

    Please check the following best practices that cover this best practice:

{covered_by_section}
"""
    return banner

def get_tools_placeholder_banner(meta):
    id = meta.get('id')
    note = meta.get('note', "This tool is a placeholder and will be created soon.")

    banner = f"""
!!! warning "Placeholder Tool"

    This tool hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that tool by following our [guidelines](https://docs.google.com/document/d/1EMsVdfrDBAu0gmjWAUEs60q-fWaOmDB5oecY9d9pOlg/edit?usp=sharing).

    <a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    If an issue doesn't exist yet, please create one and request to be assigned to it.

## Draft Description

{note}

"""
    return banner

def get_apps_placeholder_banner(meta):
    id = meta.get('id')
    note = meta.get('note', "This app is a placeholder and will be created soon.")

    banner = f"""
!!! warning "Placeholder App"

    This app hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that app by following our [guidelines](https://docs.google.com/document/d/1EMsVdfrDBAu0gmjWAUEs60q-fWaOmDB5oecY9d9pOlg/edit?usp=sharing).

    <a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    If an issue doesn't exist yet, please create one and request to be assigned to it.

## Draft Description

{note}

"""
    return banner

def get_apps_deprecated_banner(meta):
    id = meta.get('id')
    deprecation_note = meta.get('deprecation_note', "The app is no longer relevant or was replaced by other apps.")
    covered_by = meta.get('covered_by', [])

    if covered_by:
        covered_by_section = "\n".join([f"    - @{app}" for app in covered_by])
    else:
        covered_by_section = "    No apps are covering this app."

    banner = f"""
!!! danger "Deprecated App"

    This app is **deprecated** and should not be used anymore. **Reason**: {deprecation_note}

    Please check the following apps that cover this app:

{covered_by_section}
"""
    return banner

def get_techniques_placeholder_banner(meta):
    id = meta.get('id')
    note = meta.get('note', "This technique is a placeholder and will be created soon.")

    banner = f"""
!!! warning "Placeholder Technique"

    This technique hasn't been created yet and it's a **placeholder**. But you can check its status or start working on it yourself.
    If the issue has not yet been assigned, you can request to be assigned to it and submit a PR with the new content for that technique by following our [guidelines](https://docs.google.com/document/d/1EMsVdfrDBAu0gmjWAUEs60q-fWaOmDB5oecY9d9pOlg/edit?usp=sharing).

    <a href="https://github.com/OWASP/mastg/issues?q=is%3Aopen+{id}" target="_blank">:material-github: Check our GitHub Issues for {id}</a>

    If an issue doesn't exist yet, please create one and request to be assigned to it.

## Draft Description

{note}

"""
    return banner

def get_techniques_deprecated_banner(meta):
    id = meta.get('id')
    deprecation_note = meta.get('deprecation_note', "The technique is no longer relevant or was replaced by other techniques.")
    covered_by = meta.get('covered_by', [])

    if covered_by:
        covered_by_section = "\n".join([f"    - @{tech}" for tech in covered_by])
    else:
        covered_by_section = "    No techniques are covering this technique."

    banner = f"""
!!! danger "Deprecated Technique"

    This technique is **deprecated** and should not be used anymore. **Reason**: {deprecation_note}

    Please check the following techniques that cover this technique:

{covered_by_section}
"""
    return banner

def get_maswe_requirement_banner(meta):
    requirement = meta.get('requirement', '')

    banner = f"""
!!! success "MAS Requirement"

    {requirement}
"""
    return banner

def get_cwe_display_name(value, cwe_titles):
    cwe_title = cwe_titles.get(str(value))
    if cwe_title:
        return f'CWE-{value}: {cwe_title}'
    return f'CWE-{value}'

def get_maswe_mappings_banner(meta, config):
    mappings = meta.get('mappings', {})
    cwe_titles = config.get('cwe_titles', {})
    mapping_labels = {
        'masvs-v1': 'MASVS V1',
        'masvs-v2': 'MASVS V2',
        'cwe': 'CWE',
        'android-risks': 'Android Risks',
        'android-core-app-quality': 'Android Core Quality',
    }
    mapping_urls = {
        'masvs-v2': 'https://mas.owasp.org/MASVS/controls/{value}/',
        'cwe': 'https://cwe.mitre.org/data/definitions/{value}.html',
        'android-risks': 'https://developer.android.com/privacy-and-security/risks/{value}',
        'android-core-app-quality': 'https://developer.android.com/docs/quality-guidelines/core-app-quality#{value}',
    }
    mapping_sections = []

    for mapping_type in ['masvs-v1', *mapping_urls]:
        values = mappings.get(mapping_type, [])
        if not values:
            continue

        if mapping_type == 'masvs-v1':
            rendered_values = ', '.join(str(value) for value in values)
        else:
            rendered_values = ', '.join(
                f'[{get_cwe_display_name(value, cwe_titles) if mapping_type == "cwe" else value}]({mapping_urls[mapping_type].format(value=value)})'
                for value in values
            )
        mapping_sections.append(f'    **{mapping_labels[mapping_type]}:** {rendered_values}')

    mapping_content = "\n\n".join(mapping_sections)

    banner = f'''\
??? info "Mappings"

{mapping_content}
'''
    return banner

def get_maswe_deprecated_banner(meta, config):
    id = meta.get('id')
    deprecation_note = meta.get('deprecation_note', "The weakness is no longer relevant or was replaced by other weaknesses.")
    covered_by = meta.get('covered_by', [])

    if covered_by:
        covered_by_section = "\n".join([f"    - @{weakness}" for weakness in covered_by])
    else:
        covered_by_section = "    No weaknesses are covering this weakness."

    mastg_v1_tests = get_mastg_v1_coverage(meta, config)

    banner = f"""
!!! danger "Deprecated Weakness"

    This weakness is **deprecated** and should not be used anymore. **Reason**: {deprecation_note}

    Please check the following MASTG v2 weaknesses that cover this v1 weakness:

{covered_by_section}
"""
    return banner

# https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
@mkdocs.plugins.event_priority(-40)
def on_page_markdown(markdown, page, config, **kwargs):
    path = page.file.src_uri

    banners = []

    if "MASWE/" in path:
        if page.meta.get('requirement'):
            banners.append(get_maswe_requirement_banner(page.meta))
        if any(
            page.meta.get('mappings', {}).get(mapping_type)
            for mapping_type in [
                'masvs-v1',
                'masvs-v2',
                'cwe',
                'android-risks',
                'android-core-app-quality',
            ]
        ):
            banners.append(get_maswe_mappings_banner(page.meta, config))

    if "MASWE/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_maswe_deprecated_banner(page.meta, config))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_maswe_placeholder_banner(page.meta, config))

    if "MASTG/tests/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_v1_deprecated_tests_banner(page.meta))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_tests_placeholder_banner(page.meta))
        if link := config["issue_mapping"].get(page.meta.get("id")):
            banners.append(get_v1_refactor_tests_banner(page.meta, link[0], escape(link[1])))

    if "MASTG/tools/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_deprecated_tools_banner(page.meta))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_tools_placeholder_banner(page.meta))

    if "MASTG/knowledge/" in path and page.meta.get('status') == 'deprecated':
        banners.append(get_deprecated_knowledge_banner(page.meta))

    if "MASTG/apps/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_apps_deprecated_banner(page.meta))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_apps_placeholder_banner(page.meta))

    if "MASTG/techniques/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_techniques_deprecated_banner(page.meta))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_techniques_placeholder_banner(page.meta))

    if "MASTG/demos/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_demos_deprecated_banner(page.meta))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_demos_placeholder_banner(page.meta))

    if "MASTG/best-practices/" in path:
        if page.meta.get('status') == 'deprecated':
            banners.append(get_best_practices_deprecated_banner(page.meta))
        if page.meta.get('status') == 'placeholder':
            banners.append(get_best_practices_placeholder_banner(page.meta))

    if banners:
        markdown = "\n\n".join(banners) + "\n\n" + markdown

    return markdown


def on_config(config):

    config["issue_mapping"] = github_api.get_issues_for_test_refactors()
    config["v1_tests_data"] = get_v1_tests_data()
    config["cwe_titles"] = get_cwe_titles()

    return config
