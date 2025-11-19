/**
 * Documentation Scorecard - Automated Documentation Quality Scoring System
 * Analyzes documentation and generates comprehensive quality scores
 */

class DocumentationScorecard {
  /**
   * Initialize the scorecard calculator
   */
  constructor() {
    this.categories = {
      completeness: {
        weight: 0.20,
        description: 'Document completeness and coverage',
        checks: []
      },
      clarity: {
        weight: 0.20,
        description: 'Writing clarity and readability',
        checks: []
      },
      accuracy: {
        weight: 0.20,
        description: 'Technical accuracy and up-to-date information',
        checks: []
      },
      structure: {
        weight: 0.20,
        description: 'Document organization and structure',
        checks: []
      },
      examples: {
        weight: 0.20,
        description: 'Code examples and practical demonstrations',
        checks: []
      }
    };

    this.sampleDocuments = [
      {
        id: 'api-ref-001',
        title: 'API Reference Documentation',
        content: this.generateSampleAPIDoc(),
        type: 'reference'
      },
      {
        id: 'guide-001',
        title: 'Getting Started Guide',
        content: this.generateSampleGuide(),
        type: 'guide'
      },
      {
        id: 'tutorial-001',
        title: 'Advanced Features Tutorial',
        content: this.generateSampleTutorial(),
        type: 'tutorial'
      },
      {
        id: 'faq-001',
        title: 'Frequently Asked Questions',
        content: this.generateSampleFAQ(),
        type: 'faq'
      }
    ];
  }

  /**
   * Generate sample API documentation
   */
  generateSampleAPIDoc() {
    return `# API Reference v2.0

## Overview
Complete API reference for our service platform.

## Authentication
Uses OAuth 2.0 token-based authentication.

## Endpoints

### GET /api/users
Retrieve user list with pagination.

\`\`\`bash
curl -X GET https://api.example.com/users \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

**Parameters:**
- page (integer): Page number
- limit (integer): Items per page
- sort (string): Sort field

**Response:**
\`\`\`json
{
  "users": [
    {
      "id": "123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100
  }
}
\`\`\`

### POST /api/users
Create a new user.

**Request Body:**
\`\`\`json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "admin"
}
\`\`\`

**Status Codes:**
- 201 Created
- 400 Bad Request
- 409 Conflict

## Rate Limiting
Requests are limited to 1000 per hour.

## Error Handling
All errors return standardized error responses.`;
  }

  /**
   * Generate sample guide
   */
  generateSampleGuide() {
    return `# Getting Started Guide

## Introduction
Learn the fundamentals in 10 minutes.

## Prerequisites
- Node.js 14+
- npm or yarn
- Basic JavaScript knowledge

## Installation

\`\`\`bash
npm install our-package
\`\`\`

## Quick Start

\`\`\`javascript
const OurPackage = require('our-package');

const client = new OurPackage({
  apiKey: 'your-api-key'
});

// Fetch data
const data = await client.getData();
console.log(data);
\`\`\`

## Common Tasks

### Task 1: Authentication
Set up authentication tokens.

\`\`\`javascript
client.authenticate({
  username: 'user@example.com',
  password: 'secure-password'
});
\`\`\`

### Task 2: Error Handling
Properly handle errors in your code.

\`\`\`javascript
try {
  const result = await client.performAction();
} catch (error) {
  console.error('Error:', error.message);
}
\`\`\`

## Next Steps
- Read the [API Reference](./api-reference.md)
- Explore [Advanced Examples](./advanced.md)
- Check [Best Practices](./best-practices.md)

## Troubleshooting
See our [FAQ](./faq.md) for common issues.`;
  }

