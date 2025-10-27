from pathlib import Path

import shutil
import logging
import os
import re

log = logging.getLogger('mkdocs')

def on_pre_build(config):

    docs_dir = Path("docs")

    mastg_repo = structure_mastg(docs_dir)
    maswe_repo = structure_maswe(docs_dir)
    masvs_repo = structure_masvs(docs_dir)

    # Save the values so they can dynamically be watched for changes later
    config['extra']['mastg_repo'] = mastg_repo
    config['extra']['maswe_repo'] = maswe_repo
    config['extra']['masvs_repo'] = masvs_repo

def structure_maswe(docs_dir):
    # Copy MASWE into docs folder
    maswe_repo_dir = locate_external_repo("maswe")
    maswe_local_dir = docs_dir / "MASWE"
    clean_and_copy(maswe_repo_dir / "weaknesses", maswe_local_dir)

    # MASWE fixes
    batch_replace(find_md_files(maswe_local_dir), [
        ("Document/", "MASTG/")
    ])

    return maswe_repo_dir

def structure_masvs(docs_dir):
    # Copy MASVS into docs folder
    masvs_repo_dir = locate_external_repo("masvs")
    masvs_local_dir = docs_dir / "MASVS"
    clean_and_copy(masvs_repo_dir / "Document", masvs_local_dir)

    # Move the MASVS/controls folder into the docs/MASVS/controls folder
    clean_and_copy(masvs_repo_dir / "controls", masvs_local_dir / "controls")

    # Move the images to the correct location
    masvs_images_dir = docs_dir / "assets" / "MASVS" / "Images"
    masvs_images_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(masvs_local_dir / "images", masvs_images_dir, dirs_exist_ok=True)

    # Replacement patterns
    for md_path in Path(masvs_local_dir).rglob("*.md"):
        if "controls" in str(md_path):
            replace_in_file(md_path, "images/", "../../../assets/MASVS/Images/")
        else:
            replace_in_file(md_path, "images/", "../../assets/MASVS/Images/")

    # The controls pages are prettyfied with some styling
    MAS_BLUE = "499FFF"
    for md_path in Path(masvs_local_dir).rglob("controls/*.md"):
        control_id = md_path.stem
        control_regex = r"## Control\n\n([^#]*)\n\n"
        # ↓↓↓ only change is here ↓↓↓
        description_regex = r"## Description\n\n(.*?)(?=\n## |\Z)"

        content = md_path.read_text(encoding="utf-8")
        # Extract the control content
        control_content = re.search(control_regex, content, re.DOTALL).group(1).strip()
        description_content = re.search(description_regex, content, re.DOTALL).group(1).strip()

        content = f'# {control_id}\n\n'
        content += f'<p style="font-size: 2em">{control_content}</p>\n\n'
        # add html thick separation line in blue
        content += f'<hr style="height: 0.2em; background-color: #{MAS_BLUE}; border: 0;" />\n\n'
        content += f'{description_content}\n'

        md_path.write_text(content, encoding="utf-8")

    return masvs_repo_dir

