# Migration Guide

Complete guide for migrating between documentation platforms.

## Pre-Migration Checklist

- [ ] Audit current documentation
- [ ] Identify all content types
- [ ] Document custom features
- [ ] List all plugins/extensions
- [ ] Plan timeline
- [ ] Set up parallel environment
- [ ] Test on subset of content first

## Content Preparation

### Export Content

#### From Docusaurus
```bash
# Content is in /docs directory
# Export all Markdown files
cp -r docs/* exported-content/
```

#### From MkDocs
```bash
# Content is in /docs directory
# Export all Markdown files
cp -r docs/* exported-content/
```

#### From Hugo
```bash
# Content is in /content directory
# Export with frontmatter
cp -r content/* exported-content/
```

#### From VitePress
```bash
# Content is in /docs directory
# Export with frontmatter
cp -r docs/* exported-content/
```

### Normalize Markdown

Create a script to normalize frontmatter:

```python
import re
import os

def normalize_frontmatter(content):
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return content

    frontmatter = match.group(1)
    body = match.group(2)

    # Normalize key-value pairs
    lines = frontmatter.split('\n')
    normalized = {}

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            normalized[key.strip()] = value.strip()

    # Reconstruct with new platform format
    return build_frontmatter(normalized) + body

for root, dirs, files in os.walk('exported-content'):
    for file in files:
        if file.endswith('.md'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()

            normalized = normalize_frontmatter(content)

            with open(path, 'w') as f:
                f.write(normalized)
```

## Migration Paths

### Docusaurus → MkDocs

**Time estimate**: 2-4 hours (50 pages)

**Steps:**

1. Export Docusaurus content
```bash
cp -r docusaurus/docs/* mkdocs/docs/
```

2. Convert config
```yaml
# mkdocs.yml
site_name: My Project
theme:
  name: material
```

3. Update navigation
```yaml
nav:
  - Home: index.md
  - Docs:
    - Installation: installation.md
```

4. Adapt component references
- Remove React/MDX components
- Replace with Markdown equivalents
- Use MkDocs admonitions

5. Test build
```bash
mkdocs build
```

**Special considerations:**
- Docusaurus v2 versioning → Use MkDocs versioning plugin
- React components → Markdown or macros
- Sidebar structure → nav in mkdocs.yml

### MkDocs → Hugo

**Time estimate**: 3-6 hours (50 pages)

**Steps:**

1. Export MkDocs content
```bash
mkdir -p hugo/content/en
cp -r mkdocs/docs/* hugo/content/en/
```

2. Create Hugo config
```toml
baseURL = "https://example.com/"
languageCode = "en-us"
title = "My Project"
theme = "docs"
```

3. Restructure content
```
Hugo structure:
content/
  _index.md
  docs/
    _index.md
    installation.md
```

4. Create custom menu
```toml
[[menu.main]]
name = "Docs"
url = "/docs/"
```

5. Test build
```bash
hugo -D
```

**Special considerations:**
- MkDocs nav → Hugo menus
- Material theme → Find Hugo theme
- Plugins → Themes or shortcodes
- CSS customization → assets/css/

### Hugo → Docusaurus

**Time estimate**: 4-8 hours (50 pages)

**Steps:**

1. Export Hugo content
```bash
cp -r hugo/content/* docusaurus/docs/
```

2. Initialize Docusaurus
```bash
npx create-docusaurus@latest my-docs classic
```

3. Restructure content
```
Docusaurus:
docs/
  intro.md
  installation.md
  api/
    overview.md
```

4. Create sidebars.js
```javascript
module.exports = {
  docsSidebar: {
    'Getting Started': ['intro', 'installation'],
    'API': ['api/overview']
  }
}
```

5. Configure docusaurus.config.js
- Set site URL
- Configure theme
- Add plugins

6. Test build
```bash
npm run build
```

**Special considerations:**
- Hugo shortcodes → React components
- Menu structure → sidebar configuration
- Asset paths → /static directory
- Custom CSS → src/css/custom.css

### VitePress ↔ Others

**From VitePress:**

1. Export content
```bash
cp -r docs/*.md exported/
```

2. Remove VitePress-specific syntax
- Vue components → Markdown
- Import statements → Code blocks
- Custom directives → Remove

