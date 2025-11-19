# Lead Management Reference

## Quick Reference for Real Estate Lead Capture & Routing

### Lead Sources

```javascript
const LEAD_SOURCES = {
  CONTACT_FORM: 'contact_form',
  PHONE_CALL: 'phone_call',
  CHAT: 'chat',
  EMAIL: 'email',
  SAVED_SEARCH: 'saved_search',
  PROPERTY_ALERT: 'property_alert',
  TOUR_REQUEST: 'tour_request',
  MORTGAGE_CALCULATOR: 'mortgage_calculator',
  HOME_VALUATION: 'home_valuation',
  VIRTUAL_TOUR: 'virtual_tour_view',
  SOCIAL_MEDIA: 'social_media'
};
```

### Lead Schema

```javascript
const leadSchema = {
  lead_id: 'uuid',
  created_at: 'timestamp',
  source: 'string',
  property_id: 'string',          // Associated listing
  contact: {
    first_name: 'string',
    last_name: 'string',
    email: 'string',
    phone: 'string',
    preferred_contact: 'email|phone|text'
  },
  details: {
    message: 'text',
    budget: 'number',
    timeline: 'string',
    pre_approved: 'boolean',
    current_situation: 'renting|owning|first_time'
  },
  routing: {
    agent_id: 'string',
    route_method: 'listing_agent|territory|round_robin',
    routed_at: 'timestamp',
    response_time: 'number'        // seconds
  },
  engagement: {
    status: 'new|contacted|qualified|nurture|converted|closed',
    score: 'number',                // 0-100
    last_contact: 'timestamp',
    contact_attempts: 'number'
  },
  metadata: {
    ip_address: 'string',
    user_agent: 'string',
    session_id: 'string',
    utm_source: 'string',
    utm_campaign: 'string'
  }
};
```

### Lead Routing Logic

```javascript
class LeadRouter {
  async route(lead) {
    // Priority 1: Listing agent (if property-specific)
    if (lead.property_id) {
      const property = await this.getProperty(lead.property_id);
      if (property.agent_id && await this.isAgentAvailable(property.agent_id)) {
        return this.assignToAgent(lead, property.agent_id, 'listing_agent');
      }
    }

    // Priority 2: Territory-based routing
    const territoryAgent = await this.findTerritoryAgent(lead);
    if (territoryAgent) {
      return this.assignToAgent(lead, territoryAgent.id, 'territory');
    }

    // Priority 3: Round-robin among available agents
    const availableAgent = await this.getNextAvailableAgent();
    return this.assignToAgent(lead, availableAgent.id, 'round_robin');
  }

  async findTerritoryAgent(lead) {
    // Find agent assigned to ZIP code or neighborhood
    const location = lead.property_id ?
      await this.getPropertyLocation(lead.property_id) :
      this.extractLocationFromLead(lead);

    return await db.agent_territories.findOne({
      where: {
        zip_code: location.zip,
        active: true
      },
      order: [['priority', 'DESC']]
    });
  }

  async isAgentAvailable(agentId) {
    const agent = await db.agents.findByPk(agentId);

    // Check business hours
    const now = new Date();
    const hour = now.getHours();
    if (hour < 9 || hour > 18) return false;

    // Check lead capacity
    const activeLeads = await this.getActiveLeadCount(agentId);
    if (activeLeads >= agent.max_leads) return false;

    // Check vacation/out-of-office
    if (agent.out_of_office) return false;

    return true;
  }

  async assignToAgent(lead, agentId, method) {
    await db.leads.update({
      agent_id: agentId,
      route_method: method,
      routed_at: new Date(),
      status: 'assigned'
    }, {
      where: { lead_id: lead.lead_id }
    });

    // Notify agent
    await this.notifyAgent(agentId, lead);

    // Start response time tracking
    await this.startResponseTimer(lead.lead_id);

    return { agent_id: agentId, method };
  }
}
```

### Lead Scoring

