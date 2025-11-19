#!/usr/bin/env node

/**
 * Technical Writing Terminology Checker
 *
 * Validates terminology consistency across documentation
 * Enforces approved term usage and identifies inconsistencies
 *
 * Usage: node terminology-checker.js [files...]
 */

const fs = require('fs');
const path = require('path');

// Approved terminology dictionary
const TERMINOLOGY = {
  // Framework/Library names
  'frameworks': {
    'React': {
      variants: ['react', 'ReactJS', 'react.js'],
      correct: 'React',
      context: 'JavaScript UI library'
    },
    'Vue.js': {
      variants: ['vuejs', 'Vue', 'vue'],
      correct: 'Vue.js',
      context: 'Progressive framework'
    },
    'Angular': {
      variants: ['angular', 'AngularJS'],
      correct: 'Angular',
      context: 'Web framework'
    },
    'Node.js': {
      variants: ['nodejs', 'Node', 'node.js'],
      correct: 'Node.js',
      context: 'JavaScript runtime'
    }
  },

  // Database names
  'databases': {
    'MongoDB': {
      variants: ['mongodb', 'Mongo'],
      correct: 'MongoDB',
      context: 'NoSQL database'
    },
    'PostgreSQL': {
      variants: ['postgresql', 'postgres'],
      correct: 'PostgreSQL',
      context: 'Relational database'
    },
    'MySQL': {
      variants: ['mysql'],
      correct: 'MySQL',
      context: 'Relational database'
    }
  },

  // Protocol/API names
  'protocols': {
    'REST API': {
      variants: ['Rest API', 'rest api'],
      correct: 'REST API',
      context: 'Web API style'
    },
    'GraphQL': {
      variants: ['graphql', 'graph ql'],
      correct: 'GraphQL',
      context: 'Query language'
    },
    'JSON': {
      variants: ['json', 'Json'],
      correct: 'JSON',
      context: 'Data format'
    },
    'YAML': {
      variants: ['yaml', 'Yaml'],
      correct: 'YAML',
      context: 'Configuration format'
    },
    'HTTP': {
      variants: ['http', 'Http'],
      correct: 'HTTP',
      context: 'Protocol'
    }
  },

  // Tool names
  'tools': {
    'Docker': {
      variants: ['docker'],
      correct: 'Docker',
      context: 'Container platform'
    },
    'Kubernetes': {
      variants: ['kubernetes', 'K8s', 'k8s'],
      correct: 'Kubernetes',
      context: 'Orchestration platform'
    },
    'Git': {
      variants: ['git'],
      correct: 'Git',
      context: 'Version control'
    }
  },

  // Inclusive language replacements
  'inclusive': {
    'allowlist': {
      variants: ['whitelist'],
      correct: 'allowlist',
      context: 'Inclusive terminology'
    },
    'blocklist': {
      variants: ['blacklist'],
      correct: 'blocklist',
      context: 'Inclusive terminology'
    },
    'primary': {
      variants: ['master'],
      correct: 'primary',
      context: 'Inclusive terminology'
    },
    'replica': {
      variants: ['slave'],
      correct: 'replica',
      context: 'Inclusive terminology'
    }
  }
};

class TerminologyChecker {
  constructor(options = {}) {
    this.options = {
      caseSensitive: options.caseSensitive !== false,
      reportType: options.reportType || 'summary', // 'summary', 'detailed', 'json'
      verbose: options.verbose || false,
      ...options
    };
    this.issues = [];
    this.statistics = {
      filesChecked: 0,
      totalIssues: 0,
      byCategory: {},
      byType: {}
    };
  }

