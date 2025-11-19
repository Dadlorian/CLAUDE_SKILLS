# Jira Workflows for Product Teams

## Executive Overview

This guide provides complete Jira configuration templates for product teams managing complex workflows, multiple sprints, and cross-functional collaboration. Includes board setups, automation rules, custom fields, and best practices.

---

## Table of Contents

1. [Project Setup](#project-setup)
2. [Board Configuration](#board-configuration)
3. [Workflow States](#workflow-states)
4. [Automation Rules](#automation-rules)
5. [Custom Fields](#custom-fields)
6. [Templates and Standards](#templates-and-standards)
7. [Team Permissions](#team-permissions)
8. [Integration Points](#integration-points)

---

## Project Setup

### Recommended Project Structure

#### Multi-Team Configuration

```
Product Portfolio Project (Company)
├── Product A
│   ├── Backend Team
│   ├── Frontend Team
│   └── QA Team
├── Product B
│   ├── Platform Team
│   └── Mobile Team
└── Infrastructure
    ├── DevOps Team
    └── Security Team
```

### Project Initialization Checklist

- [ ] Create parent project for portfolio management
- [ ] Set up team-specific projects with shared components
- [ ] Configure issue linking structure
- [ ] Enable Jira Service Desk for intake requests
- [ ] Set up automation templates
- [ ] Initialize custom fields
- [ ] Configure permission schemes
- [ ] Enable time tracking and estimation
- [ ] Set up notification schemes
- [ ] Configure webhooks for integrations

### Project Configuration Template

```yaml
Project Name: [Product Name]
Project Key: [PROD]
Project Type: Team-Managed or Company-Managed (use Company-Managed for complex workflows)

Issue Types:
  - Epic: Large strategic initiatives (2+ sprints)
  - Story: User-facing features (~3-5 story points)
  - Task: Technical work without user value
  - Bug: Defects requiring fixes
  - Improvement: Enhancements to existing features
  - Spike: Research/investigation work (1-2 sprints max)
  - Sub-task: Granular work items under stories

Category Structure:
  - Frontend
  - Backend
  - Infrastructure
  - Data
  - DevOps
  - QA
  - Security
  - Documentation
  - Design
```

---

## Board Configuration

### Scrum Board Setup

#### Standard Sprint Workflow Board

```
COLUMN LAYOUT:

Backlog | To Do | In Progress | In Review | Testing | Done
--------|-------|-------------|-----------|---------|-----
        |       |             |           |         |
```

#### Column Automation Rules

| Column | Entry Criteria | Auto-Actions |
|--------|---|---|
| **Backlog** | Issue created | Notify Epic Lead |
| **To Do** | Sprint started | Estimate if missing |
| **In Progress** | Developer assigned | Time tracking starts |
| **In Review** | Code ready | PR link created, notify reviewers |
| **Testing** | Review approved | Testing team notified |
| **Done** | QA approved | Sprint metrics updated |

#### Board Configuration Metadata

```json
{
  "board_name": "Product Team Sprint Board",
  "board_type": "scrum",
  "sprint_field": "Sprint",
  "rank_field": "Rank",
  "columns": [
    {
      "name": "Backlog",
      "statuses": ["Backlog"],
      "min_issues": 10,
      "max_issues": 50
    },
    {
      "name": "To Do",
      "statuses": ["To Do"],
      "wip_limit": null,
      "automation": "require_estimation"
    },
    {
      "name": "In Progress",
      "statuses": ["In Progress"],
      "wip_limit": 8,
      "assignee_required": true
    },
    {
      "name": "In Review",
      "statuses": ["In Review"],
      "wip_limit": 5,
      "approval_required": true
    },
    {
      "name": "Testing",
      "statuses": ["Testing"],
      "wip_limit": 5,
      "qa_assigned": true
    },
    {
      "name": "Done",
      "statuses": ["Done"],
      "auto_metrics": ["story_points", "cycle_time", "deployment_date"]
    }
  ],
  "swimlanes": [
    "Team",
    "Priority",
    "Assignee"
  ]
}
```

### Kanban Board Setup (For Support/Ops)

```
COLUMN LAYOUT:

Incoming | Intake | Backlog | In Progress | Blocked | QA Testing | Done
---------|--------|---------|-------------|---------|------------|-----
SLA: 4h | SLA: 8h | N/A | Assigned | Details | SLA: 24h | SLA: 1h
```

#### Kanban-Specific Rules

- **WIP Limits**: Incoming (10), Backlog (20), In Progress (6), QA (4)
- **SLA Monitoring**: Red flag items in any column after SLA threshold
- **Auto-escalation**: Items in Blocked > 2 days notify manager
- **Quick Filters**: By Priority, By Assignee, By Team, SLA Status

---

## Workflow States

### Standard Product Development Workflow

```
Backlog
  ↓
To Do (Sprint Planning)
  ↓
In Progress (Team starts work)
  ↓
In Review (Code review/QA review)
  ↓ (If approved)
Testing (QA testing)
  ↓ (If passed)
Done (Deployed/Completed)

  ↓ (If rejected)
In Progress (Rework)
```

### Workflow Transition Rules

```
From To Do:
  → In Progress: [Require Assignee] [Log Time >= 15 min]
  → Backlog: [Require Comment] [Remove from Sprint]

From In Progress:
  → In Review: [Require PR Link] [Require Reviewer]
  → Backlog: [Only for Sprint Lead]
  → Blocked: [Require Blocker Description]

From In Review:
  → Testing: [Require Approval] [Notify QA Team]
  → In Progress: [Require Comment] [Unassign Reviewer]

From Testing:
  → Done: [Require QA Sign-off] [Log Completion Date]
  → In Progress: [Require Bug Report] [Create linked bug]

From Blocked:
  → In Progress: [Require Blocker Resolution] [Log blocked time]
  → Backlog: [Require Decision] [Notify stakeholder]
```

### Additional Workflow States (Optional)

- **Blocked**: Issue waiting on external dependency
- **Staging**: Deployed to staging environment
- **In Beta**: Feature in beta with subset of users
- **Documentation**: Awaiting documentation completion
- **On Hold**: Scheduled for future sprint
- **Won't Do**: Rejected or out of scope

---

## Automation Rules

### Rule 1: Auto-Assignment on Sprint Start

```
Trigger: Sprint Started
Conditions:
  - Status = To Do
  - Assignee = Empty
  - Epic != Empty
Actions:
  - Assign to Epic Owner
  - Add label "sprint-ready"
  - Send notification to assignee
```

### Rule 2: Auto-Link Related Issues

```
Trigger: Issue Created
Conditions:
  - Summary contains "API"
  - Project = Frontend
Actions:
  - Link to Backend Epic as "relates to"
  - Add label "requires-backend"
  - Mention @backend-team in comment
```

### Rule 3: Escalate Stalled Work

```
Trigger: Time-based (Daily 9 AM)
Conditions:
  - Status = In Progress
  - Updated < 2 days ago
  - Assignee != Empty
Actions:
  - Add label "stalled"
  - Send email to team lead
  - Create incident if marked Critical
```

### Rule 4: Auto-Move to Testing on PR Merge

```
Trigger: Webhook - PR Merged
Conditions:
  - Jira Issue in PR Title
  - Current Status = In Review
Actions:
  - Move to Testing
  - Notify QA Team
  - Add comment: "Merged to main branch"
  - Assign to QA Lead
```

### Rule 5: Close Related Issues on Epic Completion

```
Trigger: Status Changed to Done
Conditions:
  - Issue Type = Epic
  - Child Issues all Done
Actions:
  - Auto-close Epic
  - Calculate sprint metrics
  - Send completion summary email
  - Update dashboard
```

### Rule 6: Daily Standup Notifications

```
Trigger: Time-based (Weekdays 9 AM)
Conditions:
  - Status = In Progress
  - Assignee != Empty
Actions:
  - Send reminder to assignee
  - Request status comment if missing
  - Highlight blocked items
```

### Rule 7: Sprint Planning Prep

```
Trigger: Time-based (Friday 4 PM before sprint start)
Conditions:
  - Issue in Backlog
  - Has Story Points
Actions:
  - Notify Backlog Owner
  - Add checklist: Acceptance Criteria, Design Review
  - Tag unrefined issues with "needs-refinement"
```

### Rule 8: Auto-Create Subtasks

```
Trigger: Issue Created
Conditions:
  - Issue Type = Story
  - Has label "design-required"
Actions:
  - Create subtask: "Design Review"
  - Create subtask: "Engineering Estimate"
  - Create subtask: "Documentation"
  - Assign to respective teams
```

---

## Custom Fields

### Critical Custom Fields

#### 1. Story Points (Fibonacci Scale)

```
Type: Number Field
Display Name: Story Points
Values: 1, 2, 3, 5, 8, 13, 21
Used in: Estimation, Sprint Velocity, Capacity Planning
Required: For all Stories and Subtasks
Scope: Backlog, In Progress, Testing, Done
```

#### 2. Business Value

```
Type: Single Select
Display Name: Business Value
Options:
  - Critical (revenue, security, compliance)
  - High (directly impacts OKR)
  - Medium (improves user experience)
  - Low (nice to have, technical debt)
Default: Medium
Required: For all Stories in sprints
```

#### 3. Sprint Focus Area

```
Type: Multiple Select
Display Name: Sprint Focus Area
Options:
  - Performance
  - Reliability
  - Features
  - Technical Debt
  - Infra/DevOps
  - Security
  - UX/Design
Default: Features
```

#### 4. Design Status

```
Type: Single Select
Display Name: Design Status
Options:
  - Not Started
  - In Progress
  - Approved
  - Needs Revision
  - Final Design Ready
Linked to: Design Review Workflow
```

#### 5. External Dependencies

```
Type: Checkboxes
Display Name: Has External Dependency
Options:
  - Partner Integration Required
  - Infrastructure Change Required
  - Third-party Approval Required
  - Data Migration Required
Auto-action: Flag for dependency management
```

#### 6. Acceptance Criteria

```
Type: Rich Text Field
Display Name: Acceptance Criteria
Description: Use markdown checkboxes for tracking
Template:
  - [ ] User can [action] on [page]
  - [ ] [Scenario] behaves as expected
  - [ ] Performance meets [threshold]
```

#### 7. Test Coverage

```
Type: Single Select
Display Name: Test Coverage
Options:
  - Not Planned
  - Unit Tests Only
  - Unit + Integration
  - Full Coverage (Unit + Integration + E2E)
  - Manual Testing Only
Required: For bugs and features
```

#### 8. Effort Estimate (Days)

```
Type: Number Field
Display Name: Effort Estimate (Days)
Range: 0-20
Used for: Capacity planning, realistic timeline assessment
Different from: Story Points (which are relative complexity)
```

---

## Templates and Standards

### Story Template

```
Summary: [As a {user}] {action} [so that {benefit}]

Epic Link: [Select appropriate epic]

Story Points: [Leave empty for refinement phase]

Description:
## User Story
As a [user role]
I want to [action]
So that [benefit]

## Background
[Context about why this matters]

## Acceptance Criteria
- [ ] [Specific, measurable outcome]
- [ ] [Specific, measurable outcome]
- [ ] [Specific, measurable outcome]

## Design Notes
[Link to Figma/Design]
- Desktop mockup: [link]
- Mobile mockup: [link]

## Technical Considerations
- [API changes needed]
- [Database migrations]
- [Third-party integrations]

## Definition of Done
- [ ] Code peer reviewed (2 approvals)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests passing
- [ ] Design review approved
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] QA sign-off
- [ ] Product owner approval
```

### Bug Template

```
Summary: [Module] Issue with [specific problem]

Issue Type: Bug

Priority: [Critical/High/Medium/Low]

Description:
## Problem
[Clear description of the bug]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Bug occurs]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- Browser: [version]
- OS: [version]
- App Version: [version]
- User Type: [type]

## Severity
- User Impact: [High/Medium/Low]
- Affected Users: [number/percentage]
- Data Impact: [yes/no/describe]

## Attachments
- Screenshot: [attach]
- Video: [attach]
- Error Log: [attach]
```

### Epic Template

```
Summary: [Strategic initiative name]

Issue Type: Epic

Objective & Key Results (OKR):
- Objective: [20+ character meaningful goal]
- Key Result 1: [Measurable metric]
- Key Result 2: [Measurable metric]
- Key Result 3: [Measurable metric]

Description:
## Vision
[2-3 paragraph description of why this epic matters]

## Success Metrics
- [Metric 1]: Current [x], Target [y]
- [Metric 2]: Current [x], Target [y]
- [Metric 3]: Current [x], Target [y]

## Timeline
- Start: [Date]
- Target Completion: [Date]
- Planned Sprints: [Number]

## Dependencies
- Internal: [List teams/systems]
- External: [List partners/constraints]

## Stakeholders
- Epic Owner: [Name]
- Product Owner: [Name]
- Tech Lead: [Name]
```

---

## Team Permissions

### Role-Based Permission Matrix

```
┌─────────────────────┬──────┬──────┬───────┬────┬──────┬──────┐
│ Action              │ Dev  │ QA   │ PO    │ PM │ Lead │ Exec │
├─────────────────────┼──────┼──────┼───────┼────┼──────┼──────┤
│ Create Issue        │ Yes  │ Yes  │ Yes   │ Yes│ Yes  │ No   │
│ Edit Own Issues     │ Yes  │ Yes  │ Yes   │ Yes│ Yes  │ No   │
│ Edit All Issues     │ No   │ No   │ No    │ Yes│ Yes  │ No   │
│ Delete Issues       │ No   │ No   │ No    │ No │ Yes  │ No   │
│ Manage Sprints      │ No   │ No   │ No    │ Yes│ Yes  │ No   │
│ Manage Board        │ No   │ No   │ No    │ No │ Yes  │ No   │
│ View Reports        │ Yes  │ Yes  │ Yes   │ Yes│ Yes  │ Yes  │
│ Configure Project   │ No   │ No   │ No    │ No │ Yes  │ No   │
│ Manage Permissions  │ No   │ No   │ No    │ No │ No   │ Yes  │
│ Transition Issues   │ Yes* │ Yes* │ Yes*  │ Yes│ Yes  │ No   │
└─────────────────────┴──────┴──────┴───────┴────┴──────┴──────┘

* = Limited to specific statuses
```

### Developer Permissions

```
Group: jira-developers
Permissions:
  - Create Issues in current project
  - View Project
  - Transition issues: To Do → In Progress → In Review
  - Edit own issues
  - Add work logs
  - View board and backlog
  - Add child issues
  - Link issues
  - Add attachments
  - Create branch from issue
```

### QA Permissions

```
Group: jira-qa
Permissions:
  - View project
  - Transition issues: Testing → Done (for QA) / In Progress (for bugs)
  - Create bugs
  - Add work logs
  - View board and backlog
  - Add comments and attachments
  - Link to bug reports
```

### Product Owner Permissions

```
Group: jira-product-owners
Permissions:
  - All developer permissions
  - Create epics and stories
  - Manage backlog (reorder, add to sprint)
  - Transition issues: To Do → Backlog
  - Create and manage sprints
  - View reports
  - Edit acceptance criteria
  - Approve issues for sprint
```

### Team Lead Permissions

```
Group: jira-team-leads
Permissions:
  - All product owner permissions
  - Edit workflow transitions
  - Manage labels and components
  - Configure automation rules (read-only for team leads, edit for admins)
  - Delete issues (with review)
  - Create sub-tasks
  - Manage team capacity
```

---

## Integration Points

### GitHub Integration

```yaml
Jira <> GitHub Automation:

Smart Commits in PR descriptions:
  - Format: "PROJECT-123 #time 2h"
  - Triggers: Auto-update issue, log time, transition status

Commit Message Keywords:
  - "fixes PROJECT-123": Auto-close on merge
  - "relates to PROJECT-123": Link issue
  - "#time 1h": Log work

Webhook: GitHub → Jira
  - Trigger: PR created, commented, merged
  - Action: Update issue, move to testing column, notify team

Branch Naming:
  - Pattern: PROJECT-123-brief-description
  - Example: PROD-1234-user-authentication
```

### Slack Integration

```yaml
Slack Notifications:

Daily Standup:
  - Command: /jira standup
  - Shows: Today's active issues, blockers, completed items

Sprint Updates:
  - Trigger: Daily 9 AM standup
  - Shows: Sprint progress, burndown, at-risk items

Assignment Notifications:
  - Trigger: Issue assigned
  - Shows: Link to issue, context

Comment Mentions:
  - Trigger: @username in Jira comment
  - Action: Slack notification with context

Jira Search:
  - Command: /jira PROJECT-1234
  - Returns: Issue details, status, next steps
```

### Release Management Integration

```yaml
Jira <> CI/CD Pipeline:

Deployment Tracking:
  - Custom field: "Deployment Date"
  - Auto-populated on successful deployment
  - Triggers: Move to Done, notify stakeholders

Release Notes:
  - Automated from: All issues in Done status
  - Format: Story title + acceptance criteria
  - Attached to: Release notes document

Version Management:
  - Link sprints to releases
  - Track: Planned vs Actual
  - Monitor: Scope changes

Status Tracking:
  - Development → Staging → Production
  - Each stage tracked in custom field
  - Notifications at each transition
```

### Analytics and Reporting Integration

```yaml
Jira Data Export:

Daily Metrics:
  - Story points completed
  - Velocity trend
  - Cycle time
  - Burn-down chart

Sprint Reports:
  - Planned vs completed
  - Team performance
  - Story point accuracy
  - At-risk items

Product Metrics:
  - Feature delivery timeline
  - Bug trends
  - Tech debt accumulation
  - Team capacity utilization
```

---

## Best Practices

### Sprint Planning Best Practices

1. **Refinement in Advance**: Refine backlog in dedicated sessions 1-2 sprints ahead
2. **Estimation Consistency**: Use poker planning for relative sizing
3. **Capacity Planning**: Account for 85% team capacity (15% for interruptions)
4. **Dependency Mapping**: Identify external dependencies before sprint start
5. **Acceptance Criteria**: Ensure all stories have clear, testable criteria
6. **Technical Spike**: Max 1 spike per sprint

### Status Update Best Practices

1. **Daily Updates**: Team members log work daily (not just at sprint end)
2. **Comment Discipline**: Use issue comments for status, not Slack
3. **Blocking Issues**: Flag immediately, don't wait for standup
4. **Progress Tracking**: Update remaining estimate daily
5. **Code Links**: Always add PR/branch link when moving to review

### Board Maintenance

1. **Weekly Cleanup**: Remove old labels, close resolved issues
2. **Epic Maintenance**: Close complete epics, archive old ones
3. **Swimlane Review**: Ensure swimlanes stay relevant
4. **WIP Limits**: Review weekly and adjust based on team capacity
5. **Automation Review**: Monthly audit of automation rules

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Issues stuck in In Progress | No progress updates | Enable daily standup automation |
| Velocity unpredictable | Poor estimation | Implement estimation calibration |
| Sprints overbooked | Capacity miscalculation | Review 85% utilization rule |
| Transitions blocked | Missing required fields | Pre-populate defaults on sprint start |
| Board too cluttered | Too many swimlanes | Limit to 3 swimlanes max |
| Automation not firing | Conditions too strict | Review rule conditions quarterly |

---

## Conclusion

This Jira configuration provides a robust foundation for product teams. Customize based on team size, project complexity, and organizational structure. Review quarterly and adjust based on team feedback and metrics.

Key Success Factors:
- Consistent daily updates
- Clear acceptance criteria
- Regular retrospectives to improve process
- Data-driven decision making
- Continuous automation optimization
