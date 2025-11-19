/**
 * Construction Progress Dashboard
 */
import React from 'react';

function ProgressDashboard({ project }) {
  const calculateProgress = () => {
    const total = project.tasks.length;
    const completed = project.tasks.filter(t => t.status === 'complete').length;
    return (completed / total) * 100;
  };
  
  return (
    <div className="dashboard">
      <h2>{project.name}</h2>
      
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${calculateProgress()}%` }}
        />
      </div>
      
      <div className="metrics">
        <div className="metric">
          <h3>Budget</h3>
          <p>${project.spent.toLocaleString()} / ${project.budget.toLocaleString()}</p>
        </div>
        
        <div className="metric">
          <h3>Timeline</h3>
          <p>{project.days_elapsed} / {project.days_total} days</p>
        </div>
        
        <div className="metric">
          <h3>Tasks</h3>
          <p>{project.tasks.filter(t => t.status === 'complete').length} / {project.tasks.length}</p>
        </div>
      </div>
    </div>
  );
}

export default ProgressDashboard;
