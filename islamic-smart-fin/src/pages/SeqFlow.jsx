import React, { useState } from 'react';
import './Page.css';
import SmartFlow from '../components/Challenge_4/Agents/SmartFlow';

function SeqFlow({ isCompany }) {
  const [country, setCountry] = useState('');
  const [started, setStarted] = useState(false);

  function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (file) {
      console.log("CSV uploaded:", file.name);
    }
  }

  return (
    <div className="seqflow-container">
      {!started ? (
        <>
          <h3 className='titles'>Inputs about Entreprise and Project</h3>
          <div className="grid">
            {/* LEFT PANEL */}
            <div className="left-panel">
              <h3 className='sub_titles'>Choose Your Country</h3>
              <p className='major-text'>
                The result will be adapted to the regulations of your country
              </p>

              <select
                className="dropdown"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              >
                <option value="">Not Selected</option>
                <option value="DZ">Algeria</option>
                <option value="SA">Saudi Arabia</option>
                <option value="AE">UAE</option>
                <option value="MY">Malaysia</option>
              </select>

              <h3 className='sub_titles upload-heading'>
                Upload 3–Year Balance Sheet & Income CSV of the Entreprise
              </h3>
              <p className="major-text">
                Please upload a CSV file that contains the company's balance sheet and income data for 3 consecutive years.
                <br /><br />
                Required columns: <br />
                <span>
                  year, total_assets, non_current_assets, intangible_assets, tangible_assets, financial_assets, current_assets, stocks, receivables, cash, equity, issued_capital, retained_earnings, net_income, long_term_debt, medium_term_debt, short_term_debt, supplier_debt, tax_liabilities, other_liabilities, total_liabilities, revenue
                </span>
              </p>

              <label className="upload-btn">
                <input type="file" accept=".csv" onChange={handleCSVUpload} hidden />
                <svg xmlns="http://www.w3.org/2000/svg" className="upload-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12V4m0 0L8 8m4-4l4 4" />
                </svg>
                Upload CSV
              </label>
            </div>

            {/* RIGHT PANEL */}
            <div className="right-panel">
              <h3 className='sub_titles'>Describe the investment project</h3>
              <p className='major-text'>
                Explain the goal, cost structure, expected cash flows, delivery timeline, and any other key details.
              </p>
              <textarea
                placeholder="Add project description here"
                className="text-area"
              />
            </div>
          </div>

          <div className="btn_container">
            <button className="submit-button full-width-btn" onClick={() => setStarted(true)}>
              Start the Flow
            </button>
          </div>
        </>
      ) : (
        <SmartFlow />
      )}
    </div>
  );
}

export default SeqFlow;
