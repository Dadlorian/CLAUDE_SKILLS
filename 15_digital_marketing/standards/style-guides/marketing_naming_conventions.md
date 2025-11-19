# Marketing Naming Conventions
## Professional Standards for Digital Marketing Assets

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Industry best practices from HubSpot, Google, Salesforce, and leading marketing operations teams

---

## Purpose

Consistent naming conventions are critical for:
- **Scalability**: Find and manage thousands of marketing assets
- **Collaboration**: Enable teams to locate and understand assets quickly
- **Reporting**: Aggregate data accurately across campaigns and channels
- **Governance**: Maintain organizational standards as team grows
- **Efficiency**: Reduce time searching for assets by 60-70%

This guide establishes enterprise-grade naming standards for all digital marketing assets including campaigns, ad groups, ads, emails, landing pages, content, UTM parameters, and files.

---

## Core Principles

### 1. Descriptive and Scannable
Names should communicate purpose at a glance without requiring additional context.

```
❌ Poor: "Campaign 1", "New Email", "LP Final v2"
✅ Good: "2024Q4_BlackFriday_Email_Promo", "Product-Launch_LP_FreeTrial"
```

### 2. Consistent Structure
Use the same order of elements across all similar assets.

```
Format: [TimeFrame]_[Campaign]_[Channel]_[AssetType]_[Variation]

Examples:
- 2024Q4_ProductLaunch_Facebook_Video_A
- 2024Q4_ProductLaunch_Facebook_Video_B
- 2024Q4_ProductLaunch_Google_Search_A
```

### 3. Future-Proof
Names should remain meaningful months or years later.

```
❌ Poor: "Current_Campaign", "This_Month_Email", "New_Landing_Page"
✅ Good: "2024Q4_Webinar_Series", "2024-11_Newsletter", "Enterprise_Demo_LP_2024"
```

### 4. System-Compatible
Avoid special characters that may cause issues in various platforms.

**Safe Characters**:
- Letters: A-Z, a-z
- Numbers: 0-9
- Separators: Underscore `_`, hyphen `-`

**Avoid**:
- Spaces (use underscore or hyphen instead)
- Special characters: #, @, !, %, &, *, (, ), +, =, {, }, [, ], etc.
- Leading numbers in some systems

### 5. Length Appropriate
Balance descriptiveness with brevity.

**General Guidelines**:
- Campaign names: 30-60 characters
- Ad names: 40-80 characters
- File names: 30-100 characters
- Keep under 255 characters (system limit)

---

## Campaigns

### Campaign Naming Structure

**Standard Format**:
```
[Year][Quarter/Month]_[Campaign-Name]_[Objective]_[Audience]

Examples:
2024Q4_BlackFriday_Acquisition_Ecommerce
2024-11_ProductLaunch_Awareness_Enterprise
2025Q1_Webinar_LeadGen_SMB
```

**Elements Explained**:

**Time Frame**:
- Year + Quarter: `2024Q1`, `2024Q2`, `2024Q3`, `2024Q4`
- Year + Month: `2024-01`, `2024-02`, etc.
- Specific date for short campaigns: `2024-11-15_CyberMonday`

**Campaign Name** (use PascalCase or kebab-case):
- PascalCase: `ProductLaunch`, `BlackFriday`, `WebinarSeries`
- kebab-case: `Product-Launch`, `Black-Friday`, `Webinar-Series`
- Choose one style and use consistently

**Objective** (optional but recommended):
- `Acquisition` - New customer acquisition
- `Retention` - Existing customer retention
- `Expansion` - Upsell/cross-sell
- `Awareness` - Brand awareness
- `Engagement` - User engagement
- `LeadGen` - Lead generation

**Audience** (optional):
- `SMB` - Small/medium business
- `Enterprise` - Enterprise customers
- `Freemium` - Free tier users
- `Trial` - Trial users
- `Customer` - Existing customers
- Specific vertical: `Healthcare`, `Finance`, `Retail`

### Campaign ID System

For tracking across systems, use campaign ID prefix:

