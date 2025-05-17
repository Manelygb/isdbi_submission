import React from 'react';
import '../../../pages/Page.css';

function Agent6({ data }) {
  if (!data) return <p>Loading output for Agent 6...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Shariah Compliance Validator</h3>
          <p className="sub-title bold">Compliance Review</p>

          <p className="major-text">
            <strong>Status:</strong> {data.status} <br />
            <strong>Overall:</strong> {data.overall_status}
          </p>

          <p className="text-area major-text">
            <strong>Message:</strong> {data.message}
          </p>
        </div>
      </div>
    </div>
  );
}

export default Agent6;