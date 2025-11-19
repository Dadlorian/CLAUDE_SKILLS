import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Project Documentation',
  description: 'Comprehensive documentation for Project',

  head: [
    ['meta', { name: 'theme-color', content: '#3c8772' }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:locale', content: 'en' }],
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap' }],
  ],

  lastUpdated: true,
  cleanUrls: true,
  metaChunk: true,

  markdown: {
    math: true,
    codeTransformers: [
      {
        preprocess(code) {
          return code.replace(/\r\n/g, '\n')
        },
      },
    ],
  },

  sitemap: {
    hostname: 'https://docs.example.com',
    lastmodDateOnly: true,
  },

  themeConfig: {
    logo: {
      light: '/logo-light.svg',
      dark: '/logo-dark.svg',
    },

    nav: [
      { text: 'Home', link: '/' },
      { text: 'Getting Started', link: '/getting-started/installation' },
      { text: 'API Reference', link: '/api/overview' },
      { text: 'Guides', link: '/guides/rest-integration' },
      { text: 'Deployment', link: '/deployment/overview' },
      {
        text: 'Community',
        items: [
          { text: 'GitHub', link: 'https://github.com/organization/project' },
          { text: 'Discord', link: 'https://discord.gg/example' },
          { text: 'Twitter', link: 'https://twitter.com/example' },
        ],
      },
    ],

    sidebar: {
      '/getting-started/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/getting-started/' },
            { text: 'Installation', link: '/getting-started/installation' },
            { text: 'Configuration', link: '/getting-started/configuration' },
            { text: 'Quick Start', link: '/getting-started/quick-start' },
          ],
        },
      ],
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Overview', link: '/api/overview' },
            { text: 'Users Endpoint', link: '/api/users' },
            { text: 'Projects Endpoint', link: '/api/projects' },
            { text: 'Error Codes', link: '/api/errors' },
            { text: 'Rate Limits', link: '/api/rate-limits' },
          ],
        },
      ],
      '/guides/': [
        {
          text: 'Guides',
          items: [
            { text: 'REST Integration', link: '/guides/rest-integration' },
            { text: 'Webhook Setup', link: '/guides/webhooks' },
            { text: 'Authentication', link: '/guides/authentication' },
            { text: 'Best Practices', link: '/guides/best-practices' },
          ],
        },
      ],
      '/deployment/': [
        {
          text: 'Deployment',
          items: [
            { text: 'Overview', link: '/deployment/overview' },
            { text: 'Docker', link: '/deployment/docker' },
            { text: 'Kubernetes', link: '/deployment/kubernetes' },
            { text: 'Cloud Providers', link: '/deployment/cloud-providers' },
            { text: 'Monitoring', link: '/deployment/monitoring' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/organization/project' },
      { icon: 'twitter', link: 'https://twitter.com/example' },
      { icon: 'discord', link: 'https://discord.gg/example' },
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present Organization',
    },

    editLink: {
      pattern: 'https://github.com/organization/project-docs/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },

    search: {
      provider: 'local',
      options: {
        translations: {
          button: {
            buttonText: 'Search',
            buttonAriaLabel: 'Search Documentation',
          },
          modal: {
            noResultsText: 'No results found',
            resetButtonTitle: 'Reset search',
            footer: {
              selectText: 'to select',
              navigateText: 'to navigate',
              closeText: 'to close',
            },
          },
        },
      },
    },

    docFooter: {
      prev: 'Previous',
      next: 'Next',
    },
  },
})