```
Format: [Platform-Code]_[Year]_[Sequential-Number]

Examples:
GG_2024_001  (Google Ads campaign #1 of 2024)
FB_2024_015  (Facebook campaign #15 of 2024)
EM_2024_047  (Email campaign #47 of 2024)
```

**Platform Codes**:
- `GG` - Google Ads
- `FB` - Facebook/Instagram
- `LI` - LinkedIn
- `TW` - Twitter/X
- `TT` - TikTok
- `EM` - Email
- `WEB` - Website/Organic
- `PN` - Pinterest
- `RD` - Reddit
- `YT` - YouTube

---

## Paid Advertising

### Google Ads Naming

**Campaign Level**:
```
[CampaignType]_[Year-Quarter]_[Product/Offer]_[Geo]_[Audience]

Examples:
Search_2024Q4_FreeTrial_US_SMB
Shopping_2024Q4_BlackFriday_US_All
Display_2024Q4_Retargeting_US_CartAbandoners
PMax_2024Q4_ProductLaunch_Global_All
```

**Campaign Type Codes**:
- `Search` - Search campaigns
- `Shopping` - Shopping campaigns
- `Display` - Display campaigns
- `Video` - YouTube video campaigns
- `PMax` - Performance Max
- `Discovery` - Discovery campaigns
- `App` - App campaigns

**Ad Group Level**:
```
[Keyword-Theme]_[Match-Type]_[Device]

Examples:
email-marketing-software_Exact_All
crm-platform_Phrase_Desktop
marketing-automation_Broad_Mobile
```

**Match Type Codes**:
- `Exact` - Exact match
- `Phrase` - Phrase match
- `Broad` - Broad match
- `BMM` - Broad match modifier (legacy)

**Ad Level**:
```
[AdType]_[Variation]_[Test-Element]

Examples:
RSA_A_Headline-Test
RSA_B_Description-Test
RSA_C_CTA-Test
Image_A_Creative-Test
```

### Meta Ads (Facebook/Instagram) Naming

**Campaign Level**:
```
[Objective]_[Year-Quarter]_[Product]_[Funnel-Stage]

Examples:
Conversions_2024Q4_FreeTrial_BOF
Traffic_2024Q4_BlogContent_TOF
LeadGen_2024Q4_Webinar_MOF
Retargeting_2024Q4_CartAbandon_BOF
```

**Funnel Stage Codes**:
- `TOF` - Top of funnel (awareness)
- `MOF` - Middle of funnel (consideration)
- `BOF` - Bottom of funnel (conversion)

**Ad Set Level**:
```
[Audience-Type]_[Geo]_[Age-Range]_[Placement]

Examples:
Lookalike_US_25-45_Feed
Interest_UK_35-55_Stories
Custom_US_All_All-Placements
Retargeting_Global_25-65_Feed-Stories
```

**Ad Level**:
```
[Format]_[Creative-Theme]_[Variation]

Examples:
SingleImage_Testimonial_A
Video_Demo_B
Carousel_Features_C
Story_UGC_A
```

### LinkedIn Ads Naming

**Campaign Level**:
```
[Objective]_[Year-Quarter]_[Offer]_[Seniority]_[Industry]

Examples:
LeadGen_2024Q4_Whitepaper_Director_SaaS
WebsiteVisit_2024Q4_FreeTrial_Manager_All
Awareness_2024Q4_ThoughtLeadership_CLevel_Finance
```

**Seniority Targeting**:
- `CLevel` - C-suite executives
- `VP` - Vice Presidents
- `Director` - Directors
- `Manager` - Managers
- `IC` - Individual contributors
- `All` - All seniority levels

---

## Email Marketing

### Email Campaign Naming

**Standard Format**:
```
[Type]_[Year-Month-Day]_[Subject-or-Theme]_[Segment]_[Variation]

Examples:
Newsletter_2024-11-15_Weekly-Roundup_All_A
Promo_2024-11-24_BlackFriday_Customers_A
Nurture_2024-11_Trial-Day3_Trial-Users_A
Transactional_Order-Confirmation_All_V1
```

