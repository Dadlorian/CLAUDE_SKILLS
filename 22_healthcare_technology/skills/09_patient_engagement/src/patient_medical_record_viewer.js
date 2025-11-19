/**
 * Medical Record Viewer Component
 * Displays patient clinical information in organized, accessible format
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MedicalRecordViewer = ({ patientId, token }) => {
  const [records, setRecords] = useState({
    problems: [],
    medications: [],
    allergies: [],
    labs: [],
    vitals: []
  });
  const [activeTab, setActiveTab] = useState('problems');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMedicalRecords();
  }, [patientId]);

  const fetchMedicalRecords = async () => {
    try {
      const response = await axios.get(
        `/api/patients/${patientId}/records`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRecords(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load medical records');
      setLoading(false);
    }
  };

  if (loading) return <div>Loading records...</div>;

  const tabs = ['problems', 'medications', 'allergies', 'labs', 'vitals'];

  return (
    <div className="medical-records">
      <h1>Your Medical Records</h1>

      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="records-content">
        {activeTab === 'problems' && renderProblems(records.problems)}
        {activeTab === 'medications' && renderMedications(records.medications)}
        {activeTab === 'allergies' && renderAllergies(records.allergies)}
        {activeTab === 'labs' && renderLabs(records.labs)}
        {activeTab === 'vitals' && renderVitals(records.vitals)}
      </div>

      <button className="download-button" onClick={downloadRecords}>
        Download My Records
      </button>
    </div>
  );
};

function renderProblems(problems) {
  return (
    <div className="problems-section">
      {problems.length === 0 ? <p>No problems recorded</p> : (
        <div className="problem-list">
          {problems.map(problem => (
            <div key={problem.id} className="problem-card">
              <h3>{problem.description}</h3>
              <p><strong>Code:</strong> {problem.code}</p>
              <p><strong>Status:</strong> {problem.status}</p>
              <p><strong>Since:</strong> {new Date(problem.onsetDate).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function renderMedications(medications) {
  return (
    <div className="medications-section">
      {medications.length === 0 ? <p>No medications recorded</p> : (
        <div className="medication-list">
          {medications.map(med => (
            <div key={med.id} className="medication-card">
              <h3>{med.drugName}</h3>
              <p><strong>Dose:</strong> {med.dose} {med.unit}</p>
              <p><strong>Frequency:</strong> {med.frequency}</p>
              <p><strong>Status:</strong> {med.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function renderAllergies(allergies) {
  return (
    <div className="allergies-section">
      {allergies.length === 0 ? <p>No allergies recorded</p> : (
        <div className="allergy-list">
          {allergies.map(allergy => (
            <div key={allergy.id} className="allergy-card">
              <h3>{allergy.substance}</h3>
              <p><strong>Reaction:</strong> {allergy.reaction}</p>
              <p><strong>Severity:</strong> {allergy.severity}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function renderLabs(labs) {
  return (
    <div className="labs-section">
      {labs.length === 0 ? <p>No lab results</p> : (
        <div className="labs-list">
          {labs.map(lab => (
            <div key={lab.id} className="lab-card">
              <h3>{lab.testName}</h3>
              <p><strong>Date:</strong> {new Date(lab.date).toLocaleDateString()}</p>
              <p><strong>Result:</strong> {lab.value} {lab.unit}</p>
              <p><strong>Reference Range:</strong> {lab.referenceRange}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function renderVitals(vitals) {
  return (
    <div className="vitals-section">
      {vitals.length === 0 ? <p>No vital signs recorded</p> : (
        <div className="vitals-grid">
          {vitals.map(vital => (
            <div key={vital.id} className="vital-card">
              <h3>{vital.name}</h3>
              <p className="vital-value">{vital.value}</p>
              <p>{vital.unit}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

async function downloadRecords() {
  const response = await axios.post(
    `/api/export/records`,
    { format: 'ccda' },
    { responseType: 'blob' }
  );

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `health-records-${new Date().toISOString().split('T')[0]}.xml`);
  document.body.appendChild(link);
  link.click();
}

export default MedicalRecordViewer;
