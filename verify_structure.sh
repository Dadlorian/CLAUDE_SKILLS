#!/bin/bash

# Verification script for CLAUDE_SKILLS repository structure

echo "======================================"
echo "CLAUDE_SKILLS Structure Verification"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check global standards
echo "Checking global standards..."
GLOBAL_FILES=(
    "global_standards/style-guides/ui_ux_style_guide.md"
    "global_standards/style-guides/technical_writing_guide.md"
    "global_standards/style-guides/naming_conventions.md"
    "global_standards/style-guides/documentation_standards.md"
    "global_standards/api-guides/rest_api_integration.md"
    "global_standards/api-guides/graphql_api_integration.md"
    "global_standards/api-guides/oauth2_authentication.md"
    "global_standards/api-guides/rate_limit_handling.md"
)

for file in "${GLOBAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(wc -l < "$file")
        if [ "$SIZE" -gt 100 ]; then
            echo -e "${GREEN}✓${NC} $file ($SIZE lines)"
        else
            echo -e "${YELLOW}⚠${NC} $file exists but seems short ($SIZE lines)"
            ((WARNINGS++))
        fi
    else
        echo -e "${RED}✗${NC} Missing: $file"
        ((ERRORS++))
    fi
done

echo ""

# Check all 32 domains
DOMAINS=(
    "01_cloud_computing"
    "02_software_engineering"
    "03_data_science_ai"
    "04_cybersecurity"
    "05_devops_sre"
    "06_mobile_development"
    "07_game_development"
    "08_blockchain_web3"
    "09_iot_embedded"
    "10_product_management"
    "11_ux_ui_design"
    "12_digital_marketing"
    "13_sales_engineering"
    "14_technical_writing"
    "15_quality_assurance"
    "16_database_engineering"
    "17_network_engineering"
    "18_systems_architecture"
    "19_business_intelligence"
    "20_project_management"
    "21_financial_technology"
    "22_healthcare_technology"
    "23_education_technology"
    "24_legal_technology"
    "25_manufacturing_industry_4_0"
    "26_telecommunications"
    "27_media_entertainment_tech"
    "28_energy_sustainability_tech"
    "29_agriculture_technology"
    "30_transportation_logistics"
    "31_real_estate_technology"
    "32_research_development"
)

echo "Checking domains..."
echo ""

for domain in "${DOMAINS[@]}"; do
    echo "Checking $domain..."

    # Check required files
    REQUIRED_FILES=(
        "$domain/skill.md"
        "$domain/README.md"
    )

    DOMAIN_COMPLETE=true

    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "  ${RED}✗${NC} Missing: $file"
            ((ERRORS++))
            DOMAIN_COMPLETE=false
        fi
    done

    # Check standards directories
    if [ ! -d "$domain/standards/style-guides" ] || [ -z "$(ls -A $domain/standards/style-guides 2>/dev/null)" ]; then
        echo -e "  ${YELLOW}⚠${NC} standards/style-guides/ empty or missing"
        ((WARNINGS++))
        DOMAIN_COMPLETE=false
    fi

    # Check subskills
    SUBSKILL_COUNT=$(find "$domain/skills" -maxdepth 1 -type d -name "[0-9]*" 2>/dev/null | wc -l)
    if [ "$SUBSKILL_COUNT" -eq 10 ]; then
        echo -e "  ${GREEN}✓${NC} 10 subskills found"
    elif [ "$SUBSKILL_COUNT" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} Only $SUBSKILL_COUNT/10 subskills found"
        ((WARNINGS++))
        DOMAIN_COMPLETE=false
    else
        echo -e "  ${RED}✗${NC} No subskills found"
        ((ERRORS++))
        DOMAIN_COMPLETE=false
    fi

    # Check subskill structure
    SUBSKILL_FILES=0
    for subskill in "$domain"/skills/[0-9]*; do
        if [ -d "$subskill" ]; then
            # Count files in reference, guides, src
            REF_COUNT=$(find "$subskill/reference" -type f 2>/dev/null | wc -l)
            GUIDE_COUNT=$(find "$subskill/guides" -type f 2>/dev/null | wc -l)
            SRC_COUNT=$(find "$subskill/src" -type f 2>/dev/null | wc -l)
            SUBSKILL_FILES=$((SUBSKILL_FILES + REF_COUNT + GUIDE_COUNT + SRC_COUNT))
        fi
    done

    if [ "$SUBSKILL_FILES" -gt 100 ]; then
        echo -e "  ${GREEN}✓${NC} $SUBSKILL_FILES subskill files"
    elif [ "$SUBSKILL_FILES" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} Only $SUBSKILL_FILES subskill files (expected 100+)"
        ((WARNINGS++))
    fi

    # Total files in domain
    TOTAL_FILES=$(find "$domain" -type f 2>/dev/null | wc -l)

    if [ "$DOMAIN_COMPLETE" = true ]; then
        echo -e "  ${GREEN}✓${NC} Domain complete: $TOTAL_FILES total files"
    else
        echo -e "  ${YELLOW}⚠${NC} Domain incomplete: $TOTAL_FILES total files"
    fi

    echo ""
done

# Summary
echo "======================================"
echo "Summary"
echo "======================================"

TOTAL_FILES=$(find . -type f -name "*.md" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.sh" -o -name "*.tf" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" | wc -l)
TOTAL_DIRS=$(find . -type d | wc -l)

echo "Total files: $TOTAL_FILES"
echo "Total directories: $TOTAL_DIRS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Repository is complete.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warnings found. Review recommended.${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS errors and $WARNINGS warnings found.${NC}"
    echo "Some domains may still be generating. Wait and re-run this script."
    exit 1
fi
