#!/usr/bin/env node

/**
 * Markdown Auto-Formatter
 *
 * Automatically formats markdown files according to style guide rules
 * Handles: spacing, list formatting, heading consistency, code blocks, etc.
 *
 * Usage: node markdown-formatter.js [options] [files...]
 */

const fs = require('fs');
const path = require('path');

class MarkdownFormatter {
  constructor(options = {}) {
    this.options = {
      indent: options.indent || 2,
      lineLength: options.lineLength || 80,
      trailingNewline: options.trailingNewline !== false,
      trimTrailingWhitespace: options.trimTrailingWhitespace !== false,
      headingStyle: options.headingStyle || 'atx', // 'atx' (#) vs 'setext' (===)
      listMarker: options.listMarker || '-', // '-', '*', or '+'
      bold: options.bold || '**', // '**' or '__'
      italic: options.italic || '*', // '*' or '_'
      codeBlockStyle: options.codeBlockStyle || 'fenced', // 'fenced' (```) vs 'indented'
      dryRun: options.dryRun || false,
      verbose: options.verbose || false,
      ...options
    };
    this.stats = {
      filesProcessed: 0,
      changesApplied: 0,
      linesFormatted: 0
    };
  }

  /**
   * Format a markdown file
   */
  formatFile(filePath) {
    if (!fs.existsSync(filePath)) {
      console.error(`File not found: ${filePath}`);
      return false;
    }

    const originalContent = fs.readFileSync(filePath, 'utf-8');
    const formattedContent = this.formatContent(originalContent);

    this.stats.filesProcessed++;

    if (originalContent !== formattedContent) {
      this.stats.changesApplied++;

      if (!this.options.dryRun) {
        fs.writeFileSync(filePath, formattedContent, 'utf-8');
        if (this.options.verbose) {
          console.log(`✓ Formatted: ${filePath}`);
        }
      } else {
        if (this.options.verbose) {
          console.log(`[DRY RUN] Would format: ${filePath}`);
        }
      }
      return true;
    }

    if (this.options.verbose) {
      console.log(`- No changes needed: ${filePath}`);
    }
    return false;
  }

  /**
   * Format markdown content
   */
  formatContent(content) {
    let lines = content.split('\n');

    lines = this.formatHeadings(lines);
    lines = this.formatLists(lines);
    lines = this.formatCodeBlocks(lines);
    lines = this.formatParagraphs(lines);
    lines = this.normalizeSpacing(lines);
    lines = this.trimTrailingWhitespace(lines);

    let result = lines.join('\n');

    // Ensure trailing newline
    if (this.options.trailingNewline && !result.endsWith('\n')) {
      result += '\n';
    }

    return result;
  }