  /**
   * Generate sample tutorial
   */
  generateSampleTutorial() {
    return `# Advanced Features Tutorial

## Part 1: Understanding Caching
Improve performance with intelligent caching.

### Cache Strategies
There are three main strategies:

1. **Write-through**: Safe but slower
2. **Write-back**: Fast but complex
3. **Write-around**: Balanced approach

### Implementation

\`\`\`python
from our_package import CacheManager

cache = CacheManager(strategy='write-around')

# Store value
cache.set('user:123', user_data, ttl=3600)

# Retrieve value
user = cache.get('user:123')

# Invalidate
cache.delete('user:123')
\`\`\`

## Part 2: Advanced Querying
Master complex data retrieval patterns.

### Query Builder

\`\`\`python
query = (Query()
  .select(['id', 'name', 'email'])
  .filter(age__gt=18)
  .order_by('-created_at')
  .limit(10))

results = client.execute(query)
\`\`\`

## Part 3: Performance Optimization
Optimize for production workloads.

### Benchmarking

\`\`\`javascript
const benchmark = require('our-package/benchmark');

const metrics = benchmark.compare([
  () => approach1(),
  () => approach2(),
  () => approach3()
]);

metrics.print();
\`\`\`

## Summary
You now understand advanced features!`;
  }

  /**
   * Generate sample FAQ
   */
  generateSampleFAQ() {
    return `# Frequently Asked Questions

## General

### Q: What is this product?
A: A comprehensive platform for managing technical documentation.

### Q: Who should use it?
A: Technical writers, developers, and documentation teams.

## Technical

### Q: What languages are supported?
A: JavaScript, Python, Java, Go, and Rust are officially supported.

### Q: How do I authenticate?
A: Use OAuth 2.0 or API keys. See the [Authentication Guide](./auth.md).

\`\`\`bash
curl -H "Authorization: Bearer token" https://api.example.com/data
\`\`\`

### Q: What are rate limits?
A: Standard tier: 1000 requests/hour. Pro: 10000 requests/hour.

## Troubleshooting

### Q: Getting "401 Unauthorized" errors?
A: Check your authentication token and ensure it hasn't expired.

\`\`\`javascript
const token = await client.refreshToken();
\`\`\`

### Q: Performance is slow?
A: Enable caching and consider pagination for large datasets.

## Billing

### Q: Is there a free tier?
A: Yes, our free tier includes 10,000 monthly API calls.

### Q: Can I upgrade anytime?
A: Yes, upgrades take effect immediately.`;
  }

  /**
   * Score a document
   */
  scoreDocument(document) {
    const scores = {
      document: document,
      scores: {},
      details: {},
      timestamp: new Date().toISOString(),
      overallScore: 0,
      issues: []
    };

    // Score each category
    for (const [category, config] of Object.entries(this.categories)) {
      const categoryScore = this.scoreCategory(category, document.content);
      scores.scores[category] = categoryScore;
      scores.details[category] = this.getCategoryDetails(category, document.content);
    }

    // Calculate weighted overall score
    scores.overallScore = this.calculateWeightedScore(scores.scores);

    // Identify issues
    scores.issues = this.identifyIssues(document.content);

    // Get recommendations
    scores.recommendations = this.getRecommendations(scores);

    return scores;
  }

