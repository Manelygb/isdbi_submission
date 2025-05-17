// === Agent4.jsx ===
import React from 'react';
import '../../../pages/Page.css';
import ReactMarkdown from 'react-markdown';

function Agent4({ data }) {
  if (!data) return <p>Loading output for Agent 4...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Contract Drafting Agent</h3>
          <p className="sub-title bold">Formalized Contract Output</p>

          <p className="major-text">
            <strong>Type:</strong> {data.contract_type} <br />
            <strong>Status:</strong> {data.status}
          </p>

          <div className="text-area major-text markdown-output">
            <ReactMarkdown>{data.document_text_summary}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Agent4;