  /**
   * Format headings
   */
  formatHeadings(lines) {
    return lines.map((line, i) => {
      const match = line.match(/^(#{1,6})\s+(.+?)(?:\s+#*)?$/);
      if (match) {
        const hashes = match[1];
        const title = match[2].trim();
        // Ensure single space after hashes
        return `${hashes} ${title}`;
      }
      return line;
    });
  }

  /**
   * Format lists
   */
  formatLists(lines) {
    const result = [];
    let inList = false;
    let listIndent = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trimStart();

      // Check for list marker
      const unorderedMatch = trimmed.match(/^[*\-+]\s+/);
      const orderedMatch = trimmed.match(/^\d+\.\s+/);

      if (unorderedMatch || orderedMatch) {
        inList = true;
        const indent = line.length - trimmed.length;
        listIndent = indent;

        if (unorderedMatch) {
          // Normalize unordered list marker
          const content = trimmed.substring(unorderedMatch[0].length).trim();
          const spaces = ' '.repeat(indent);
          result.push(`${spaces}${this.options.listMarker} ${content}`);
        } else if (orderedMatch) {
          // Normalize ordered list
          const match = trimmed.match(/^(\d+)\.\s+(.+)/);
          const number = match[1];
          const content = match[2].trim();
          const spaces = ' '.repeat(indent);
          result.push(`${spaces}${number}. ${content}`);
        }
      } else if (inList && (trimmed === '' || (!unorderedMatch && !orderedMatch && line.length > 0 && !line.match(/^\s/)))) {
        // End of list
        inList = false;
        result.push(line);
      } else {
        result.push(line);
      }
    }

    return result;
  }

  /**
   * Format code blocks
   */
  formatCodeBlocks(lines) {
    const result = [];
    let inCodeBlock = false;
    let codeBlockMarker = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isFencedStart = line.match(/^```/);
      const isIndented = line.match(/^    /) && !inCodeBlock;

      if (isFencedStart) {
        inCodeBlock = !inCodeBlock;
        codeBlockMarker = line;

        // Ensure language identifier format
        if (inCodeBlock) {
          const match = line.match(/^```(\w+)?/);
          if (match && match[1]) {
            result.push(`\`\`\`${match[1].toLowerCase()}`);
          } else {
            result.push('```');
          }
        } else {
          result.push('```');
        }
      } else if (inCodeBlock) {
        result.push(line);
      } else if (isIndented && this.options.codeBlockStyle === 'fenced') {
        // Convert indented code block to fenced
        if (i > 0 && result[result.length - 1] !== '') {
          result.push('');
        }
        result.push('```');
        result.push(line.trim());
        // Collect all indented lines
        let j = i + 1;
        while (j < lines.length && lines[j].match(/^    /)) {
          result.push(lines[j].trim());
          j++;
        }
        result.push('```');
        if (j < lines.length && lines[j] !== '') {
          result.push('');
        }
        i = j - 1;
      } else {
        result.push(line);
      }
    }

    return result;
  }

  /**
   * Format paragraphs
   */
  formatParagraphs(lines) {
    const result = [];
    let paragraph = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Check if line is special (heading, list, code, etc.)
      const isSpecial = line.match(/^(#{1,6}\s|[-*+]\s|\d+\.\s|```|---|===|>)/) ||
                        trimmed === '' ||
                        line.match(/^    /);

      if (isSpecial) {
        // Flush paragraph
        if (paragraph.length > 0) {
          result.push(paragraph.join(' ').trim());
          result.push('');
          paragraph = [];
        }
        result.push(line);
      } else {
        paragraph.push(trimmed);
      }
    }

    if (paragraph.length > 0) {
      result.push(paragraph.join(' ').trim());
    }

    return result;
  }

  /**
   * Normalize spacing
   */
  normalizeSpacing(lines) {
    const result = [];
    let previousWasBlank = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isBlank = line.trim() === '';

      // Don't add multiple consecutive blank lines
      if (isBlank && previousWasBlank) {
        continue;
      }

      // Special rule: blank line before headings (except first line)
      if (line.match(/^#{1,6}\s/) && i > 0 && !previousWasBlank) {
        result.push('');
      }

      result.push(line);
      previousWasBlank = isBlank;
    }

    return result;
  }

  /**
   * Trim trailing whitespace
   */
  trimTrailingWhitespace(lines) {
    if (!this.options.trimTrailingWhitespace) {
      return lines;
    }

    return lines.map(line => {
      // Preserve intentional trailing spaces in some markdown contexts
      // (like double space for line break)
      if (line.endsWith('  ')) {
        return line;
      }
      return line.trimEnd();
    });
  }

  /**
   * Get statistics
   */
  getStatistics() {
    return this.stats;
  }
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node markdown-formatter.js [options] [files...]');
    console.error('\nOptions:');
    console.error('  --indent <n>           Indentation spaces (default: 2)');
    console.error('  --line-length <n>      Max line length (default: 80)');
    console.error('  --list-marker <m>      List marker: -, *, + (default: -)');
    console.error('  --dry-run              Show what would be changed');
    console.error('  --verbose, -v          Verbose output');
    process.exit(1);
  }

  const options = {
    indent: 2,
    lineLength: 80,
    listMarker: '-',
    dryRun: false,
    verbose: false
  };

  const files = [];

  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--indent' && i + 1 < args.length) {
      options.indent = parseInt(args[++i], 10);
    } else if (args[i] === '--line-length' && i + 1 < args.length) {
      options.lineLength = parseInt(args[++i], 10);
    } else if (args[i] === '--list-marker' && i + 1 < args.length) {
      options.listMarker = args[++i];
    } else if (args[i] === '--dry-run') {
      options.dryRun = true;
    } else if (args[i] === '--verbose' || args[i] === '-v') {
      options.verbose = true;
    } else if (!args[i].startsWith('--')) {
      files.push(args[i]);
    }
  }

  // Create formatter and process files
  const formatter = new MarkdownFormatter(options);

  console.log('Starting markdown formatting...\n');

  files.forEach(file => {
    if (fs.statSync(file).isDirectory()) {
      // Process directory
      const mdFiles = findMarkdownFiles(file);
      mdFiles.forEach(f => formatter.formatFile(f));
    } else {
      formatter.formatFile(file);
    }
  });

  // Print statistics
  const stats = formatter.getStatistics();
  console.log('\n=== FORMATTING SUMMARY ===');
  console.log(`Files processed: ${stats.filesProcessed}`);
  console.log(`Files changed: ${stats.changesApplied}`);

  if (options.dryRun) {
    console.log('\n[DRY RUN MODE] No files were actually modified.');
  }
}

/**
 * Find all markdown files in directory
 */
function findMarkdownFiles(dir) {
  const files = [];

  function walk(currentPath) {
    const entries = fs.readdirSync(currentPath, { withFileTypes: true });

    entries.forEach(entry => {
      const fullPath = path.join(currentPath, entry.name);

      if (entry.isDirectory() && !entry.name.startsWith('.')) {
        walk(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        files.push(fullPath);
      }
    });
  }

  walk(dir);
  return files;
}

module.exports = MarkdownFormatter;