  /**
   * Score a single category
   */
  scoreCategory(category, content) {
    let score = 0;
    let checks = 0;

    const metrics = this.extractMetrics(content);

    switch (category) {
      case 'completeness':
        score += metrics.hasTitleSection ? 15 : 0;
        score += metrics.hasIntroduction ? 15 : 0;
        score += metrics.hasExamples ? 15 : 0;
        score += metrics.hasLinks ? 15 : 0;
        score += metrics.hasConclusion ? 15 : 0;
        score += metrics.numSections >= 3 ? 15 : 5;
        score += metrics.numSections >= 5 ? 10 : 0;
        checks = 80;
        break;

      case 'clarity':
        const avgWordLength = metrics.totalWords / metrics.numWords;
        score += metrics.numWords >= 100 ? 15 : 0;
        score += avgWordLength < 6 ? 20 : avgWordLength < 8 ? 10 : 0;
        score += metrics.numSentences >= 5 ? 15 : 0;
        score += !metrics.hasTODOs ? 20 : 0;
        score += metrics.numHeadings >= 2 ? 15 : 0;
        score += metrics.numHeadings <= 10 ? 15 : 0;
        checks = 100;
        break;

      case 'accuracy':
        score += metrics.numLinks >= 2 ? 20 : 0;
        score += metrics.numCodeBlocks >= 1 ? 20 : 0;
        score += !metrics.hasDeprecatedSyntax ? 20 : 0;
        score += metrics.numCodeBlocks >= 3 ? 20 : 0;
        score += !metrics.hasBrokenLinks ? 20 : 0;
        checks = 100;
        break;

      case 'structure':
        score += metrics.hasHeadings ? 15 : 0;
        score += metrics.hasCodeBlocks ? 15 : 0;
        score += metrics.numLists >= 1 ? 15 : 0;
        score += metrics.numLists >= 2 ? 15 : 0;
        score += metrics.numTables >= 0 ? 15 : 0;
        score += metrics.numHeadings >= 3 ? 10 : 0;
        score += metrics.numHeadings <= 8 ? 15 : 0;
        checks = 100;
        break;

      case 'examples':
        score += metrics.numCodeBlocks >= 1 ? 20 : 0;
        score += metrics.numCodeBlocks >= 2 ? 20 : 0;
        score += metrics.numCodeBlocks >= 3 ? 20 : 0;
        score += metrics.codeBlockCoverage >= 0.3 ? 20 : 0;
        score += metrics.numLanguages >= 2 ? 20 : 0;
        checks = 100;
        break;
    }

    return Math.min(100, (score / checks) * 100);
  }

