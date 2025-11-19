# Linear Workflows for Modern Product Teams

## Executive Overview

Linear is a next-generation issue tracking platform optimized for software teams. This guide covers best practices for configuring Linear workflows, team structures, automation, and integration patterns for high-velocity product development.

---

## Table of Contents

1. [Linear Platform Fundamentals](#linear-platform-fundamentals)
2. [Team and Project Structure](#team-and-project-structure)
3. [Issue Management](#issue-management)
4. [Workflow and Automation](#workflow-and-automation)
5. [Custom Fields and Properties](#custom-fields-and-properties)
6. [Views and Filtering](#views-and-filtering)
7. [Integration Ecosystem](#integration-ecosystem)
8. [Performance and Scaling](#performance-and-scaling)
9. [Best Practices](#best-practices)

---

## Linear Platform Fundamentals

### Why Linear Over Jira

| Aspect | Linear | Jira |
|--------|--------|------|
| **Setup Time** | 15 minutes | 2-3 hours |
| **Performance** | Sub-second UI | Variable, can be slow at scale |
| **Learning Curve** | Minimal | Steep (custom fields, workflows) |
| **Mobile Experience** | Native app, full featured | Web-only, limited |
| **Pricing** | Flat per user | Scales with complexity |
| **API/Automation** | GraphQL, webhooks, first-class | REST, limited webhooks |
| **GitHub Integration** | Native, bidirectional | Requires configuration |
| **Search Speed** | Instant, full-text | Indexed, sometimes slow |

### Core Concepts in Linear

```
Team
├── Projects
│   ├── Cycles (Sprints)
│   │   ├── Issues
│   │   │   └── Sub-issues
│   │   └── Milestones
│   └── Workflows (Status progressions)
├── Teams & Groups (Permissions)
├── Custom Fields
├── Views (Saved filters)
└── Integrations (GitHub, Slack, etc.)
```

---

## Team and Project Structure

### Organizational Setup Template

#### Single Product Team

```
Linear Workspace: [Company Name]

Team: Product Engineering
├── Project: Frontend
│   └── Workflows: Feature → In Progress → Review → Testing → Done
├── Project: Backend
│   └── Workflows: Feature → In Progress → Review → Deploy → Done
├── Project: Mobile
│   └── Workflows: Feature → In Progress → Review → Testing → Done
└── Project: Infra
    └── Workflows: Task → In Progress → Review → Done

Cycle Management: 2-week sprints
Standup: Daily 9 AM (async in Slack)
Demo: Friday 4 PM
Retro: Friday 4:30 PM
```

#### Multi-Product Organization

```
Workspace: [Company Org]

Team: Product A
├── Project: PA-Frontend
├── Project: PA-Backend
└── Project: PA-Mobile

Team: Product B
├── Project: PB-Frontend
├── Project: PB-Backend
└── Project: PB-Infra

Team: Platform
├── Project: SDK
├── Project: API
└── Project: DevOps

Team: Design
├── Project: Design System
└── Project: UX Research
```

### Project Naming Convention

```
Pattern: [ABBREVIATION]-[COMPONENT]

Examples:
  - FE-WEB (Frontend Web)
  - BE-API (Backend API)
  - BE-WORKER (Backend Workers)
  - INFRA-DEPLOY (Infrastructure Deployment)
  - DATA-PIPELINE (Data Pipeline)
  - SECURITY (Security)
  - QA-AUTO (QA Automation)
  - MOBILE-IOS (Mobile iOS)
  - MOBILE-ANDROID (Mobile Android)
```

### Team Access Levels

```
Workspace Roles:

1. Admin
   - Full workspace access
   - Can create/delete teams and projects
   - Manage billing
   - Control integrations
   - Typical: 1-2 per organization

2. Team Lead
   - Manage team members
   - Create/configure projects
   - Set workflows
   - Manage automations
   - Typical: 1-2 per team

3. Member
   - Create and edit issues
   - Comment and collaborate
   - View all team data
   - Typical: All engineers and PMs

4. Guest
   - View-only access
   - Can see issues assigned to them
   - Limited collaboration
   - Typical: Contractors, stakeholders
```

---

## Issue Management

### Issue Types in Linear

Linear uses a simpler model than Jira - all items are "Issues" with customizable types.

#### Standard Issue Type Configuration

```
Issue Types:

1. Feature
   - Description: New user-facing functionality
   - Prefix: FEAT
   - Color: Blue
   - Default Priority: Medium
   - Default Estimate: 3 points

2. Bug
   - Description: Defects in existing functionality
   - Prefix: BUG
   - Color: Red
   - Default Priority: High
   - Default Estimate: 2 points

3. Task
   - Description: Technical work without user impact
   - Prefix: TASK
   - Color: Gray
   - Default Priority: Medium
   - Default Estimate: 1 point

4. Spike
   - Description: Research/investigation work
   - Prefix: SPIKE
   - Color: Orange
   - Default Priority: Medium
   - Default Estimate: 2 points
   - Max Duration: 1 cycle

5. Improvement
   - Description: Enhancement to existing feature
   - Prefix: IMP
   - Color: Green
   - Default Priority: Low
   - Default Estimate: 2 points

6. Docs
   - Description: Documentation updates
   - Prefix: DOCS
   - Color: Purple
   - Default Priority: Low
   - Default Estimate: 1 point
```

### Issue Lifecycle Template

```
CREATE ISSUE
  ↓
Title: [Concise description]
Type: [Feature/Bug/Task/Spike/Improvement/Docs]
Description: [Markdown formatted]
Project: [Select appropriate project]
Assignee: [Unassigned initially]
Priority: [Determined in triage]
Estimate: [Fibonacci: 1, 2, 3, 5, 8, 13]
Labels: [Team, Feature Area, Type]
  ↓
TRIAGE (Daily)
  ↓
Priority assigned
Status: Backlog
Labels added for filtering
  ↓
CYCLE PLANNING (Sprint Planning)
  ↓
Added to upcoming cycle
Assigned to team member
Estimate confirmed
  ↓
IN PROGRESS
  ↓
Assignee actively working
Updated daily with progress
Linked to PR/branch
  ↓
REVIEW/TESTING
  ↓
Peer review completed
QA testing if needed
  ↓
DONE
  ↓
Deployed to production
Metrics captured
Closed successfully
```

### Creating Effective Issue Descriptions

#### Feature Template

```markdown
# Feature Request: [Title]

## User Story
As a [user role], I want to [action] so that [benefit].

## Problem Statement
[Context and why this matters]
[Current limitations]
[User pain points]

## Proposed Solution
[How we'll solve this]
[Key features]
[User experience flow]

## Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]
- [ ] Performance meets [specific threshold]
- [ ] Accessibility requirements met (WCAG 2.1 AA)

## Technical Notes
- API endpoint changes: [details]
- Database schema changes: [details]
- Third-party integrations: [details]
- Infrastructure changes: [details]

## Design References
[Link to Figma/Design](link)
[Desktop mockup](link)
[Mobile mockup](link)

## Related Issues
- Relates to: [ISSUE-123]
- Blocked by: [ISSUE-456]
- Blocks: [ISSUE-789]

## Definition of Done
- [ ] Code peer reviewed (2 approvals minimum)
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests passing
- [ ] Staging deployment successful
- [ ] QA sign-off received
- [ ] Documentation updated
- [ ] Product owner approval
- [ ] Production deployment completed
```

#### Bug Template

```markdown
# Bug: [Title]

## Description
[Clear, concise description of the bug]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Bug occurs]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]
[Error messages if applicable]

## Environment
- Browser: [Chrome 120, Safari 17, etc.]
- OS: [macOS 14, Windows 11, Linux, etc.]
- App Version: [1.2.3]
- User Type: [Free/Pro/Enterprise]

## Impact Assessment
- Severity: [Critical/High/Medium/Low]
- Affected Users: [number/percentage]
- Data Loss Risk: [Yes/No]
- Security Impact: [Yes/No]

## Attachments
- Screenshot: [image showing issue]
- Video: [reproduction video]
- Error Log: [relevant error logs]
- Network Request: [HAR file or request details]

## Potential Root Cause
[If obvious, describe suspected cause]
```

---

## Workflow and Automation

### Standard Development Workflow

```
BACKLOG → STARTED → IN REVIEW → DONE → SHIPPED
   ↓
[UNSTARTED]
```

### Workflow States Explained

```
BACKLOG (Unstarted)
├── Purpose: Issues not yet assigned to a cycle
├── Team: Product owners, leads
├── DurationTarget: < 2 weeks before cycle
└── NextAction: Add to upcoming cycle

STARTED (In Progress)
├── Purpose: Actively being worked on
├── Team: Assigned engineer
├── DurationTarget: < 5 days
├── NextAction: Move to review when code ready
└── Tracking: Daily updates expected

IN REVIEW (Review/QA)
├── Purpose: Code/design under review
├── Team: Code reviewers, QA team
├── DurationTarget: < 2 days
├── NextAction: Address feedback or approve
└── Tracking: Reviewer comment expectations

DONE (Completed)
├── Purpose: Work completed, in staging
├── Team: QA confirmation
├── DurationTarget: < 1 day
├── NextAction: Wait for production deployment
└── Tracking: Deployment tracking field

SHIPPED (Production)
├── Purpose: Successfully deployed to production
├── Team: DevOps/Platform
├── DurationTarget: Same day or next day
├── NextAction: Monitor for issues
└── Tracking: Deployment date recorded
```

### Linear Automation Setup

#### Automation Rule 1: Auto-Assign on Cycle Start

```
Trigger: Issue added to cycle
Conditions:
  - Status is Backlog
  - Assignee is empty
  - Priority is not Low

Actions:
  - Assign to project default assignee
  - Add label "cycle-ready"
  - Send Slack notification to assignee
```

#### Automation Rule 2: Update Status on PR Link

```
Trigger: PR linked to issue
Conditions:
  - Current status is Backlog
  - PR status is Draft

Actions:
  - Move issue to Started
  - Add label "in-progress"
  - Send notification to watchers
```

#### Automation Rule 3: Auto-Move to Review

```
Trigger: PR marked Ready for Review
Conditions:
  - Linked issue exists
  - Current status is Started

Actions:
  - Move to In Review
  - Request reviews from codeowners
  - Notify QA team
  - Add comment: "Ready for review"
```

#### Automation Rule 4: Escalate Stalled Issues

```
Trigger: Time-based (Daily 10 AM)
Conditions:
  - Status is Started or In Review
  - No updates in last 48 hours
  - Not marked as blocked

Actions:
  - Add label "stalled"
  - Send Slack reminder to assignee
  - Notify team lead
```

#### Automation Rule 5: Daily Standup Digest

```
Trigger: Time-based (Daily 9 AM)
Conditions:
  - Team members have active issues

Actions:
  - Send Slack message to channel
  - List: Issues in Started status
  - List: Blocked issues
  - List: Completed since yesterday
```

#### Automation Rule 6: Archive Completed Cycles

```
Trigger: Cycle end date reached
Conditions:
  - All issues in cycle are Done or Shipped
  - 7 days have passed since cycle end

Actions:
  - Archive cycle
  - Calculate metrics (velocity, cycle time)
  - Send summary report
```

#### Automation Rule 7: Auto-Create Sub-Issues

```
Trigger: Issue created with label "design-required"
Conditions:
  - Issue type is Feature
  - Priority is High or Critical

Actions:
  - Create sub-issue: Design Review
  - Create sub-issue: Technical Specification
  - Create sub-issue: QA Testing Plan
  - Assign to respective teams
```

#### Automation Rule 8: Link Related Issues

```
Trigger: Issue created or updated
Conditions:
  - Summary contains "API"
  - Project contains "Frontend"

Actions:
  - Search for related Backend issues
  - Create "Relates to" link
  - Add comment with link
  - Notify backend team
```

---

## Custom Fields and Properties

### Essential Custom Fields

#### 1. Story Points

```
Type: Number
Range: 1-21 (Fibonacci)
Default: Unset
Required: Yes, before sprint
Used In: Capacity planning, velocity tracking
Formula: Relative complexity assessment
```

#### 2. Business Value

```
Type: Single Select
Options:
  - Critical (revenue impact, blocking)
  - High (OKR aligned, user visible)
  - Medium (improves UX, useful)
  - Low (nice to have, technical debt)
Default: Medium
Required: Yes, for all features
Priority: Used for prioritization
```

#### 3. Component/Area

```
Type: Single Select
Options:
  - Frontend
  - Backend
  - Mobile
  - Infrastructure
  - DevOps
  - Security
  - Data
  - Performance
  - Design
  - QA
Default: Varies by project
Required: Yes
Used In: Filtering, reports, ownership
```

#### 4. Sprint/Cycle

```
Type: Cycle
Auto-Assigned: Yes
Linked To: Linear native cycles
Used In: Sprint planning, burndown
Visible In: All views
```

#### 5. Effort Estimate (Days)

```
Type: Number
Range: 0.5-20
Default: Unset
Different From: Story Points (relative vs absolute)
Used In: Calendar planning, capacity
```

#### 6. Dependencies

```
Type: Multiple Select
Options:
  - Frontend Dependency
  - Backend Dependency
  - Mobile Dependency
  - Data Migration
  - Third-party Integration
  - Design Review
  - Security Review
Default: None
Used In: Dependency tracking, release planning
```

#### 7. Design Status

```
Type: Single Select
Options:
  - Not Started
  - In Progress
  - Under Review
  - Approved
  - Needs Revision
  - Final Ready
Default: Not Started
Used In: Design workflow tracking
```

#### 8. QA Status

```
Type: Single Select
Options:
  - Not Tested
  - Testing
  - Test Failed
  - Test Passed
  - Production Verified
Default: Not Tested
Used In: QA workflow
```

### Advanced Custom Properties

#### Target Release

```
Type: Single Select
Options: [v1.0, v1.1, v2.0, etc.]
Used For: Release planning and versioning
View: Roadmap view
```

#### Risk Level

```
Type: Single Select
Options:
  - Low Risk
  - Medium Risk
  - High Risk (requires review)
Critical For: Changes to core systems
```

#### Affected Systems

```
Type: Multiple Select
Options: [List of microservices, components]
Used For: Impact analysis
```

---

## Views and Filtering

### Essential Views

#### View 1: Current Sprint

```
Filter: Cycle = Current Cycle
  AND Status != Shipped
Display: Board view
Grouping: Status (columns)
Sorting: Priority, then Estimate
WIP Limits: Started (8), In Review (5)
Purpose: Daily work focus
```

#### View 2: Backlog Prioritization

```
Filter: Cycle = Unassigned
  AND Status = Backlog
Display: List view
Sorting: Priority (High to Low), then Business Value
Grouping: Component
Purpose: Backlog refinement
```

#### View 3: In Progress (Daily Standup)

```
Filter: Status = Started OR Status = In Review
Display: List view
Columns: Title, Assignee, Priority, Estimate, Days in Status
Sorting: Days in Status (descending - show stalled)
Purpose: Identify blockers and progress
```

#### View 4: Team Capacity

```
Filter: Cycle = Current Cycle
Display: Table view
Columns: Assignee, Issue Count, Total Points, % Capacity
Grouping: Assignee
Purpose: Load balancing, sprint planning
```

#### View 5: Bugs by Severity

```
Filter: Type = Bug
  AND Status != Shipped
Display: List view
Grouping: Priority
Sorting: Priority (High to Low), then Created (newest first)
Purpose: Bug triage and fixes
```

#### View 6: Blocked Issues

```
Filter: Status = Blocked
  OR (Labels contains "blocked" OR "waiting")
Display: Board view
Sorting: Days blocked (descending)
Purpose: Unblock work, resolve dependencies
```

#### View 7: Release Ready

```
Filter: Cycle = [Target Release]
  AND Status = Done
Display: List view
Columns: Title, Component, Estimate, Assignee
Grouping: Component
Purpose: Release notes, deployment planning
```

#### View 8: Cycle Analytics

```
Filter: Cycle = [Selected Cycle]
Display: Metrics
Metrics:
  - Total Issues: [count]
  - Completed: [count, %]
  - Carried Over: [count]
  - Velocity: [story points]
  - Cycle Time: [average days]
  - On Time: [%]
Purpose: Retrospective, planning accuracy
```

### Advanced Filter Syntax

```
Simple Filters:
  - assignee:me (my issues)
  - status:started (in progress)
  - priority:high (high priority only)
  - cycle:[current] (current sprint)
  - label:frontend (team area)
  - type:bug (issue type)

Complex Filters:
  - (status:started OR status:"in review") AND priority:high
  - assignee:me AND type:bug AND status:started
  - cycle:[current] AND estimate:<=3 (small issues)
  - status:done AND cycle:"last 2 weeks" (recently completed)
  - label:frontend AND label:critical
```

---

## Integration Ecosystem

### GitHub Integration (Native)

#### Issue Linking

```
In PR description, reference issues:

  "Fixes #FE-123" - Auto-closes issue on merge
  "Relates to #BE-456" - Links without closing
  "Blocked by #INFRA-789" - Documents dependency

In commits:
  "git commit -m 'FE-123: Add dark mode toggle'"
  - Auto-links commit to issue
  - Creates activity log entry
```

#### Branch Naming Convention

```
Pattern: [PROJECT]-[ISSUE_NUMBER]-[brief-description]

Examples:
  - FE-234-dark-mode-toggle
  - BE-567-user-auth-endpoint
  - MOBILE-123-offline-support
  - INFRA-89-aws-migration

Benefits:
  - Auto-linking to Linear issues
  - Clear issue context in git history
  - Easy to identify branch purpose
```

#### PR Status Sync

```
PR State → Linear Action

Draft:
  - Move to Started (if not already)
  - Add "in-progress" label

Ready for Review:
  - Move to In Review
  - Request Linear reviewers

Changes Requested:
  - Keep in In Review
  - Notify assignee of feedback

Approved:
  - Mark as ready to merge
  - Can move to Done before merge

Merged:
  - Auto-move to Done (if configured)
  - Auto-move to Shipped (if configured)
```

### Slack Integration

#### Notification Configuration

```
Critical Alerts:
  - High/Critical issues assigned to you
  - Issues you're watching updated
  - @mentions in issues
  - Issues unblocked/blocked

Daily Digest:
  - Morning standup: Your active issues
  - Issues stalled > 2 days
  - Cycle progress
  - Due dates approaching

Custom Alerts:
  - Frontend issues priority high
  - Bugs in production
  - Security issues
  - Issues assigned to your team
```

#### Slack Commands

```
/linear
  - /linear [issue] - Show issue details
  - /linear my issues - List my active issues
  - /linear assign me [issue] - Self-assign
  - /linear update [issue] [status] - Quick status change
  - /linear comment [issue] [message] - Add comment

Shortcuts:
  - Use "Save to Linear" on any message
  - Create issues from Slack conversation
  - Get issue summaries inline
```

### Gmail Integration

```
Issue Creation from Email:
  - Forward email to [project]@linear.app
  - Auto-creates issue with email content
  - Attaches email as context

Issue Notifications:
  - Subscription to issue updates
  - Threaded email conversations
  - Digest emails for cycles
```

### Calendar Integration (Google/Outlook)

```
Sync Events:
  - Cycle start/end dates
  - Cycle deadlines
  - Sprint planning sessions
  - Demo sessions
  - Retro sessions

Cycle Duration:
  - Block calendar for cycle length
  - Mark planning/demo/retro as busy
  - Share with stakeholders
```

### Analytics Integration

```
Tools: Tableau, Looker, Amplitude

Metrics Exported:
  - Velocity per cycle
  - Cycle time by type/priority
  - Team productivity
  - Feature delivery timeline
  - Bug trends
  - Deployment frequency

API Endpoint:
  - GraphQL queries for metrics
  - Webhook for real-time updates
  - Automatic syncs hourly
```

---

## Performance and Scaling

### Optimization Tips

#### Query Optimization

```
Inefficient:
  - Loading all issues (10,000+)
  - No filtering on cycle/project
  - Fetching all custom fields

Optimized:
  - Filter by current cycle
  - Limit to active projects
  - Only fetch needed fields
  - Use pagination (first: 50)
```

#### Board Performance

```
For large teams (50+ members):
  - Use swimlanes by team, not assignee
  - Limit WIP to collapse columns
  - Group by status (not by multiple fields)
  - Archive old cycles (> 3 months)

For many projects:
  - Use project teams instead of workspace views
  - Create team-specific dashboards
  - Archive completed projects
```

#### Custom Field Usage

```
Best Practices:
  - Use built-in fields where possible
  - Limit custom fields to < 15 active
  - Archive unused custom fields
  - Use Single Select (not free text) for options

Performance Impact:
  - Each custom field slows load slightly
  - Large number of options in select = slower
  - Computed fields = slower searches
```

---

## Best Practices

### Estimation Best Practices

```
Fibonacci Sequence: 1, 2, 3, 5, 8, 13, 21

Guidelines:
  1 = Simple task, < 2 hours
  2 = Straightforward, 2-4 hours
  3 = Clear scope, < 1 day
  5 = Some complexity, 1-2 days
  8 = Significant work, 2-3 days
  13 = Complex, 3-5 days
  21 = Very complex, > 5 days (consider breaking down)

Rules:
  - 21 is a warning to split the issue
  - Don't estimate during creation (estimate in planning)
  - Re-estimate if scope changes > 50%
  - Track estimation accuracy quarterly
```

### Labeling Strategy

```
Recommended Labels:

Team/Ownership:
  - team:frontend
  - team:backend
  - team:mobile
  - team:platform

Feature Area:
  - area:auth
  - area:payments
  - area:analytics
  - area:ui

Type/Category:
  - type:refactoring
  - type:tech-debt
  - type:performance
  - type:security
  - type:accessibility

Status/Flags:
  - blocked
  - needs-design-review
  - needs-security-review
  - on-hold
  - in-progress
  - rework

Naming Convention:
  - Lowercase, hyphen-separated
  - Max 20 characters
  - Meaningful, reusable
  - < 30 total labels per workspace
```

### Cycle Planning Best Practices

```
Cycle Length: 2 weeks (10 working days)
  - Planning: Day 1 (morning)
  - Demo: Day 10 (afternoon)
  - Retro: Day 10 (after demo)
  - Planning Break: Between cycles

Capacity Planning:
  - Target: 80% team capacity per cycle
  - Account for: Meetings, interrupts, support
  - Reserve: 20% for unexpected issues
  - Track: Actual vs planned

Cycle Composition:
  - Features: 50%
  - Bug fixes: 20%
  - Tech debt/improvements: 20%
  - Spikes/research: 10%
```

### Issue Backlog Health

```
Metrics to Track:

Backlog Sizing:
  - Target: 2-3 cycles of work in backlog
  - Too small: Risk of running out
  - Too large: Decision paralysis

Issue Staleness:
  - Review quarterly
  - Archive issues > 6 months old with no updates
  - Move unstarted > 2 cycles to external tracker

Estimation Coverage:
  - Target: > 90% of backlog estimated
  - Unestimated items get reviewed in planning

Acceptance Criteria:
  - 100% of stories should have clear criteria
  - Review in backlog refinement sessions
```

### Team Communication

```
Async Standup:
  - Post daily in #standup channel
  - Format: What I did | What I'm doing | Blockers
  - Timing: Before standup meeting time

Weekly Sync:
  - Cycle progress review
  - Blockers discussion
  - Priorities for next days
  - Duration: 30 minutes

Weekly Demo:
  - Show completed features
  - Gather feedback
  - Demo to stakeholders
  - Duration: 30 minutes

Bi-weekly Retro:
  - What went well
  - What could improve
  - Action items
  - Duration: 45 minutes
```

### Issue Lifecycle Checklist

Before Creating Issue:
- [ ] Check for duplicates
- [ ] Add to appropriate project
- [ ] Use clear, searchable title
- [ ] Select correct type

During Sprint:
- [ ] Update status daily
- [ ] Link to PR/branch
- [ ] Comment on progress
- [ ] Flag blockers immediately

On Completion:
- [ ] Code reviewed and merged
- [ ] QA tested and approved
- [ ] Move to Shipped
- [ ] Comment with deployment date

---

## Migration from Other Platforms

### From Jira to Linear

```
Migration Steps:

1. Export from Jira
   - Projects
   - Issues with history
   - Custom fields mapping
   - Team structure

2. Map Jira Concepts → Linear
   - Epic → Parent issue
   - Sprint → Cycle
   - Workflow → Linear workflow
   - Custom fields → Linear properties

3. Import into Linear
   - Use official Jira importer
   - Validate data accuracy
   - Test automation rules
   - Verify permissions

4. Validation Phase
   - Check issue counts
   - Verify assignments
   - Test key automations
   - Confirm permissions

5. Team Training
   - Feature walkthrough
   - Workflow demonstration
   - Automation overview
   - Q&A session
```

### Data Mapping Reference

| Jira | Linear |
|------|--------|
| Epic | Parent Issue (Type) |
| Sprint | Cycle |
| Story | Feature (Issue) |
| Bug | Bug (Issue) |
| Task | Task (Issue) |
| Sub-task | Sub-issue |
| Workflow Status | Status |
| Label | Label |
| Custom Field | Custom Property |
| Issue Link | Issue Relation |

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Issues not syncing with GitHub | Integration disconnected | Reconnect in Settings > Integrations |
| Automations not firing | Conditions too strict | Check condition logic, test manually |
| Performance degradation | Too many custom fields | Archive unused fields, clean up |
| Wrong assignees in cycle | Auto-assign rule misconfigured | Review assignment rules |
| Estimates incorrect | Poor process discipline | Implement estimation training |
| Team can't find issues | Poor labeling/filtering | Create saved views, improve labels |

---

## Conclusion

Linear provides a modern, efficient platform for product teams. Success depends on:

1. **Clear Process**: Defined workflows and statuses
2. **Consistent Discipline**: Daily updates, honest estimates
3. **Smart Automation**: Reduce manual work, increase accuracy
4. **Team Communication**: Regular syncs and feedback
5. **Data-Driven Decisions**: Use metrics to improve

Monitor these metrics quarterly:
- Velocity trends
- Cycle time by issue type
- On-time delivery rate
- Bug escape rate
- Team satisfaction

Continuously refine based on team feedback and organizational needs.
