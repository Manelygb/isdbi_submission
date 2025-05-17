import React, { useState, useEffect } from 'react';
import AgentStepper from './AgentStepper';
import Agent1 from './Agent1';
import Agent2 from './Agent2';
import Agent3 from './Agent3';
import Agent4 from './Agent4';
import Agent5 from './Agent5';
import Agent6 from './Agent6';
import Agent7 from './Agent7';
import Agent8 from './Agent8';
import simulationData from '../../../simulation_ch4.json';

const agents = [
  { id: 'EnterpriseAuditAgent', Component: Agent1, data: simulationData.enterprise_audit_results },
  { id: 'ProjectEvaluationAgent', Component: Agent2, data: simulationData.project_evaluation_results },
  { id: 'IslamicContractSelectorAgent', Component: Agent3, data: simulationData.selected_contract_details },
  { id: 'ContractDraftingAgent', Component: Agent4, data: simulationData.formalized_contract },
  { id: 'AccountingAgent', Component: Agent5, data: simulationData.accounting_entries_report },
  { id: 'ShariahComplianceValidatorAgent', Component: Agent6, data: simulationData.shariah_compliance_report },
  { id: 'CountryLawsValidatorAgent', Component: Agent7, data: simulationData.country_law_validation_report },
  { id: 'FinalDecisionAgent', Component: Agent8, data: simulationData.final_decision },
];

function SmartFlow() {
  const [currentStep, setCurrentStep] = useState(0);
  const [visibleAgents, setVisibleAgents] = useState([]);

  useEffect(() => {
    if (currentStep < agents.length) {
      const timer = setTimeout(() => {
        setVisibleAgents((prev) => [...prev, agents[currentStep]]);
        setCurrentStep((prev) => prev + 1);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [currentStep]);

  return (
    <div className="smart-flow-container">
      <h2 className="titles">Smart Advisor Results</h2>

      {visibleAgents.map((agent, index) => (
        <div key={index} className="agent-block" style={{ marginBottom: '3rem' }}>
          <AgentStepper activeStep={index} />
          <agent.Component data={agent.data} />
        </div>
      ))}

      {currentStep < agents.length && (
        <div className="agent-block" style={{ marginBottom: '3rem' }}>
          <AgentStepper activeStep={currentStep} />
          <p>Processing Agent {currentStep + 1}...</p>
        </div>
      )}
    </div>
  );
}

export default SmartFlow;
