/**
 * Feedback Aggregator - Multi-source Documentation Feedback Collection
 * Aggregates feedback from multiple sources and provides analytics
 */

class FeedbackAggregator {
  /**
   * Initialize the feedback aggregator
   */
  constructor() {
    this.feedbackSources = [
      'user_surveys',
      'support_tickets',
      'analytics',
      'code_reviews',
      'community'
    ];

    this.feedbackData = [];
    this.generateSampleFeedback();
  }

  /**
   * Generate sample feedback data
   */
  generateSampleFeedback() {
    const feedbackExamples = {
      user_surveys: [
        {
          id: 'survey-001',
          source: 'user_surveys',
          timestamp: new Date('2024-11-15'),
          rating: 4.5,
          category: 'clarity',
          comment: 'API documentation is very clear and helpful',
          respondent: 'Developer',
          documentId: 'api-ref-001'
        },
        {
          id: 'survey-002',
          source: 'user_surveys',
          timestamp: new Date('2024-11-14'),
          rating: 3.5,
          category: 'completeness',
          comment: 'Missing examples for advanced features',
          respondent: 'DevOps Engineer',
          documentId: 'guide-advanced'
        },
        {
          id: 'survey-003',
          source: 'user_surveys',
          timestamp: new Date('2024-11-13'),
          rating: 4.0,
          category: 'organization',
          comment: 'Good structure but could use better navigation',
          respondent: 'Technical Writer',
          documentId: 'guide-001'
        },
        {
          id: 'survey-004',
          source: 'user_surveys',
          timestamp: new Date('2024-11-12'),
          rating: 5.0,
          category: 'examples',
          comment: 'Excellent code examples!',
          respondent: 'Developer',
          documentId: 'tutorial-001'
        }
      ],
      support_tickets: [
        {
          id: 'ticket-001',
          source: 'support_tickets',
          timestamp: new Date('2024-11-15'),
          severity: 'high',
          category: 'accuracy',
          issue: 'Documentation example code contains deprecated API calls',
          relatedDoc: 'api-ref-001',
          status: 'open',
          mentions: 3
        },
        {
          id: 'ticket-002',
          source: 'support_tickets',
          timestamp: new Date('2024-11-10'),
          severity: 'medium',
          category: 'clarity',
          issue: 'Installation guide lacks system requirements',
          relatedDoc: 'install-guide',
          status: 'resolved',
          mentions: 5
        },
        {
          id: 'ticket-003',
          source: 'support_tickets',
          timestamp: new Date('2024-11-08'),
          severity: 'low',
          category: 'organization',
          issue: 'Table of contents formatting needs improvement',
          relatedDoc: 'guide-001',
          status: 'resolved',
          mentions: 2
        },
        {
          id: 'ticket-004',
          source: 'support_tickets',
          timestamp: new Date('2024-11-05'),
          severity: 'high',
          category: 'completeness',
          issue: 'Missing troubleshooting section for common errors',
          relatedDoc: 'getting-started',
          status: 'open',
          mentions: 8
        }
      ],
      analytics: [
        {
          id: 'analytics-001',
          source: 'analytics',
          timestamp: new Date('2024-11-15'),
          metric: 'bounce_rate',
          value: 0.15,
          documentId: 'api-ref-001',
          assessment: 'good'
        },
        {
          id: 'analytics-002',
          source: 'analytics',
          timestamp: new Date('2024-11-15'),
          metric: 'avg_time_on_page',
          value: 180,
          documentId: 'tutorial-001',
          unit: 'seconds',
          assessment: 'excellent'
        },
        {
          id: 'analytics-003',
          source: 'analytics',
          timestamp: new Date('2024-11-15'),
          metric: 'scroll_depth',
          value: 0.72,
          documentId: 'guide-001',
          assessment: 'good'
        },
        {
          id: 'analytics-004',
          source: 'analytics',
          timestamp: new Date('2024-11-15'),
          metric: 'search_exit_rate',
          value: 0.35,
          documentId: 'faq',
          assessment: 'fair'
        },
        {
          id: 'analytics-005',
          source: 'analytics',
          timestamp: new Date('2024-11-15'),
          metric: 'copy_paste_events',
          value: 847,
          documentId: 'api-ref-001',
          assessment: 'excellent'
        }
      ],
      code_reviews: [
        {
          id: 'review-001',
          source: 'code_reviews',
          timestamp: new Date('2024-11-14'),
          reviewer: 'Senior Developer',
          status: 'approved',
          feedback: 'Documentation examples are well-tested and comprehensive',
          category: 'technical_accuracy',
          documentId: 'api-ref-001'
        },
        {
          id: 'review-002',
          source: 'code_reviews',
          timestamp: new Date('2024-11-12'),
          reviewer: 'Code Quality Team',
          status: 'requested_changes',
          feedback: 'Code snippets need better error handling examples',
          category: 'completeness',
          documentId: 'guide-advanced'
        },
        {
          id: 'review-003',
          source: 'code_reviews',
          timestamp: new Date('2024-11-10'),
          reviewer: 'Security Team',
          status: 'approved',
          feedback: 'Security documentation meets all requirements',
          category: 'accuracy',
          documentId: 'security-guide'
        }
      ],
      community: [
        {
          id: 'community-001',
          source: 'community',
          timestamp: new Date('2024-11-15'),
          platform: 'forum',
          engagement: 'positive',
          sentiment: 0.85,
          mentions: 12,
          topic: 'Getting Started Guide is very helpful'
        },
        {
          id: 'community-002',
          source: 'community',
          timestamp: new Date('2024-11-14'),
          platform: 'slack',
          engagement: 'mixed',
          sentiment: 0.55,
          mentions: 8,
          topic: 'API documentation could use more examples'
        },
        {
          id: 'community-003',
          source: 'community',
          timestamp: new Date('2024-11-13'),
          platform: 'github_issues',
          engagement: 'negative',
          sentiment: 0.25,
          mentions: 15,
          topic: 'Documentation outdated for v2.0'
        },
        {
          id: 'community-004',
          source: 'community',
          timestamp: new Date('2024-11-12'),
          platform: 'twitter',
          engagement: 'positive',
          sentiment: 0.90,
          mentions: 34,
          topic: 'Excellent documentation quality'
        }
      ]
    };

    this.feedbackData = Object.values(feedbackExamples).flat();
  }