```javascript
const calculateLeadScore = (lead) => {
  let score = 0;

  // Source quality (0-30 points)
  const sourceScores = {
    tour_request: 30,
    contact_form: 25,
    phone_call: 28,
    saved_search: 20,
    mortgage_calculator: 22,
    property_alert: 15,
    virtual_tour_view: 10
  };
  score += sourceScores[lead.source] || 0;

  // Contact completeness (0-20 points)
  if (lead.contact.phone && lead.contact.email) score += 20;
  else if (lead.contact.phone || lead.contact.email) score += 10;

  // Financial readiness (0-25 points)
  if (lead.details.pre_approved) score += 25;
  else if (lead.details.budget) score += 15;

  // Timeline urgency (0-15 points)
  const timelineScores = {
    'immediately': 15,
    'within_30_days': 12,
    'within_90_days': 8,
    'within_6_months': 5,
    'just_looking': 2
  };
  score += timelineScores[lead.details.timeline] || 0;

  // Engagement level (0-10 points)
  const pageViews = lead.session_data?.page_views || 0;
  score += Math.min(pageViews * 2, 10);

  return Math.min(score, 100);
};
```

### Contact Form Implementation

```javascript
// Frontend form
const ContactForm = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    message: '',
    preferred_contact: 'email',
    timeline: 'within_90_days',
    budget: '',
    pre_approved: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const lead = {
      ...formData,
      source: 'contact_form',
      property_id: propertyId,
      metadata: {
        url: window.location.href,
        referrer: document.referrer,
        utm_source: getUTMParam('utm_source'),
        utm_campaign: getUTMParam('utm_campaign')
      }
    };

    const response = await fetch('/api/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lead)
    });

    if (response.ok) {
      // Show thank you message
      showThankYou();
      // Track conversion
      gtag('event', 'generate_lead', { method: 'contact_form' });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="first_name"
        placeholder="First Name"
        required
        value={formData.first_name}
        onChange={handleChange}
      />
      <input
        type="text"
        name="last_name"
        placeholder="Last Name"
        required
        value={formData.last_name}
        onChange={handleChange}
      />
      <input
        type="email"
        name="email"
        placeholder="Email"
        required
        value={formData.email}
        onChange={handleChange}
      />
      <input
        type="tel"
        name="phone"
        placeholder="Phone"
        value={formData.phone}
        onChange={handleChange}
      />
      <select name="timeline" value={formData.timeline} onChange={handleChange}>
        <option value="immediately">Ready to buy now</option>
        <option value="within_30_days">Within 30 days</option>
        <option value="within_90_days">Within 90 days</option>
        <option value="within_6_months">Within 6 months</option>
        <option value="just_looking">Just browsing</option>
      </select>
      <textarea
        name="message"
        placeholder="Message (optional)"
        value={formData.message}
        onChange={handleChange}
      />
      <button type="submit">Contact Agent</button>
    </form>
  );
};
```

### Agent Notification

```javascript
const notifyAgent = async (agentId, lead) => {
  const agent = await db.agents.findByPk(agentId);

  // Email notification
  await sendEmail({
    to: agent.email,
    subject: `New Lead: ${lead.contact.first_name} ${lead.contact.last_name}`,
    template: 'new_lead',
    data: {
      agent_name: agent.name,
      lead_name: `${lead.contact.first_name} ${lead.contact.last_name}`,
      lead_email: lead.contact.email,
      lead_phone: lead.contact.phone,
      property_address: lead.property?.address,
      message: lead.details.message,
      lead_url: `https://crm.example.com/leads/${lead.lead_id}`
    }
  });

  // SMS notification (if enabled)
  if (agent.sms_notifications) {
    await sendSMS({
      to: agent.phone,
      message: `New lead from ${lead.contact.first_name}. ` +
               `Contact: ${lead.contact.phone || lead.contact.email}. ` +
               `View: https://crm.example.com/leads/${lead.lead_id}`
    });
  }

  // Push notification (if mobile app)
  if (agent.push_token) {
    await sendPushNotification({
      token: agent.push_token,
      title: 'New Lead',
      body: `${lead.contact.first_name} ${lead.contact.last_name} is interested in ${lead.property?.address}`,
      data: { lead_id: lead.lead_id }
    });
  }

  // CRM webhook (if integrated)
  if (agent.crm_webhook_url) {
    await fetch(agent.crm_webhook_url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lead)
    });
  }
};
```

### Response Time Tracking

```javascript
const trackResponseTime = async (leadId, agentId) => {
  const lead = await db.leads.findByPk(leadId);
  const responseTime = Date.now() - lead.created_at.getTime();

  await db.lead_responses.create({
    lead_id: leadId,
    agent_id: agentId,
    response_time: responseTime / 1000, // seconds
    response_channel: 'email' // or 'phone', 'text'
  });

  // Update agent metrics
  await db.agent_metrics.increment({
    total_responses: 1,
    total_response_time: responseTime
  }, {
    where: { agent_id: agentId }
  });

  return responseTime;
};
```

### Lead Nurture Automation

```javascript
const leadNurtureWorkflow = {
  new_lead: {
    immediate: {
      action: 'send_agent_notification',
      delay: 0
    },
    day_1: {
      action: 'send_welcome_email',
      template: 'welcome_lead',
      delay: 3600 // 1 hour
    },
    day_2: {
      action: 'send_similar_properties',
      delay: 86400 // 1 day
    },
    day_7: {
      action: 'send_market_report',
      delay: 604800 // 7 days
    }
  },

  no_response: {
    day_3: {
      action: 'agent_reminder',
      message: 'Follow up with lead'
    },
    day_7: {
      action: 'reassign_lead',
      method: 'round_robin'
    }
  },

  qualified: {
    weekly: {
      action: 'send_property_matches',
      frequency: 604800
    }
  }
};

