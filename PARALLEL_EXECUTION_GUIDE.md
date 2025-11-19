# Parallel Execution Guide
## Generate All 32 Domains Simultaneously in 60 Minutes

### Quick Start (3 Steps)

1. **Run this first** (in your current tab):
   ```bash
   cd /home/user/CLAUDE_SKILLS
   cat 00_MASTER_PROMPT.md
   ```
   Copy and paste the output to generate global standards.

2. **Open 32 browser tabs** to Claude Code

3. **Run one domain per tab** - Copy the prompt from `PROMPTS.md` for each domain

---

## Execution Strategy

### Tab Organization
```
Tab 01: 01_cloud_computing
Tab 02: 02_software_engineering
Tab 03: 03_data_science_ai
Tab 04: 04_cybersecurity
Tab 05: 05_devops_sre
Tab 06: 06_mobile_development
Tab 07: 07_game_development
Tab 08: 08_blockchain_web3
Tab 09: 09_iot_embedded
Tab 10: 10_product_management
Tab 11: 11_ux_ui_design
Tab 12: 12_digital_marketing
Tab 13: 13_sales_engineering
Tab 14: 14_technical_writing
Tab 15: 15_quality_assurance
Tab 16: 16_database_engineering
Tab 17: 17_network_engineering
Tab 18: 18_systems_architecture
Tab 19: 19_business_intelligence
Tab 20: 20_project_management
Tab 21: 21_financial_technology
Tab 22: 22_healthcare_technology
Tab 23: 23_education_technology
Tab 24: 24_legal_technology
Tab 25: 25_manufacturing_industry_4_0
Tab 26: 26_telecommunications
Tab 27: 27_media_entertainment_tech
Tab 28: 28_energy_sustainability_tech
Tab 29: 29_agriculture_technology
Tab 30: 30_transportation_logistics
Tab 31: 31_real_estate_technology
Tab 32: 32_research_development
```

---

## Cost Calculation

**Budget**: $781 for 60 minutes

**Estimated tokens per domain**:
- Domain generation: ~50K tokens output
- 10 subskills × 15K tokens: ~150K tokens output
- Total per domain: ~200K tokens output

**Pricing** (Claude Sonnet):
- Input: $3 per million tokens
- Output: $15 per million tokens

**Cost per domain**: ~200K × $15/1M = $3 per domain output
**Total for 32 domains**: 32 × $3 = ~$96-$200 (depending on input reuse)

**With your budget**: You can easily run all 32 in parallel!

---

## Time Estimation

Each domain should complete in: **20-40 minutes**

Running in parallel: **All 32 domains complete in ~40 minutes**

---

## Monitoring Progress

Each tab will:
1. Generate domain `skill.md` (2 min)
2. Generate `README.md` (1 min)
3. Generate `standards/` (5-10 min)
4. Generate 10 subskills (20-30 min total)
5. Commit and push to branch

---

## What Gets Generated Per Domain

### Domain Level (5-10 minutes)
- `skill.md` - Domain definition with schema
- `README.md` - Comprehensive domain overview
- `standards/style-guides/` - 3-5 domain-specific guides
- `standards/api-guides/` - 3-5 API integration patterns
- `standards/legacy-integration-guides/` - 2-3 migration guides
- `standards/evidence/` - Research and benchmarks
- `standards/patterns/` - 4-6 domain patterns

### Subskill Level × 10 (20-30 minutes)
For each of 10 subskills:
- `skill.md` - Subskill definition
- `reference/` - 5-10 quick reference files
- `guides/` - 5-10 step-by-step guides
- `src/` - 10-20 code examples/templates

**Total files per domain**: ~150-200 files
**Total files for 32 domains**: ~5,000-6,500 files

---

## Quality Checklist

Each generated domain must include:
- ✅ References to tier-1 professional practices
- ✅ Citations from industry leaders (FAANG, research papers)
- ✅ Production-grade code examples
- ✅ Evidence-based approaches
- ✅ Real-world context and use cases
- ✅ Proper schema compliance
- ✅ Consistent naming conventions
- ✅ Exhaustive coverage (not superficial)

---

## After Completion

Once all 32 tabs complete:

1. **Verify**: Check that all domains have complete structure
   ```bash
   ./verify_structure.sh
   ```

2. **Commit**: Each domain auto-commits, but verify:
   ```bash
   git status
   git log --oneline -32
   ```

3. **Create PR**:
   ```bash
   gh pr create --title "Add 32 professional skill domains" --body "Generated comprehensive skill repository across 32 domains"
   ```

---

## Troubleshooting

**If a tab fails mid-generation**:
- Check the last generated file
- Re-run just that domain's prompt
- It will skip already-generated files

**If rate limited**:
- Stagger tab starts by 10 seconds each
- Or run in 2 batches of 16

**If content quality is low**:
- The prompts enforce elite standards
- If output is superficial, re-run that domain

---

## Next Steps

1. Read `PROMPTS.md` for all 32 domain prompts
2. Copy each prompt into a separate browser tab
3. Let them run in parallel
4. Monitor progress across tabs
5. Verify completion

---

**Estimated Total Time**: 40-50 minutes
**Estimated Total Cost**: $150-$300 (well under budget!)
**Expected Output**: ~5,500 professional-grade skill files
