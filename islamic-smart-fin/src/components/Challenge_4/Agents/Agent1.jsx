import React from 'react';
import '../../../pages/Page.css';
import ReactMarkdown from 'react-markdown';

function Agent1({ data }) {
  if (!data) return <p>Loading output for Agent 1...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className='titles'>Enterprise Audit Agent</h3>
          <p className='sub-title bold'>Company Score & Financial Overview</p>
          <p className='major-text'>
            <strong>Company Score:</strong> {data.company_score}
          </p>

          <div className="text-area major-text markdown-output">
            <ReactMarkdown>{data.summary}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Agent1;
