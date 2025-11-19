/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a set of docs in a dedicated sidebar
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

module.exports = {
  docsSidebar: {
    'Getting Started': [
      'intro',
      'installation',
      'configuration',
      'quick-start',
    ],
    'Core Concepts': [
      {
        type: 'category',
        label: 'Fundamentals',
        items: [
          'concepts/architecture',
          'concepts/data-model',
          'concepts/lifecycle',
        ],
      },
      {
        type: 'category',
        label: 'Advanced',
        items: [
          'concepts/optimization',
          'concepts/scaling',
          'concepts/security',
        ],
      },
    ],
    'API Reference': [
      'api/overview',
      {
        type: 'category',
        label: 'Endpoints',
        items: [
          'api/endpoints/users',
          'api/endpoints/projects',
          'api/endpoints/tasks',
        ],
      },
      'api/errors',
      'api/rate-limits',
    ],
    'Guides': [
      {
        type: 'category',
        label: 'Integration',
        items: [
          'guides/rest-integration',
          'guides/webhook-setup',
          'guides/authentication',
        ],
      },
      {
        type: 'category',
        label: 'Best Practices',
        items: [
          'guides/performance',
          'guides/security',
          'guides/error-handling',
        ],
      },
      {
        type: 'category',
        label: 'Tutorials',
        items: [
          'guides/tutorial-setup',
          'guides/tutorial-first-api-call',
          'guides/tutorial-advanced-workflow',
        ],
      },
    ],
    'Deployment': [
      'deployment/overview',
      'deployment/docker',
      'deployment/kubernetes',
      'deployment/cloud-providers',
      'deployment/monitoring',
    ],
    'Reference': [
      'reference/changelog',
      'reference/faq',
      'reference/glossary',
      'reference/roadmap',
    ],
  },
};
