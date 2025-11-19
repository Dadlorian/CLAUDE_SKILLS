# Video Script: Integration Workflows Guide

## Project Details
- **Title:** Connect [Product Name] with Your Favorite Tools
- **Duration:** 12-18 minutes
- **Target Audience:** Power Users, Teams, Enterprises
- **Skill Level:** Intermediate
- **Recording Format:** Screen capture + voiceover + live integration demos

---

## Pre-Production Checklist
- [ ] All integration accounts prepared (Slack, Salesforce, Google, GitHub, etc.)
- [ ] OAuth test connections verified
- [ ] Webhook endpoints ready for testing
- [ ] API keys generated and tested
- [ ] Sample data prepared in all third-party services
- [ ] Integration error logs cleared
- [ ] VPN/proxy configured if needed for webhooks
- [ ] Backup credentials stored safely

---

## VIDEO SCRIPT

### SEGMENT 1: INTRODUCTION (0:00 - 1:30)
**Duration:** ~1.5 minutes

**VISUAL ELEMENTS:**
- Animated icons of popular integration services
- Data flowing between systems
- Productivity metrics showing time savings
- Workflow diagram visualization

**VOICEOVER:**
"Your team uses multiple tools every day: Slack for communication, GitHub for code, Salesforce for sales, Google Drive for files. What if these tools could talk to each other automatically?

That's the power of integrations. [Product Name] connects with hundreds of services, letting your tools work together seamlessly.

In this video, I'll show you how to set up integrations that save hours every week. We'll start with simple built-in integrations, then move to powerful APIs and webhooks.

By the end, you'll have [Product Name] and your entire tool stack working in harmony. Let's connect!"

---

### SEGMENT 2: BUILT-IN INTEGRATIONS (1:30 - 5:00)
**Duration:** ~3.5 minutes

**VISUAL ELEMENTS:**
- Integration marketplace interface
- Popular integration cards
- OAuth authorization flow
- Configuration panels
- Test notification preview

**VOICEOVER:**
"Let's start with the easiest approach: built-in integrations.

Navigate to Settings and look for the Integrations section. You'll see our marketplace of pre-built integrations. These are tested and verified to work perfectly with [Product Name].

Browse the list. You'll see integrations for:
- Communication: Slack, Microsoft Teams, Discord
- Project Management: Asana, Jira, Monday.com
- CRM: Salesforce, HubSpot, Pipedrive
- Cloud Storage: Google Drive, Dropbox, OneDrive
- Developer Tools: GitHub, GitLab, Bitbucket
- Analytics: Amplitude, Mixpanel, Google Analytics
- And dozens more...

Let's set up Slack as our first example. Click the Slack integration. You'll see a description, setup instructions, and configuration options.

Click 'Connect.' This opens the Slack OAuth flow. You're taken to Slack's login page. Log in with your Slack workspace account. You'll see a permission request: '[Product Name] wants to access your workspace.'

Review the permissions. [Product Name] requests:
- Access to send messages to channels
- Access to read channel names and member information
- Access to create and manage connections

These are minimal permissions. We only request what we need. Click 'Allow' to grant access.

You're redirected back to [Product Name] with the connection confirmed.

Now configure the integration. You'll see options like:
- 'Notify on project creation'
- 'Notify on task completion'
- 'Notify on mention'
- 'Target Slack channel: #projects'

Configure based on your needs. For example, maybe you want all project notifications to go to #projects, but mentions go to direct messages.

You can also test the integration. Click 'Send Test Message.' If configured correctly, you'll get a message in your Slack channel within seconds. This proves the connection works.

Most team members don't realize that many integrations support two-way communication. Not only can [Product Name] send to Slack, but you can perform actions in [Product Name] from Slack.

For instance, you might create a Slack command /project that opens project details in [Product Name]. Or receive a Slack message and create a task in [Product Name] with a Slack button.

Let's set up a two-way workflow. In the Slack integration settings, enable 'Slack Commands.' Copy the command instructions. In your Slack workspace, go to App Directory and add [Product Name]. It will register our commands.

Now team members can type /project-create in Slack to start creating a project without ever opening a browser. Slack becomes a command center for [Product Name].

Finally, explore notification customization. Most integrations let you choose which events trigger notifications. You don't want spam, so carefully select events you care about. Maybe:
- New projects: Yes
- Project status changes: Yes
- Task assignments: Yes
- Comments: No (would be too much)
- Daily summaries: Yes