  /**
   * Check a single file for terminology issues
   */
  checkFile(filePath) {
    if (!fs.existsSync(filePath)) {
      console.error(`File not found: ${filePath}`);
      return;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    const fileName = path.relative(process.cwd(), filePath);

    this.statistics.filesChecked++;

    lines.forEach((line, lineNumber) => {
      this.checkLine(line, lineNumber + 1, fileName);
    });
  }

  /**
   * Check a single line for terminology issues
   */
  checkLine(line, lineNumber, fileName) {
    // Skip code blocks and inline code
    if (line.trim().startsWith('```') || line.trim().startsWith('    ')) {
      return;
    }

    // Check each terminology category
    for (const category in TERMINOLOGY) {
      const terms = TERMINOLOGY[category];

      for (const correctTerm in terms) {
        const termData = terms[correctTerm];

        // Check variants
        for (const variant of termData.variants) {
          const regex = new RegExp(`\\b${this.escapeRegex(variant)}\\b`,
            this.options.caseSensitive ? 'g' : 'gi');

          let match;
          while ((match = regex.exec(line)) !== null) {
            // Skip if it's in code block or link
            if (this.isInCode(line, match.index)) {
              continue;
            }

            const issue = {
              file: fileName,
              line: lineNumber,
              column: match.index + 1,
              type: 'terminology',
              category: category,
              found: match[0],
              suggested: correctTerm,
              context: termData.context,
              message: `Use "${correctTerm}" instead of "${match[0]}"`,
              lineText: line.trim()
            };

            this.issues.push(issue);
            this.statistics.totalIssues++;
            this.statistics.byCategory[category] =
              (this.statistics.byCategory[category] || 0) + 1;
            this.statistics.byType['terminology'] =
              (this.statistics.byType['terminology'] || 0) + 1;

            if (this.options.verbose) {
              console.log(`  [${lineNumber}:${match.index + 1}] ${issue.message}`);
            }
          }
        }
      }
    }
  }

  /**
   * Check if position is inside code block
   */
  isInCode(line, position) {
    const beforeText = line.substring(0, position);
    const backtickCount = (beforeText.match(/`/g) || []).length;
    return backtickCount % 2 === 1; // Odd number means inside code
  }

  /**
   * Escape special regex characters
   */
  escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  /**
   * Generate report based on type
   */
  generateReport() {
    switch (this.options.reportType) {
      case 'json':
        return this.generateJsonReport();
      case 'detailed':
        return this.generateDetailedReport();
      case 'summary':
      default:
        return this.generateSummaryReport();
    }
  }

  /**
   * Generate summary report
   */
  generateSummaryReport() {
    let report = '\n=== TERMINOLOGY CHECK SUMMARY ===\n\n';

    report += `Files Checked: ${this.statistics.filesChecked}\n`;
    report += `Total Issues: ${this.statistics.totalIssues}\n\n`;

    if (this.statistics.totalIssues === 0) {
      report += 'No terminology issues found!\n';
      return report;
    }

    report += 'Issues by Category:\n';
    for (const category in this.statistics.byCategory) {
      report += `  ${category}: ${this.statistics.byCategory[category]}\n`;
    }

    report += '\nTop Issues:\n';
    const groupedByTerm = this.groupIssuesByTerm();
    Object.entries(groupedByTerm)
      .sort((a, b) => b[1].length - a[1].length)
      .slice(0, 10)
      .forEach(([term, issues]) => {
        report += `  "${term}" (${issues.length} occurrences)\n`;
      });

    return report;
  }

  /**
   * Generate detailed report
   */
  generateDetailedReport() {
    let report = '\n=== DETAILED TERMINOLOGY CHECK REPORT ===\n\n';

    if (this.issues.length === 0) {
      report += 'No terminology issues found!\n';
      return report;
    }

    // Group by file
    const byFile = {};
    this.issues.forEach(issue => {
      if (!byFile[issue.file]) {
        byFile[issue.file] = [];
      }
      byFile[issue.file].push(issue);
    });

    // Report by file
    for (const file in byFile) {
      report += `\n${file}:\n`;
      byFile[file].forEach(issue => {
        report += `  Line ${issue.line}:${issue.column}\n`;
        report += `    Found: "${issue.found}"\n`;
        report += `    Suggested: "${issue.suggested}"\n`;
        report += `    Context: ${issue.context}\n`;
        report += `    Text: ${issue.lineText}\n`;
      });
    }

    report += `\n\nSummary:\n`;
    report += `Total Issues: ${this.statistics.totalIssues}\n`;
    report += `Files Affected: ${Object.keys(byFile).length}\n`;

    return report;
  }

  /**
   * Generate JSON report
   */
  generateJsonReport() {
    return JSON.stringify({
      summary: this.statistics,
      issues: this.issues,
      timestamp: new Date().toISOString()
    }, null, 2);
  }

  /**
   * Group issues by incorrect term
   */
  groupIssuesByTerm() {
    const grouped = {};
    this.issues.forEach(issue => {
      const key = issue.found;
      grouped[key] = grouped[key] || [];
      grouped[key].push(issue);
    });
    return grouped;
  }

  /**
   * Get issues
   */
  getIssues() {
    return this.issues;
  }

  /**
   * Get statistics
   */
  getStatistics() {
    return this.statistics;
  }
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node terminology-checker.js [options] [files...]');
    console.error('\nOptions:');
    console.error('  --report-type <type>  Report format: summary|detailed|json (default: summary)');
    console.error('  --verbose, -v         Verbose output');
    console.error('  --case-sensitive      Case-sensitive checking');
    process.exit(1);
  }

  const options = {
    reportType: 'summary',
    verbose: false,
    caseSensitive: false
  };

  const files = [];

  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--report-type' && i + 1 < args.length) {
      options.reportType = args[++i];
    } else if (args[i] === '--verbose' || args[i] === '-v') {
      options.verbose = true;
    } else if (args[i] === '--case-sensitive') {
      options.caseSensitive = true;
    } else if (!args[i].startsWith('--')) {
      files.push(args[i]);
    }
  }

  // Create checker and process files
  const checker = new TerminologyChecker(options);

  files.forEach(file => {
    if (fs.statSync(file).isDirectory()) {
      // Process directory
      const mdFiles = this.findMarkdownFiles(file);
      mdFiles.forEach(f => checker.checkFile(f));
    } else {
      checker.checkFile(file);
    }
  });

  // Generate and display report
  console.log(checker.generateReport());

  // Exit with error code if issues found
  if (checker.getStatistics().totalIssues > 0) {
    process.exit(1);
  }
}

module.exports = TerminologyChecker;
