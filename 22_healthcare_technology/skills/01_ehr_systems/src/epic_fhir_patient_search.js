/**
 * Epic FHIR Patient Search Example
 * Demonstrates searching for patients using Epic's FHIR R4 API
 */

const axios = require('axios');

class EpicFHIRClient {
  constructor(baseUrl, accessToken) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
    this.axios = axios.create({
      baseURL: baseUrl,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/fhir+json',
        'Content-Type': 'application/fhir+json'
      }
    });
  }

  /**
   * Search patients by name
   * @param {string} family - Family name (last name)
   * @param {string} given - Given name (first name)
   * @returns {Promise<Array>} Array of matching patients
   */
  async searchPatientsByName(family, given) {
    try {
      const params = {};
      if (family) params.family = family;
      if (given) params.given = given;

      const response = await this.axios.get('/Patient', { params });

      if (response.data.entry) {
        return response.data.entry.map(entry => this.formatPatient(entry.resource));
      }
      return [];
    } catch (error) {
      console.error('Error searching patients:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Search patient by identifier (MRN)
   * @param {string} identifier - Medical Record Number
   * @returns {Promise<Object|null>} Patient resource or null
   */
  async searchPatientByMRN(identifier) {
    try {
      const response = await this.axios.get('/Patient', {
        params: { identifier }
      });

      if (response.data.entry && response.data.entry.length > 0) {
        return this.formatPatient(response.data.entry[0].resource);
      }
      return null;
    } catch (error) {
      console.error('Error searching by MRN:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Get patient by ID
   * @param {string} id - FHIR patient ID
   * @returns {Promise<Object>} Patient resource
   */
  async getPatient(id) {
    try {
      const response = await this.axios.get(`/Patient/${id}`);
      return this.formatPatient(response.data);
    } catch (error) {
      console.error('Error getting patient:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Format patient resource for easy consumption
   */
  formatPatient(patient) {
    return {
      id: patient.id,
      mrn: patient.identifier?.find(id => id.type?.coding?.[0]?.code === 'MR')?.value,
      name: {
        full: patient.name?.[0] ? 
          `${patient.name[0].given?.join(' ')} ${patient.name[0].family}` : '',
        family: patient.name?.[0]?.family,
        given: patient.name?.[0]?.given?.join(' ')
      },
      birthDate: patient.birthDate,
      gender: patient.gender,
      phone: patient.telecom?.find(t => t.system === 'phone')?.value,
      email: patient.telecom?.find(t => t.system === 'email')?.value,
      address: patient.address?.[0] ? {
        line: patient.address[0].line?.join(', '),
        city: patient.address[0].city,
        state: patient.address[0].state,
        postalCode: patient.address[0].postalCode
      } : null
    };
  }
}

// Example usage
async function main() {
  const client = new EpicFHIRClient(
    'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4',
    process.env.EPIC_ACCESS_TOKEN
  );

  // Search by name
  const patients = await client.searchPatientsByName('Smith', 'John');
  console.log(`Found ${patients.length} patients`);
  patients.forEach(p => console.log(p.name.full));

  // Search by MRN
  const patient = await client.searchPatientByMRN('MRN123456');
  if (patient) {
    console.log('Patient found:', patient);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = EpicFHIRClient;
