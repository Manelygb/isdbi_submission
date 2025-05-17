import React from 'react';
import './stepper.css';

function AgentStepper({ activeStep }) {
  return (
    <div className="stepper">
      {[...Array(8)].map((_, i) => (
        <div
          key={i}
          className={`step-circle ${i === activeStep ? 'active' : ''} ${i < activeStep ? 'done' : ''}`}
        >
          {i + 1}
        </div>
      ))}
    </div>
  );
}

export default AgentStepper;