**Email Type Codes**:
- `Newsletter` - Regular newsletters
- `Promo` - Promotional emails
- `Nurture` - Nurture sequence emails
- `Transactional` - Transactional (receipts, confirmations)
- `Trigger` - Behavioral triggers
- `Reengagement` - Win-back campaigns
- `Onboarding` - New user onboarding
- `Announcement` - Product/company announcements

**Segment Examples**:
- `All` - All subscribers
- `Customers` - Paying customers
- `Trial` - Trial users
- `Freemium` - Free tier users
- `Engaged` - Highly engaged users
- `AtRisk` - At-risk for churn
- `Churned` - Churned customers
- Specific behavior: `Cart-Abandoners`, `Webinar-Attendees`

### Email Automation Workflows

```
[Workflow-Type]_[Trigger]_[Goal]_[Version]

Examples:
Onboarding_Trial-Signup_Activation_V2
Nurture_Download-Whitepaper_SQL_V1
Abandoned-Cart_Cart-Inactive-24h_Purchase_V3
Reengagement_Inactive-60d_Reactivation_V1
```

### Subject Line Testing

When A/B testing subject lines, append variation code:

```
Promo_2024-11-24_BlackFriday_All_A
Promo_2024-11-24_BlackFriday_All_B
Promo_2024-11-24_BlackFriday_All_C
```

Track what's being tested in campaign notes:
- A: Emoji in subject line
- B: Urgency messaging
- C: Personalization with name

---

## Landing Pages and Website Assets

### Landing Page Naming

**Standard Format**:
```
[Type]_[Campaign/Offer]_[Audience]_[Variation]

Examples:
LP_FreeTrial_SMB_A
LP_Demo_Enterprise_B
LP_Webinar_Marketing-Managers_A
LP_Download_Ebook-SEO-Guide_All_A
```

**Page Type Codes**:
- `LP` - Landing page
- `HP` - Homepage
- `PLP` - Product listing page
- `PDP` - Product detail page
- `Pricing` - Pricing page
- `Thank-You` - Thank you page
- `Form` - Standalone form page

### Form Naming

```
[Page-Location]_[Form-Purpose]_[Fields-Count]_[Version]

Examples:
Homepage_Newsletter-Signup_1-Field_V1
LP-FreeTrial_Demo-Request_5-Fields_V2
Footer_Content-Download_2-Fields_V1
```

### Popup/Modal Naming

```
[Trigger]_[Offer]_[Placement]_[Variation]

Examples:
Exit-Intent_Discount_All-Pages_A
Time-5sec_Newsletter_Homepage_B
Scroll-50_Ebook_Blog-Posts_A
```

---

## Content Marketing

### Blog Post File Naming

**Standard Format**:
```
[Year-Month-Day]_[URL-Slug]_[Status]

Examples:
2024-11-15_how-to-improve-email-open-rates_published
2024-11-20_ultimate-guide-to-seo_draft
2024-12-01_content-marketing-trends-2025_scheduled
```

**Status Codes**:
- `draft` - In progress
- `review` - In review
- `scheduled` - Scheduled for publication
- `published` - Live
- `updated` - Updated version of existing post

### Content Downloads (Ebooks, Whitepapers, Guides)

```
[Content-Type]_[Topic]_[Year]_[Version]

Examples:
Ebook_Email-Marketing-Guide_2024_V1
Whitepaper_State-of-Marketing_2024_V1
Checklist_SEO-Audit_2024_V2
Template_Email-Campaign_2024_V1
Report_Industry-Benchmarks_2024-Q4_V1
```

**Content Type Codes**:
- `Ebook`
- `Whitepaper`
- `Guide`
- `Checklist`
- `Template`
- `Report`
- `Case-Study`
- `Infographic`
- `Webinar-Deck`

### Video Content Naming

```
[Platform]_[Content-Type]_[Topic]_[Length]_[Version]

Examples:
YouTube_Tutorial_GA4-Setup_10min_V1
LinkedIn_ThoughtLeadership_Marketing-Trends_3min_V1
Instagram_ProductDemo_Features_60sec_V2
TikTok_Educational_SEO-Tip_30sec_V1
```

