# Collaboration Tools & Research Communication Skill

## Purpose
Master distributed research collaboration platforms, enable effective team communication, version control for protocols and publications, literature management, and open peer review systems for seamless multi-institutional research.

## Core Competencies

### Literature Management & Reference Systems
- **Zotero**: Free, open-source reference manager with browser extension
- **Mendeley**: Commercial alternative with collaboration features
- **EndNote**: Enterprise solution with institutional licensing
- **BibTeX/Citation Management**: For LaTeX users, native text-based approach
- **Literature Reviews**: Systematic search strategies, synthesis, meta-analysis preparation

### Protocol Sharing & Version Control
- **protocols.io**: Shareable, citable, versioned research protocols
- **GitHub**: Code + documentation version control with DOI
- **Open Science Framework (OSF)**: Project management + preregistration
- **Zenodo**: Archiving protocols with persistent DOI

### Document Collaboration & Writing
- **Overleaf**: Cloud-based LaTeX with real-time collaboration
- **Google Docs**: Simple collaborative writing (export to Word/PDF)
- **Microsoft 365**: OneDrive for team document management
- **Notion**: Project documentation and team wikis

### Data & Code Collaboration
- **GitHub/GitLab**: Version control, issue tracking, continuous integration
- **Slack**: Team communication, notifications, integrations
- **Microsoft Teams**: Enterprise messaging with document integration
- **Discord**: Community-based collaboration (academic communities)

### Research Communication Platforms
- **ResearchGate**: Researcher profiles, question Q&A
- **Twitter/X**: Disseminating research findings, engaging scientists
- **Mastodon/Bluesky**: Decentralized social networks for researchers
- **LinkedIn**: Professional networking, career opportunities

### Institutional Collaboration Tools
- **REDCap**: Secure data capture for clinical research
- **Open Science Framework (OSF)**: Preregistration, project management
- **Figshare**: Sharing figures, posters, presentations
- **Zenodo**: Open access repository with DOI integration

## Detailed Workflow: Collaborative Research Project

### Phase 1: Project Setup & Planning (Weeks 1-2)

**Create OSF Project**:
1. Go to osf.io → Create new project
2. Add collaborators (invite by email)
3. Set permissions (admin, read/write, read-only)
4. Connect components (separate workspaces for data, analysis, manuscripts)

**Example OSF Structure**:
```
Project: "Machine Learning for Biomarker Discovery"
├── Component: "Raw Data"
│   ├── Files: Sequencing data, metadata
│   └── Permissions: Read-only (data curators), write access (data collectors)
├── Component: "Analysis Code"
│   ├── Files: Python scripts, Jupyter notebooks
│   └── Linked to: GitHub repo (synced automatically)
├── Component: "Manuscript"
│   ├── Files: Main text, figures, tables
│   └── Linked to: Overleaf project
└── Component: "Preregistration"
    ├── File: Preregistration form (locked, timestamped)
    └── Status: Public (registered at: osf.io/abcde/)
```

**Protocol Setup in protocols.io**:
1. Create protocol with step-by-step instructions
2. Add materials (linked to supplier databases)
3. Version control: Updates create new versions (v1.0, v1.1, v2.0)
4. Collaborators can suggest changes (approval workflow)
5. Final protocol gets DOI (citable: doi.org/10.17504/protocols.io.xxxxx)

### Phase 2: Literature & Reference Management

**Zotero Setup for Team**:
```
1. Install Zotero (zotero.org) + browser connector
2. Create shared group library (File → New Group Library)
3. Invite collaborators (library settings → manage members)
4. Organize by topic:
   - /Reviews/Machine Learning Fundamentals
   - /Reviews/Biomarker Discovery Methods
   - /Methods/Feature Selection
   - /Data/Sequencing Technologies
```

**Workflow**:
- When reading paper → Click Zotero button → Auto-captures citation + PDF
- Highlight important sections in PDF (Zotero annotation tool)
- Add tags + notes for collaboration
- Example note: "@alice Should we cite this for the Feature Selection section?"
- Collaborators see notes, can reply

**Integration with Writing**:
- Overleaf + Zotero: Export bibliography as BibTeX
- Automatically linked: \cite{key} in LaTeX → appears in references with correct formatting

### Phase 3: Code & Data Version Control

