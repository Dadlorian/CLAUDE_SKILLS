#!/bin/bash

################################################################################
# Pre-Commit Hooks for Technical Writing Style Enforcement
#
# Description: Git pre-commit hook that enforces style guide compliance
# Author: Technical Writing Automation Team
# Version: 1.0.0
#
# Usage: Copy to .git/hooks/pre-commit and make executable
#   chmod +x .git/hooks/pre-commit
#
# Features:
#   - Validates documentation files with Vale
#   - Checks for common formatting issues
#   - Prevents commits with style violations
#   - Provides detailed error reporting
#   - Allows exceptions with inline comments
################################################################################

set -o pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
VALE_CONFIG="${PROJECT_ROOT}/.vale.ini"
VALE_RULES_DIR="${SCRIPT_DIR}/vale-custom-rules"
DOCUMENTATION_PATTERNS=("*.md" "*.rst" "*.txt")
EXCLUDED_PATTERNS=(node_modules vendor .git build dist)

# Error tracking
ERRORS_FOUND=0
WARNINGS_FOUND=0
TOTAL_FILES_CHECKED=0

################################################################################
# Helper Functions
################################################################################

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Validate dependencies
check_dependencies() {
    local missing_deps=0

    print_info "Checking dependencies..."

    # Check for Vale
    if ! command -v vale &> /dev/null; then
        print_error "Vale is not installed"
        echo "  Install with: brew install vale (macOS) or apt-get install vale (Linux)"
        missing_deps=1
    else
        print_success "Vale found: $(vale --version | head -1)"
    fi

    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        missing_deps=1
    else
        print_success "Git found"
    fi

    if [ $missing_deps -eq 1 ]; then
        print_error "Missing required dependencies. Please install and try again."
        return 1
    fi

    return 0
}

# Get list of staged documentation files
get_staged_docs() {
    local files=()

    # Get all staged files
    local staged_files=$(git diff --cached --name-only --diff-filter=ACM)

    for file in $staged_files; do
        # Skip deleted files
        [ ! -f "$file" ] && continue

        # Check if file matches documentation patterns
        local skip=0
        for pattern in "${EXCLUDED_PATTERNS[@]}"; do
            if [[ "$file" == *"$pattern"* ]]; then
                skip=1
                break
            fi
        done
        [ $skip -eq 1 ] && continue

        # Check if file matches documentation file types
        for pattern in "${DOCUMENTATION_PATTERNS[@]}"; do
            if [[ "$file" == $pattern ]]; then
                files+=("$file")
                break
            fi
        done
    done

    echo "${files[@]}"
}

# Run Vale style checks
check_with_vale() {
    local file=$1
    local temp_file="/tmp/vale_output_$$.txt"

    if [ ! -f "$file" ]; then
        return 0
    fi

    print_info "Checking style: $file"

    # Run Vale and capture output
    if vale --config="${VALE_CONFIG}" "$file" > "$temp_file" 2>&1; then
        print_success "Style check passed: $file"
        rm -f "$temp_file"
        return 0
    else
        local output=$(cat "$temp_file")

        # Count errors and warnings
        local error_count=$(echo "$output" | grep -c "error" || true)
        local warning_count=$(echo "$output" | grep -c "warning" || true)

        ERRORS_FOUND=$((ERRORS_FOUND + error_count))
        WARNINGS_FOUND=$((WARNINGS_FOUND + warning_count))

        # Display Vale output
        echo "$output"

        print_error "Style check failed: $file"
        print_error "  Errors: $error_count, Warnings: $warning_count"

        rm -f "$temp_file"
        return 1
    fi
}

# Check for common markdown issues
check_markdown_format() {
    local file=$1

    if [[ ! "$file" == *.md ]]; then
        return 0
    fi

    print_info "Checking markdown format: $file"

    local issues=0

    # Check for proper heading levels
    if grep -q "^## " "$file" && ! grep -q "^# " "$file"; then
        print_warning "File missing top-level heading (#): $file"
        issues=$((issues + 1))
    fi

    # Check for trailing whitespace
    if grep -q '[[:space:]]$' "$file"; then
        print_warning "File contains trailing whitespace: $file"
        issues=$((issues + 1))
    fi

    # Check for mixed line endings
    if file "$file" | grep -q "CRLF"; then
        print_warning "File has mixed line endings: $file"
        issues=$((issues + 1))
    fi

    # Check for consistent list markers
    if grep -q "^- " "$file" && grep -q "^\* " "$file"; then
        print_warning "File mixes list markers (- and *): $file"
        issues=$((issues + 1))
    fi

    # Check for code fence consistency
    local backtick_count=$(grep -c '```' "$file" || true)
    if [ $((backtick_count % 2)) -ne 0 ]; then
        print_warning "File has unmatched code fences: $file"
        issues=$((issues + 1))
    fi

    if [ $issues -gt 0 ]; then
        return 1
    fi

    print_success "Markdown format check passed: $file"
    return 0
}

