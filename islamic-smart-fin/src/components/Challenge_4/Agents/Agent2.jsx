import React from 'react';
import '../../../pages/Page.css';
import ReactMarkdown from 'react-markdown';

function Agent2({ data }) {
  if (!data) return <p>Loading output for Agent 2...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Project Evaluation Agent</h3>
          <p className="sub-title bold">Viability & Risk Analysis</p>

          <p className="major-text">
            <strong>Viable:</strong> {data.is_viable ? '✅ Yes' : '❌ No'}
          </p>
          <p className="major-text">
            <strong>Decision:</strong> {data.decision}
          </p>
          <p className="major-text">
            <strong>Confidence:</strong> {data.confidence}
          </p>

          <div className="text-area major-text markdown-output">
            <h4>Justification</h4>
            <ReactMarkdown>{data.justification}</ReactMarkdown>
          </div>

          <div className="text-area major-text markdown-output">
            <h4>Identified Risks</h4>
            <ul>
              {data.identified_risks.map((risk, i) => (
                <li key={i}>{risk}</li>
              ))}
            </ul>
          </div>

          <div className="text-area major-text markdown-output">
            <h4>Preliminary Shariah Fit</h4>
            <ReactMarkdown>{data.shariah_preliminary_fit}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Agent2;