**GitHub Repository Setup**:
```bash
# Initialize project
git clone https://github.com/mylab/biomarker_ml
cd biomarker_ml

# Typical structure
tree -L 2
biomarker_ml/
├── README.md
├── LICENSE
├── .gitignore
├── data/
│   ├── raw/          # Original, immutable (not in Git, use large file storage)
│   └── processed/    # Cleaned, analysis-ready
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── model_training.py
│   └── evaluation.py
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   └── 02_model_comparison.ipynb
├── tests/
│   ├── test_preprocessing.py
│   └── test_model.py
├── docs/
│   ├── index.md
│   ├── setup.md
│   └── api.md
└── requirements.txt   # Python dependencies + versions
```

**Collaboration Workflow**:
```bash
# Create feature branch
git checkout -b feature/add-cross-validation

# Make changes, commit frequently
git add src/model_training.py
git commit -m "Implement k-fold cross-validation"

# Push to remote
git push origin feature/add-cross-validation

# Create Pull Request on GitHub
# → Team reviews changes
# → Suggest improvements in comments
# → Merge when approved
```

**GitHub Actions for Continuous Integration**:
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/
```

### Phase 4: Document Collaboration & Writing

**Overleaf Workflow**:
1. Create project: New Project → Blank Project
2. Invite collaborators: Share → Add Collaborators (link or email)
3. Real-time co-editing: See collaborator's cursor, typed characters
4. Comment feature: Highlight text → Add comment → Assign to collaborator
5. Version history: Restore previous versions if needed

**Manuscript Structure**:
```latex
% main.tex
\documentclass{article}
\usepackage{natbib}

\title{Machine Learning for Biomarker Discovery}
\author{Alice Smith \and Bob Johnson}

\begin{document}

\input{sections/introduction}
\input{sections/methods}
\input{sections/results}
\input{sections/discussion}

\bibliography{references}  % Pulls from Zotero-exported references.bib

\end{document}
```

**Example Comment Workflow**:
- Editor highlights: "This paragraph is unclear"
- Comment: "@alice Can you expand on the feature selection rationale?"
- Alice responds: "Done! See v1.3"
- Editor: "Perfect!" → Resolves comment
- Tracks who resolved and when

### Phase 5: Communication & Feedback

**Slack Integration for Research**:
```
Team channels:
- #general: Announcements, team updates
- #research-methods: Discussion of statistical approaches
- #paper-writing: Manuscript feedback, deadlines
- #code-review: GitHub PR notifications (auto-posted)
- #data-quality: Issues with data, validation results

Slack Bots:
- GitHub bot: Notifies when PR is ready for review
- Zotero bot: Shares important papers with team
- Calendar bot: Reminders for manuscript deadlines
```

**Slack + GitHub Integration Example**:
```
When PR submitted:
GitHub → Slack notification:
"Alice submitted PR: Add k-fold cross-validation
#234 in biomarker_ml/src/model_training.py
Assigned reviewers: Bob, Carol"

Team can discuss in Slack before reviewing in GitHub
```

## Preregistration & Open Science

### OSF Preregistration Workflow

**Why Preregister?**
- Separates confirmatory (planned) vs exploratory (post-hoc) analyses
- Prevents p-hacking, increases credibility
- Publicly timestamps your hypotheses

**Steps**:
1. Create OSF project
2. Pre-data collection: Write detailed protocol
   - Hypotheses
   - Study design (sample size, power analysis)
   - Exclusion criteria
   - Analysis plan (not results!)
3. Submit for preregistration
4. Publicly timestamped at: osf.io/abcde/registrations/xxxxx
5. Conduct study
6. Publish with preregistration link → Shows rigor

**Preregistration Template**:
```
1. Study Information
   Title: "Machine Learning Model for Early Cancer Detection"
   Hypothesis: "Model trained on imaging + biomarkers will achieve >85% sensitivity"

2. Study Design
   Population: 500 cancer patients + 500 controls
   Sample size: Calculated to detect d=0.6, power=0.9
   Randomization: 1:1 disease:control

3. Analysis Plan
   Primary: Logistic regression with 5-fold cross-validation
   Metrics: Sensitivity, specificity, AUC, confidence intervals
   Subgroup: Separate analyses for gender (pre-specified)

4. Deviations
   (Completed after data collection if changes made)
