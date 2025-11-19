// @ts-check
const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');
const math = require('remark-math');
const katex = require('rehype-katex');

const config = {
  title: 'Project Documentation',
  tagline: 'Comprehensive guide to our platform',
  url: 'https://docs.example.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  organizationName: 'organization',
  projectName: 'project-docs',
  deploymentBranch: 'gh-pages',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr', 'es'],
  },

  markdown: {
    mermaid: true,
    remarkPlugins: [math],
    rehypePlugins: [katex],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/organization/project-docs/tree/main/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          remarkPlugins: [
            [require('@docusaurus/remark-plugin-npm2yarn'), { sync: true }],
          ],
          admonitions: {
            keywords: ['note', 'tip', 'info', 'caution', 'danger', 'example', 'quote'],
          },
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/organization/project-docs/tree/main/',
          postsPerPage: 5,
          feedOptions: {
            type: 'all',
            copyright: `Copyright © ${new Date().getFullYear()} Organization`,
          },
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-ideal-image',
      {
        quality: 70,
        max: 1030,
        min: 640,
        steps: 2,
        disableInDev: false,
      },
    ],
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          {
            to: '/docs/intro',
            from: '/docs/getting-started',
          },
        ],
      },
    ],
    '@docusaurus/plugin-sitemap',
  ],

  themeConfig: {
    navbar: {
      title: 'Project Docs',
      logo: {
        alt: 'Project Logo',
        src: 'img/logo.svg',
        srcDark: 'img/logo-dark.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left',
        },
        {
          type: 'dropdown',
          label: 'Resources',
          position: 'left',
          items: [
            {
              label: 'API Reference',
              to: '/docs/api',
            },
            {
              label: 'Tutorials',
              to: '/docs/tutorials',
            },
            {
              label: 'FAQ',
              to: '/docs/faq',
            },
          ],
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/organization/project-docs',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'Installation',
              to: '/docs/installation',
            },
            {
              label: 'Configuration',
              to: '/docs/configuration',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/organization/project-docs',
            },
            {
              label: 'Discord',
              href: 'https://discord.gg/example',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/example',
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
              label: 'Status',
              href: 'https://status.example.com',
            },
            {
              label: 'Changelog',
              to: '/docs/changelog',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Organization. Built with Docusaurus.`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['bash', 'json', 'yaml', 'python', 'javascript', 'typescript'],
    },
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    algolia: {
      appId: 'YOUR_ALGOLIA_APP_ID',
      apiKey: 'YOUR_ALGOLIA_API_KEY',
      indexName: 'project_docs',
    },
    metadata: [
      {
        name: 'description',
        content: 'Comprehensive documentation for our platform',
      },
      {
        name: 'og:image',
        content: 'https://docs.example.com/img/og-image.png',
      },
    ],
  },
};

module.exports = config;
