import React from 'react'

function Agent2Independent({ data }) {
  if (!data) return <p>Loading output for Agent 2...</p>;

  return (
    <div className="agent-output-box">
         <div className="grid">
         <div className="left-panel">
          <h3 className='titles'>Expert in Enterprise Audit 2</h3>
          <p className='sub-title bold'>
            Contract Structuring Logic
          </p>
          <p className='major-text'>
            Here, we uses the selected Islamic contract type and the evaluated project details to generate a formal financing scenario that aligns with Shariah principles and the structure of the proposed investment.          </p>
        
          <div
          className="text-area major-text"
          >
           {data.response}
          </div>
        </div>
      </div>
    </div>
  );
}


export default Agent2Independent