```

## Consortium Coordination

### Multi-Site Research Network

**Challenge**: 10 sites across 3 countries, 50 researchers

**Solution Stack**:
1. **OSF**: Central hub for project info, shared protocols
2. **GitHub**: Shared code, analysis standards
3. **Google Drive**: Shared analysis templates, documents
4. **REDCap**: Centralized data capture (secure, HIPAA-compliant)
5. **Zoom/WebEx**: Weekly coordination meetings (recorded)
6. **Slack**: Daily communication

**Governance Structure**:
- Steering Committee (12 members): Makes major decisions
- Data Analysis Subcommittee: Statistical standards, QC rules
- Publications Subcommittee: Manuscript review, authorship

**Example Meeting Minutes (Slack)**:
```
Steering Committee Meeting - 2024-11-19

Attendees: 12 members
Decisions:
- Approved new inclusion criterion (age ≥18, previously 21)
- Accepted statistical analysis plan for primary hypothesis
- Assigned 3 sites to lead manuscript writing

Action Items:
- @alice: Update protocol on protocols.io (v1.1) by Nov 26
- @bob: Coordinate site training calls for new criterion (by Dec 3)
- @carol: Prepare manuscript outline (by Dec 10)

Next meeting: Dec 17, 2pm EST
```

## Open Peer Review Systems

### Transparent Peer Review Platforms

**Platforms supporting open peer review**:
- **eLife**: Sciety (crowdsourced pre-print reviews)
- **Frontiers**: Open peer review (reviewer names disclosed)
- **F1000Research**: Post-publication peer review (immediate publication)
- **PubPeer**: Post-publication commenting on papers

**Benefits**:
- Transparency: See reviewer critiques
- Accountability: Reviewers identifiable, careful criticism
- Crowd sourcing: Community provides feedback beyond 2-3 reviewers
- Speed: Can begin peer review before formal submission

## Tools Integration Examples

### Automated Workflow: From Data to Publication

**Scenario**: New dataset uploaded, want full analysis & preprint

**Automation Script** (pseudocode):
```python
# Trigger: New data file uploaded to OSF
on_file_upload("data/raw/new_cohort.csv"):

    # 1. Data validation
    validate_data()  # Check formats, ranges, missing values
    if validation_fails:
        notify_slack("#data-quality", "Data validation failed")
        return

    # 2. Run analysis
    github_api.trigger_workflow("analysis.yml")
    # GitHub runs: preprocessing → model training → evaluation

    # 3. Generate report
    generate_html_report()  # R Markdown → HTML
    upload_to_osf("reports/")

    # 4. Notify team
    notify_slack("#research-methods", f"New analysis complete: {report_link}")

    # 5. Create preprint
    create_preprint("medRxiv")  # Auto-generates from manuscript
    post_twitter(f"New preprint: {doi}")  # Share findings
```

## Best Practices for Research Collaboration

### Communication Norms
- **Response time**: Aim for 24-hour response to messages
- **Meeting cadence**: Weekly team calls (30-60 min), monthly steering committee
- **Decision making**: Document major decisions in writing (email or Slack thread)
- **Conflict resolution**: Address disagreements promptly, escalate if needed

### Code Quality Standards
- **Code review**: Minimum 1 reviewer per PR (more for critical code)
- **Testing**: All new code must have unit tests (>80% coverage)
- **Documentation**: Docstrings for all functions, README for setup
- **Reproducibility**: Include environment.yml or requirements.txt

### Data Governance
- **Access levels**: Different permissions for different roles (see, edit, admin)
- **Audit trail**: Log who accessed/modified data and when
- **Backup**: Daily backups of shared data to multiple locations
- **Retention**: Define when data can be deleted (often 5-7 years post-publication)

---

## Success Metrics

- [ ] All collaborators can access project materials (OSF/GitHub/Overleaf)
- [ ] Version control maintained (no "final_final_FINAL.docx")
- [ ] Manuscript has clear attribution (contribution statements)
- [ ] Preregistration completed before data analysis
- [ ] Code review process established and followed
- [ ] Team communication structured (channels, meeting notes)
- [ ] Data properly documented (README, data dictionary)

## Common Pitfalls

- **Over-communication**: Too many channels (Slack, email, Teams) → missed messages
- **Unclear permissions**: Collaborator deletes important file by accident
- **Version conflicts**: Multiple people editing document simultaneously → conflicts
- **Scope creep**: Team keeps adding analyses, delays publication
- **Silent collaborators**: Some members inactive; unclear who responsible for what

---

**Version**: 1.0 (Comprehensive)
**Expertise Level**: Intermediate to Advanced
**Estimated Learning Time**: 80-150 hours
**Total Content**: 550+ lines of comprehensive material