Save your configuration. The integration is now live. Every time those events occur, Slack receives a notification."

---

### SEGMENT 3: ADVANCED INTEGRATIONS - WEBHOOKS (5:00 - 10:00)
**Duration:** ~5 minutes

**VISUAL ELEMENTS:**
- Webhook settings interface
- Event payload examples
- HTTP POST requests visualization
- External server receiving webhook
- Webhook delivery logs with timing
- Retry logic visualization

**VOICEOVER:**
"Built-in integrations are great, but webhooks unlock unlimited possibilities. A webhook is a way for [Product Name] to notify your own system when something happens.

Here's how it works: You give [Product Name] a URL—maybe your company's internal server. Whenever an event occurs, [Product Name] sends an HTTP POST request to that URL with event data. Your system receives it and responds.

Let me show you how to set this up.

Navigate to Settings > Webhooks > Create Webhook.

Step 1: Choose the event that triggers this webhook. Common events include:
- Project created
- Project status changed
- Task assigned
- Comment added
- User added to team
- Integration connected

Let's say we want to notify our data warehouse whenever a project completes. Select 'Project status changed.'

Step 2: Configure trigger conditions. You probably don't want every status change—only completions. So set the condition: 'Status changes to Completed.'

Step 3: Enter your webhook URL. This is a public URL on your server that receives POST requests. For example:

https://your-company.com/webhooks/project-complete

Make sure your server is running and the URL is accessible. [Product Name] won't be able to reach localhost or internal URLs.

Step 4: Set authentication if needed. Many webhooks include a signature header for security. [Product Name] signs each request with your secret key. Your server verifies the signature to ensure the request came from [Product Name] and wasn't tampered with.

Step 5: Add custom headers and payloads if needed. Most integrations use standard payloads, but you can customize what data is sent.

Step 6: Click 'Test.' [Product Name] sends a test webhook to your URL. Check your server logs. You should see an HTTP POST request with this payload:

```json
{
  \"event_type\": \"project.status_changed\",
  \"timestamp\": \"2024-01-15T14:30:00Z\",
  \"project_id\": \"proj_abc123\",
  \"project_name\": \"Q1 Marketing Campaign\",
  \"old_status\": \"In Progress\",
  \"new_status\": \"Completed\",
  \"changed_by\": \"user@example.com\"
}
```

Parse this JSON in your application. Your system probably sends data to a data warehouse like BigQuery, Snowflake, or Redshift. Process this webhook and insert the data.

Important: Respond with HTTP 200 OK within 30 seconds. If your server processes slowly, respond immediately with 200, then process the webhook asynchronously in the background.

If you don't respond with 200, [Product Name] assumes delivery failed and retries. We retry up to 5 times with exponential backoff: immediately, after 5 minutes, after 30 minutes, after 3 hours, and after 1 day.

View webhook delivery logs by clicking your webhook. You'll see every delivery attempt, response status, and response body. This is invaluable for debugging.

If you see repeated failures, check:
1. Is your server online?
2. Is your server responding with 200?
3. Are there firewall rules blocking [Product Name]'s IP?
4. Did you change your webhook URL but not update it here?
5. Is your server's certificate valid if using HTTPS?

Now here's where webhooks get powerful: You can build complex automations using webhooks as the trigger.

Example 1: When a project completes, [Product Name] sends a webhook. Your server receives it. Your system automatically:
- Updates your data warehouse
- Sends a notification email to stakeholders
- Generates a completion report
- Triggers billing if it's a billable project
- Logs the completion in your accounting system
- Cleans up associated resources

All this happens automatically, instantly, in real-time.

Example 2: You have a custom tool or system we don't have a built-in integration for. Instead of manually moving data, use webhooks.

Set up webhooks for the events you care about. Your system receives the webhooks and processes them however you need. No additional integrations required.

Example 3: Multi-system synchronization. [Product Name] has a project. When it changes, a webhook fires. Your system updates the same project in three other systems—keeping everything in sync automatically."

---

### SEGMENT 4: API INTEGRATIONS (10:00 - 14:00)
**Duration:** ~4 minutes

**VISUAL ELEMENTS:**
- API documentation interface
- Code editor with API calls
- Request/response examples
- API authentication screen
- Rate limiting dashboard
- API key management panel

**VOICEOVER:**
"Webhooks are great for responding to events. APIs are great for actively querying data or making changes.

