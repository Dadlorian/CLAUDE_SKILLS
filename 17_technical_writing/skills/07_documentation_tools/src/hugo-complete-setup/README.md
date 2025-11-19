# Hugo Complete Setup

Production-ready Hugo documentation site with complete configuration, content, and deployment.

## What's Included

- ✅ Hugo 0.121.x configuration
- ✅ Documentation theme setup
- ✅ Complete content structure
- ✅ API documentation
- ✅ Blog section
- ✅ Docker and Docker Compose setup
- ✅ GitHub Actions CI/CD
- ✅ Search capability
- ✅ Responsive design
- ✅ SEO optimization

## Quick Start

### 1. Install Hugo

```bash
# macOS
brew install hugo

# Ubuntu
sudo apt-get install hugo

# Windows
choco install hugo
```

### 2. Start Development Server

```bash
hugo server -D
```

Visit http://localhost:1313

### 3. Build for Production

```bash
hugo --minify
```

### 4. Deploy

#### GitHub Pages
```bash
hugo --minify --baseURL https://username.github.io/project/
```

#### Docker
```bash
docker build -t my-docs:latest .
docker run -p 1313:80 my-docs:latest
```

#### Docker Compose
```bash
docker-compose up -d
```

## Project Structure

```
hugo-complete-setup/
├── content/
│   ├── _index.md                # Home page
│   ├── docs/
│   │   ├── _index.md
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── architecture.md
│   ├── api/
│   │   ├── _index.md
│   │   ├── users.md
│   │   └── errors.md
│   ├── guides/
│   └── blog/
├── layouts/
│   ├── index.html
│   ├── _default/
│   │   ├── single.html
│   │   └── list.html
│   └── partials/
├── static/
│   ├── img/
│   ├── css/
│   └── js/
├── themes/                      # Hugo themes
├── config.toml                  # Configuration
├── Dockerfile
├── docker-compose.yml
└── .github/
    └── workflows/
        └── deploy.yml
```

## Configuration

### Basic Settings

Edit `config.toml`:

```toml
baseURL = "https://docs.example.com/"
languageCode = "en-us"
title = "My Documentation"
theme = "docs"

[params]
  author = "Your Name"
  description = "Documentation guide"
```

### Menu Configuration

```toml
[[menu.main]]
  name = "Home"
  url = "/"
  weight = 1

[[menu.main]]
  name = "Docs"
  url = "/docs/"
  weight = 2

[[menu.main]]
  name = "API"
  url = "/api/"
  weight = 3
```

## Features

### 1. Fast Performance

- Build time: <100ms
- Minimal dependencies
- Excellent for large sites
- Static HTML output

### 2. Content Organization

- Hierarchical content structure
- Sections and taxonomies
- Categories and tags
- Related content

### 3. Customization

- Template inheritance
- Partial templates
- Shortcodes
- Custom CSS

### 4. SEO Optimization

- Automatic sitemaps
- Meta tags
- Open Graph support
- Structured data

## Creating Content

### Add New Documentation Page

Create `content/docs/page-name.md`:

```markdown
---
title: "Page Title"
description: "Page description"
weight: 10
---

# Page Title

Content here...
```

### Add Blog Post

Create `content/blog/post-name.md`:

```markdown
---
title: "Post Title"
date: 2024-01-15
categories:
  - announcement
tags:
  - important
---

Post content...
```

## Customization

### Custom CSS

Edit `static/css/custom.css`:

```css
body {
  font-family: 'Custom Font', sans-serif;
}

.container {
  max-width: 1200px;
}
```

### Custom Layouts

Create `layouts/_default/custom.html`:

```html
{{ define "main" }}
  <main>
    <h1>{{ .Title }}</h1>
    {{ .Content }}
  </main>
{{ end }}
```

### Shortcodes

Create `layouts/shortcodes/highlight.html`:

```html
<div class="highlight">
  {{ .Inner }}
</div>
```

Use in Markdown:

```
{{< highlight >}}
Important content
{{< /highlight >}}
```

## Navigation

### Configure Menu Structure

In `config.toml`:

```toml
[[menu.main]]
  name = "Documentation"
  url = "/docs/"
  weight = 1

  [[menu.main]]
    name = "Installation"
    parent = "Documentation"
    url = "/docs/installation/"
```

### Add Breadcrumbs

Create `layouts/partials/breadcrumb.html`:

```html
<nav aria-label="breadcrumb">
  {{ partial "breadcrumb" . }}
</nav>
```

## Deployment

### GitHub Pages

```bash
hugo -D --baseURL https://username.github.io/
cd public
git push origin main
```

### Docker

```bash
docker build -t my-docs:latest .
docker run -p 1313:80 my-docs:latest
```

### Docker Compose

```bash
docker-compose up -d
```

### CI/CD Pipeline

GitHub Actions automatically builds and deploys on push.

## Search Implementation

### Using Lunr

Generate search index:

```bash
npm install -g hugo-lunr
hugo-lunr
```

Add search functionality to templates.

## Performance Optimization

### Image Optimization

Use Hugo image processing:

```html
{{ $image := resources.Get "image.jpg" }}
{{ $resized := $image.Resize "800x600 webp" }}
<img src="{{ $resized.RelPermalink }}" alt="...">
```

### CSS Minification

Build with minification:

```bash
hugo --minify
```

### Asset Pipelining

Configure in `config.toml`:

```toml
[minify]
  minifyOutput = true
```

## Production Checklist

- [ ] Set correct baseURL
- [ ] Update site title
- [ ] Configure analytics
- [ ] Test all links
- [ ] Test mobile responsiveness
- [ ] Generate sitemap
- [ ] Set up SSL/HTTPS
- [ ] Configure CDN
- [ ] Add robots.txt
- [ ] Verify SEO

## Troubleshooting

### Port Already in Use

```bash
hugo server -p 8000
```

### Content Not Showing

1. Check file location in `/content`
2. Verify frontmatter syntax
3. Run `hugo --verbose` for debugging

### Images Not Loading

1. Place images in `/static/img/`
2. Reference as `/img/filename.jpg`
3. Use absolute paths

### Theme Not Loading

```bash
git submodule add https://github.com/theme/repo themes/theme-name
```

## Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Hugo Themes](https://themes.gohugo.io/)
- [Go Templates](https://golang.org/pkg/text/template/)
- [Content Management](https://gohugo.io/content-management/)

## Performance Metrics

- Build time: <100ms
- Page load: <300ms
- Bundle size: 2-3MB
- Mobile optimized

## License

MIT
