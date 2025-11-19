/**
 * Lab Results Display Component
 * React component for displaying patient lab results
 */

import React, { useState, useEffect } from 'react';

const LabResultsDisplay = ({ patientId, fhirClient }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchLabResults();
  }, [patientId]);

  const fetchLabResults = async () => {
    try {
      setLoading(true);
      const observations = await fhirClient.search('Observation', {
        patient: patientId,
        category: 'laboratory',
        _sort: '-date',
        _count: 50
      });

      const formattedResults = observations.entry.map(entry => ({
        id: entry.resource.id,
        date: entry.resource.effectiveDateTime,
        name: entry.resource.code.text || entry.resource.code.coding[0].display,
        value: formatValue(entry.resource),
        unit: entry.resource.valueQuantity?.unit,
        interpretation: entry.resource.interpretation?.[0]?.coding?.[0]?.code,
        referenceRange: entry.resource.referenceRange?.[0]?.text,
        status: entry.resource.status
      }));

      setResults(formattedResults);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const formatValue = (observation) => {
    if (observation.valueQuantity) {
      return observation.valueQuantity.value;
    } else if (observation.valueString) {
      return observation.valueString;
    } else if (observation.valueCodeableConcept) {
      return observation.valueCodeableConcept.text;
    }
    return 'N/A';
  };

  const getInterpretationBadge = (interpretation) => {
    const badges = {
      'H': <span className="badge badge-danger">High</span>,
      'L': <span className="badge badge-warning">Low</span>,
      'N': <span className="badge badge-success">Normal</span>,
      'A': <span className="badge badge-warning">Abnormal</span>
    };
    return badges[interpretation] || null;
  };

  const filteredResults = results.filter(result => {
    if (filter === 'all') return true;
    if (filter === 'abnormal') return result.interpretation !== 'N';
    return result.interpretation === filter;
  });

  if (loading) return <div className="spinner">Loading...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div className="lab-results-container">
      <div className="lab-results-header">
        <h2>Laboratory Results</h2>
        <div className="filter-buttons">
          <button onClick={() => setFilter('all')} className={filter === 'all' ? 'active' : ''}>
            All
          </button>
          <button onClick={() => setFilter('abnormal')} className={filter === 'abnormal' ? 'active' : ''}>
            Abnormal
          </button>
          <button onClick={() => setFilter('H')} className={filter === 'H' ? 'active' : ''}>
            High
          </button>
          <button onClick={() => setFilter('L')} className={filter === 'L' ? 'active' : ''}>
            Low
          </button>
        </div>
      </div>

      <table className="lab-results-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Test</th>
            <th>Result</th>
            <th>Reference Range</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {filteredResults.map(result => (
            <tr key={result.id} className={result.interpretation !== 'N' ? 'abnormal-row' : ''}>
              <td>{new Date(result.date).toLocaleDateString()}</td>
              <td>{result.name}</td>
              <td>
                {result.value} {result.unit}
                {getInterpretationBadge(result.interpretation)}
              </td>
              <td>{result.referenceRange || 'N/A'}</td>
              <td><span className="status-badge">{result.status}</span></td>
            </tr>
          ))}
        </tbody>
      </table>

      {filteredResults.length === 0 && (
        <div className="no-results">No lab results found.</div>
      )}
    </div>
  );
};

export default LabResultsDisplay;
