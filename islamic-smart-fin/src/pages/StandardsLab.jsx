import React, { useState } from 'react';
import './Page.css';
import axios from 'axios';
import Step1 from '../components/Challenge_3/Step1';
import Step2 from '../components/Challenge_3/Step2';
import Step3 from '../components/Challenge_3/Step3';

import spark from '../assets/spark.svg';

function StandardsLab() {
  const [scenario, setScenario] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
   
  };

  return (
    <div className="page-container">
      <div className='title_skltn'>
        <h2 className='titles'>Standards Lab</h2>
        <p className="description">For reviewing and enhancing AAOIFI standards using multi-agent AI collaboration.</p>
      </div>
      <div className='line_p'></div>

      <div className="grid">
        <div className="left-panel">
          <h3 className='sub_titles'>Standard Selection & Focus</h3>
          <p className='major-text'>
          Choose an AAOIFI standard (e.g., FAS 10 – Ijarah) and optionally describe the focus area or known ambiguity you’d like the agents to address.
          </p>
          <textarea
            placeholder="Add scenario here"
            className="text-area"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          />
          <div className='btn_container'>
            <button
              className="submit-button button-34"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "Processing..." : "Analyze & Enhance Standard"}
            </button>
          </div>
        </div>
      </div>
      
      <Step1/>
      <Step2/>
      <Step3/>


        <div className="left-panel" style={{ padding: '20px'}}>
        <div className="header-section" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <h3 className='sub_titles' style={{ fontSize: '1.5rem' }}>AI Final Verdict</h3>
            <img 
                src={spark} 
                alt="AI Verdict" 
                className="ai-image" 
                style={{ width: '40px', height: '40px', objectFit: 'contain' }}
            />
        </div>

        <p className='major-text' style={{ fontSize: '1.1rem' }}>
            Choose an AAOIFI standard (e.g., FAS 10 – Ijarah) and optionally describe the focus area or known ambiguity you’d like the agents to address.
        </p>

        <div className="text-area-result major-text" style={{ fontSize: '1rem', marginTop: '15px' }}>
            Using the structured contract scenario, our AI will:
            <ul style={{ paddingLeft: '20px', listStyleType: 'disc' }}>
                <li style={{ marginBottom: '10px' }}>Identify the correct Islamic accounting treatment based on AAOIFI Financial Accounting Standards (FAS).</li>
                <li style={{ marginBottom: '10px' }}>Generate the initial and subsequent journal entries (Dr/Cr) required by the selected contract type.</li>
                <li style={{ marginBottom: '10px' }}>Align with specific FAS standards like FAS 7 (Murabaha), FAS 10 (Ijarah), FAS 28 (Salam), or FAS 32 (Istisna’a).</li>
                <li style={{ marginBottom: '10px' }}>Ensure all entries are realistic, standard-compliant, and ready for financial reporting or audit documentation.</li>
            </ul>
        </div>
    </div>

     

    </div>
  );
}

export default StandardsLab;
