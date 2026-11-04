
import re
import mkdocs.plugins

def extract_github_repo(url):
    match = re.search(r'github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$', url)
    if match:
        return match.group(1), match.group(2)
    return None


# https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
@mkdocs.plugins.event_priority(-40)
def on_page_markdown(markdown, page, **kwargs):

    if source := page.meta.get("source"):

        # Remove (Android) or (iOS) from the title if it exists
        title = page.meta.get("title")
        if title:
            title = re.sub(r'\s*\(Android\)|\s*\(iOS\)', '', title, flags=re.IGNORECASE)
            
        # If there's a source, convert the first occurrence of the title in the markdown to a link to the source
        if title and title.lower() in markdown.lower():
            markdown = re.sub(re.escape(title), f"[{title}]({source} \"{title}\")", markdown, count=1, flags=re.IGNORECASE)

        info = extract_github_repo(source)
        if info:
            account, repo = info
            return f"""
[![](https://mas-github-images.vercel.app/api/pin/?username={account}&repo={repo}&show_owner=true&theme=calm){{.floating-right .dark-img}}]({source}){{:target="_blank"}}
[![](https://mas-github-images.vercel.app/api/pin/?username={account}&repo={repo}&show_owner=true){{.floating-right .light-img}}]({source}){{:target="_blank"}}
""" + markdown
        


    return markdown
