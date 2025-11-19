/**
 * Documentation Analytics Tracking
 *
 * Comprehensive analytics implementation for tracking documentation usage,
 * user behavior, and engagement metrics.
 *
 * Prerequisites:
 * - Google Analytics 4 configured
 * - npm install gtag
 */

// Initialize Google Analytics
function initializeAnalytics() {
  if (typeof gtag === 'undefined') {
    console.warn('Google Analytics not loaded');
    return;
  }

  // GA4 configuration
  gtag('config', 'G-XXXXXXXXXX', {
    'anonymize_ip': true,
    'allow_google_signals': false,
    'allow_ad_personalization_signals': false
  });
}

/**
 * Track page views with additional context
 */
function trackPageView(pagePath, pageTitle) {
  gtag('event', 'page_view', {
    'page_path': pagePath,
    'page_title': pageTitle,
    'page_location': window.location.href
  });

  logDebug(`Tracked page view: ${pageTitle}`);
}

/**
 * Track search queries
 * Call this when user performs a search
 */
function trackSearch(query, resultCount, searchType = 'documentation') {
  gtag('event', 'search', {
    'search_term': query,
    'results_count': resultCount,
    'search_type': searchType
  });

  logDebug(`Tracked search: "${query}" (${resultCount} results)`);
}

/**
 * Track search result clicks
 * Call this when user clicks a search result
 */
function trackSearchResultClick(query, resultTitle, position) {
  gtag('event', 'view_search_results', {
    'search_term': query,
    'result_title': resultTitle,
    'result_position': position
  });

  logDebug(`Tracked search click: ${resultTitle} (position: ${position})`);
}

/**
 * Track code copy events
 * Call this when user copies code from a code block
 */
function trackCodeCopy(codeLanguage, codeLength = 0) {
  gtag('event', 'code_copy', {
    'event_category': 'engagement',
    'code_language': codeLanguage,
    'code_length': codeLength
  });

  logDebug(`Tracked code copy: ${codeLanguage} (${codeLength} chars)`);
}

/**
 * Track link clicks
 * Call this when user clicks a link to external resource
 */
function trackLinkClick(linkUrl, linkText = '') {
  gtag('event', 'click_external_link', {
    'event_category': 'outbound',
    'link_url': linkUrl,
    'link_text': linkText
  });

  logDebug(`Tracked link click: ${linkUrl}`);
}

/**
 * Track documentation helpfulness
 * Call this when user clicks "Was this helpful?" buttons
 */
function trackHelpfulness(pageTitle, helpful) {
  gtag('event', 'page_helpful', {
    'event_category': 'satisfaction',
    'event_label': helpful ? 'helpful' : 'not_helpful',
    'page_title': pageTitle,
    'value': helpful ? 1 : 0
  });

  logDebug(`Tracked helpfulness: ${pageTitle} - ${helpful ? 'Helpful' : 'Not Helpful'}`);
}

/**
 * Track detailed feedback
 * Call this when user submits feedback form
 */
function trackDetailedFeedback(pageTitle, feedbackType, comments = '') {
  gtag('event', 'page_feedback', {
    'event_category': 'satisfaction',
    'feedback_type': feedbackType,  // 'confusing', 'incomplete', 'incorrect', 'outdated'
    'has_comments': comments.length > 0,
    'comment_length': comments.length,
    'page_title': pageTitle
  });

  logDebug(`Tracked feedback: ${pageTitle} - ${feedbackType}`);
}

/**
 * Track time on page
 * Automatically called before page unload
 */
function trackTimeOnPage(pageTitle, timeInSeconds) {
  gtag('event', 'page_engagement', {
    'event_category': 'engagement',
    'engagement_time_msec': timeInSeconds * 1000,
    'page_title': pageTitle
  });

  logDebug(`Tracked time on page: ${pageTitle} - ${timeInSeconds}s`);
}

/**
 * Track tutorial progress
 * Call this when user completes tutorial steps
 */
function trackTutorialProgress(tutorialName, stepNumber, totalSteps) {
  const percentageComplete = (stepNumber / totalSteps) * 100;

  gtag('event', 'tutorial_progress', {
    'event_category': 'tutorial',
    'tutorial_name': tutorialName,
    'step_number': stepNumber,
    'total_steps': totalSteps,
    'percentage_complete': Math.round(percentageComplete)
  });

  logDebug(`Tracked tutorial: ${tutorialName} - Step ${stepNumber}/${totalSteps}`);
}

/**
 * Track tutorial completion
 * Call this when user finishes a tutorial
 */
function trackTutorialCompletion(tutorialName, timeInSeconds) {
  gtag('event', 'tutorial_complete', {
    'event_category': 'tutorial',
    'event_label': tutorialName,
    'completion_time_seconds': timeInSeconds
  });

  logDebug(`Tracked tutorial completion: ${tutorialName} (${timeInSeconds}s)`);
}