def structure_mastg(docs_dir):
    # Move all MASTG folders into the docs folder
    mastg_repo_dir = locate_external_repo("mastg")
    mastg_local_dir = docs_dir / "MASTG"
    images_dir = docs_dir / "assets" / "Images"

    mastg_local_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Using MASTG directory: {mastg_repo_dir}")
    
    directories = ["knowledge", "tests", "techniques", "tools", "apps", "demos", "rules", "utils", "best-practices"]
    
    for d in directories:
        src = mastg_repo_dir / d
        dest = mastg_local_dir / d
        clean_and_copy(src, dest)

    # Copy beta tests if the directory exists
    tests_beta_dir = mastg_repo_dir / "tests-beta"
    if tests_beta_dir.exists():
        for file in tests_beta_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(tests_beta_dir)
                dest_path = mastg_local_dir / "tests" / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file, dest_path)

    # Copy top-level .md files from mastg_repo_dir/Document
    document_dir = mastg_repo_dir / "Document"
    
    # If Document directory doesn't exist, try docs directory
    if not document_dir.exists():
        document_dir = mastg_repo_dir / "docs"
        log.info(f"Document directory not found, trying: {document_dir}")
    
    # Create minimal structure if needed
    if not document_dir.exists() or not (document_dir / "index.md").exists():
        log.warning(f"Document directory or index.md not found, creating minimal structure")
        with open(mastg_local_dir / "index.md", "w") as f:
            f.write("# Mobile Application Security Testing Guide\n\nThis is the MASTG index page.\n")
    else:
        # Copy the index file if it exists
        shutil.copy(document_dir / "index.md", mastg_local_dir / "index.md")
    
    # Try to copy 0x0* files if they exist
    if document_dir.exists():
        for mdfile in document_dir.glob("0x0*.md"):
            shutil.copy(mdfile, mastg_local_dir / mdfile.name)
    
    # Copy the Images directory if it exists
    images_src = document_dir / "Images"
    if images_src.exists():
        shutil.copytree(images_src, images_dir, dirs_exist_ok=True)
    else:
        log.warning(f"Images directory not found at {images_src}")
        # Create empty Images directory
        images_dir.mkdir(parents=True, exist_ok=True)

    # Specific subdir replacements
    rel_paths = {
        "knowledge": "../../../../../assets/Images/",
        "tests": "../../../../../assets/Images/",
        "techniques": "../../../../../assets/Images/",
        "tools": "../../../../../assets/Images/",
        "apps": "../../../../../assets/Images/",
        "best-practices": "../../../../../assets/Images/",
        "demos": "../../../../../assets/Images/",
    }

    for subdir, rel_img in rel_paths.items():
        files = find_md_files(mastg_local_dir / subdir)
        batch_replace(files, [("src=\"Images/", f"src=\"{rel_img}")])

    # Generic MASTG markdown fix
    batch_replace(find_md_files(mastg_local_dir), [
        ("src=\"Images/", "src=\"../../../assets/Images/"),
        ("Document/", "")
    ])



def locate_external_repo(repo_name):
    # Check multiple possible locations
    repo_candidates = [
        Path("repos") / repo_name,  # New primary location in repos/ subdirectory
        Path("..") / repo_name,     # Parent directory (original location)
        Path(".") / repo_name,      # Current directory
    ]
    
    # Log which paths we're checking
    for candidate in repo_candidates:
        log.info(f"Checking {repo_name} at: {candidate.absolute()}, exists: {candidate.is_dir()}")
    
    repo_location = next((p for p in repo_candidates if p.is_dir()), None)

    if not repo_location:
        # If we couldn't find the repo, provide a helpful error
        raise Exception(f"Error: Could not find {repo_name} repository. Expected in {[str(p.absolute()) for p in repo_candidates]}")

    log.info(f"Using {repo_name.upper()} directory: {repo_location}")

    return repo_location


def clean_and_copy(source, destination):
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if source exists before copying
    if not source.exists():
        log.warning(f"Source directory does not exist: {source}")
        destination.mkdir(parents=True, exist_ok=True)
        return
    
    shutil.copytree(source, destination, dirs_exist_ok=True)

def clean_and_move(source, destination):
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source, destination)


def find_md_files(base_dir):
    # Get all md files but strip out md files in node_modules or anything inside hidden directories
    return [p for p in Path(base_dir).rglob("*.md") if not "/node_modules/" in str(p) and not "/." in str(p)]

def batch_replace(filepaths, replacements):
    for file in filepaths:
        for old, new in replacements:
            replace_in_file(file, old, new)


def replace_in_file(file_path, old, new):
    path = Path(file_path)
    content = path.read_text(encoding="utf-8").replace(old, new)
    path.write_text(content, encoding="utf-8")
