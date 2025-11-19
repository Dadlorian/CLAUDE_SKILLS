# Matter Intake Workflow Automation Guide

## Overview

Matter intake is the first impression clients have of your firm and sets the foundation for successful client relationships. An automated, efficient intake process ensures consistency, reduces response time, improves client experience, and minimizes administrative burden. This guide provides a step-by-step approach to automating matter intake workflows.

## Benefits of Automated Intake

### For the Firm
- Faster response to inquiries (captures leads before they call competitors)
- Consistent information capture (no missing fields)
- Automated conflicts checking
- Reduced administrative time (automatic data entry)
- Better lead tracking and conversion analysis
- 24/7 availability for inquiries

### For Clients
- Convenient online submission (anytime, anywhere)
- Immediate acknowledgment
- Clear next steps
- Professional first impression
- Reduced need for repetitive information sharing

## Intake Workflow Steps

### Step 1: Initial Contact Capture

#### Online Intake Form
**Form Fields**
- Contact Information (name, email, phone, address)
- Case description (free text)
- Case type/practice area
- Relevant dates (incident date, deadline awareness)
- Opposing parties
- How they found you (referral source)
- Urgency/timeline
- Financial capacity (ability to pay retainer)
- Availability for consultation

**Form Best Practices**
- Mobile-friendly (60%+ of inquiries may be mobile)
- Minimal required fields (reduce abandonment)
- Progress indicator if multi-page
- Save and resume capability
- Clear privacy policy and terms
- Secure (SSL encryption)
- Conditional logic (show relevant questions based on answers)

**Form Tools**
- **Google Forms**: Free, simple, integrates with Google Sheets and Zapier
- **Typeform**: Beautiful UI, conversational flow, integrations
- **JotForm**: Legal-specific templates, HIPAA compliance, payment integration
- **Clio Grow**: Legal-specific intake, integrates with Clio Manage
- **Lawmatics**: Full legal CRM with intake automation
- **Practice Management System Forms**: Native forms in PM system (Clio, MyCase, PracticePanther)

**Form Placement**
- Prominent on website (navigation, footer, sidebar)
- Dedicated "Contact Us" or "Free Consultation" page
- Practice area pages
- Blog posts (relevant CTAs)
- Email signature links

#### Other Contact Channels
**Phone**
- Intake specialist enters information into form/system
- Recorded call notes
- Schedule consultation during call if appropriate

**Email**
- Automated response with link to intake form
- Manual data entry if detailed email received

**Chatbot**
- Initial screening via website chatbot
- Qualify lead
- Route to intake form or human if qualified

### Step 2: Immediate Acknowledgment