  /**
   * Extract metrics from content
   */
  extractMetrics(content) {
    return {
      numWords: content.split(/\s+/).length,
      numSentences: (content.match(/[.!?]/g) || []).length,
      totalWords: content.split(/\s+/).reduce((sum, word) => sum + word.length, 0),
      numHeadings: (content.match(/^#+\s/gm) || []).length,
      hasHeadings: /^#+\s/gm.test(content),
      numSections: (content.match(/^##\s/gm) || []).length,
      hasIntroduction: /introduction|overview/i.test(content),
      hasTitleSection: /^#\s/m.test(content),
      hasExamples: /example|sample/i.test(content),
      hasLinks: /\[.*?\]\(.*?\)/g.test(content),
      numLinks: (content.match(/\[.*?\]\(.*?\)/g) || []).length,
      numCodeBlocks: (content.match(/```[\s\S]*?```/g) || []).length,
      hasCodeBlocks: /```[\s\S]*?```/g.test(content),
      numLanguages: new Set((content.match(/```(\w+)/g) || []).map(m => m.slice(3))).size,
      numLists: (content.match(/^[-*+]\s/gm) || []).length,
      numTables: (content.match(/\|.*\|/g) || []).length,
      hasConclusion: /conclusion|summary|next steps/i.test(content),
      hasTODOs: /TODO|FIXME|XXX/i.test(content),
      hasDeprecatedSyntax: /deprecated|obsolete|legacy/i.test(content),
      hasBrokenLinks: /\[.*?\]\(\)/g.test(content),
      codeBlockCoverage: (content.match(/```[\s\S]*?```/g) || []).length > 0 ? 0.5 : 0
    };
  }

  /**
   * Get category details
   */
  getCategoryDetails(category, content) {
    const metrics = this.extractMetrics(content);

    const details = {
      completeness: {
        sections: metrics.numSections,
        hasIntroduction: metrics.hasIntroduction,
        hasExamples: metrics.hasExamples,
        internalLinks: metrics.numLinks
      },
      clarity: {
        wordCount: metrics.numWords,
        headings: metrics.numHeadings,
        hasTODOs: metrics.hasTODOs,
        avgWordLength: (metrics.totalWords / metrics.numWords).toFixed(2)
      },
      accuracy: {
        externalReferences: metrics.numLinks,
        codeBlocks: metrics.numCodeBlocks,
        isDeprecated: metrics.hasDeprecatedSyntax,
        hasBrokenLinks: metrics.hasBrokenLinks
      },
      structure: {
        headings: metrics.numHeadings,
        lists: metrics.numLists,
        tables: metrics.numTables,
        codeBlocks: metrics.numCodeBlocks
      },
      examples: {
        codeBlocks: metrics.numCodeBlocks,
        languages: metrics.numLanguages,
        coverage: (metrics.codeBlockCoverage * 100).toFixed(1) + '%'
      }
    };

    return details[category] || {};
  }

  /**
   * Identify issues in document
   */
  identifyIssues(content) {
    const issues = [];
    const metrics = this.extractMetrics(content);

    if (metrics.numWords < 100) {
      issues.push({
        severity: 'warning',
        message: 'Document is too short (< 100 words)'
      });
    }

    if (metrics.hasTODOs) {
      issues.push({
        severity: 'error',
        message: 'Document contains TODO/FIXME markers'
      });
    }

    if (metrics.hasBrokenLinks) {
      issues.push({
        severity: 'error',
        message: 'Document contains broken links'
      });
    }

    if (metrics.numHeadings === 0) {
      issues.push({
        severity: 'warning',
        message: 'No section headings found'
      });
    }

    if (metrics.numCodeBlocks === 0 && metrics.numWords > 500) {
      issues.push({
        severity: 'warning',
        message: 'Long document with no code examples'
      });
    }

    if (metrics.numLinks === 0) {
      issues.push({
        severity: 'info',
        message: 'No external references or links found'
      });
    }

    return issues;
  }

  /**
   * Calculate weighted score
   */
  calculateWeightedScore(scores) {
    let weighted = 0;
    for (const [category, config] of Object.entries(this.categories)) {
      weighted += scores[category] * config.weight;
    }
    return Math.round(weighted * 10) / 10;
  }

  /**
   * Get recommendations
   */
  getRecommendations(scores) {
    const recommendations = [];

    for (const [category, score] of Object.entries(scores.scores)) {
      if (score < 70) {
        const config = this.categories[category];
        recommendations.push({
          category,
          priority: 'high',
          message: `Improve ${category} (current score: ${score.toFixed(1)}/100). ${config.description}`
        });
      }
    }

    if (scores.issues.length > 0) {
      recommendations.unshift({
        category: 'critical',
        priority: 'critical',
        message: `Fix ${scores.issues.length} identified issue(s) before publishing`
      });
    }

    return recommendations;
  }

  /**
   * Score all sample documents
   */
  scoreAll() {
    return this.sampleDocuments.map(doc => this.scoreDocument(doc));
  }

  /**
   * Generate report
   */
  generateReport() {
    const allScores = this.scoreAll();

    return {
      timestamp: new Date().toISOString(),
      summary: {
        totalDocuments: allScores.length,
        averageScore: (allScores.reduce((sum, s) => sum + s.overallScore, 0) / allScores.length).toFixed(1),
        excellentCount: allScores.filter(s => s.overallScore >= 85).length,
        goodCount: allScores.filter(s => s.overallScore >= 70 && s.overallScore < 85).length,
        needsImprovementCount: allScores.filter(s => s.overallScore < 70).length
      },
      documents: allScores,
      topIssues: this.getTopIssues(allScores)
    };
  }

  /**
   * Get top issues across all documents
   */
  getTopIssues(allScores) {
    const issueCount = {};

    allScores.forEach(score => {
      score.issues.forEach(issue => {
        const key = issue.message;
        issueCount[key] = (issueCount[key] || 0) + 1;
      });
    });

    return Object.entries(issueCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([issue, count]) => ({ issue, affectedDocuments: count }));
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DocumentationScorecard;
}