---

## UTM Parameters

### UTM Naming Standards

**Required Parameters**:
- `utm_source` - Traffic source
- `utm_medium` - Marketing medium
- `utm_campaign` - Campaign name

**Optional Parameters**:
- `utm_content` - Content/creative variation
- `utm_term` - Paid keyword (for search ads)

**Formatting Rules**:
- Use lowercase only
- Use hyphens instead of underscores or spaces
- Be consistent and specific
- Keep under 50 characters per parameter when possible

### UTM Source

Identifies where traffic originated:

```
Social Media:
- facebook
- instagram
- linkedin
- twitter
- tiktok
- pinterest

Email:
- newsletter
- promotional-email
- transactional-email
- nurture-email

Paid Advertising:
- google-ads
- facebook-ads
- linkedin-ads

Other:
- partner-[partner-name]
- affiliate-[affiliate-name]
```

### UTM Medium

Identifies marketing medium/channel:

```
- organic (organic social posts)
- cpc (cost per click - paid search)
- ppc (pay per click - paid search)
- cpm (cost per thousand - display)
- social-paid (paid social media)
- social-organic (organic social media)
- email (email marketing)
- referral (referral traffic)
- affiliate (affiliate marketing)
- display (display advertising)
- video (video advertising)
```

### UTM Campaign

Aligns with campaign naming convention:

```
Format: [year-quarter]_[campaign-name]

Examples:
- 2024q4_black-friday
- 2024q4_product-launch
- 2024-11_webinar-series
- 2025q1_free-trial-promotion
```

### UTM Content

Differentiates similar content/ads in same campaign:

```
Examples:
- ad-variation-a
- ad-variation-b
- hero-cta
- sidebar-cta
- email-link-1
- email-link-2
- text-link
- image-link
- button-cta
```

### UTM Term

For paid search, use the actual keyword:

```
Examples:
- email-marketing-software
- crm-platform
- marketing-automation-tool
```

### Complete UTM Examples

```
Facebook Ad:
https://example.com/landing-page?utm_source=facebook&utm_medium=social-paid&utm_campaign=2024q4_product-launch&utm_content=video-ad-a

Newsletter Link:
https://example.com/blog-post?utm_source=newsletter&utm_medium=email&utm_campaign=2024-11_weekly-newsletter&utm_content=featured-article

Google Search Ad:
https://example.com/free-trial?utm_source=google-ads&utm_medium=cpc&utm_campaign=2024q4_free-trial&utm_content=ad-variation-b&utm_term=email-marketing-software
```

### UTM Best Practices

1. **Use UTM Builder Tool**: Google's Campaign URL Builder or similar
2. **Document Your Conventions**: Maintain central reference document
3. **Create Approved Lists**: Pre-approved values for source, medium, campaign
4. **Use URL Shorteners**: For social media, use Bitly or similar (with UTMs already included)
5. **Test Before Sending**: Always test UTM links before campaign launch
6. **Don't Use on Internal Links**: UTMs can reset sessions and inflate traffic

---

## File Management

### Image and Creative Asset Naming

**Standard Format**:
```
[Asset-Type]_[Campaign]_[Placement]_[Size]_[Variation]

Examples:
Banner_BlackFriday_Facebook-Feed_1200x628_A.jpg
Video_ProductLaunch_YouTube_1920x1080_B.mp4
Icon_Features_Website_64x64_v1.png
Logo_Brand_All-Platforms_Square_v2.svg
```

**Asset Type Codes**:
- `Banner` - Banner images
- `Video` - Video files
- `Icon` - Icons
- `Logo` - Logos
- `Thumbnail` - Video thumbnails
- `Hero` - Hero images
- `Infographic` - Infographics
- `Photo` - Photography
- `Illustration` - Illustrations

**Size Format**:
- Use actual pixel dimensions: `1200x628`, `1920x1080`
- Or use standard names: `Square`, `Portrait`, `Landscape`

