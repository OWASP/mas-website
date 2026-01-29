# How to Run the OWASP MAS Website Locally

This guide will help you set up and run the OWASP MAS website locally on your machine. Follow the steps below to get started.

Steps overview:

1. Prerequisite: [Clone the required repositories](#cloning-the-repositories).
2. Build the website using one of the following methods:
    - [Without Docker](#without-docker): You'll need to install Python dependencies manually. 
    - [Using Docker](#using-docker): Python dependencies come pre-installed.

## Cloning the Repositories

Before you begin, you need to clone the following repositories from GitHub. Open your terminal and run the following commands:

```bash
git clone https://github.com/OWASP/mastg.git
git clone https://github.com/OWASP/masvs.git
git clone https://github.com/OWASP/maswe.git
git clone https://github.com/OWASP/mas-website.git
```

**Note 1:** Any local changes in the mastg, masvs, or maswe repositories will be reflected in the website when it is built locally, including errors.

**Note 2:** By default, interactions with the Github API are disabled, which means some dynamically retrieved content will not be available. If you want to enable the Github API, [create a personal access token](https://github.com/settings/personal-access-tokens) and export it as an environment variable (e.g., in your .zshrc file). Make sure to export this token in your shell before running the website:

```bash
export GITHUB_TOKEN=<TOKEN>
```

## Without Docker

> **TLDR for advanced users:**
>
> - Set up a virtual environment
> - Install dependencies from `mas-website/requirements.txt`
> - Run the website using `./run_web.sh`

### Prerequisites

Before running the website, ensure you have the following installed on your system:

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Visual Studio Code (vscode)

### Step 1: Open the OWASP MAS Website Repository in vscode

Run the following commands in your terminal:

```bash
cd mas-website
code .
```

### Step 2: Install Python Dependencies

It is highly recommended to use a virtual environment (venv) to manage dependencies and avoid conflicts with other Python projects.

Use vscode's [`Command Palette`](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) (Press `⌘+Shift+P` on macOS or `Ctrl+Shift+P` on Windows/Linux)

1. Create a venv:
    - Press `⌘+Shift+P` -> `Python: Create Environment`
    - Select `"Quick Create"`
2. Select the venv as the Python interpreter:
    - Press `⌘+Shift+P` -> `Python: Select Interpreter`
    - Choose the venv you just created.
3. Install the dependencies
   - Press `⌘+j` to open the terminal
   - Run `pip install -r src/scripts/requirements.txt`

### Step 3: Run the Website

Run the following command in the terminal:

```bash
./run_web.sh
```

The script runs `mkdocs serve` with some additional arguments. Open the script in a code editor for more information.

Access the website at [http://localhost:8000](http://localhost:8000).

### Step 4: Debugging the Website

To debug the website:

- Go to `Run and Debug` in vscode (or press `⌘+Shift+D` on macOS)
- Select `Python: MkDocs Serve`
- Click the green play button to start debugging
- Set breakpoints in the code as needed

## Using Docker

The following commands will clone the necessary repositories, build the Docker image, and run the website, which will be accessible at [http://localhost:8000](http://localhost:8000).

```bash
cd mas-website
docker build . -t mas-website
docker run --rm -it \
  -p 8000:8000 \
  -u $(id -u):$(id -g) \
  -e GITHUB_TOKEN \
  -v "$PWD":/workspaces/mas-website \
  -v "../mastg":/workspaces/mastg \
  -v "../masvs":/workspaces/masvs \
  -v "../maswe":/workspaces/maswe \
  mas-website
```