  /**
   * Aggregate feedback by source
   */
  aggregateBySource() {
    const aggregated = {};

    this.feedbackSources.forEach(source => {
      const sourceFeedback = this.feedbackData.filter(f => f.source === source);
      aggregated[source] = {
        count: sourceFeedback.length,
        feedback: sourceFeedback,
        summary: this.summarizeSource(source, sourceFeedback)
      };
    });

    return aggregated;
  }

  /**
   * Summarize feedback by source
   */
  summarizeSource(source, feedback) {
    const summary = {
      source,
      total: feedback.length,
      details: {}
    };

    switch (source) {
      case 'user_surveys':
        const avgRating = feedback.reduce((sum, f) => sum + (f.rating || 0), 0) / feedback.length;
        const categories = {};
        feedback.forEach(f => {
          categories[f.category] = (categories[f.category] || 0) + 1;
        });
        summary.details = {
          averageRating: avgRating.toFixed(2),
          ratingOut: 5,
          categoriesCovered: categories,
          participantTypes: [...new Set(feedback.map(f => f.respondent))]
        };
        break;

      case 'support_tickets':
        const bySeverity = { high: 0, medium: 0, low: 0 };
        const byStatus = { open: 0, resolved: 0 };
        feedback.forEach(f => {
          bySeverity[f.severity]++;
          byStatus[f.status]++;
        });
        const totalMentions = feedback.reduce((sum, f) => sum + (f.mentions || 0), 0);
        summary.details = {
          bySeverity,
          byStatus,
          totalMentions,
          openIssues: feedback.filter(f => f.status === 'open').length,
          averageMentions: (totalMentions / feedback.length).toFixed(1)
        };
        break;

      case 'analytics':
        summary.details = {
          metrics: feedback.map(f => ({
            metric: f.metric,
            value: f.value,
            unit: f.unit || '',
            assessment: f.assessment
          })),
          overallAssessment: this.assessAnalytics(feedback)
        };
        break;

      case 'code_reviews':
        const byStatus2 = { approved: 0, requested_changes: 0 };
        feedback.forEach(f => {
          byStatus2[f.status]++;
        });
        summary.details = {
          totalReviews: feedback.length,
          approved: byStatus2.approved,
          requestedChanges: byStatus2.requested_changes,
          reviewers: [...new Set(feedback.map(f => f.reviewer))],
          categories: [...new Set(feedback.map(f => f.category))]
        };
        break;

      case 'community':
        const platforms = {};
        let totalSentiment = 0;
        let totalMentions2 = 0;
        feedback.forEach(f => {
          platforms[f.platform] = (platforms[f.platform] || 0) + 1;
          totalSentiment += f.sentiment || 0;
          totalMentions2 += f.mentions || 0;
        });
        summary.details = {
          platforms,
          averageSentiment: (totalSentiment / feedback.length).toFixed(2),
          sentimentScale: [-1, 1],
          totalMentions: totalMentions2,
          topPlatforms: Object.entries(platforms)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([platform, count]) => ({ platform, count }))
        };
        break;
    }

