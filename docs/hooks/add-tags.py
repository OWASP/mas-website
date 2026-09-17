import logging
import mkdocs.plugins
import re

log = logging.getLogger('mkdocs')

# Canonical display/sort order for MAS profiles - keep in sync with
# create_dynamic_tables.py's PROFILE_ORDER.
PROFILE_ORDER = ["L1", "L2", "R", "P"]

def get_profiles_from_maswe(maswe_ids, maswe_profiles_map):
    """Union of the `profiles` of the given MASWE ids, deduplicated and
    ordered L1, L2, R, P."""
    profiles = set()
    for maswe_id in maswe_ids or []:
        profiles.update(maswe_profiles_map.get(maswe_id, []))
    return [profile for profile in PROFILE_ORDER if profile in profiles]

# https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
# mkdocs/tags runs at -50 so this has to be called before -50
@mkdocs.plugins.event_priority(-49)
def _on_page_markdown_2(markdown, page, config, **kwargs):

    tags = page.meta.get('tags', [])

    if meta_platform := page.meta.get('platform'):
        if type(meta_platform) == str:
            tags.append(meta_platform)
        elif type(meta_platform) == list:
            for platform in meta_platform:
                tags.append(platform)

    # Profile applicability lives on the MASWE only. A MASWE page still
    # declares its own `profiles`; a MASTG-TEST page no longer does, so it
    # inherits the union of the profiles of the MASWE(s) it maps to.
    profiles = page.meta.get('profiles')
    if profiles is None:
        maswe_profiles_map = config.get("maswe_profiles", {})
        profiles = get_profiles_from_maswe(page.meta.get('maswe'), maswe_profiles_map)
    for profile in profiles or []:
        tags.append(profile)

    # If any of these tags don't exist, they will be stripped automatically at the end of the function
    tags.append(page.meta.get("masvs_category"))
    if page.meta.get("test"):
        tags.append("placeholder-tag-test")
    tags.append(page.meta.get("component_type", "").lower())

    # If there are weaknesses (maswe: [...]), add one placeholder per weakness,
    # indexed so multiple weaknesses on the same test each get their own
    # distinct placeholder (needed since a tag's text appears more than once
    # in its rendered chip - e.g. the href fragment and the visible label - so
    # a shared placeholder can't be told apart and swapped correctly later).
    # Registering the type in config.extra.tags here (instead of listing a
    # fixed number of indices in mkdocs.yml) means this scales automatically
    # to however many weaknesses a test actually declares.
    for weakness_index, _ in enumerate(page.meta.get("maswe") or []):
        placeholder = f"placeholder-tag-maswe-{weakness_index}"
        tags.append(placeholder)
        config.extra["tags"].setdefault(placeholder, "maswe")

    # TODO - This is only for the MASTG v1 tests; remove this once all pages have been updated to use mappings
    tags += page.meta.get("masvs_v1_id", [])
    tags += [tag.lower() for tag in page.meta.get("masvs_v2_id", [])]
    # END TODO

    if mappings:=page.meta.get('mappings'):
        if masvs_v2:=mappings.get('masvs-v2'):
            for masvs_id in masvs_v2:
                tags.append(masvs_id.lower())

    meta_status = page.meta.get('status')
    if meta_status in ["placeholder", "deprecated"]:
        tags.append(meta_status)

    page.meta['tags'] = [tag for tag in tags if tag]

    return markdown

# Run again after the tags have been rendered
# This way, the correct value gets picked up for the search indexer
@mkdocs.plugins.event_priority(-51)
def _on_page_markdown_1(markdown, page, **kwargs):

    tags = page.meta.get('tags', [])

    for weakness_index, weakness in enumerate(page.meta.get("maswe") or []):
        placeholder = f"placeholder-tag-maswe-{weakness_index}"
        if placeholder in tags:
            tags.remove(placeholder)
        tags.append(weakness)

    if test := page.meta.get("test"):
        tags.remove("placeholder-tag-test")
        tags.append(test)

    page.meta['tags'] = [tag for tag in tags if tag]


on_page_markdown = mkdocs.plugins.CombinedEvent(_on_page_markdown_1, _on_page_markdown_2)

# The tag renderer used the placeholder value, so we have to convert it to the actual value
# At the same time, we're making some of the URLs more purposeful
@mkdocs.plugins.event_priority(-51)
def on_post_page(output, page, config):

    # Replace maswe placeholders with their actual values
    for weakness_index, weakness in enumerate(page.meta.get("maswe") or []):
        output = output.replace(f"placeholder-tag-maswe-{weakness_index}", weakness)

    if test := page.meta.get("test"):
        output = output.replace("placeholder-tag-test", test)

    # By default, tags link to the main tags page. These substitutions make the tag links more useful
    # Transform URLs for MASWE tags to a more purposeful format.
    # Matches URLs like '/tags/#tag:MASWE-<number>' and replaces them with '/MASWE-<number>'
    output = re.sub(r'/tags/#tag:(MASWE-\d+)"', lambda x: f'/{x.group(1)}"' , output)
    output = re.sub(r'/tags/#tag:know"', '/MASTG/knowledge/"' , output)
    output = re.sub(r'/tags/#tag:test"', '/MASTG/tests/"' , output)
    output = re.sub(r'/tags/#tag:maswe"', '/MASWE/"' , output)
    output = re.sub(r'/tags/#tag:demo"', '/MASTG/demos/"' , output)
    output = re.sub(r'/tags/#tag:tool"', '/MASTG/tools/"' , output)
    output = re.sub(r'/tags/#tag:app"', '/MASTG/apps/"' , output)
    output = re.sub(r'/tags/#tag:best"', '/MASTG/best-practices/"' , output)
    output = re.sub(r'/tags/#tag:tech"', '/MASTG/techniques/"' , output)
    output = re.sub(r'/tags/#tag:network"', '/MASTG/tests/#network"' , output)
    output = re.sub(r'/tags/#tag:l1"', '/MASTG/tests/#l1"' , output)
    output = re.sub(r'/tags/#tag:l2"', '/MASTG/tests/#l2"' , output)
    output = re.sub(r'/tags/#tag:r"', '/MASTG/tests/#r"' , output)
    output = re.sub(r'/tags/#tag:p"', '/MASTG/tests/#p"' , output)
    output = re.sub(r'/tags/#tag:(MASTG-TEST-\d+)"', lambda x: f'/{x.group(1).upper()}"', output)
    output = re.sub(r'/tags/#tag:(masvs-[^"]*)"', lambda x: f'/{x.group(1).upper()}"' , output)

    # TODO - These are disabled currently, as multiple pages have android/ios labels and they shouldn't always to go the tests page
    # output = re.sub(r'/tags/#tag:android"', '/MASTG/tests/#android"' , output)
    # output = re.sub(r'/tags/#tag:ios"', '/MASTG/tests/#ios"' , output)

    # A final switch for things like the main tags page or other places where tags were collected
    output = re.sub(r"placeholder-tag-maswe-\d+", "MASWE", output)
    output = output.replace("placeholder-tag-test", "TEST")

    return output


