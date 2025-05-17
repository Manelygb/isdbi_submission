import React, { useState } from 'react';
import './Page.css';
import axios from 'axios';

function ReverseAudit() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
     const response = await axios.post('http://localhost:8000/api/challenge2/analyze', {

        input: input
      });
      setResult(response.data.output);  
    } catch (err) {
      alert(' API error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className='title_skltn'>
        <h2 className='titles'>Reverse Audit</h2>
        <p className="description">For identifying the applicable FAS from reverse or out-of-context journal entries.</p>
      </div>
      <div className='line_p'></div>

      <div className="grid">
        <div className="left-panel">
          <h3 className='sub_titles'>Journal Entry Context</h3>
          <p className='major-text'>
            Provide the context and financial journal entry — such as equity buyouts, revenue reversals, or stake transfers.
          </p>
          <textarea
            placeholder="Add scenario here"
            className="text-area h-350"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <div className='btn_container'>
            <button
              className="submit-button button-34"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Generate Journal Entry"}
            </button>
          </div>
        </div>

        <div className="right-panel major-text">
          <h3 className='sub_titles'>FAS Detection Result</h3>
          {result ? (
            <>
              <div className="result-box">
                <strong>Response:</strong>
                <div className='text-area-mini'>
                  {result.split('\n').map((line, idx) => (
                    <p key={idx}>{line}</p>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className='text-area-mini'>
              <p>The system will analyze the entry and return:</p>
             
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ReverseAudit;
