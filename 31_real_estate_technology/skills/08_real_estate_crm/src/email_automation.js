/**
 * Email Drip Campaign Automation
 */
const nodemailer = require('nodemailer');

class EmailAutomation {
  constructor() {
    this.transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: 587,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
      }
    });
  }
  
  async sendDripCampaign(lead, campaign) {
    const emails = this.getCampaignEmails(campaign);
    
    for (let i = 0; i < emails.length; i++) {
      const email = emails[i];
      
      // Schedule email
      setTimeout(async () => {
        await this.sendEmail({
          to: lead.email,
          subject: email.subject,
          html: this.personalizeEmail(email.template, lead)
        });
      }, email.delay * 1000);  // delay in seconds
    }
  }
  
  getCampaignEmails(campaign) {
    const campaigns = {
      buyer_nurture: [
        {
          subject: 'Welcome! Let\'s find your dream home',
          template: 'welcome',
          delay: 0
        },
        {
          subject: 'Here are some properties you might like',
          template: 'property_matches',
          delay: 86400  // 1 day
        },
        {
          subject: 'How to get pre-approved for a mortgage',
          template: 'mortgage_guide',
          delay: 259200  // 3 days
        }
      ]
    };
    
    return campaigns[campaign] || [];
  }
  
  personalizeEmail(template, lead) {
    let html = templates[template];
    html = html.replace('{{NAME}}', lead.name);
    html = html.replace('{{BUDGET}}', lead.budget.toLocaleString());
    return html;
  }
  
  async sendEmail(options) {
    return await this.transporter.sendMail(options);
  }
}

module.exports = EmailAutomation;
