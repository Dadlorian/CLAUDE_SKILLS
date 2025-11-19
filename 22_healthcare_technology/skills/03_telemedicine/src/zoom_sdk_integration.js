/**
 * Zoom Healthcare SDK Integration
 * Production-ready implementation for creating and managing Zoom telehealth sessions
 */

const axios = require('axios');
const jwt = require('jsonwebtoken');

class ZoomHealthcareService {
  constructor() {
    this.accountId = process.env.ZOOM_ACCOUNT_ID;
    this.clientId = process.env.ZOOM_CLIENT_ID;
    this.clientSecret = process.env.ZOOM_CLIENT_SECRET;
    this.accessToken = null;
    this.tokenExpiry = null;
  }

  /**
   * Get OAuth access token for Zoom API
   */
  async getAccessToken() {
    if (this.accessToken && this.tokenExpiry > Date.now()) {
      return this.accessToken;
    }

    const credentials = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString('base64');

    try {
      const response = await axios.post(
        `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${this.accountId}`,
        {},
        {
          headers: {
            'Authorization': `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      this.accessToken = response.data.access_token;
      this.tokenExpiry = Date.now() + (response.data.expires_in * 1000) - 60000; // Refresh 1 min early

      return this.accessToken;
    } catch (error) {
      console.error('Error getting Zoom access token:', error.response?.data || error.message);
      throw new Error('Failed to authenticate with Zoom');
    }
  }

  /**
   * Create HIPAA-compliant Zoom meeting for telehealth
   */
  async createTelehealthMeeting({
    providerEmail,
    patientName,
    scheduledTime,
    duration = 30,
    appointmentId
  }) {
    const accessToken = await this.getAccessToken();

    const meetingData = {
      topic: `Telehealth Visit - ${patientName}`,
      type: 2, // Scheduled meeting
      start_time: scheduledTime,
      duration: duration,
      timezone: 'America/New_York',
      agenda: `Telehealth appointment #${appointmentId}`,
      settings: {
        host_video: true,
        participant_video: true,
        join_before_host: false, // REQUIRED for security
        mute_upon_entry: true,
        watermark: true,
        use_pmi: false,
        approval_type: 0,
        audio: 'both',
        auto_recording: 'cloud',
        waiting_room: true, // REQUIRED for HIPAA
        meeting_authentication: true,
        encryption_type: 'enhanced_encryption',
        alternative_hosts_email_notification: true
      }
    };

    try {
      const response = await axios.post(
        `https://api.zoom.us/v2/users/${providerEmail}/meetings`,
        meetingData,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return {
        meetingId: response.data.id,
        joinUrl: response.data.join_url,
        startUrl: response.data.start_url,
        password: response.data.password,
        createdAt: response.data.created_at
      };
    } catch (error) {
      console.error('Error creating Zoom meeting:', error.response?.data || error.message);
      throw new Error('Failed to create telehealth meeting');
    }
  }

  /**
   * Update existing meeting
   */
  async updateMeeting(meetingId, updates) {
    const accessToken = await this.getAccessToken();

    try {
      const response = await axios.patch(
        `https://api.zoom.us/v2/meetings/${meetingId}`,
        updates,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error updating Zoom meeting:', error.response?.data || error.message);
      throw new Error('Failed to update meeting');
    }
  }

  /**
   * Delete/cancel meeting
   */
  async deleteMeeting(meetingId) {
    const accessToken = await this.getAccessToken();

    try {
      await axios.delete(
        `https://api.zoom.us/v2/meetings/${meetingId}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );

      return { success: true };
    } catch (error) {
      console.error('Error deleting Zoom meeting:', error.response?.data || error.message);
      throw new Error('Failed to delete meeting');
    }
  }

  /**
   * Get meeting details
   */
  async getMeeting(meetingId) {
    const accessToken = await this.getAccessToken();

    try {
      const response = await axios.get(
        `https://api.zoom.us/v2/meetings/${meetingId}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error getting Zoom meeting:', error.response?.data || error.message);
      throw new Error('Failed to retrieve meeting');
    }
  }

  /**
   * List cloud recordings for a user
   */
  async getCloudRecordings(userId, fromDate, toDate) {
    const accessToken = await this.getAccessToken();

    try {
      const response = await axios.get(
        `https://api.zoom.us/v2/users/${userId}/recordings`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          },
          params: {
            from: fromDate, // YYYY-MM-DD
            to: toDate
          }
        }
      );

      return response.data.meetings;
    } catch (error) {
      console.error('Error getting recordings:', error.response?.data || error.message);
      throw new Error('Failed to retrieve recordings');
    }
  }
}

module.exports = ZoomHealthcareService;
