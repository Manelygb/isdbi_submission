import React from 'react';
import '../../../pages/Page.css';
import ReactMarkdown from 'react-markdown';

function Agent3({ data }) {
  if (!data) return <p>Loading output for Agent 3...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Islamic Contract Selector Agent</h3>
          <p className="sub-title bold">Contract Recommendation</p>

          <p className="major-text">
            <strong>Primary Contract:</strong> {data.primary_contract_type}
          </p>

          <div className="text-area major-text markdown-output">
            <h4>Probabilities</h4>
            <ul>
              {Object.entries(data.contract_probabilities).map(([k, v]) => (
                <li key={k}><strong>{k}</strong>: {v}</li>
              ))}
            </ul>

            <h4>Relevant AAOIFI Standards</h4>
            <ul>
              {data.relevant_aaoifi_fas.map((std, i) => (
                <li key={i}>{std}</li>
              ))}
            </ul>

            <h4>Justification</h4>
            <ReactMarkdown>{data.justification}</ReactMarkdown>

            <h4>Required Parameters</h4>
            <ul>
              {data.key_parameters_required.map((param, i) => (
                <li key={i}>{param}</li>
              ))}
            </ul>

            <h4>Supporting Contracts</h4>
            <ul>
              {data.supporting_contracts.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Agent3;