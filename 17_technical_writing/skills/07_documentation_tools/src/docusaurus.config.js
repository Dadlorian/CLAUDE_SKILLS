// docusaurus.config.js
// Production-ready Docusaurus configuration

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

module.exports = {
  // Basic site information
  title: 'My Awesome API',
  tagline: 'Comprehensive documentation for developers',
  url: 'https://docs.example.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  // Organization info
  organizationName: 'example',
  projectName: 'documentation',

  // Internationalization
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'fr', 'ja', 'zh-CN'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
      },
      es: {
        label: 'Español',
        direction: 'ltr',
      },
      fr: {
        label: 'Français',
        direction: 'ltr',
      },
      ja: {
        label: '日本語',
        direction: 'ltr',
      },
      'zh-CN': {
        label: '简体中文',
        direction: 'ltr',
      },
    },
  },

  // Presets
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Edit URL for GitHub
          editUrl: 'https://github.com/example/documentation/tree/main/',
          // Show "Last Updated" timestamp
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/example/documentation/tree/main/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  // Plugins
  plugins: [
    // Local search (no external dependencies)
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en', 'es', 'fr', 'ja', 'zh'],
      },
    ],
    // API documentation plugin
    [
      'docusaurus-plugin-openapi-docs',
      {
        id: 'openapi',
        docsPluginId: 'classic',
        config: {
          petstore: {
            specPath: 'openapi/petstore.json',
            outputDir: 'docs/petstore',
            downloadUrl: 'https://example.com/openapi.json',
          },
        },
      },
    ],
  ],

  // Theme configuration
  themeConfig: {
    // Image for social sharing
    image: 'img/social-card.png',

    // Navigation bar
    navbar: {
      title: 'My Docs',
      logo: {
        alt: 'My Logo',
        src: 'img/logo.svg',
      },
      items: [
        // Documentation dropdown
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          label: 'Documentation',
          position: 'left',
        },
        // API Reference
        {
          type: 'docSidebar',
          sidebarId: 'apiSidebar',
          label: 'API Reference',
          position: 'left',
        },
        // Blog
        {
          to: '/blog',
          label: 'Blog',
          position: 'left',
        },
        // Version dropdown
        {
          type: 'docsVersionDropdown',
          position: 'right',
          dropdownActiveClassDisabled: true,
          dropdownItemsAfter: [
            {
              to: '/versions',
              label: 'All versions',
            },
          ],
        },
        // Language dropdown
        {
          type: 'localeDropdown',
          position: 'right',
        },
        // GitHub link
        {
          href: 'https://github.com/example/documentation',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    // Footer
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started',
            },
            {
              label: 'API Reference',
              to: '/docs/api/introduction',
            },
            {
              label: 'Guides',
              to: '/docs/guides',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.com/invite/example',
            },
            {
              label: 'GitHub Discussions',
              href: 'https://github.com/example/discussions',
            },
            {
              label: 'Stack Overflow',
              href: 'https://stackoverflow.com/questions/tagged/example',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'Status Page',
              href: 'https://status.example.com',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/example',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Example Inc. All rights reserved.`,
    },

    // Theme colors and styles
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    // Prism (code highlighting) configuration
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['bash', 'python', 'javascript', 'typescript', 'json', 'yaml', 'rust', 'go'],
    },

    // Search configuration (Algolia)
    algolia: {
      // The Algolia appId you have in your Algolia dashboard
      appId: 'YOUR_ALGOLIA_APP_ID',
      // Public API key: it is safe to commit it
      apiKey: 'YOUR_ALGOLIA_API_KEY',
      // The index name for your site
      indexName: 'docs',
      // Optional: specify whether the search page should be opened on initial load
      contextualSearch: true,
      // Optional: Specify domains where the navigation should occur through window.location instead on history.push
      externalUrlRegex: 'external\\.com|domain\\.com',
      // Optional: Algolia search parameters
      searchParameters: {},
      // Optional: path for search page that enabled this search functionality
      searchPagePath: 'search',
    },

    // Announcement bar
    announcementBar: {
      id: 'v2-migration',
      content:
        '⚠️ <strong>API v1 is deprecated</strong>. <a href="/docs/migration-guide">Migrate to v2</a> by December 2026.',
      backgroundColor: '#fbbf24',
      textColor: '#000',
      isCloseable: true,
    },
  },

  // Additional metadata
  metadata: [
    {
      name: 'google-site-verification',
      content: 'YOUR_GOOGLE_SITE_VERIFICATION',
    },
    {
      name: 'theme-color',
      content: '#3b82f6',
    },
  ],

  // Scripts
  scripts: [
    {
      src: 'https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX',
      async: true,
    },
  ],

  // Client modules
  clientModules: [
    require.resolve('./src/clientModule'),
  ],
};
