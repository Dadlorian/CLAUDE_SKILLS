# How-To Guide Structure: Standard Framework for Task-Oriented Documentation

Comprehensive guide to structuring effective how-to documentation that helps developers solve specific problems quickly.

## Table of Contents

1. [What is a How-To Guide](#definition)
2. [Core Structure](#structure)
3. [Section-by-Section Guide](#sections)
4. [Writing Best Practices](#practices)
5. [Industry Examples](#examples)
6. [Templates by Use Case](#templates)

---

## What is a How-To Guide

A how-to guide provides step-by-step instructions for accomplishing a specific task.

### How-To Guides vs. Other Documentation

| Type | Purpose | Scope | Length |
|------|---------|-------|--------|
| **How-To** | Accomplish specific task | Narrow, focused | 5-15 min read |
| **Tutorial** | Learn by building | Broader, educational | 20-60 min |
| **Reference** | Look up information | Comprehensive | Variable |
| **Explanation** | Understand concepts | Theoretical | 5-20 min read |

**How-to guides are task-oriented:** "How do I deploy to production?" not "What is deployment?"

### When to Write a How-To Guide

Write a how-to guide when you're answering:
- "How do I...?"
- "How do I set up...?"
- "How do I configure...?"
- "How do I troubleshoot...?"

You're NOT trying to teach concepts; you're solving immediate problems.

---

## Core Structure

Every how-to guide should follow this structure:

```
TITLE
(Concise, action-oriented)

OVERVIEW
(What you'll accomplish, estimated time)

PREREQUISITES
(Requirements, assumptions)

STEPS
(Numbered, logical sequence)

VERIFICATION
(Confirm success)

TROUBLESHOOTING
(Common issues)

NEXT STEPS
(Related guides)
```

---

## Section-by-Section Guide

### 1. Title

**Formula:** "How to [Action] [Object] [in Context]"

**Examples:**
- "How to Deploy a Next.js App to Vercel"
- "How to Configure CORS in Your API"
- "How to Debug Authentication Issues"
- "How to Set Up GitHub Actions for CI/CD"
- "How to Optimize Images for Web"

**Good Titles Share These Qualities:**
- Action verb at start (Deploy, Configure, Debug, Optimize)
- Specific object (not "Settings", but "CORS Headers")
- Context if needed (in Vercel, in AWS, for React)
- Searchable keywords included
- Under 60 characters when possible

**Avoid These Title Mistakes:**
- ✗ "Working with Deployment" (vague action)
- ✗ "Advanced Vercel Tips" (not specific task)
- ✗ "Getting Started" (unclear what for)
- ✓ "How to Deploy a Next.js App to Vercel" (clear and specific)

---

### 2. Overview/Introduction

**Purpose:** Reader quickly understands what they'll accomplish and whether this guide is for them.

**What to Include:**

#### A. One-Sentence Summary
"This guide shows you how to set up continuous integration using GitHub Actions."

#### B. What You'll Accomplish
- Outcome focused: "You'll have automated tests running on every push"
- Specific benefits: "Save 5 minutes per deployment"

#### C. Time Estimate
"Estimated time: 10-15 minutes (5 min setup + 5-10 min configuration)"

#### D. Context/Why This Matters (Optional)
"Without GitHub Actions, you'd manually run tests before deploying, which is error-prone and slow."

**Example Overview:**

```markdown
## How to Deploy a React App to Netlify

In this guide, you'll connect your GitHub repository to Netlify and set up
automatic deployments. After completing this guide, your app will redeploy
automatically whenever you push code to your main branch.

**Time estimate:** 5 minutes
**What you'll have:** A live app at `yourname.netlify.app` with auto-deployments

**Why this matters:** Manual deployments are time-consuming and error-prone.
Automatic deployments let you ship faster with confidence.
```

---

### 3. Prerequisites / Before You Start

**Purpose:** Reader has everything needed before beginning.

**What to Include:**

#### A. Required Tools/Software
Specify versions if important:
```markdown
Required:
- Node.js 14.0 or higher
- npm 6.0 or higher
- Git 2.25 or higher
```

#### B. Existing Knowledge/Setup
```markdown
You should:
- Know how to use command line basics
- Have React fundamentals knowledge
- Have a GitHub account
```

#### C. Accounts/Services Needed
```markdown
You'll need:
- A Netlify account (free tier is fine)
  - Sign up at netlify.com
- A GitHub account (free tier is fine)
  - Need a public or private repository
```

#### D. Installation Instructions
If tool installation is complex, link to guide:
```markdown
If you don't have Node.js installed,
see [How to Install Node.js](link) for your operating system.
```

#### E. Assumptions Documented
```markdown
This guide assumes:
- You have a React app already created
- Your app runs locally with `npm start`
- You're using Git to version control your code
```

**Common Prerequisites Checklist:**
- [ ] Operating system (Windows/macOS/Linux or all)
- [ ] Required software with versions
- [ ] Required knowledge level
- [ ] Required accounts or API keys
- [ ] Required files or templates
- [ ] Installation time estimate

---

### 4. Steps Section

The heart of your how-to guide. Clear, sequential steps that reader can follow.

#### Step Formatting Rules

**Rule 1: One Primary Task Per Step**
```markdown
✓ GOOD
## Step 1: Create a GitHub Repository
1. Go to github.com and log in
2. Click "New" to create repository
3. Name it "my-app"

✗ BAD
## Step 1: Set Up GitHub and Connect to Netlify
1. Go to GitHub...
[too many things in one step]
```

**Rule 2: Clear Action Verbs**
Start with what to do:
```
✓ Click the Deploy button
✓ Run this command:
✓ Open the Settings panel
✗ The Deploy button should be clicked
✗ Run and execute the following command:
```

**Rule 3: Show What Success Looks Like**
After each significant step, show expected result:

```markdown
## Step 1: Create Netlify Account

1. Go to [netlify.com](https://netlify.com)
2. Click "Sign Up"
3. Choose "Sign up with GitHub" (or email)
4. Complete the signup process

**You should now see the Netlify dashboard with your email in the top-right.**
```

**Rule 4: Include Relevant Screenshots**
For UI-heavy steps, show a screenshot:

```markdown
## Step 2: Connect Your GitHub Repository

1. Click "New site from Git" (see image below)
2. Select "GitHub" as your Git provider
3. Authorize Netlify to access your repositories

![Netlify new site button](./images/netlify-new-site.png)
```

#### Step Progression

**Logical Sequence:**
1. Prerequisites (account creation, installation)
2. Initial configuration
3. Core functionality
4. Optional enhancements
5. Finalization/testing

**Example: "How to Set Up Database Backup"**

```markdown
## Step 1: Enable Backups in Database Settings
## Step 2: Choose Backup Frequency and Retention
## Step 3: Configure Backup Location (S3/GCS/Dropbox)
## Step 4: Test Backup Creation
## Step 5: Verify Restore Process Works
## Step 6: Set Up Monitoring and Alerts
```

#### Handling Multiple Paths

When there are multiple valid approaches:

```markdown
## Step 2: Choose Your Deployment Method

**Option A: Using GitHub Integration (Recommended)**
[Steps for this option]

**Option B: Using Netlify CLI**
[Steps for this option]

**Option C: Manual Drag & Drop**
[Steps for this option]

All three approaches achieve the same result.
Choose whichever matches your workflow best.
```

---

### 5. Code Samples in Steps

When including code:

#### Include Context
```markdown
Create a file `config.json` in your project root:

javascript
{
  "apiUrl": "https://api.example.com",
  "environment": "production",
  "timeout": 5000
}
```

#### Explain Important Lines
```markdown
javascript
const db = new Database({
  host: 'localhost',
  port: 5432,
  name: 'myapp'  // ← Use your database name here
});
```

#### Show Expected Output
```markdown
Run:
bash
npm run build


You should see:
text
> my-app@1.0.0 build
> react-scripts build

Creating an optimized production build...
Compiled successfully!

File sizes after gzip:

  build/main.js:  45.32 KB
```

---

### 6. Verification Section

Help reader confirm they did it correctly.

**Formula for Verification Steps:**
1. What to do to test
2. What correct output looks like
3. What incorrect output means

**Example:**

```markdown
## Verify Your Setup

### Test that deployment works:

1. Push a change to your GitHub repository:
   bash
   git add .
   git commit -m "Test deployment"
   git push


2. Go to your Netlify dashboard
3. Wait for the deployment to complete (green checkmark means success)
4. Click the URL to visit your live site

**Expected result:** Your site loads without errors and shows your latest changes

**If deployment fails:** Check your build command in Netlify settings.
It should match how you run `npm run build` locally.
```

**Verification Checklist Format:**

```markdown
## Verify Everything is Working

You've successfully set up CORS when:

- [ ] API requests from your frontend complete without errors
- [ ] You see `Access-Control-Allow-Origin` in response headers
- [ ] No "CORS policy" error appears in the browser console
- [ ] Cross-origin requests return actual data (not blocked)
```

---

### 7. Troubleshooting Section

Document common problems and solutions.

**Format:**

```markdown
## Troubleshooting

### Issue: "Permission denied" when running deploy command

**Possible causes:**
- API key not configured correctly
- Insufficient permissions in account

**Solution:**
1. Verify API key: `auth -c token list`
2. Regenerate if expired
3. Try deploy again

**Still not working?** See [authentication debugging guide](link)
```

**Comprehensive Troubleshooting Template:**

```markdown
### Problem: Deployment fails with "Build timeout"

**What this means:** Your build process took longer than 10 minutes

**Common causes:**
1. Installing large dependencies
2. Building heavy assets
3. Network requests during build

**Solutions to try:**
1. **Use npm ci instead of npm install** (faster)
   bash
   npm ci

2. **Enable npm caching** in build settings
3. **Remove unnecessary dependencies** with `npm audit`
4. **Increase timeout** if available in platform settings

**Verification:** Re-run deployment and watch the build log for timing

**Escalation:** If still failing, check [build optimization guide](link)
```

---

### 8. Next Steps

Point readers toward related content.

**Smart Next Steps Suggestions:**

```markdown
## What's Next?

**To customize your deployment:**
- [How to Set Custom Domain in Netlify](link)
- [How to Configure Environment Variables](link)

**To improve performance:**
- [How to Optimize Images for Faster Loads](link)
- [How to Enable Caching Headers](link)

**To add advanced features:**
- [How to Set Up A/B Testing](link)
- [How to Configure Edge Functions](link)
```

---

## Writing Best Practices

### 1. Tone and Voice
- Imperative and direct: "Click the button" not "You should click the button"
- Active voice: "Click X" not "X should be clicked"
- Friendly but professional
- Avoid puns or humor that could confuse

### 2. Clarity
- **Short sentences:** Under 20 words when possible
- **Technical terms:** Explain on first use: "CI/CD (Continuous Integration/Continuous Deployment)"
- **Consistent terminology:** Same term for same concept throughout
- **Clear references:** "the button below" with visual indicator, not "the button"

### 3. Accessibility
- Keyboard navigation: commands work with Tab/Enter
- Screen reader friendly: images have alt text
- Color-blind safe: don't rely only on color to convey meaning
- High contrast: text readable without zooming

### 4. Scanability
- Descriptive headers (not just "Step 1")
- Bullet points for lists
- Bold key terms
- Short paragraphs

### 5. Completeness
- Every command includes full context
- Every screenshot labeled
- Every UI element named (not "the button" but "the Deploy button")
- Nothing left to user assumption

---

## Industry Examples

### Firebase Authentication Setup

**Location:** https://firebase.google.com/docs/auth/web/start

**Structure Used:** How-to Guide

**Notable Elements:**
1. Very clear prerequisites (Firebase project needed)
2. Each step shows both console and code changes
3. Verification step shows how to test auth
4. Troubleshooting for common issues
5. Links to more advanced guides

**Why it works:** Combines visual UI steps with code snippets, acknowledging users need both.

### Stripe Payment Processing

**Location:** https://stripe.com/docs/payments/accept-a-payment

**Structure Used:** How-to Guide + API Integration

**Notable Elements:**
1. Multiple language code samples in tabs
2. Test card numbers provided for verification
3. Common errors documented
4. Dashboard screenshots showing what to look for
5. Next steps for advanced features

**Why it works:** Handles security concerns explicitly and provides realistic test data.

### GitHub Actions CI/CD

**Location:** https://docs.github.com/en/actions

**Structure Used:** How-to Guides (multiple)

**Notable Elements:**
1. Prerequisites clearly state OS testing
2. Workflow files shown completely (copy-paste ready)
3. Each step explains what happens in GitHub UI
4. Troubleshooting for common workflow failures
5. Variables section explains what to customize

**Why it works:** Acknowledges that users need both automation and understanding.

### FreeCodeCamp Database Tutorials

**Location:** https://freecodecamp.org

**Structure Used:** How-to + Tutorial hybrid

**Notable Elements:**
1. "Why this matters" section in introduction
2. Step progression is very logical
3. Code is always complete (not fragments)
4. Each section ends with recap
5. Next steps point to related topics

**Why it works:** Balances practical steps with conceptual understanding.

---

## Templates by Use Case

### Template 1: API Integration How-To

```markdown
# How to [Integrate Service] in [Framework]

## Overview
[What you'll accomplish in 1-2 sentences]
Estimated time: [X minutes]

## Prerequisites
- [Service] account (free tier available at [link])
- [Framework] project set up locally
- Basic knowledge of [relevant concept]

## Step 1: Get Your API Credentials
[Create account, get key section]

## Step 2: Install SDK
[Package installation]

## Step 3: Initialize Service
[Setup code]

## Step 4: Make Your First Request
[Simple example that works]

## Step 5: Handle Errors
[Error handling code]

## Verify Your Integration
[Testing steps]

## Troubleshooting
[Common errors]

## Next Steps
[Related guides]
```

### Template 2: Configuration How-To

```markdown
# How to Configure [Setting] for [System]

## Overview
[What you'll accomplish]
Estimated time: [X minutes]

## Why Configure This?
[Why this setting matters]

## Prerequisites
[What's needed before starting]

## Step 1: Access the Settings
[Where to find the settings]

## Step 2: Understand Each Option
[Explanation of each setting]

## Step 3: Apply Your Configuration
[How to change the settings]

## Step 4: Save and Verify
[Confirmation that it worked]

## Common Configurations
[Preset configurations for common scenarios]

## Troubleshooting
[Common issues]

## Next Steps
[Related configurations]
```

### Template 3: Debugging How-To

```markdown
# How to Debug [Problem Type] in [System]

## Overview
[What you'll learn to fix]
Estimated time: [X minutes]

## Prerequisites
[Tools or knowledge needed]

## Step 1: Identify the Problem
[How to recognize this type of issue]

## Step 2: Gather Information
[What to look for in logs/console]

## Step 3: Isolate the Cause
[How to narrow down the problem]

## Step 4: Apply the Fix
[Solution implementation]

## Verify the Fix Works
[Testing steps]

## Prevention
[How to prevent this issue]

## Troubleshooting
[If fix didn't work]

## Next Steps
[Related debugging guides]
```

---

## How-To Guide Checklist

Before publishing your how-to guide:

### Content
- [ ] Title is action-oriented and specific
- [ ] Overview explains what you'll accomplish
- [ ] Prerequisites are complete and linked
- [ ] Each step has one primary task
- [ ] Steps are in logical sequence
- [ ] Code is complete and tested
- [ ] Screenshots included for UI steps
- [ ] Verification section confirms success
- [ ] Troubleshooting covers common issues
- [ ] Next steps point to related content

### Writing Quality
- [ ] Grammar and spelling checked
- [ ] Imperative voice throughout
- [ ] Short sentences and paragraphs
- [ ] Technical terms defined
- [ ] Consistent terminology used
- [ ] No ambiguous pronouns

### Accessibility
- [ ] Images have descriptive alt text
- [ ] No color-only indicators
- [ ] Keyboard navigable
- [ ] Readable without zooming
- [ ] Links open in correct context

### Testing
- [ ] Followed by external tester
- [ ] Tested on target OS(s)
- [ ] All commands work exactly as written
- [ ] Screenshots up to date
- [ ] Links valid (internal and external)
- [ ] Verification steps actually verify

---

## Quick Reference: Common How-To Titles

**Deployment:**
- "How to Deploy to [Platform]"
- "How to Configure Auto-Deploy from Git"
- "How to Deploy with Zero Downtime"

**Configuration:**
- "How to Configure [Service]"
- "How to Set Environment Variables"
- "How to Optimize Settings for Performance"

**Troubleshooting:**
- "How to Debug [Error Type]"
- "How to Troubleshoot [Common Issue]"
- "How to Fix [Performance Problem]"

**Integration:**
- "How to Integrate [Service]"
- "How to Connect [System A] to [System B]"
- "How to Add [Feature] to Your App"

**Security:**
- "How to Set Up [Security Feature]"
- "How to Secure [Component]"
- "How to Manage [Credentials/Keys]"

---

## Additional Resources

- Google's How-To Guide Style: https://developers.google.com/tech-writing/how-to-guides
- FreeCodeCamp How-To Standards: https://contribute.freecodecamp.org
- Stripe API How-To Collection: https://stripe.com/docs
- Firebase How-To Guides: https://firebase.google.com/docs
- Diataxis Framework (How-To vs Tutorial): https://diataxis.fr