[Product Name]'s REST API lets you build custom integrations for anything. You can:
- Create projects programmatically
- Update tasks automatically
- Retrieve reports and data
- Delete old items
- Query the database for analysis
- And much more

Let's start with API basics.

Navigate to Settings > API > API Keys. Click 'Generate Key.' You'll get a long token. Treat this like a password. Never share it or commit it to public repositories.

Store your API key securely. We recommend environment variables:

```bash
export PRODUCT_API_KEY=\"your_key_here\"
```

Now, make an API call. Use any HTTP client. Here's an example with curl:

```bash
curl -X GET https://api.example.com/projects \
  -H \"Authorization: Bearer $PRODUCT_API_KEY\" \
  -H \"Content-Type: application/json\"
```

This retrieves all your projects. The response is JSON containing your project list.

Here's a more complex example: Create a new project via API.

```bash
curl -X POST https://api.example.com/projects \
  -H \"Authorization: Bearer $PRODUCT_API_KEY\" \
  -H \"Content-Type: application/json\" \
  -d '{
    \"name\": \"API-Created Project\",
    \"description\": \"Created via API\",
    \"type\": \"standard\",
    \"team_id\": \"team_xyz789\"
  }'
```

The API responds with your new project's details, including its ID. Use this ID for future operations.

Now, a practical example: Bulk create projects from a CSV file.

Imagine you have a CSV with 100 projects to create. Manually creating them would take hours. With the API, do it in seconds.

Write a simple script in your language of choice (Python, Node.js, Go, etc.):

```python
import requests
import csv

API_KEY = \"your_api_key\"
API_URL = \"https://api.example.com\"
HEADERS = {
    \"Authorization\": f\"Bearer {API_KEY}\",
    \"Content-Type\": \"application/json\"
}

with open('projects.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        payload = {
            \"name\": row['name'],
            \"description\": row['description'],
            \"type\": row['type']
        }
        response = requests.post(
            f\"{API_URL}/projects\",
            headers=HEADERS,
            json=payload
        )
        print(f\"Created project: {response.json()['id']}\")
```

Run this script, and all 100 projects are created automatically. Each one follows the exact configuration specified in your CSV.

Here's another powerful pattern: Synchronization. You have data in [Product Name]. You need it in your data warehouse or analytics tool.

Query [Product Name]'s API to get all projects:

```bash
curl -X GET https://api.example.com/projects?filter=status:completed \
  -H \"Authorization: Bearer $PRODUCT_API_KEY\"
```

This returns all completed projects. Parse the response and load the data into your warehouse. Schedule this to run hourly, and your warehouse is always in sync with [Product Name].

Key API concepts:

Pagination: If you have 10,000 projects, the API doesn't return all at once. It returns in pages. Use the 'page' and 'limit' parameters to navigate.

Filters: Instead of getting all projects, filter by status, date, owner, or custom fields. This reduces data transfer and speeds up your code.

Rate Limiting: You're limited to [X] requests per minute. If you exceed this, you get a 429 response. Implement exponential backoff in your code.

Error Handling: Always check HTTP status codes. 2xx means success. 4xx means you made a mistake (bad request, unauthorized, not found). 5xx means [Product Name] has an error. Log errors and retry appropriately.

Webhooks vs. APIs: Use webhooks when you want to be notified of events. Use APIs when you want to actively query or modify data. Often, you'll use both.

Finally, explore our API documentation at [api-docs-url]. It's comprehensive, with examples in multiple languages, error codes, and rate limit details.

For advanced developers, we also offer GraphQL API for more efficient querying. And our SDK in Python, JavaScript, and Go simplifies API interactions significantly."

---

### SEGMENT 5: REAL-WORLD INTEGRATION EXAMPLES (14:00 - 16:30)
**Duration:** ~2.5 minutes

**VISUAL ELEMENTS:**
- Workflow architecture diagrams
- Multi-service integration visualization
- Before/after productivity comparison
- Case study metrics and results

**VOICEOVER:**
"Let's look at real-world examples of powerful integrations.

Example 1: Sales Pipeline Automation

A sales team uses Salesforce for CRM and [Product Name] for project management. Without integration, information exists in both systems, and staying in sync is manual work.

Solution: Connect [Product Name] and Salesforce with a two-way integration.

When a sales opportunity reaches 'Proposal' stage in Salesforce, automatically create a project in [Product Name] with all proposal details. Sales reps use [Product Name] to manage proposal tasks.

When the project reaches 'Won' status, automatically update the Salesforce opportunity to 'Closed-Won.' A webhook notifies accounting to invoice the customer.