/**
 * Track code sample execution
 * Call this when user runs code sample
 */
function trackCodeExecution(language, success) {
  gtag('event', 'code_execute', {
    'event_category': 'engagement',
    'code_language': language,
    'execution_success': success
  });

  logDebug(`Tracked code execution: ${language} - ${success ? 'Success' : 'Failed'}`);
}

/**
 * Track API documentation access patterns
 */
function trackAPIAccess(endpointPath, method = 'GET') {
  gtag('event', 'api_reference_view', {
    'event_category': 'api',
    'endpoint_path': endpointPath,
    'http_method': method
  });

  logDebug(`Tracked API access: ${method} ${endpointPath}`);
}

/**
 * Track documentation version access
 */
function trackVersionAccess(versionNumber) {
  gtag('event', 'view_version', {
    'event_category': 'version',
    'version_number': versionNumber
  });

  logDebug(`Tracked version access: ${versionNumber}`);
}

/**
 * Track language/locale selection
 */
function trackLanguageSelection(language) {
  gtag('event', 'language_selected', {
    'event_category': 'localization',
    'language': language
  });

  logDebug(`Tracked language: ${language}`);
}

/**
 * Track page errors
 * Call this when user encounters an error
 */
function trackPageError(errorMessage, errorType = 'unknown') {
  gtag('event', 'documentation_error', {
    'event_category': 'error',
    'error_message': errorMessage,
    'error_type': errorType
  });

  logDebug(`Tracked error: ${errorMessage}`);
}

/**
 * Track broken links
 * Call this when user finds a broken link
 */
function trackBrokenLink(brokenUrl, referrerUrl) {
  gtag('event', 'broken_link', {
    'event_category': 'error',
    'broken_url': brokenUrl,
    'referrer_url': referrerUrl
  });

  logDebug(`Tracked broken link: ${brokenUrl}`);
}

/**
 * Track feature flags/experiments
 */
function trackExperiment(experimentName, variant) {
  gtag('event', 'experiment_view', {
    'event_category': 'experiment',
    'experiment_id': experimentName,
    'variant': variant
  });

  logDebug(`Tracked experiment: ${experimentName} - ${variant}`);
}

/**
 * Setup automatic event listeners
 * Call this on page load to enable automatic tracking
 */
function setupAutomaticTracking() {
  // Track code copy buttons
  document.addEventListener('copy', (e) => {
    const selection = window.getSelection().toString();
    if (selection.length > 0) {
      const codeBlock = e.target.closest('pre');
      const language = codeBlock?.className?.match(/language-(\w+)/)?.[1] || 'unknown';
      trackCodeCopy(language, selection.length);
    }
  });

  // Track external links
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (link && link.href.startsWith('http') && !link.href.includes(window.location.hostname)) {
      trackLinkClick(link.href, link.textContent);
    }
  });

  // Track helpfulness button clicks
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('helpful-button')) {
      const helpful = e.target.dataset.helpful === 'true';
      const pageTitle = document.title;
      trackHelpfulness(pageTitle, helpful);
    }
  });

  // Track time on page
  let timeOnPageStart = Date.now();
  window.addEventListener('beforeunload', () => {
    const timeInSeconds = Math.round((Date.now() - timeOnPageStart) / 1000);
    const pageTitle = document.title;
    trackTimeOnPage(pageTitle, timeInSeconds);
  });

  logDebug('Automatic tracking enabled');
}

/**
 * Track scroll depth
 * Track how far down the page user scrolls
 */
function trackScrollDepth() {
  let maxScroll = 0;

  window.addEventListener('scroll', () => {
    const scrollPercent = Math.round(
      (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
    );

    if (scrollPercent > maxScroll) {
      maxScroll = scrollPercent;

      // Report at 25%, 50%, 75%, 100%
      if ([25, 50, 75, 100].includes(scrollPercent)) {
        gtag('event', 'scroll_depth', {
          'event_category': 'engagement',
          'scroll_percentage': scrollPercent
        });

        logDebug(`Tracked scroll depth: ${scrollPercent}%`);
      }
    }
  });
}

/**
 * Debug logging helper
 */
function logDebug(message) {
  if (process.env.DEBUG_ANALYTICS === 'true') {
    console.log(`[Analytics] ${message}`);
  }
}

/**
 * Export for use in other modules
 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initializeAnalytics,
    trackPageView,
    trackSearch,
    trackSearchResultClick,
    trackCodeCopy,
    trackLinkClick,
    trackHelpfulness,
    trackDetailedFeedback,
    trackTimeOnPage,
    trackTutorialProgress,
    trackTutorialCompletion,
    trackCodeExecution,
    trackAPIAccess,
    trackVersionAccess,
    trackLanguageSelection,
    trackPageError,
    trackBrokenLink,
    trackExperiment,
    setupAutomaticTracking,
    trackScrollDepth
  };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  initializeAnalytics();
  setupAutomaticTracking();
  trackScrollDepth();
});
