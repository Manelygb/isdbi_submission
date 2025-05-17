import React from 'react';
import '../../../pages/Page.css';
import ReactMarkdown from 'react-markdown';

function Agent7({ data }) {
  if (!data) return <p>Loading output for Agent 7...</p>;

  return (
    <div className="agent-output-box">
      <div className="grid">
        <div className="left-panel">
          <h3 className="titles">Country Law Validator</h3>
          <p className="sub-title bold">Legal Compatibility Review</p>

          <p className="major-text">
            <strong>Status:</strong> {data.status} <br />
            <strong>Compliant:</strong> {data.is_compliant ? '✅ Yes' : '❌ No'}
          </p>

          <div className="text-area major-text markdown-output">
            <h4>Country Profile</h4>
            <ReactMarkdown>{data.country_profile}</ReactMarkdown>

            <h4>Notes / Observations</h4>
            <ul>
              {data.notes_or_observations.map((note, i) => (
                <li key={i}>{note}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Agent7;