**File Extension Best Practices**:
- Images: `.jpg` (photos), `.png` (graphics with transparency), `.svg` (logos/icons)
- Video: `.mp4` (preferred), `.mov`, `.avi`
- Documents: `.pdf` (final), `.docx` (drafts)
- Presentations: `.pptx`, `.key`, `.pdf`

### Document Naming

**Standard Format**:
```
[Doc-Type]_[Topic]_[Date]_[Version]_[Status]

Examples:
Campaign-Brief_Q4-Product-Launch_2024-10-15_V2_Final.docx
Report_Monthly-Analytics_2024-11_V1_Draft.xlsx
Presentation_Board-Meeting_2024-11-20_V3_Final.pptx
```

**Status Codes**:
- `Draft` - Work in progress
- `Review` - Under review
- `Final` - Approved final version
- `Archive` - Archived/superseded

---

## Folder Structure

### Campaign Folder Organization

```
Marketing/
├── 2024/
│   ├── Q1/
│   ├── Q2/
│   ├── Q3/
│   └── Q4/
│       ├── Black-Friday/
│       │   ├── Creative/
│       │   │   ├── Images/
│       │   │   ├── Video/
│       │   │   └── Copy/
│       │   ├── Landing-Pages/
│       │   ├── Email/
│       │   ├── Ads/
│       │   │   ├── Google/
│       │   │   ├── Facebook/
│       │   │   └── LinkedIn/
│       │   ├── Analytics/
│       │   └── Campaign-Brief.docx
│       └── Product-Launch/
└── 2025/
    └── Q1/
```

### Asset Library Organization

```
Brand-Assets/
├── Logos/
│   ├── Primary/
│   ├── Secondary/
│   ├── Icon/
│   └── Wordmark/
├── Colors/
├── Fonts/
├── Templates/
│   ├── Email/
│   ├── Social-Media/
│   ├── Landing-Pages/
│   └── Presentations/
├── Photography/
├── Icons/
└── Brand-Guidelines.pdf
```

---

## Platform-Specific Conventions

### Salesforce Campaign Naming

```
[Type]-[Year][Quarter]-[Campaign-Name]-[Region]

Examples:
ADV-2024Q4-Black-Friday-US
EVT-2024Q4-Webinar-Series-Global
CNT-2024Q4-Ebook-Download-US
EML-2024-11-Newsletter-All
```

**Type Codes**:
- `ADV` - Advertising
- `EVT` - Event
- `CNT` - Content
- `EML` - Email
- `WEB` - Webinar
- `TRD` - Tradeshow
- `PRT` - Partner

### HubSpot Workflow Naming

```
[Workflow-Type]_[Trigger]_[Action]_[Version]

Examples:
Lead-Nurture_Form-Submit_Email-Series_V2
Lead-Scoring_Behavior_Increase-Score_V1
Notification_High-Value-Lead_Alert-Sales_V1
```

### Google Analytics 4 Event Naming

Use snake_case for consistency:

```
Examples:
- form_submit
- video_play
- cta_click
- page_scroll_50
- file_download
- outbound_link_click
```

---

## Testing and Experimentation

### A/B Test Naming

**Standard Format**:
```
[Asset]_[Test-Element]_[Hypothesis]_[Date]_[Variation]

Examples:
LP-FreeTrial_Headline_Benefit-vs-Feature_2024-11_A
LP-FreeTrial_Headline_Benefit-vs-Feature_2024-11_B

Email_Subject-Line_Urgency-vs-Curiosity_2024-11-15_A
Email_Subject-Line_Urgency-vs-Curiosity_2024-11-15_B
```

**Test Element Examples**:
- `Headline`
- `CTA`
- `Hero-Image`
- `Form-Length`
- `Color-Scheme`
- `Layout`
- `Pricing-Display`
- `Social-Proof`

**Variation Codes**:
- Simple A/B: `A`, `B`
- Multivariate: `A`, `B`, `C`, `D`, etc.
- Control vs. Variant: `Control`, `Variant-1`, `Variant-2`

