#!/bin/bash
# Tableau Server CLI (TSM) Management Scripts

# ================================================
# BACKUP AND RESTORE
# ================================================

# Create backup
echo "Creating Tableau Server backup..."
tsm maintenance backup -f backup-$(date +%Y%m%d-%H%M%S).tsbak -d

# Restore from backup
# tsm maintenance restore -f backup-20241119-120000.tsbak

# ================================================
# USER MANAGEMENT
# ================================================

# Add user to site
tabcmd createusers users.csv --site production

# users.csv format:
# Username,Password,DisplayName,SiteRole,Publisher,Email
# john.doe,password123,John Doe,Viewer,no,john.doe@company.com

# Remove user
tabcmd deleteusers users_to_remove.csv

# ================================================
# CONTENT MANAGEMENT
# ================================================

# Publish workbook
tabcmd publish "Sales_Dashboard.twbx" \
    --name "Sales Dashboard" \
    --project "Finance" \
    --overwrite

# Export workbook
tabcmd export "Finance/Sales Dashboard" \
    --pdf \
    --pagesize letter \
    --orientation landscape \
    --filename "sales_report.pdf"

# Delete workbook
tabcmd delete "Finance/Sales Dashboard"

# ================================================
# EXTRACT REFRESH
# ================================================

# Refresh all extracts for a workbook
tabcmd refreshextracts --workbook "Sales Dashboard"

# Refresh specific datasource
tabcmd refreshextracts --datasource "Sales Data"

# ================================================
# SERVER CONFIGURATION
# ================================================

# Set configuration value
tsm configuration set -k wgserver.session.idle_limit -v 240

# Apply pending configuration changes
tsm pending-changes apply

# Restart server
tsm restart

# ================================================
# MONITORING
# ================================================

# Check server status
tsm status -v

# View recent logs
tsm maintenance ziplogs \
    --file logs-$(date +%Y%m%d).zip \
    --recent-hours 24

# ================================================
# AUTOMATED PUBLISHING WORKFLOW
# ================================================

#!/bin/bash
# publish_dashboards.sh

TABLEAU_SERVER="https://tableau.company.com"
SITE_ID="production"
PROJECT="Finance"

# Sign in
tabcmd login -s $TABLEAU_SERVER -t $SITE_ID \
    -u admin -p $TABLEAU_PASSWORD

# Publish all workbooks in directory
for workbook in /path/to/workbooks/*.twbx; do
    echo "Publishing $workbook..."
    tabcmd publish "$workbook" \
        --project "$PROJECT" \
        --overwrite \
        --tabbed
done

# Sign out
tabcmd logout
