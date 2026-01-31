# OWASP MAS Website - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Build the Repository

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   - Takes approximately 20-25 seconds
   - Requires Python 3.8 or higher (Python 3.12+ recommended)

2. **Clone external repositories**:
   ```bash
   mkdir -p repos/mastg repos/maswe repos/masvs
   git clone --depth 1 https://github.com/OWASP/mastg.git repos/mastg
   git clone --depth 1 https://github.com/OWASP/maswe.git repos/maswe
   git clone --depth 1 https://github.com/OWASP/masvs.git repos/masvs
   ```
   - Takes approximately 3-5 seconds total
   - **CRITICAL**: The external repos are required for the build to work

3. **Generate MASVS YAML file**:
   ```bash
   MASVS_VERSION=$(curl -s https://api.github.com/repos/OWASP/masvs/releases/latest | jq -r '.tag_name' 2>/dev/null || echo "v2.1.0")
   python3 repos/masvs/tools/generate_masvs_yaml.py -v "$MASVS_VERSION" -i repos/masvs/Document -c repos/masvs/controls
   ```

4. **Build the website**:
   ```bash
   mkdocs build --clean --verbose
   ```
   - Takes approximately 65-70 seconds. **NEVER CANCEL**. Set timeout to 120+ minutes.
   - Produces 1700+ HTML files in the `site/` directory
   - **CRITICAL TIMING**: Always use timeout of 120+ minutes for build commands

### Development Server

1. **Start the development server**:
   ```bash
   ./run_web.sh
   ```
   - Alternative: `mkdocs serve -a localhost:8000`
   - Takes approximately 65 seconds to start. **NEVER CANCEL**. Set timeout to 120+ minutes.
   - Serves website on http://localhost:8000
   - **CRITICAL TIMING**: Always use timeout of 120+ minutes for serve commands

2. **GitHub Token (Optional)**:
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```
   - Without token: Shows warnings but works with limited functionality
   - With token: Enables GitHub API features but may fail with invalid tokens
   - Create token at: https://github.com/settings/personal-access-tokens

## Validation

### Build Validation
- Always validate that build completes successfully:
  ```bash
  mkdocs build --clean
  ls site/index.html  # Should exist
  find site/ -name "*.html" | wc -l  # Should show 1700+ files
  ```

### Development Server Validation
- Always test that the server responds:
  ```bash
  curl -I http://localhost:8000  # Should return HTTP 200
  ```

### Manual Testing Scenarios
- **ALWAYS** run through these scenarios after making changes:
  1. **Homepage load**: Visit http://localhost:8000 and verify the homepage loads
  2. **Navigation test**: Navigate to MASTG section and verify content loads
  3. **Search functionality**: Test the search feature works
  4. **Cross-references**: Verify internal links work between sections

## CI/CD and Validation

### GitHub Actions Workflows
- **Build validation**: `.github/workflows/check-website-build.yml` runs on PRs
- **Deployment**: `.github/workflows/build-website.yml` runs on main branch
- Always ensure your changes pass the build check workflow

### No Additional Linting
- This repository does not include Python linting tools (black, flake8, etc.)
- The main validation is successful MkDocs build and deployment

## Repository Structure

### Key Files and Directories
- `mkdocs.yml`: Main configuration file for the website
- `requirements.txt`: Python dependencies
- `run_web.sh`: Development server script
- `docs/`: Website content and static files
- `docs/hooks/`: Custom MkDocs hooks for processing content
- `repos/`: External repositories (auto-generated, not committed)
- `site/`: Built website (auto-generated, not committed)

### External Dependencies
The website aggregates content from three external repositories:
- **MASTG**: https://github.com/OWASP/mastg (master branch)
- **MASVS**: https://github.com/OWASP/masvs (master branch)  
- **MASWE**: https://github.com/OWASP/maswe (main branch)

### Common File Locations
```
/home/runner/work/mas-website/mas-website/
├── mkdocs.yml                    # Main config
├── requirements.txt              # Python deps
├── run_web.sh                   # Dev server script
├── docs/
│   ├── hooks/                   # Custom processing
│   ├── contributing/            # Contribution guides
│   └── news/                    # Blog posts
├── repos/                       # External repos (generated)
│   ├── mastg/
│   ├── masvs/
│   └── maswe/
└── site/                        # Built website (generated)
```

## Troubleshooting

### Common Issues
1. **Build fails with "Could not find mastg repository"**:
   - Solution: Clone the external repositories to `repos/` directory

2. **Server shows GitHub API warnings**:
   - Expected behavior without GITHUB_TOKEN
   - Set GITHUB_TOKEN environment variable to enable full functionality

3. **Build takes very long or appears stuck**:
   - **NORMAL BEHAVIOR**: Build takes 65-70 seconds
   - **NEVER CANCEL**: Always wait for completion
   - Use timeouts of 120+ minutes to avoid premature cancellation

4. **Server startup is slow**:
   - **NORMAL BEHAVIOR**: Development server takes 65 seconds to start
   - **NEVER CANCEL**: Always wait for "Serving on http://localhost:8000/" message

### Expected Warnings
- Multiple "contains a link but target not found" warnings are normal
- "GitHub Token not set" warnings are normal without token
- Broken internal links warnings are expected from external content

## Performance Expectations

### Timing Summary (Never Cancel These Operations)
- **Dependency install**: 20-25 seconds
- **Repo cloning**: 3-5 seconds  
- **Build process**: 65-70 seconds (**SET 120+ MINUTE TIMEOUT**)
- **Server startup**: 65 seconds (**SET 120+ MINUTE TIMEOUT**)
- **Total setup**: ~2-3 minutes from fresh clone

### Resource Usage
- **Disk**: ~100MB for dependencies, ~500MB for external repos
- **Memory**: ~500MB during build, ~200MB for serving
- **Files**: 1700+ HTML files generated