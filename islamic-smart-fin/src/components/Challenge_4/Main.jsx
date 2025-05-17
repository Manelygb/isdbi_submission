import React from 'react'
import './Page.css';


function Main() {
    function handleCSVUpload(event) {
        const file = event.target.files[0];
        if (file) {
          console.log("CSV uploaded:", file.name);
         
        }
      }

      
  return (
    <div className="page-container">
    <div className='title_skltn'>
    <h2 className='titles'>Smart Advisors</h2>
    <p className="description">Audit companies/projects, recommend contracts with their  journal entries.</p>
    </div>
    <div className='line_p'></div>
    <p className='major-text'>
    You should follow this flow step by step in order to get a complete audit for your project.
    </p>
   
    <div>
            <h3 className='titles'>1 - Upload Balance Sheet & Analyze Enterprise</h3>
            <div className="grid">
            <div className="left-panel">
                <h3 className='sub_titles'>Upload 3-Year Balance Sheet & Income CSV</h3>
                <p className='major-text'>
                Please upload a CSV file that contains the company's balance sheet and income data for 3 consecutive years. The file must include the following columns:
                year, total_assets, non_current_assets, intangible_assets, tangible_assets, financial_assets,
                current_assets, stocks, receivables, cash, equity, issued_capital, retained_earnings, net_income,
                long_term_debt, medium_term_debt, short_term_debt, supplier_debt, tax_liabilities, other_liabilities,
                total_liabilities, revenue        </p>
               
                <label className="upload-btn">
                <input type="file" accept=".csv" onChange={handleCSVUpload} hidden />
                <svg xmlns="http://www.w3.org/2000/svg" className="upload-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12V4m0 0L8 8m4-4l4 4" />
                </svg>
                Upload CSV
                </label>


                <div className='btn_container'>
                <button className="submit-button button-34">Run Entreprise Analysis</button>
                </div>
            </div>
            <div className="right-panel">
                <h3 className='sub_titles'>Journal Entry</h3>
                <div className='text-area major-text'> 
                    <p>Once you upload the company's 3-year balance sheet and income data, our AI will:</p>
                    <ul>
                    <li>Calculate key financial ratios (liquidity, solvency, profitability, growth, and treasury).</li>
                    <li>Interpret each ratio in plain language, identifying financial strengths and weaknesses.</li>
                    <li>Analyze trends across the 3 years (e.g., declining margins or improving solvency).</li>
                    <li>Score the enterprise using a weighted system based on Islamic credit scoring principles.</li>
                    <li>Decide if the company is financially eligible for investment project financing.</li>
                    </ul>
                    <p>
                    This automated financial audit follows the structure of AAOIFI-aligned Islamic finance evaluation methods.
                    </p>
                </div>
            </div>
            </div>
    </div>
    <div>
            <h3 className='titles'>2 - Enterprise's Project Evaluation</h3>
            <div className="grid">
            <div className="left-panel">
                <h3 className='sub_titles'>Describe the investment project</h3>
                <p className='major-text'>
                Explain the goal, cost structure, expected cash flows, delivery timeline, and any other key details.   </p>
                <textarea placeholder="Add scenario here" className="text-area" />
                <div className='btn_container'>
                <button className="submit-button button-34">Generate Journal Entry</button>
                </div>
            </div>
            <div className="right-panel">
                <h3 className='sub_titles'>Project Evaluation & Contract Selection</h3>
                <div className='text-area major-text'> 
                    <p>After analyzing your project description, our AI will:</p>
                    <ul>
                    <li>Evaluate the project's feasibility by reasoning over expected costs, revenues, duration, and risks.</li>
                    <li>Assign a project score (out of 2) based on financial logic and alignment with Islamic financing principles..</li>
                    <li>Decide whether the project is eligible for financing, considering the enterprise’s financial health.</li>
                    <li>Recommend the most suitable Islamic finance contract, such as Istisna’a, Murabaha, Salam, or Ijarah.</li>
                    <li>Justify its recommendation using AAOIFI guidelines, your project profile, and Shariah-compliance considerations.</li>

                    </ul>
                    <p>
                    This step blends financial reasoning with Islamic contract logic to propose the most appropriate and ethical financing model.
                    </p>
                </div>
            </div>
            </div>
    </div>

    <div>
            <h3 className='titles'>3 - Generate Contract Scenario</h3>
            <div className="grid">
            <div className="left-panel">
                <h3 className='sub_titles'>Contract Structuring Logic</h3>
                <p className='major-text'>
                Here, we uses the selected Islamic contract type and the evaluated project details to generate a formal financing scenario that aligns with Shariah principles and the structure of the proposed investment.  </p>
                <div className='text-area-mini major-text'> 
                    <p>After analyzing your project description, our AI will:</p>
                    <ul>
                    <li>Evaluate the project's feasibility by reasoning over expected costs, revenues, duration, and risks.</li>
                    <li>Assign a project score (out of 2) based on financial logic and alignment with Islamic financing principles..</li>
                    <li>Decide whether the project is eligible for financing, considering the enterprise’s financial health.</li>
                    <li>Recommend the most suitable Islamic finance contract, such as Istisna’a, Murabaha, Salam, or Ijarah.</li>
                    <li>Justify its recommendation using AAOIFI guidelines, your project profile, and Shariah-compliance considerations.</li>

                    </ul>
                    <p>
                    This step blends financial reasoning with Islamic contract logic to propose the most appropriate and ethical financing model.
                    </p>
                </div>
            </div>
            
            </div>
    </div>
    <div>
            <h3 className='titles'>4 - Generate Accounting Entries</h3>
            <div className="grid">
            <div className="left-panel">
                <h3 className='sub_titles'>AAOIFI-Based Journal Entries</h3>
                <p className='major-text'>
                Here we take the generated contract scenario as input and produce the corresponding AAOIFI-compliant journal entries based on the applied Islamic finance contract.                  </p>
                <div className='text-area-mini major-text'> 
                    <p>After analyzing your project description, our AI will:</p>
                    <ul>
                    <li>Evaluate the project's feasibility by reasoning over expected costs, revenues, duration, and risks.</li>
                    <li>Assign a project score (out of 2) based on financial logic and alignment with Islamic financing principles..</li>
                    <li>Decide whether the project is eligible for financing, considering the enterprise’s financial health.</li>
                    <li>Recommend the most suitable Islamic finance contract, such as Istisna’a, Murabaha, Salam, or Ijarah.</li>
                    <li>Justify its recommendation using AAOIFI guidelines, your project profile, and Shariah-compliance considerations.</li>

                    </ul>
                    <p>
                    This step blends financial reasoning with Islamic contract logic to propose the most appropriate and ethical financing model.
                    </p>
                </div>
            </div>
            
            </div>
    </div>

    
   
  </div>
  )
}

export default Main