const executeNurtureWorkflow = async (lead) => {
  const workflow = leadNurtureWorkflow[lead.status];

  for (const [step, config] of Object.entries(workflow)) {
    await scheduleTask({
      task: config.action,
      lead_id: lead.lead_id,
      delay: config.delay,
      data: config
    });
  }
};
```

### Lead Analytics

```javascript
const leadMetrics = {
  // Source performance
  bySource: {
    contact_form: {
      total: 150,
      converted: 12,
      conversion_rate: 0.08,
      avg_score: 65
    },
    tour_request: {
      total: 45,
      converted: 15,
      conversion_rate: 0.33,
      avg_score: 82
    }
  },

  // Agent performance
  byAgent: {
    agent_123: {
      assigned: 25,
      contacted: 23,
      qualified: 15,
      converted: 4,
      avg_response_time: 342, // seconds
      conversion_rate: 0.16
    }
  },

  // Time-based
  byHour: {
    9: 15,  // 9am
    10: 22,
    11: 18,
    // ...
  },

  // Overall
  overall: {
    total_leads: 500,
    avg_score: 58,
    median_response_time: 420,
    conversion_rate: 0.12
  }
};
```

### Duplicate Detection

```javascript
const findDuplicateLeads = async (newLead) => {
  // Check for duplicates within 30 days
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  const duplicates = await db.leads.findAll({
    where: {
      created_at: { [Op.gte]: thirtyDaysAgo },
      [Op.or]: [
        { 'contact.email': newLead.contact.email },
        { 'contact.phone': newLead.contact.phone }
      ]
    }
  });

  if (duplicates.length > 0) {
    // Append to existing lead instead of creating new
    const existingLead = duplicates[0];
    await db.lead_activities.create({
      lead_id: existingLead.lead_id,
      type: 'duplicate_submission',
      property_id: newLead.property_id,
      details: newLead.details
    });

    return { isDuplicate: true, existingLeadId: existingLead.lead_id };
  }

  return { isDuplicate: false };
};
```

### Lead Export/Integration

```javascript
// Export to external CRM
const exportToCRM = async (lead, crmType) => {
  const exporters = {
    salesforce: async (lead) => {
      return await salesforce.createLead({
        FirstName: lead.contact.first_name,
        LastName: lead.contact.last_name,
        Email: lead.contact.email,
        Phone: lead.contact.phone,
        LeadSource: lead.source,
        Property__c: lead.property_id
      });
    },

    hubspot: async (lead) => {
      return await hubspot.contacts.create({
        properties: {
          firstname: lead.contact.first_name,
          lastname: lead.contact.last_name,
          email: lead.contact.email,
          phone: lead.contact.phone,
          lead_source: lead.source,
          lead_score: lead.score
        }
      });
    },

    follow_up_boss: async (lead) => {
      return await followUpBoss.createPerson({
        firstName: lead.contact.first_name,
        lastName: lead.contact.last_name,
        emails: [{ value: lead.contact.email }],
        phones: [{ value: lead.contact.phone }],
        source: lead.source,
        assignedTo: lead.routing.agent_id
      });
    }
  };

  return await exporters[crmType](lead);
};
```

### Performance Benchmarks

| Metric | Target | Industry Avg |
|--------|--------|--------------|
| Response time | < 5 min | 47 min |
| Contact rate | > 80% | 27% |
| Qualification rate | > 30% | 25% |
| Conversion rate | > 10% | 2-5% |
| Lead score accuracy | > 70% | N/A |

## See Also
- property_search_reference.md
- seo_reference.md
- valuation_models_reference.md
