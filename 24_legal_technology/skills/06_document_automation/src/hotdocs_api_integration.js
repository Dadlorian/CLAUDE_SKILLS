/**
 * HotDocs API Integration Example
 * Demonstrates integration with HotDocs cloud services
 */

const https = require('https');
const querystring = require('querystring');

class HotDocsAPIClient {
  constructor(apiKey, serverUrl = 'https://api.hotdocs.com') {
    this.apiKey = apiKey;
    this.serverUrl = serverUrl;
  }

  /**
   * Generate a document from a template
   */
  generateDocument(templateId, answers, outputFormat = 'pdf') {
    const data = JSON.stringify({
      templateId: templateId,
      answers: answers,
      outputFormat: outputFormat
    });

    const options = {
      hostname: 'api.hotdocs.com',
      port: 443,
      path: '/v1/templates/' + templateId + '/documents',
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + this.apiKey,
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    return new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let responseData = '';

        res.on('data', (chunk) => {
          responseData += chunk;
        });

        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(responseData));
          } else {
            reject(new Error('HotDocs API error: ' + res.statusCode));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.write(data);
      req.end();
    });
  }

  /**
   * Get template information
   */
  getTemplate(templateId) {
    const options = {
      hostname: 'api.hotdocs.com',
      path: '/v1/templates/' + templateId,
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + this.apiKey
      }
    };

    return this._makeRequest(options);
  }

  /**
   * Create a document with assembly interview
   */
  startInterview(templateId, interview = {}) {
    const data = JSON.stringify({
      templateId: templateId,
      interviewFormat: 'web',
      ...interview
    });

    const options = {
      hostname: 'api.hotdocs.com',
      path: '/v1/interviews',
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + this.apiKey,
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    return this._makeRequest(options, data);
  }

  /**
   * Get interview status and results
   */
  getInterviewStatus(interviewId) {
    const options = {
      hostname: 'api.hotdocs.com',
      path: '/v1/interviews/' + interviewId,
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + this.apiKey
      }
    };

    return this._makeRequest(options);
  }

  /**
   * List available templates
   */
  listTemplates() {
    const options = {
      hostname: 'api.hotdocs.com',
      path: '/v1/templates',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + this.apiKey
      }
    };

    return this._makeRequest(options);
  }

  /**
   * Internal method to make HTTP requests
   */
  _makeRequest(options, data = null) {
    return new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let responseData = '';

        res.on('data', (chunk) => {
          responseData += chunk;
        });

        res.on('end', () => {
          try {
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(JSON.parse(responseData));
            } else {
              reject(new Error('HotDocs API error: ' + res.statusCode + ' - ' + responseData));
            }
          } catch (e) {
            reject(e);
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      if (data) {
        req.write(data);
      }

      req.end();
    });
  }
}

/**
 * Example usage
 */
async function exampleUsage() {
  const apiKey = 'YOUR_HOTDOCS_API_KEY';
  const client = new HotDocsAPIClient(apiKey);

  try {
    // Get available templates
    const templates = await client.listTemplates();
    console.log('Available templates:', templates);

    // Prepare answers for document generation
    const answers = {
      'ClientName': 'John Smith',
      'ClientAddress': '123 Main Street, New York, NY 10001',
      'EngagementDate': '2024-01-15',
      'HourlyRate': 350,
      'RetainerAmount': 5000,
      'IsContingency': false,
      'Services': [
        'Contract Review',
        'Legal Advice',
        'Document Preparation'
      ]
    };

    // Generate document
    const result = await client.generateDocument(
      'engagement-letter-template',
      answers,
      'pdf'
    );

    console.log('Document generated:', result);

    // Alternative: Start an interactive interview
    const interview = await client.startInterview('engagement-letter-template');
    console.log('Interview started:', interview);

    // Check interview status
    const status = await client.getInterviewStatus(interview.interviewId);
    console.log('Interview status:', status);

  } catch (error) {
    console.error('Error:', error);
  }
}

// Export for use in other modules
module.exports = HotDocsAPIClient;