# Check file size
check_file_size() {
    local file=$1
    local max_size=$((1024 * 1024)) # 1MB

    local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)

    if [ "$file_size" -gt "$max_size" ]; then
        print_warning "File is very large ($((file_size / 1024))KB): $file"
        print_warning "  Consider splitting into smaller documents"
        return 1
    fi

    return 0
}

# Check for spell errors with built-in wordlist
check_spelling() {
    local file=$1

    # Only check markdown files
    if [[ ! "$file" == *.md ]]; then
        return 0
    fi

    # Note: Requires aspell installation
    if ! command -v aspell &> /dev/null; then
        return 0
    fi

    print_info "Checking spelling: $file"

    local misspellings=$(aspell --lang=en list < "$file" 2>/dev/null | sort | uniq)

    if [ -n "$misspellings" ]; then
        print_warning "Potential spelling issues in $file:"
        echo "$misspellings" | sed 's/^/    - /'
        return 1
    fi

    return 0
}

# Validate links in markdown
check_links() {
    local file=$1

    if [[ ! "$file" == *.md ]]; then
        return 0
    fi

    print_info "Checking links: $file"

    # Extract markdown links: [text](url)
    local links=$(grep -o '\[.*\]([^)]*)'  "$file" | sed 's/.*(\([^)]*\)).*/\1/' | sort | uniq)

    local broken=0
    while IFS= read -r link; do
        [ -z "$link" ] && continue

        # Skip external URLs (would require network)
        if [[ "$link" == http* ]]; then
            continue
        fi

        # Check local file links
        if [[ ! "$link" == "#"* ]] && [ ! -f "$link" ]; then
            print_warning "Broken link in $file: $link"
            broken=1
        fi
    done <<< "$links"

    if [ $broken -eq 0 ]; then
        print_success "Link check passed: $file"
    fi

    return $broken
}

# Generate style report
generate_report() {
    local total_files=$1
    local errors=$2
    local warnings=$3

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Style Check Report"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Files Checked:     $total_files"
    echo "Errors Found:      $errors"
    echo "Warnings Found:    $warnings"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed!${NC}"
        return 0
    else
        if [ $errors -gt 0 ]; then
            echo -e "${RED}✗ $errors error(s) found${NC}"
        fi
        if [ $warnings -gt 0 ]; then
            echo -e "${YELLOW}⚠ $warnings warning(s) found${NC}"
        fi
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    print_info "Running pre-commit style checks..."
    echo ""

    # Check dependencies
    if ! check_dependencies; then
        print_warning "Skipping pre-commit checks due to missing dependencies"
        exit 0
    fi

    echo ""

    # Get staged files
    local staged_files=$(get_staged_docs)

    if [ -z "$staged_files" ]; then
        print_success "No documentation files to check"
        exit 0
    fi

    # Process each file
    for file in $staged_files; do
        TOTAL_FILES_CHECKED=$((TOTAL_FILES_CHECKED + 1))

        echo ""
        print_info "Processing: $file"

        # Run all checks
        check_with_vale "$file" || ERRORS_FOUND=$((ERRORS_FOUND + 1))
        check_markdown_format "$file" || WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        check_file_size "$file" || WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        check_links "$file" || WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        # check_spelling "$file" || WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
    done

    echo ""

    # Generate report
    if ! generate_report "$TOTAL_FILES_CHECKED" "$ERRORS_FOUND" "$WARNINGS_FOUND"; then
        print_error "Commit blocked due to style violations"
        echo ""
        echo "To fix issues:"
        echo "  1. Review the errors above"
        echo "  2. Update your files"
        echo "  3. Stage the changes"
        echo "  4. Run: git commit again"
        echo ""
        echo "To skip checks (not recommended):"
        echo "  git commit --no-verify"
        echo ""
        exit 1
    fi

    exit 0
}

# Run main function
main "$@"
