import React , {useState} from 'react'
import '../../pages/Page.css';

function Step1() {


      const [scenario, setScenario] = useState('');
      const [response, setResponse] = useState(null);
      const [loading, setLoading] = useState(false);
    
      const handleSubmit = async () => {
       
      };

  return (
    <div className="grid">
        <div className="left-panel">
          <h3 className='titles'>1.AI Reviewing</h3>
          <p className='major-text'>
            Here, we uses the selected Islamic contract type and the evaluated project details to generate a formal financing scenario that aligns with Shariah principles and the structure of the proposed investment.          </p>
        

          <p className='sub-title bold' >
            - Trigger : 
          </p>
          <div
          className="text-area major-text"
          >
            Based on the approved project and the recommended Islamic contract type, our AI will:
            Formulate a detailed financing scenario that describes how the contract will be applied in practice.

          </div>
          <div
          className="text-area major-text"
          >
            Based on the approved project and the recommended Islamic contract type, our AI will:
            Formulate a detailed financing scenario that describes how the contract will be applied in practice.
            Use real-world Islamic finance structuring logic (e.g., parallel Istisna’a, Murabaha markup, Ijarah with purchase option).
            Ensure the contract follows AAOIFI guidelines and reflects the actual project structure — without inventing values or assumptions.
            Output a professional, Shariah-compliant contract description ready for review or submission to accounting.
          </div>
        
        </div>
      </div>
  )
}

export default Step1
