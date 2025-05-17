import React from 'react';
import '../../../pages/Page.css';
import ReactMarkdown from 'react-markdown';

function Agent5({ data }) {
  if (!data) return <p>Loading output for Agent 5...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Accounting Agent</h3>
          <p className="sub-title bold">Journal Entries & Financial Breakdown</p>

          <p className="major-text">
            <strong>Status:</strong> {data.status} <br />
            <strong>Contract Type:</strong> {data.contract_type}
          </p>

          <div className="text-area major-text markdown-output">
            <ReactMarkdown>{data.content}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Agent5;