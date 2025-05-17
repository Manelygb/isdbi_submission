import React from 'react';
import '../../../pages/Page.css';

function Agent8({ data }) {
  if (!data) return <p>Loading output for Agent 8...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Final Decision Agent</h3>
          <p className="sub-title bold">Integrated Final Recommendation</p>

          <p className="text-area major-text">
            <strong>Status:</strong> {data.status} <br />
            <strong>Decision:</strong> {data.recommendation || 'Pending'} <br />
            <strong>Message:</strong> {data.summary || 'Awaiting final judgment from all prior agents.'}
          </p>
        </div>
      </div>
    </div>
  );
}

export default Agent8;