#### Auto-Response Email
**Contents**
- Thank you for contacting us
- Confirmation we received inquiry
- Timeline for response (within 24 hours typical)
- Next steps (we'll review and contact you)
- Contact information if urgent
- Link to client portal (if pre-creating account)

**Automation**
- Form submission triggers email
- Use email template with merge fields
- Send from attorney or intake specialist email (not no-reply@)

#### SMS Confirmation (Optional)
- Text message confirmation
- Brief acknowledgment
- "We received your inquiry and will contact you within 24 hours"

### Step 3: Lead Routing and Assignment

#### Routing Logic
**Practice Area-Based**
- Assign to attorney by case type
- Round-robin for general practice
- Workload-based assignment

**Geographic**
- Assign by client location (if multi-office)
- Jurisdictional considerations

**Conflict of Interest**
- Hold for conflicts check before assignment
- Auto-assign to conflicts specialist first

#### Assignment Notification
- Email to assigned attorney: "New intake assigned to you"
- Include form submission details
- Link to full intake record
- Task created in PM system for follow-up

### Step 4: Automated Conflicts Check

#### Pre-Screening
**Automatic Search**
- Search practice management system for:
  - Client name (and variations)
  - Opposing parties
  - Related entities
- Flag potential conflicts
- Generate conflicts check report

**Manual Review Required**
- Attorney or conflicts specialist reviews flagged results
- Determines if actual conflict or false positive
- Proceeds with clearance or declination

**No Conflicts**
- Auto-generate clearance confirmation
- Proceed to next step

#### Timing
- Run conflicts check immediately upon intake submission
- Or run when intake assigned to attorney (faster)
- Results ready before attorney reviews intake

### Step 5: Qualification and Triage

#### Automated Qualification
**Disqualifiers**
- Statute of limitations expired (based on dates provided)
- Outside practice area
- Jurisdiction not served
- Conflict of interest identified

**Auto-Response for Disqualified**
- Polite declination email
- Explanation (if appropriate)
- Referral to bar association or other resources
- Log as declined lead in CRM

#### Manual Qualification
**Attorney Review**
- Reviews intake details
- Assesses case merits
- Determines if wants to take case
- May need additional information or consultation

**Qualification Criteria**
- Case has merit
- Within statute of limitations
- Firm has expertise
- Client can afford fees
- Capacity available
- Good client fit

### Step 6: Consultation Scheduling

#### Automated Scheduling
**Scheduling Tools**
- **Calendly**: Popular, easy setup, integrations
- **Acuity Scheduling**: Advanced features, payments
- **PM System Scheduling**: Built into Clio, MyCase, etc.

**Workflow**
- Qualified lead receives email with scheduling link
- Client selects available time
- Appointment auto-added to attorney calendar
- Confirmation email to client
- Reminder emails (1 day before, 1 hour before)
- Zoom/video conference link included

**Alternative: Manual Scheduling**
- Intake specialist calls client to schedule
- More personal touch
- Better for complex cases or high-value clients

#### Pre-Consultation Tasks
**Information Gathering**
- Send questionnaire for client to complete before meeting
- Request relevant documents (upload to portal)
- Review fee schedule and estimate
- Prepare engagement letter template

**Attorney Preparation**
- Review intake information
- Review conflicts check results
- Research relevant law
- Prepare consultation questions
- Estimate fees and costs

### Step 7: Consultation and Decision

#### Consultation
- Attorney meets with client (in-person or video)
- Discusses case details
- Assesses viability
- Explains process and timeline
- Discusses fees and costs
- Answers client questions

#### Decision Points
**Accept Case**
- Proceed to engagement
- Send engagement letter
- Request retainer
- Schedule next steps

**Decline Case**
- Polite explanation
- Referral if appropriate
- Follow-up email confirming declination

**More Information Needed**
- Request additional documents or information
- Schedule follow-up
- Set deadline for decision

### Step 8: Engagement and Onboarding

#### Engagement Letter
**Automated Generation**
- Template with merge fields (client name, matter details, fee arrangement)
- Generate PDF
- Send via email or client portal
- E-signature (DocuSign, Adobe Sign)

**Contents** (see ABA Model Rule 1.5)
- Scope of representation
- Fee arrangement
- Billing rates and rules
- Cost estimate
- Payment terms
- Retainer amount
- Client responsibilities
- Termination provisions

#### Retainer Payment
**Online Payment**
- Include payment link in engagement email
- Credit card or ACH
- Automatically posts to trust account
- Triggers next steps upon payment

**Traditional Payment**
- Check or wire transfer
- Manual posting to trust account
- Confirm receipt before proceeding

#### Matter Creation
**Automated Matter Opening**
- Upon signed engagement letter + retainer payment
- Create matter in practice management system
- Assign matter number
- Set up matter team
- Create matter folders in DMS
- Add initial tasks and calendar entries
- Send welcome email to client with portal access

### Step 9: CRM and Follow-Up

#### Lead Tracking
**CRM Fields**
- Lead source (how they found you)
- Practice area/case type
- Status (new, contacted, consultation scheduled, engaged, declined)
- Assigned attorney
- Important dates
- Tags for segmentation

**Lead Nurturing**
- Automated email sequences for leads not yet ready
- Educational content
- Stay top-of-mind for when ready
- Track engagement

#### Conversion Analysis
**Metrics**
- Lead volume by source
- Conversion rate (leads to consultations)
- Consultation to engagement rate
- Overall conversion (leads to clients)
- Time from inquiry to engagement
- Reasons for declination

**Optimization**
- Test different form designs
- A/B test confirmation emails
- Improve qualifying questions
- Streamline scheduling
- Reduce friction points

## Automation Implementation

### Tools and Integrations

#### Option 1: Native PM System Intake
**Clio Grow**
- Dedicated intake and CRM
- Integrates with Clio Manage
- Forms, scheduling, lead tracking
- Automated workflows

**MyCase / PracticePanther Built-In**
- Contact forms create leads
- Basic automation
- Scheduling integration

**Pros**: Fully integrated, less setup
**Cons**: May lack advanced features

#### Option 2: Third-Party Form + Zapier
**Workflow**
1. Google Forms or Typeform for intake
2. Zapier automation triggers on submission
3. Create contact in PM system
4. Send confirmation email (Gmail/Outlook)
5. Create task for attorney follow-up
6. Add to CRM (if separate)

**Pros**: Flexible, customizable, affordable
**Cons**: Requires setup, multiple tools

#### Option 3: Legal CRM (Lawmatics)
**Lawmatics Features**
- Legal-specific CRM and intake
- Forms and questionnaires
- Automated email sequences
- Scheduling
- E-signature integration
- Integrates with Clio, PracticePanther, etc.

**Pros**: Purpose-built for legal intake, powerful automation
**Cons**: Additional cost ($99-$299/user/month)

### Zapier Automation Example

**Trigger**: New Google Form submission
**Actions**:
1. **Create Contact** in Clio (or other PM system)
   - Map form fields to contact fields
   - Set contact type to "Lead"

2. **Create Lead Matter** in Clio
   - Set matter status to "Intake"
   - Set practice area from form response
   - Add matter description from form

3. **Send Email** (Gmail)
   - To: Form respondent
   - Template: "Thank you for contacting us..."
   - Include next steps

4. **Create Task** in Clio
   - Assign to attorney (based on practice area)
   - Title: "Review new intake: [Client Name]"
   - Due: Tomorrow
   - Description: Link to form responses

5. **Send Slack Notification** (optional)
   - Alert intake team of new lead
   - Include client name and case type

### Email Automation Sequences

#### Sequence 1: Initial Contact
- **Day 0**: Confirmation email (immediate)
- **Day 1**: "We're reviewing your case" (if no contact yet)
- **Day 3**: "Have you had a chance to review our availability?" (if scheduling link sent but not used)

#### Sequence 2: Post-Consultation
- **Day 0**: "Thank you for meeting with us" + engagement letter
- **Day 3**: Follow-up if engagement letter not signed
- **Day 7**: Final follow-up before closing lead

#### Sequence 3: Nurture (Not Ready Now)
- **Monthly**: Educational content, blog posts, newsletters
- **Quarterly**: Check-in "Are you still experiencing [problem]?"
- Stay top-of-mind for future needs or referrals

## Best Practices

### Form Design
1. **Mobile-First**: Design for smartphone use
2. **Keep It Short**: Only essential questions upfront
3. **Conditional Logic**: Show relevant questions only
4. **Progress Indicator**: Show how much left
5. **Clear CTAs**: "Get Free Consultation" not just "Submit"

### Response Time
1. **Immediate Auto-Response**: Within seconds
2. **Human Follow-Up**: Within 4 business hours (ideally same day)
3. **Weekend Inquiries**: Auto-response explains Monday follow-up
4. **Emergency Cases**: Provide emergency contact option

### Communication
1. **Clear Expectations**: Tell them what to expect and when
2. **Professional Tone**: Friendly but professional
3. **Responsive**: Answer questions promptly
4. **Personalized**: Use their name, reference their specific case

### Data Quality
1. **Required Fields**: Make critical fields required (name, email, phone)
2. **Validation**: Email and phone format validation
3. **Duplicate Detection**: Check for existing contacts
4. **Data Cleanup**: Regularly review and clean lead data

### Security and Compliance
1. **Secure Forms**: HTTPS/SSL encryption
2. **Privacy Policy**: Link to privacy policy on form
3. **Confidentiality Notice**: Disclaimer that submission doesn't create attorney-client relationship (until engagement)
4. **Data Retention**: Policy for how long to keep declined leads

## Measuring Success

### Key Metrics
- **Lead Volume**: Number of inquiries per month
- **Lead Source**: Where do leads come from?
- **Response Time**: Time from submission to first contact
- **Conversion Rate**: Percentage of leads that become clients
- **Time to Engagement**: Days from inquiry to signed engagement
- **Drop-Off Points**: Where do leads abandon process?

### Continuous Improvement
- A/B test form designs
- Test different confirmation email copy
- Experiment with scheduling vs. manual outreach
- Optimize qualification questions
- Refine email sequences based on open/click rates

## Common Pitfalls

### Over-Automation
- Don't eliminate human touch entirely
- High-value or complex cases may need personal outreach
- Balance efficiency with client service

### Poor Form Design
- Too long or complex forms have high abandonment
- Mobile-unfriendly forms frustrate users
- Confusing language or legalese

### Slow Follow-Up
- Automated confirmation but slow human follow-up defeats purpose
- Must have process to ensure timely attorney review

### Ignoring Leads
- Leads fall through cracks without system
- Need clear assignment and accountability

### No Tracking
- Without tracking, can't measure ROI or optimize
- Implement CRM to track all leads

## Checklist

### Setup Phase
- [ ] Choose intake form tool
- [ ] Design intake form (fields, conditional logic, mobile-friendly)
- [ ] Embed form on website
- [ ] Create confirmation email template
- [ ] Set up automation (Zapier or native)
- [ ] Configure conflicts check search
- [ ] Set up scheduling tool
- [ ] Create engagement letter templates
- [ ] Configure online payment for retainers

### Process Phase
- [ ] Define lead routing rules
- [ ] Assign responsibility for lead follow-up
- [ ] Create email sequence templates
- [ ] Define qualification criteria
- [ ] Document declination procedures
- [ ] Train staff on intake process

### Monitoring Phase
- [ ] Set up lead tracking in CRM
- [ ] Define key metrics to track
- [ ] Create dashboard or reports
- [ ] Schedule regular reviews (weekly, monthly)
- [ ] Collect feedback from clients and attorneys
- [ ] Continuously optimize based on data

## Resources

- **Clio Grow**: Legal intake and CRM
- **Lawmatics**: Legal intake automation
- **Zapier**: Workflow automation
- **Typeform, JotForm, Google Forms**: Form builders
- **Calendly, Acuity**: Scheduling automation
- **DocuSign, Adobe Sign**: E-signature for engagement letters