### Experiment Tracking

Maintain experiment log:

```
Experiment ID: EXP-2024-047
Name: LP-FreeTrial_Headline_Benefit-vs-Feature_2024-11
Start Date: 2024-11-01
End Date: 2024-11-15
Hypothesis: Benefit-focused headline will increase conversions by 15%
Variations: A (Benefit), B (Feature)
Primary Metric: Conversion rate
Winner: Variation A (+23% conversion rate)
```

---

## Governance and Maintenance

### Naming Convention Documentation

Maintain a central naming conventions document that includes:

1. **Current Standards** - This document
2. **Platform-Specific Guidelines** - Nuances for each platform
3. **Approved Values List** - Pre-approved campaign names, sources, mediums
4. **Examples Library** - Real examples from your organization
5. **Exception Process** - How to request exceptions
6. **Change Log** - History of updates to naming conventions

### Enforcement

**Methods**:
1. **Training**: Onboard all new team members
2. **Templates**: Provide pre-formatted naming templates
3. **Checklists**: Include naming verification in launch checklists
4. **Audits**: Quarterly audits of campaign names
5. **Tools**: Use automation to enforce (custom fields, validation rules)

### Review Cycle

- **Quarterly Review**: Check if conventions still serve team needs
- **Annual Update**: Incorporate learnings, new platforms, team growth
- **Ad Hoc Updates**: When adding new channels or campaign types

---

## Quick Reference

### Campaign Naming Template
```
[Year][Quarter]_[Campaign-Name]_[Objective]_[Audience]
Example: 2024Q4_ProductLaunch_Acquisition_SMB
```

### UTM Template
```
?utm_source=[source]&utm_medium=[medium]&utm_campaign=[campaign]&utm_content=[content]
Example: ?utm_source=facebook&utm_medium=social-paid&utm_campaign=2024q4_product-launch&utm_content=video-ad-a
```

### File Naming Template
```
[Asset-Type]_[Campaign]_[Placement]_[Size]_[Variation].[ext]
Example: Banner_BlackFriday_Facebook_1200x628_A.jpg
```

### Email Naming Template
```
[Type]_[Year-Month-Day]_[Theme]_[Segment]_[Variation]
Example: Promo_2024-11-24_BlackFriday_Customers_A
```

---

## Appendix: Complete Examples

### Complete Campaign Setup

**Campaign**: Black Friday 2024 Promotion

**Campaign Name**: `2024Q4_BlackFriday_Acquisition_All`

**Google Ads Campaign**: `Search_2024Q4_BlackFriday_US_All`
- Ad Group: `discount-software_Exact_All`
  - Ad: `RSA_A_Urgency-Headline`

**Facebook Campaign**: `Conversions_2024Q4_BlackFriday_BOF`
- Ad Set: `Lookalike_US_25-54_Feed`
  - Ad: `SingleImage_Discount_A`

**Email Campaign**: `Promo_2024-11-24_BlackFriday_All_A`

**Landing Page**: `LP_BlackFriday_All_A`

**UTM for Facebook Ad**:
```
?utm_source=facebook&utm_medium=social-paid&utm_campaign=2024q4_black-friday&utm_content=single-image-a
```

**Creative Assets**:
- `Banner_BlackFriday_Facebook-Feed_1200x628_A.jpg`
- `Video_BlackFriday_Instagram-Stories_1080x1920_B.mp4`

**Campaign Folder**:
```
Marketing/2024/Q4/Black-Friday/
```

---

**Version**: 1.0
**Maintained by**: Elite Digital Marketing Skills Project
**Next Review**: 2025-02-19

---

## Summary

Consistent naming conventions are non-negotiable for professional digital marketing operations. They enable:
- Faster asset discovery
- Accurate reporting and attribution
- Seamless collaboration across teams
- Scalable growth as team and campaigns expand
- Reduced errors and confusion

Adopt these standards, customize for your organization's specific needs, enforce through training and tools, and review quarterly to ensure they continue serving your team's growth.
