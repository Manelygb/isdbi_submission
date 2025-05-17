import React, { useState } from 'react';
import './Page.css';
import '../components/Challenge_4/ch4.css';

import PurpleCard from '../components/Challenge_4/PurpleCard';
import LightCard from '../components/Challenge_4/LightCard';

import SeqFlow from './SeqFlow';
import Agent1 from '../components/Challenge_4/Agents/Agent1';
import Agent2 from '../components/Challenge_4/Agents/Agent2';
import Agent3 from '../components/Challenge_4/Agents/Agent3';
import Agent4 from '../components/Challenge_4/Agents/Agent4';
import Agent5 from '../components/Challenge_4/Agents/Agent5';
import Agent6 from '../components/Challenge_4/Agents/Agent6';
import Agent7 from '../components/Challenge_4/Agents/Agent7';
import Agent8 from '../components/Challenge_4/Agents/Agent8';

import simulationData from '../simulation_ch4.json'; 


function SmartAdvisor() {
  const [mode, setMode] = useState("menu");
  const [isCompany, setIsCompany] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);

  const handlePurpleCardClick = (companyType) => {
    setIsCompany(companyType);
    setMode("flow");
  };

  const handleLightCardClick = (agentComponent) => {
    setSelectedAgent(() => agentComponent);
    setMode("agent");
  };

  const data_purple = {
    normalClient: {
      title: "You have a new Client with a new project here?",
      desc: "Get Full Audit and Product Design with an organized flow.",
    },
    companyClient: {
      title: "Some Entreprise has proposed a project today?",
      desc: "Get Full Audit and Product Design with an organized flow.",
    },
  };

  const data_agents = {
    agent1: {
      title: "Enterprise Audit Agent",
      desc: "Analyzes enterprise-level context. Calculates a company score for corporate clients based on operational and financial KPIs.",
    },
    agent2: {
      title: "Project Evaluation Agent",
      desc: "Checks the feasibility of the project based on similarity with previous Islamic-compliant projects. Returns boolean with justification.",
    },
    agent3: {
      title: "Islamic Contract Selector Agent",
      desc: "Chooses the most appropriate Islamic contract (e.g., Murabaha, Ijarah, Istisna) based on project structure and AAOIFI standards.",
    },
    agent4: {
      title: "Contract Formalization Agent",
      desc: "Generates complete Islamic contract terms and clauses based on the selected contract. Customizable and Shariah-compliant.",
    },
    agent5: {
      title: "Accounting Agent",
      desc: "Creates journal entries from the contract using AAOIFI-compliant accounting treatment for asset transfer, recognition, and liabilities.",
    },
    agent6: {
      title: "Shariah Compliance Validator",
      desc: "Flags potential issues such as Ribā or Gharar. Validates against AAOIFI standards. Future version will suggest fixes.",
    },
    agent7: {
      title: "Country Law Validator",
      desc: "Checks compatibility of the contract with national laws. Lightweight processing of known constraints vs contract outputs.",
    },
    agent8: {
      title: "Final Decision Agent",
      desc: "Aggregates all results and provides a final recommendation: Approve, Revise, or Reject. Cites previous agent outputs.",
    },
  };

  return (
    <div className="page-container">
      <div className="title_skltn">
        <h2 className="titles">Smart Advisors</h2>
        <p className="description">
          Audit companies/projects, recommend contracts with their journal entries.
        </p>
      </div>

      <div className="line_p"></div>

      {mode === "menu" && (
        <div className="main-content">
          <div>
            <h2 className="titles">Ready Flows</h2>
            <div className="purple-card-container">
              <PurpleCard
                title={data_purple.companyClient.title}
                desc={data_purple.companyClient.desc}
                onClick={() => handlePurpleCardClick(true)}
              />
              <PurpleCard
                title={data_purple.normalClient.title}
                desc={data_purple.normalClient.desc}
                onClick={() => handlePurpleCardClick(false)}
              />
            </div>
          </div>

          <div>
            <h2 className="titles">Independent Agents</h2>
            <div className="light-card-container">
              <LightCard
                title={data_agents.agent1.title}
                desc={data_agents.agent1.desc}
                onClick={() => handleLightCardClick(Agent1)}
              />
              <LightCard
                title={data_agents.agent2.title}
                desc={data_agents.agent2.desc}
                onClick={() => handleLightCardClick(Agent2)}
              />
              <LightCard
                title={data_agents.agent3.title}
                desc={data_agents.agent3.desc}
                onClick={() => handleLightCardClick(Agent3)}
              />
              <LightCard
                title={data_agents.agent4.title}
                desc={data_agents.agent4.desc}
                onClick={() => handleLightCardClick(Agent4)}
              />
              <LightCard
                title={data_agents.agent5.title}
                desc={data_agents.agent5.desc}
                onClick={() => handleLightCardClick(Agent5)}
              />
              <LightCard
                title={data_agents.agent6.title}
                desc={data_agents.agent6.desc}
                onClick={() => handleLightCardClick(Agent6)}
              />
              <LightCard
                title={data_agents.agent7.title}
                desc={data_agents.agent7.desc}
                onClick={() => handleLightCardClick(Agent7)}
              />
              <LightCard
                title={data_agents.agent8.title}
                desc={data_agents.agent8.desc}
                onClick={() => handleLightCardClick(Agent8)}
              />
            </div>
          </div>
        </div>
      )}

      {mode === "flow" && <SeqFlow isCompany={isCompany} />}

      {mode === "agent" && selectedAgent && (() => {
        const AgentComponent = selectedAgent;
        return <AgentComponent />;
      })()}
    </div>
  );
}

export default SmartAdvisor;