Result: Sales team spends zero time updating systems. Accounting gets instant notification. No data entry errors. Time saved: 10 hours per week.

Example 2: Engineering Workflow

Developers work in GitHub for code. [Product Name] for project management. Slack for communication. Without integration, context is scattered.

Solution: Connect all three.

When a developer opens a pull request on GitHub, a webhook fires. [Product Name] automatically creates a task for code review and assigns it to the designated reviewer.

When the task is marked complete in [Product Name], post a message in the project's Slack channel so the team knows it's done.

When code merges to main, [Product Name] marks the associated task complete, and a webhook notifies the deployment pipeline to run.

Result: All three systems are in sync automatically. Team spends zero time updating systems. Deployment pipeline automatically triggers. Time saved: 15 hours per week.

Example 3: Support Ticket Processing

A support team uses a ticketing system for customer issues. [Product Name] for team project management. Google Sheets for reporting.

Solution: API integration between ticketing system and [Product Name].

Every night, a scheduled job:
1. Queries the ticketing system API for all open tickets
2. For each ticket, creates or updates a [Product Name] task
3. Assigns it to the appropriate team member based on ticket category
4. Queries [Product Name] API for completion status
5. Updates the ticketing system with the status
6. Exports key metrics to a Google Sheet for reporting

Result: Ticketing system and [Product Name] are synchronized automatically. Reports are always current. No manual data entry. Time saved: 20 hours per week.

Common pattern in all these examples: Automation reduces manual work, eliminates errors, and keeps systems synchronized.

Your specific integration depends on your tools, but the pattern is the same. Identify the data that needs to move between systems and set up automated movement."

---

### SEGMENT 6: BEST PRACTICES & TROUBLESHOOTING (16:30 - 17:30)
**Duration:** ~1 minute

**VISUAL ELEMENTS:**
- Best practices checklist
- Error handling flowchart
- Security best practices list
- Integration monitoring dashboard

**VOICEOVER:**
"Before we wrap up, here are critical best practices:

Security: Never hardcode API keys in code. Use environment variables. Rotate keys periodically. Enable IP whitelisting if available. Use HTTPS for all API calls.

Error Handling: Always check response status codes. Implement retry logic for transient failures. Log all integrations for debugging. Monitor integration health.

Performance: Use filtering and pagination to minimize data transfer. Batch operations when possible. Cache data when appropriate. Monitor API rate limits.

Testing: Test integrations in a staging environment before production. Test error scenarios, not just the happy path. Have a plan if integration breaks.

Monitoring: Set up alerts for integration failures. Monitor API rate limit usage. Track integration performance metrics. Have on-call response for failures.

Troubleshooting: Check OAuth token expiration. Verify webhook URLs are accessible. Ensure servers respond with 200 status. Review error logs for specific failures. Contact support with detailed information.

Finally, security note: If you suspect your API key leaked, regenerate it immediately. Old keys instantly stop working, and your system starts using the new key."

---

### SEGMENT 7: CLOSING (17:30 - 18:00)
**Duration:** ~0.5 minutes

**VISUAL ELEMENTS:**
- Resource compilation slide
- Integration marketplace link
- Support contact options
- Subscribe prompt

**VOICEOVER:**
"You now have the knowledge to integrate [Product Name] with your entire tool stack.

Start simple with built-in integrations. As your needs grow, explore webhooks and APIs.

Our documentation at [api-docs-url] has detailed guides for every integration. Our community at [community-url] shares integration patterns and solutions.

If you need help, support is available at [support-email].

Thanks for watching. Like and subscribe for more integration guides. Good luck building your connected workflow!"

---

## Production Notes

### Code Display
- Use syntax highlighting
- Dark background for code blocks
- Large font (14pt minimum)
- Overlay code on screen rather than typing it live
- Show code and output side-by-side when possible

### API Examples
- Show multiple languages (curl, Python, JavaScript)
- Include request and response examples
- Highlight important fields
- Explain error codes

### Visual Aids
- Flowcharts for multi-step integrations
- Arrows showing data flow between systems
- Screenshots of configuration screens
- Before/after comparisons

### Pacing
- Slow down for technical content
- Allow time for viewers to read code
- Pause between major sections
- Speed up for UI navigation

---

## Supplementary Materials
- API reference documentation link
- Integration setup guides PDF
- Code examples repository
- Troubleshooting flowchart image
- Security best practices guide

