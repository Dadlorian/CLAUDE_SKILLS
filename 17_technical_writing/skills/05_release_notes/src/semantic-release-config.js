/**
 * Semantic Release Configuration
 *
 * Complete semantic-release setup with comprehensive plugins and automation.
 * This configuration generates changelogs, manages versioning, and publishes releases
 * across multiple platforms (npm, GitHub, GitLab, etc.)
 *
 * Install: npm install --save-dev semantic-release
 *
 * @see https://semantic-release.gitbook.io/
 */

module.exports = {
  /**
   * Branch Release Configuration
   * Defines which branches trigger releases and how
   */
  branches: [
    {
      name: 'main',
      prerelease: false,
    },
    {
      name: 'next',
      prerelease: true,
    },
    {
      name: 'next-major',
      prerelease: true,
    },
    {
      name: 'beta',
      prerelease: true,
    },
    {
      name: 'alpha',
      prerelease: true,
    },
    {
      name: 'develop',
      prerelease: 'rc',
    },
  ],

  /**
   * Repository Configuration
   */
  repositoryUrl: 'https://github.com/organization/repository.git',

  /**
   * Tag Format
   * How version tags are formatted in git
   */
  tagFormat: 'v${version}',

  /**
   * Plugins Configuration
   * Plugins are executed in the order specified
   */
  plugins: [
    /**
     * Analyze Commits Plugin
     * Determines version bump based on conventional commits
     */
    [
      '@semantic-release/commit-analyzer',
      {
        preset: 'conventionalcommits',
        releaseRules: [
          // Custom release rules beyond defaults
          {
            type: 'docs',
            scope: 'README',
            release: 'patch',
            // Documentation changes to README trigger patch release
          },
          {
            type: 'refactor',
            release: 'patch',
            // Refactoring triggers patch release
          },
          {
            type: 'perf',
            release: 'patch',
            // Performance improvements trigger patch
          },
          {
            scope: 'no-release',
            release: false,
            // Skip release for commits with this scope
          },
        ],
        parserOpts: {
          noteKeywords: [
            'BREAKING CHANGE',
            'BREAKING-CHANGE',
            'BREAKING',
          ],
          issuePrefixes: ['#', 'GH-'],
        },
      },
    ],

    /**
     * Release Notes Generator Plugin
     * Generates changelog content
     */
    [
      '@semantic-release/release-notes-generator',
      {
        preset: 'conventionalcommits',
        presetConfig: {
          // Customize commit grouping and formatting
          types: [
            {
              type: 'feat',
              section: 'Features',
              hidden: false,
            },
            {
              type: 'fix',
              section: 'Bug Fixes',
              hidden: false,
            },
            {
              type: 'perf',
              section: 'Performance',
              hidden: false,
            },
            {
              type: 'docs',
              section: 'Documentation',
              hidden: false,
            },
            {
              type: 'style',
              section: 'Styling',
              hidden: true,
            },
            {
              type: 'refactor',
              section: 'Refactoring',
              hidden: false,
            },
            {
              type: 'test',
              section: 'Tests',
              hidden: true,
            },
            {
              type: 'chore',
              section: 'Chores',
              hidden: true,
            },
            {
              type: 'ci',
              section: 'CI/CD',
              hidden: true,
            },
            {
              type: 'revert',
              section: 'Reverts',
              hidden: false,
            },
            {
              type: 'security',
              section: 'Security',
              hidden: false,
            },
          ],
        },
        parserOpts: {
          noteKeywords: ['BREAKING CHANGE', 'SECURITY'],
          issuePrefixes: ['#', 'GH-'],
        },
        writerOpts: {
          // Custom template for release notes formatting
          mainTemplate: `{{#if isPatch}}{{#if @root.linkCompare~}}
[{{version}}]({{@root.linkCompare}}) ({{date}})
{{~else~}}
{{version}} ({{date}})
{{~/if}}{{else~}}
# [{{version}}]({{@root.linkCompare}}) ({{date}})
{{~/if}}
{{#if @root.isPatch}}{{else}}
{{#if @root.previousTag~}}
[Full Changelog]({{@root.linkCompare}})
{{~/if}}
{{~/if}}
{{/if}}

{{#if noteGroups}}
{{#each noteGroups}}
### {{title}}

{{#each notes}}
* {{#if issue}}[{{this.issue}}]({{@root.linkIssue}}{{this.issue}}) {{/if}}{{this.text}}
{{/each}}
{{/each}}
{{/if}}

{{#if features}}
### Features

{{#each features}}
* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if issue}} ([{{issue}}]({{@root.linkIssue}}{{issue}})){{/if}}
{{/each}}
{{/if}}

{{#if fixes}}
### Bug Fixes

{{#each fixes}}
* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if issue}} ([{{issue}}]({{@root.linkIssue}}{{issue}})){{/if}}
{{/each}}
{{/if}}

{{#if performance}}
### Performance

{{#each performance}}
* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if issue}} ([{{issue}}]({{@root.linkIssue}}{{issue}})){{/if}}
{{/each}}
{{/if}}

{{#if merges}}
### Merges

{{#each merges}}
* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if issue}} ([{{issue}}]({{@root.linkIssue}}{{issue}})){{/if}}
{{/each}}
{{/if}}

{{#if closes}}
{{#if features~}}
### Closes

{{#each closes}}
* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if issue}} ([{{issue}}]({{@root.linkIssue}}{{issue}})){{/if}}
{{/each}}
{{~/if}}
{{/if}}

{{#if breaking}}
### BREAKING CHANGES

{{#each breaking}}
* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if issue}} ([{{issue}}]({{@root.linkIssue}}{{issue}})){{/if}}

{{this.text}}

{{/each}}
{{/if}}
`,
        },
      },
    ],

    /**
     * Changelog Generation Plugin
     * Generates and updates CHANGELOG.md
     */
    [
      '@semantic-release/changelog',
      {
        changelogFile: 'CHANGELOG.md',
        changelogTitle: '# Changelog',
      },
    ],

    /**
     * npm Package Publishing Plugin
     * Publishes package to npm registry
     */
    [
      '@semantic-release/npm',
      {
        npmPublish: true,
        tarballDir: 'dist',
        pkgRoot: './',
        // Only publish from main branch
        publishBranches: ['main'],
      },
    ],

    /**
     * Git Plugin
     * Creates git tags and commits changes
     */
    [
      '@semantic-release/git',
      {
        assets: [
          'CHANGELOG.md',
          'package.json',
          'package-lock.json',
          'dist',
        ],
        message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
      },
    ],

    /**
     * GitHub Plugin
     * Creates GitHub releases and publishes assets
     */
    [
      '@semantic-release/github',
      {
        assets: [
          {
            path: 'dist/bundle.js',
            label: 'JavaScript Bundle',
          },
          {
            path: 'dist/bundle.min.js',
            label: 'Minified JavaScript Bundle',
          },
          {
            path: 'dist/styles.css',
            label: 'Stylesheet',
          },
          {
            path: 'build/app.tar.gz',
            label: 'Application Archive',
          },
        ],
        releasedLabels: ['released'],
        labels: false,
        assignees: ['@semantic-release'],
        successComment:
          ':tada: This issue has been resolved in [version ${nextRelease.version}](${releases.url}) :tada:\n\n${successComments}',
        failComment: false,
        failTitle: 'The automated release failed :scream_cat:',
        draftRelease: false,
        // Release notes template
        releaseBodyTemplate: `## ${nextRelease.channel ? 'Pre-release' : 'Release'}: Version ${nextRelease.version}

${nextRelease.notes}

### Contributors to this Release

${commits
  .filter(commit => commit.author)
  .map(commit => `- [@${commit.author.login}](${commit.author.html_url})`)
  .join('\n')}

---

**Release Date:** \`${new Date().toISOString()}\`
**Commit:** [\`${commits[commits.length - 1].hash.substring(0, 7)}\`](${commits[commits.length - 1].url})`,
      },
    ],

    /**
     * GitLab Plugin
     * Creates GitLab releases (alternative to GitHub)
     */
    [
      '@semantic-release/gitlab',
      {
        gitlabUrl: 'https://gitlab.com',
        assets: [
          {
            path: 'dist/bundle.js',
          },
          {
            path: 'dist/bundle.min.js',
          },
        ],
      },
    ],

    /**
     * Slack Notification Plugin
     * Sends release notifications to Slack
     */
    [
      'semantic-release-slack-bot',
      {
        notifyOnSuccess: true,
        notifyOnFail: true,
        slackWebhook: process.env.SLACK_WEBHOOK_URL,
        slackReleaseTemplate: `
*Release :rocket:*
*Version:* \`$RELEASE_VERSION\`
*Branch:* \`$RELEASE_BRANCH\`
*Changes:*
$RELEASE_NOTES_SUMMARY
*Changelog:* <$RELEASE_URL|View on GitHub>
        `,
      },
    ],

    /**
     * Docker Plugin
     * Publishes Docker images with release tags
     */
    [
      '@semantic-release-docker/semantic-release-docker',
      {
        registries: [
          {
            name: 'ghcr.io',
            images: ['ghcr.io/organization/app'],
            skipLogin: false,
          },
          {
            name: 'docker.io',
            images: ['docker.io/organization/app'],
            skipLogin: false,
          },
        ],
        additionalTags: ['latest'],
      },
    ],
  ],

  /**
   * Extends Configuration
   * Inherits from shareable configs
   */
  extends: [
    'semantic-release:recommended',
  ],

  /**
   * CI Environment Configuration
   * Detects and configures for CI environments
   */
  ci: true,

  /**
   * Dry Run Mode
   * Set to true to simulate release without publishing
   * Override with: --dry-run flag
   */
  dryRun: false,

  /**
   * Debug Mode
   * Set to true for verbose logging
   */
  debug: false,
};

/**
 * Usage Examples:
 *
 * # Standard release (auto-detects version)
 * $ npx semantic-release
 *
 * # Dry run (simulate without publishing)
 * $ npx semantic-release --dry-run
 *
 * # Force release version
 * $ npx semantic-release --force-release major
 *
 * # CI/CD Integration (GitHub Actions)
 * See .github/workflows/release.yml
 *
 * # Manual Trigger
 * $ git push origin main
 * (automatically triggers release pipeline)
 *
 * Environment Variables Required:
 * - GITHUB_TOKEN: GitHub API token for releases
 * - NPM_TOKEN: npm registry authentication token
 * - SLACK_WEBHOOK_URL: Slack webhook for notifications
 * - DOCKER_USERNAME: Docker Hub username
 * - DOCKER_PASSWORD: Docker Hub password
 */
