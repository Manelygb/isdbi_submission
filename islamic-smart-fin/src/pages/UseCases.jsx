import React, { useState } from 'react';
import './Page.css';
import axios from 'axios';
import PurpleCard from '../components/Challenge_4/PurpleCard';
import ReactMarkdown from 'react-markdown';


function UseCases() {
  const [scenario, setScenario] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!scenario.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/usecase/analyze', {
      scenario: scenario
    });
      setResponse(res.data);
    } catch (err) {
      alert(' Error connecting to backend API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">

      <div className='title_skltn'>
        <h2 className='titles'>Use Cases</h2>
        <p className="description">For guided FAS-based accounting scenario solving.</p>
      </div>
      <div className='line_p'></div>

      <div className="grid">
        {/* LEFT PANEL */}
        <div className="left-panel">
          <h3 className='sub_titles'>Contract Scenario</h3>
          <p className='major-text'>
            Provide the details of a financial transaction or Islamic finance scenario — such as Ijarah, Murabaha, or Istisna’a — including asset costs, rental terms, residual values, and contract details.
          </p>
          <textarea
            placeholder="Add scenario here"
            className="text-area h-350"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          />
          <div className='btn_container'>
            <button
              className="submit-button button-34"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "Processing..." : "Generate Journal Entry"}
            </button>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="right-panel">
          <h3 className='sub_titles'>Journal Entry</h3>
          <div className='text-area h-500 major-text scroll-box'>
          {response ? (
            <>
              <p><strong>Classification:</strong> {response.classification}</p>
              <p><strong>Justification:</strong> {response.justification}</p>
              <div className="markdown-output">
                <ReactMarkdown>{response.journal_entry}</ReactMarkdown>
              </div>
            </>
          ) : (
            <>
              <p>The system will apply the appropriate AAOIFI FAS (e.g., FAS 10 for Ijarah MBT) and return:</p>
              <ul>
                <li>Calculations: ROU asset, deferred cost, amortisable amount</li>
                <li>Initial journal entries (Dr/Cr format)</li>
                <li>Amortization schedule if applicable</li>
              </ul>
            </>
          )}
        </div>

        </div>
     
      </div>
    </div>
  );
}

export default UseCases;