    return summary;
  }

  /**
   * Assess analytics
   */
  assessAnalytics(feedback) {
    const assessments = feedback.map(f => f.assessment);
    const excellent = assessments.filter(a => a === 'excellent').length;
    const good = assessments.filter(a => a === 'good').length;
    const fair = assessments.filter(a => a === 'fair').length;

    return {
      excellent,
      good,
      fair,
      overallTrend: excellent + good > feedback.length / 2 ? 'positive' : 'needs_improvement'
    };
  }

  /**
   * Get feedback by category
   */
  feedbackByCategory() {
    const categories = {};

    this.feedbackData.forEach(feedback => {
      const category = feedback.category || feedback.metric || 'general';
      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(feedback);
    });

    return categories;
  }

  /**
   * Get top issues
   */
  getTopIssues(limit = 10) {
    const issues = this.feedbackData.filter(f => f.source === 'support_tickets');

    return issues
      .sort((a, b) => {
        const severityScore = { high: 3, medium: 2, low: 1 };
        const scoreA = (severityScore[a.severity] || 0) + (a.mentions || 0);
        const scoreB = (severityScore[b.severity] || 0) + (b.mentions || 0);
        return scoreB - scoreA;
      })
      .slice(0, limit)
      .map(issue => ({
        id: issue.id,
        issue: issue.issue,
        severity: issue.severity,
        mentions: issue.mentions,
        relatedDoc: issue.relatedDoc,
        status: issue.status,
        score: (({ high: 3, medium: 2, low: 1 })[issue.severity] || 0) + (issue.mentions || 0)
      }));
  }

  /**
   * Get sentiment analysis
   */
  getSentimentAnalysis() {
    const community = this.feedbackData.filter(f => f.source === 'community');
    const surveys = this.feedbackData.filter(f => f.source === 'user_surveys');

    const communitySentiment = community.length > 0
      ? community.reduce((sum, f) => sum + (f.sentiment || 0), 0) / community.length
      : 0;

    const surveyRating = surveys.length > 0
      ? surveys.reduce((sum, f) => sum + (f.rating || 0), 0) / (surveys.length * 5)
      : 0;

    const positiveTickets = this.feedbackData.filter(f =>
      f.source === 'support_tickets' && f.status === 'resolved'
    ).length;

    const totalTickets = this.feedbackData.filter(f => f.source === 'support_tickets').length;
    const ticketResolutionRate = totalTickets > 0 ? positiveTickets / totalTickets : 0;

    return {
      overallSentiment: ((communitySentiment + surveyRating) / 2).toFixed(2),
      sources: {
        community: {
          sentiment: communitySentiment.toFixed(2),
          scale: [-1, 1],
          quality: this.interpretSentiment(communitySentiment)
        },
        surveys: {
          rating: surveyRating.toFixed(2),
          scale: [0, 1],
          quality: this.interpretSentiment(surveyRating)
        },
        ticketResolution: {
          rate: (ticketResolutionRate * 100).toFixed(1) + '%',
          resolved: positiveTickets,
          total: totalTickets
        }
      },
      trend: 'positive'
    };
  }

  /**
   * Interpret sentiment value
   */
  interpretSentiment(value) {
    if (value >= 0.75) return 'excellent';
    if (value >= 0.5) return 'good';
    if (value >= 0.25) return 'fair';
    return 'poor';
  }

  /**
   * Get recommendations based on feedback
   */
  getRecommendations() {
    const topIssues = this.getTopIssues(5);
    const categories = this.feedbackByCategory();
    const sentiment = this.getSentimentAnalysis();

    const recommendations = [];

    // Based on top issues
    topIssues.forEach((issue, index) => {
      if (issue.severity === 'high') {
        recommendations.push({
          priority: 'critical',
          action: `Fix: ${issue.issue}`,
          document: issue.relatedDoc,
          impact: issue.mentions,
          effort: 'medium'
        });
      }
    });

    // Based on low ratings
    const surveys = this.feedbackData.filter(f => f.source === 'user_surveys');
    const lowRated = surveys.filter(f => f.rating < 3);

    lowRated.forEach(rating => {
      recommendations.push({
        priority: 'high',
        action: `Improve ${rating.category}: ${rating.comment}`,
        document: rating.documentId,
        feedback: rating.comment,
        effort: 'medium'
      });
    });

    // Based on community sentiment
    const communityFeedback = this.feedbackData.filter(f => f.source === 'community');
    const negativeFeedback = communityFeedback.filter(f => f.sentiment < 0.4);

    negativeFeedback.forEach(feedback => {
      recommendations.push({
        priority: 'medium',
        action: `Address: ${feedback.topic}`,
        platform: feedback.platform,
        mentions: feedback.mentions,
        effort: 'low'
      });
    });

    return recommendations.slice(0, 10);
  }

  /**
   * Generate comprehensive report
   */
  generateReport() {
    return {
      timestamp: new Date().toISOString(),
      summary: {
        totalFeedbackItems: this.feedbackData.length,
        sources: this.feedbackSources.length,
        coverageMap: {
          api_documentation: 'high',
          guides: 'high',
          tutorials: 'medium',
          faq: 'medium'
        }
      },
      bySource: this.aggregateBySource(),
      byCategory: this.feedbackByCategory(),
      topIssues: this.getTopIssues(),
      sentiment: this.getSentimentAnalysis(),
      recommendations: this.getRecommendations(),
      actionItems: {
        critical: this.getRecommendations().filter(r => r.priority === 'critical').length,
        high: this.getRecommendations().filter(r => r.priority === 'high').length,
        medium: this.getRecommendations().filter(r => r.priority === 'medium').length
      }
    };
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FeedbackAggregator;
}
