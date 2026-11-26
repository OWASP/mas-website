import mkdocs.plugins
import github_api
import json

def get_android_demo_buttons(page, artifacts_url):
    id = page.meta.get('id')

    page_uri = page.file.src_uri

    demo_folder = page_uri.replace("MASTG/demos/android/", "https://github.com/OWASP/mastg/blob/master/demos/android/").replace(f"/{id}.md", "/")

    banner = f"""
<a href="{artifacts_url}" class="md-button md-button--primary" style="margin: 5px; min-width: 12em;">:material-download:  Download {id} APK</a>
<a href="{demo_folder}" target='_blank' class="md-button md-button--primary" style="margin: 5px; min-width: 12em;">:material-folder-open:  Open {id} Folder</a>
<a href="https://github.com/cpholguera/mas-app-android" target='_blank' class="md-button md-button--primary" style="margin: 5px; min-width: 12em;">:fontawesome-solid-compass-drafting: Build {id} APK</a>
"""
    return banner

def get_ios_demo_buttons(page, artifacts_url):


    id = page.meta.get('id')

    page_uri = page.file.src_uri

    demo_folder = page_uri.replace("MASTG/demos/ios/", "https://github.com/OWASP/mastg/blob/master/demos/ios/").replace(f"/{id}.md", "/")

    banner = f"""
<a href="{artifacts_url}" class="md-button md-button--primary" style="margin: 5px; min-width: 12em;">:material-download:  Download {id} IPA</a>
<a href="{demo_folder}" target='_blank' class="md-button md-button--primary" style="margin: 5px; min-width: 12em;">:material-folder-open:  Open {id} Folder</a>
<a href="https://github.com/cpholguera/mas-app-ios" target='_blank' class="md-button md-button--primary" style="margin: 5px; min-width: 12em;">:fontawesome-solid-compass-drafting: Build {id} IPA</a>
"""
    return banner


# The snippets get added at -40 so this needs to be earlier
@mkdocs.plugins.event_priority(-30)
def on_page_markdown(markdown, page, config, **kwargs):
    path = page.file.src_uri

    buttons = []

    if "MASTG/demos/android/" in path and not page.meta.get('status') == 'placeholder':
        buttons.append(get_android_demo_buttons(page, config["artifacts_url_android"].get(page.meta.get('id'), config["default_android"])))
    elif "MASTG/demos/ios/" in path and not page.meta.get('status') == 'placeholder':
        buttons.append(get_ios_demo_buttons(page, config["artifacts_url_ios"].get(page.meta.get('id'), config["default_ios"])))

    if buttons:
        markdown = "\n\n".join(buttons) + "\n\n" + markdown

    return markdown

def on_config(config):

    fallback_ios = "https://github.com/OWASP/mastg/actions/workflows/build-ios-demos.yml"
    fallback_android = "https://github.com/OWASP/mastg/actions/workflows/build-android-demos.yml"

    config["artifacts_url_ios"], better_fallback_ios = github_api.get_latest_successful_run("build-ios-demos.yml")
    config["artifacts_url_android"], better_fallback_android = github_api.get_latest_successful_run("build-android-demos.yml")

    config["default_ios"] = better_fallback_ios if better_fallback_ios else fallback_ios
    config["default_android"] = better_fallback_android if better_fallback_android else fallback_android
    
    return config