**To VitePress:**

1. Copy Markdown files
```bash
cp -r other-docs/*.md vitepress/docs/
```

2. Create .vitepress/config.ts
3. Restructure if needed
4. Add Vue components if desired

## Link Migration

### Update Internal Links

**From relative to format-specific:**

```python
import re

def update_links(content, platform):
    # Docusaurus: [link](/docs/guide)
    # MkDocs: [link](guide.md)
    # Hugo: [link]({{< ref "guide" >}})
    # VitePress: [link](/guide)

    if platform == 'mkdocs':
        # Convert /docs/guide to guide.md
        content = re.sub(
            r'\[([^\]]+)\]\(/([^)]+)\)',
            r'[\1](\2.md)',
            content
        )

    return content
```

### Asset Path Updates

```
# Before (MkDocs)
![Image](../../assets/image.png)

# After (Hugo)
![Image](/images/image.png)

# After (Docusaurus)
![Image](/img/image.png)
```

## Configuration Migration

### Search Configuration

#### From Docusaurus (Algolia)
```javascript
algolia: {
  appId: 'XXXX',
  apiKey: 'XXXX',
  indexName: 'docs'
}
```

#### To MkDocs
```yaml
plugins:
  - search
```

#### To Hugo
```bash
# Build search index via script
hugo-lunr
```

## Testing Checklist

- [ ] All pages render
- [ ] Internal links work
- [ ] Images load
- [ ] Code blocks display correctly
- [ ] Navigation structure is correct
- [ ] Search functionality works
- [ ] Mobile responsive
- [ ] Dark mode works (if applicable)
- [ ] Performance acceptable
- [ ] Accessibility validated
- [ ] 404 pages configured
- [ ] Redirects set up

## Deployment Migration

### Update CI/CD Pipeline

**GitHub Actions Example:**

```yaml
# MkDocs
- name: Build docs
  run: mkdocs build

# Hugo
- name: Build docs
  run: hugo -D

# Docusaurus
- name: Build docs
  run: npm run build

# VitePress
- name: Build docs
  run: npm run docs:build
```

### Update DNS/Hosting

1. Update CNAME record if needed
2. Configure SSL certificate
3. Update sitemap.xml
4. Set up redirects
5. Test from multiple locations

## Rollback Plan

- Keep old documentation accessible
- Set up 301 redirects from old URLs
- Test all redirects
- Monitor 404 errors
- Maintain old build for reference
- Plan 30-day grace period

## Performance Comparison Post-Migration

```bash
# Compare build times
time mkdocs build
time hugo -D
time npm run build
time npm run docs:build

# Compare output size
du -sh mkdocs/site/
du -sh hugo/public/
du -sh docusaurus/build/
du -sh vitepress/docs/.vitepress/dist/

# Test accessibility
axe-core yoursite.com
```

## Common Issues & Solutions

### Issue: Links Break After Migration

**Solution:**
1. Use migration script to update links
2. Set up comprehensive redirects
3. Test all internal links

### Issue: Images Don't Load

**Solution:**
1. Verify asset directory structure
2. Check image path references
3. Update paths in migration script
4. Test on multiple pages

### Issue: Search Doesn't Work

**Solution:**
1. Rebuild search index
2. Verify search configuration
3. Check for indexing errors
4. Test search functionality

### Issue: Styling Looks Wrong

**Solution:**
1. Check CSS imports
2. Verify theme is installed
3. Review custom CSS
4. Test in multiple browsers

## Success Metrics

- 100% of content migrated
- All links functional
- Build time < expected
- Search working properly
- Mobile responsive
- Accessibility passing
- SEO score improved
- User feedback positive

## Timeline Example (50 pages)

| Phase | Time | Tasks |
|-------|------|-------|
| Planning | 1 day | Review, prepare, plan |
| Export | 2 hours | Extract all content |
| Normalize | 2 hours | Fix frontmatter, links |
| Build | 4 hours | Set up new platform |
| Test | 4 hours | Verify all content |
| Deploy | 2 hours | Set up hosting/DNS |
| Rollout | 1 day | Go live, monitor |
| Cleanup | 1 day | Fix issues, optimize |

**Total: 3-4 weeks for production migration**
