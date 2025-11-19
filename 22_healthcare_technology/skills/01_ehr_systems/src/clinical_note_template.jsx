/**
 * Clinical Note Template Component
 * React component for clinical documentation
 */

import React, { useState } from 'react';

const ClinicalNoteTemplate = ({ patientId, encounterId, onSave }) => {
  const [note, setNote] = useState({
    chiefComplaint: '',
    historyPresentIllness: '',
    reviewOfSystems: {
      constitutional: false,
      heent: false,
      cardiovascular: false,
      respiratory: false,
      gastrointestinal: false
    },
    vitalSigns: {
      temperature: '',
      heartRate: '',
      bloodPressure: '',
      respiratoryRate: '',
      oxygenSaturation: ''
    },
    physicalExam: '',
    assessment: '',
    plan: ''
  });

  const handleChange = (field, value) => {
    setNote({ ...note, [field]: value });
  };

  const handleVitalChange = (vital, value) => {
    setNote({
      ...note,
      vitalSigns: { ...note.vitalSigns, [vital]: value }
    });
  };

  const handleROSChange = (system) => {
    setNote({
      ...note,
      reviewOfSystems: {
        ...note.reviewOfSystems,
        [system]: !note.reviewOfSystems[system]
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onSave(note);
  };

  return (
    <form className="clinical-note-form" onSubmit={handleSubmit}>
      <h2>SOAP Note</h2>

      {/* Subjective */}
      <section className="note-section">
        <h3>Subjective</h3>
        
        <div className="form-group">
          <label>Chief Complaint *</label>
          <input
            type="text"
            value={note.chiefComplaint}
            onChange={(e) => handleChange('chiefComplaint', e.target.value)}
            placeholder="Patient's primary concern"
            required
          />
        </div>

        <div className="form-group">
          <label>History of Present Illness *</label>
          <textarea
            value={note.historyPresentIllness}
            onChange={(e) => handleChange('historyPresentIllness', e.target.value)}
            placeholder="OLDCARTS: Onset, Location, Duration, Character, Aggravating factors, Relieving factors, Timing, Severity"
            rows="6"
            required
          />
        </div>

        <div className="form-group">
          <label>Review of Systems</label>
          <div className="checkbox-group">
            {Object.keys(note.reviewOfSystems).map(system => (
              <label key={system}>
                <input
                  type="checkbox"
                  checked={note.reviewOfSystems[system]}
                  onChange={() => handleROSChange(system)}
                />
                {system.charAt(0).toUpperCase() + system.slice(1)}
              </label>
            ))}
          </div>
        </div>
      </section>

      {/* Objective */}
      <section className="note-section">
        <h3>Objective</h3>

        <div className="vital-signs-grid">
          <div className="form-group">
            <label>Temperature (°F)</label>
            <input
              type="number"
              step="0.1"
              value={note.vitalSigns.temperature}
              onChange={(e) => handleVitalChange('temperature', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Heart Rate (bpm)</label>
            <input
              type="number"
              value={note.vitalSigns.heartRate}
              onChange={(e) => handleVitalChange('heartRate', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Blood Pressure</label>
            <input
              type="text"
              placeholder="120/80"
              value={note.vitalSigns.bloodPressure}
              onChange={(e) => handleVitalChange('bloodPressure', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Respiratory Rate</label>
            <input
              type="number"
              value={note.vitalSigns.respiratoryRate}
              onChange={(e) => handleVitalChange('respiratoryRate', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>O2 Saturation (%)</label>
            <input
              type="number"
              value={note.vitalSigns.oxygenSaturation}
              onChange={(e) => handleVitalChange('oxygenSaturation', e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Physical Examination *</label>
          <textarea
            value={note.physicalExam}
            onChange={(e) => handleChange('physicalExam', e.target.value)}
            placeholder="General appearance, HEENT, Cardiovascular, Respiratory, Abdomen, Extremities, Neurological"
            rows="8"
            required
          />
        </div>
      </section>

      {/* Assessment */}
      <section className="note-section">
        <h3>Assessment</h3>
        <div className="form-group">
          <label>Assessment/Diagnoses *</label>
          <textarea
            value={note.assessment}
            onChange={(e) => handleChange('assessment', e.target.value)}
            placeholder="Primary and differential diagnoses with ICD-10 codes"
            rows="4"
            required
          />
        </div>
      </section>

      {/* Plan */}
      <section className="note-section">
        <h3>Plan</h3>
        <div className="form-group">
          <label>Treatment Plan *</label>
          <textarea
            value={note.plan}
            onChange={(e) => handleChange('plan', e.target.value)}
            placeholder="Diagnostic studies, medications, procedures, referrals, patient education, follow-up"
            rows="6"
            required
          />
        </div>
      </section>

      <div className="form-actions">
        <button type="button" className="btn-secondary">Save as Draft</button>
        <button type="submit" className="btn-primary">Sign and Submit</button>
      </div>
    </form>
  );
};

export default ClinicalNoteTemplate;
