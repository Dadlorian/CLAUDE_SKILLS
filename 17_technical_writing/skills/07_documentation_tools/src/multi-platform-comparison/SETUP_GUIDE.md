# Complete Setup Guide

Step-by-step guide to set up and run each documentation platform.

## Prerequisites

All platforms require:
- Git
- Code editor (VS Code recommended)
- Terminal/Command line

## Platform-Specific Prerequisites

### Docusaurus

- Node.js 18+ (https://nodejs.org/)
- npm or yarn

### MkDocs

- Python 3.9+ (https://www.python.org/)
- pip

### Hugo

- Hugo 0.112+ (https://gohugo.io/)
- No runtime dependencies!

### VitePress

- Node.js 18+ (https://nodejs.org/)
- npm or yarn

## Step-by-Step Setup

### 1. Docusaurus Setup

**Installation:**
```bash
cd docusaurus-complete-setup
npm install
```

**Development:**
```bash
npm start
```

Visit: http://localhost:3000

**Production Build:**
```bash
npm run build
npm run serve
```

**Key Files to Customize:**
- `docusaurus.config.js` - Site configuration
- `sidebars.js` - Navigation structure
- `docs/` - Content files
- `src/css/custom.css` - Styling

**Typical First Customizations:**
1. Change site title in `docusaurus.config.js`
2. Update favicon and logo
3. Modify sidebar structure in `sidebars.js`
4. Replace sample content in `docs/`
5. Customize colors in `src/css/custom.css`

### 2. MkDocs Setup

**Installation:**
```bash
cd mkdocs-complete-setup
pip install -r requirements.txt
```

**Development:**
```bash
mkdocs serve
```

Visit: http://localhost:8000

**Production Build:**
```bash
mkdocs build
```

**Key Files to Customize:**
- `mkdocs.yml` - Site configuration
- `docs/` - Content files
- `overrides/` - Theme customization
- `docs/assets/custom.css` - Styling

**Typical First Customizations:**
1. Update site_name in `mkdocs.yml`
2. Configure navigation structure
3. Replace sample content
4. Customize theme colors
5. Add custom CSS

### 3. Hugo Setup

**Installation:**
```bash
cd hugo-complete-setup
# Hugo binary already included in most package managers
hugo version
```

**Development:**
```bash
hugo server -D
```

Visit: http://localhost:1313

**Production Build:**
```bash
hugo --minify
```

**Key Files to Customize:**
- `config.toml` - Site configuration
- `content/` - Content files
- `themes/` - Theme customization
- `static/` - Static assets

**Typical First Customizations:**
1. Update baseURL in `config.toml`
2. Change site title
3. Configure navigation menu
4. Replace sample content
5. Customize theme

### 4. VitePress Setup

**Installation:**
```bash
cd vitepress-complete-setup
npm install
```

**Development:**
```bash
npm run docs:dev
```

Visit: http://localhost:5173

**Production Build:**
```bash
npm run docs:build
npm run docs:serve
```

**Key Files to Customize:**
- `docs/.vitepress/config.ts` - Site configuration
- `docs/` - Content files
- `docs/.vitepress/theme/` - Custom theme
- `docs/public/` - Static assets

**Typical First Customizations:**
1. Update config in `docs/.vitepress/config.ts`
2. Customize sidebar navigation
3. Replace sample content
4. Add custom Vue components
5. Modify theme styles

## Common Tasks

### Adding a New Page

#### Docusaurus
```markdown
---
title: New Page
description: Description here
sidebar_position: 5
---

# New Page

Content...
```

Then add to `sidebars.js`.

#### MkDocs
```markdown
---
title: New Page
description: Description here
---

# New Page

Content...
```

Then add to `mkdocs.yml` nav.

#### Hugo
```markdown
---
title: "New Page"
description: "Description here"
weight: 5
---

# New Page

Content...
```

Then add to `config.toml` menu.

#### VitePress
```markdown
---
title: New Page
description: Description here
---

# New Page

Content...
```

Then add to `docs/.vitepress/config.ts` sidebar.

### Changing Colors

#### Docusaurus
Edit `src/css/custom.css`:
```css
:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
}
```

#### MkDocs
Edit `mkdocs.yml`:
```yaml
theme:
  palette:
    - scheme: light
      primary: green
      accent: lime
```

#### Hugo
Edit `static/css/custom.css` or theme.

#### VitePress
Edit `docs/.vitepress/theme/custom.css`:
```css
:root {
  --vp-c-primary: #2e8555;
}
```

### Adding Images

#### Docusaurus
Place in `static/img/` and reference:
```markdown
![Alt text](/img/image.png)
```

#### MkDocs
Place in `docs/assets/` and reference:
```markdown
![Alt text](assets/image.png)
```

#### Hugo
Place in `static/img/` and reference:
```markdown
![Alt text](/img/image.png)
```

#### VitePress
Place in `docs/public/` and reference:
```markdown
![Alt text](/image.png)
```

## Verification Checklist

After setup, verify:

- [ ] Development server starts
- [ ] Site loads at localhost
- [ ] Navigation works
- [ ] Search functions (if enabled)
- [ ] Sample content displays
- [ ] Static assets load
- [ ] Production build completes
- [ ] Mobile responsive
- [ ] Dark mode works (if applicable)

## Deployment Preparation

### 1. Configure Domain

Update configuration with your domain:
- Set `baseURL` / `url` / domain
- Generate sitemap
- Set up DNS records

### 2. Build Optimization

```bash
# Docusaurus
npm run build

# MkDocs
mkdocs build --strict

# Hugo
hugo --minify

# VitePress
npm run docs:build
```

### 3. Test Build Output

```bash
# Verify build directory
ls -la build/   # Docusaurus
ls -la site/    # MkDocs
ls -la public/  # Hugo
ls -la docs/.vitepress/dist/  # VitePress
```

### 4. Deploy

```bash
# See DEPLOYMENT.md for detailed instructions
```

## Troubleshooting

### Port Already in Use

**Docusaurus:**
```bash
npm start -- --port 3001
```

**MkDocs:**
```bash
mkdocs serve -a 0.0.0.0:8001
```

**Hugo:**
```bash
hugo server -p 1314
```

**VitePress:**
```bash
npm run docs:dev -- --port 3000
```

### Dependency Issues

**Docusaurus:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**MkDocs:**
```bash
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Hugo:**
```bash
hugo mod get -u
```

**VitePress:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Build Failing

**Docusaurus:**
```bash
npm run clear
npm run build
```

**MkDocs:**
```bash
mkdocs build --strict
```

**Hugo:**
```bash
hugo -v
```

**VitePress:**
```bash
npm run docs:build --verbose
```

## Performance Tips

### General
- Minimize number of plugins
- Optimize images
- Use appropriate asset sizes
- Cache static files

### Docusaurus
- Use code splitting
- Lazy load heavy components
- Optimize assets with ideal-image plugin

### MkDocs
- Use minify plugin
- Enable search caching
- Compress images

### Hugo
- Use webp format
- Minimize CSS/JS
- Use asset pipelining

### VitePress
- Lazy load Vue components
- Use script setup
- Minimize dynamic imports

## Learning Resources

### Docusaurus
- Official docs: https://docusaurus.io/
- Tutorial: https://docusaurus.io/docs/category/getting-started
- Showcase: https://docusaurus.io/showcase

### MkDocs
- Official docs: https://www.mkdocs.org/
- Material theme: https://squidfunk.github.io/mkdocs-material/
- Plugins: https://www.mkdocs.org/user-guide/plugins/

### Hugo
- Official docs: https://gohugo.io/
- Themes: https://themes.gohugo.io/
- Tutorial: https://gohugo.io/getting-started/

### VitePress
- Official docs: https://vitepress.dev/
- GitHub: https://github.com/vuejs/vitepress
- Examples: https://vitepress.dev/guide/using-vue

## Next Steps

1. **Customize** your chosen platform
2. **Add content** - Replace sample files
3. **Test thoroughly** - All links, search, mobile
4. **Deploy** - Choose your hosting
5. **Monitor** - Set up analytics and tracking

## Quick Reference

| Task | Docusaurus | MkDocs | Hugo | VitePress |
|------|-----------|--------|------|-----------|
| Install | `npm i` | `pip install -r` | `brew install` | `npm i` |
| Dev server | `npm start` | `mkdocs serve` | `hugo server` | `npm run docs:dev` |
| Build | `npm run build` | `mkdocs build` | `hugo` | `npm run docs:build` |
| Config file | docusaurus.config.js | mkdocs.yml | config.toml | .vitepress/config.ts |
| Content dir | docs/ | docs/ | content/ | docs/ |
| Output dir | build/ | site/ | public/ | docs/.vitepress/dist/ |

## Support

For platform-specific issues:
- Check respective official documentation
- Review sample content in each setup
- Check community forums
- File issues on GitHub repositories

---

Start with your preferred platform and follow the specific setup section above!
