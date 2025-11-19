/**
 * Patient Engagement Analytics Dashboard
 * Displays engagement metrics and trends for healthcare organizations
 */

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PatientEngagementDashboard = () => {
  const [metrics, setMetrics] = useState({
    portalRegistration: [],
    activeUsers: 0,
    featureUtilization: [],
    adherenceByCondition: [],
    engagementTrend: []
  });
  const [dateRange, setDateRange] = useState('month');

  useEffect(() => {
    fetchMetrics();
  }, [dateRange]);

  const fetchMetrics = async () => {
    const response = await fetch(
      `/api/analytics/engagement?range=${dateRange}`
    );
    const data = await response.json();
    setMetrics(data);
  };

  return (
    <div className="engagement-dashboard">
      <h1>Patient Engagement Analytics</h1>

      <div className="controls">
        <select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
          <option value="week">Past Week</option>
          <option value="month">Past Month</option>
          <option value="quarter">Past Quarter</option>
          <option value="year">Past Year</option>
        </select>
      </div>

      <div className="kpi-cards">
        <KPICard
          title="Active Users"
          value={metrics.activeUsers}
          target={1000}
          trend={12}
        />
        <KPICard
          title="Portal Registration Rate"
          value="62%"
          target="70%"
          trend={5}
        />
        <KPICard
          title="Monthly Logins"
          value="2.8"
          unit="avg"
          trend={8}
        />
        <KPICard
          title="Feature Adoption"
          value="58%"
          target="75%"
          trend={3}
        />
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h2>Engagement Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics.engagementTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="activeUsers" stroke="#8884d8" />
              <Line type="monotone" dataKey="newLogins" stroke="#82ca9d" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h2>Feature Utilization</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.featureUtilization}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="feature" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="users" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h2>Medication Adherence by Condition</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.adherenceByCondition}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="condition" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="adherenceRate" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h2>Portal Registration Rate</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics.portalRegistration}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="registrationRate" stroke="#ffc658" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="detailed-metrics">
        <h2>Detailed Metrics by Department</h2>
        <DepartmentMetricsTable />
      </div>

      <div className="recommendations">
        <h2>Recommended Actions</h2>
        <RecommendationsList />
      </div>
    </div>
  );
};

const KPICard = ({ title, value, unit, target, trend }) => {
  const trendClass = trend >= 0 ? 'positive' : 'negative';

  return (
    <div className="kpi-card">
      <h3>{title}</h3>
      <div className="value">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
      {target && <div className="target">Target: {target}</div>}
      <div className={`trend ${trendClass}`}>
        {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
      </div>
    </div>
  );
};

const DepartmentMetricsTable = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchDepartmentMetrics();
  }, []);

  const fetchDepartmentMetrics = async () => {
    const response = await fetch('/api/analytics/departments');
    const result = await response.json();
    setData(result);
  };

  return (
    <table className="metrics-table">
      <thead>
        <tr>
          <th>Department</th>
          <th>Portal Registration</th>
          <th>Active Users</th>
          <th>Avg Session Length</th>
          <th>Feature Adoption</th>
          <th>Patient Satisfaction</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            <td>{row.department}</td>
            <td>{row.registration}%</td>
            <td>{row.activeUsers}</td>
            <td>{row.avgSession} min</td>
            <td>{row.adoption}%</td>
            <td>{row.satisfaction}/5</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

const RecommendationsList = () => {
  const recommendations = [
    {
      title: 'Increase Medication Adherence Education',
      priority: 'High',
      condition: 'Hypertension adherence at 72% (target 80%)'
    },
    {
      title: 'Promote Health Metrics Tracking Feature',
      priority: 'Medium',
      condition: 'Only 35% of patients using feature'
    },
    {
      title: 'Expand Mobile App Promotion',
      priority: 'High',
      condition: 'Web usage 3x higher than mobile'
    },
    {
      title: 'Develop Specialty-Specific Education',
      priority: 'Medium',
      condition: 'Cardiology education completion 20% below average'
    }
  ];

  return (
    <div className="recommendations-list">
      {recommendations.map((rec, i) => (
        <div key={i} className={`recommendation ${rec.priority.toLowerCase()}`}>
          <h4>{rec.title}</h4>
          <p className="condition">{rec.condition}</p>
          <span className={`priority ${rec.priority.toLowerCase()}`}>{rec.priority}</span>
        </div>
      ))}
    </div>
  );
};

export default PatientEngagementDashboard;
