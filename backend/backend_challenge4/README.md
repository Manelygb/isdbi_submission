# Islamic Finance Advisory System

This backend system implements an AI-powered workflow for Islamic finance advisory using a multi-agent architecture. Each agent specializes in a distinct aspect of Islamic finance analysis, working together to process and evaluate financial proposals according to Islamic finance principles.

## System Architecture

The system follows a sequential agent pipeline architecture where each agent performs a specialized task and updates a Process Control Object (PCO) that is passed between agents. The PCO contains all relevant information about the client, project, and evaluation results.

### Agents

1. **EnterpriseAuditAgent**: Evaluates the financial health of the enterprise based on financial data.
2. **ProjectEvaluationAgent**: Analyzes the viability of the proposed project.
3. **IslamicContractSelectorAgent**: Recommends the most appropriate Islamic financial contract type.
4. **ContractDraftingAgent**: Drafts a formalized contract based on the selected contract type.
5. **AccountingAgent**: Generates accounting entries for the Islamic financial instrument.
6. **ShariahComplianceValidatorAgent**: Validates the contract against Shariah compliance rules.
7. **CountryLawsValidatorAgent**: Checks the contract against relevant local legal requirements.
8. **FinalDecisionAgent**: Provides a comprehensive summary and final decision based on all previous evaluations.

## Setup and Configuration

### Prerequisites

- Python 3.8+
- Required packages listed in `requirements.txt`

### Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment: 
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install the required packages: `pip install -r requirements.txt`
5. Set up environment variables in the `.env` file:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

## Running the System

### Running Individual Agents

The system is designed for agents to be run sequentially as part of an orchestrated pipeline. See the test files for examples of how to run individual agents.

### Running the Tests

To test the entire agent pipeline:

```bash
# Run the first 4 agents
python backend/tests/test_first_four_agents.py

# Run the first 5 agents
python backend/tests/test_first_five_agents.py

# Run the first 7 agents
python backend/tests/test_first_seven_agents.py

# Run all 8 agents including the final decision agent
python backend/tests/test_first_eight_agents.py

# Test specific agents
python backend/tests/test_enterprise_audit_agent.py
python backend/tests/test_project_evaluation_agent.py
python backend/tests/test_islamic_contract_selector_agent.py
python backend/tests/test_accounting_agent.py
python backend/tests/test_country_laws_agent.py
```

### Test Output

Test results are saved as JSON files in the `backend/tests/outputs/` directory. These files contain the complete PCO with all agent outputs.

## Process Control Object (PCO)

The PCO is a JSON structure that contains:

- **case_id**: Unique identifier for the case
- **client_details**: Information about the client
- **project_details**: Information about the proposed project
- **enterprise_audit_results**: Results from the enterprise financial audit
- **project_evaluation_results**: Results from the project viability evaluation
- **selected_contract_details**: Selected Islamic contract type and details
- **formalized_contract**: The finalized contract document
- **accounting_entries_report**: Accounting treatments for the contract
- **shariah_compliance_report**: Results of Shariah compliance validation
- **country_law_validation_report**: Results of country law validation
- **final_decision_report**: Comprehensive summary and final decision
- **processing_log**: Log of all agent actions
- **current_status**: Current status of the processing pipeline
- **error_info**: Details about any errors encountered

## Advanced Usage

### Using the API

The system exposes an API through `orchestrator_api.py`, which can be used to process new cases.

### Adding New Agents

To add a new agent:

1. Create a new agent class that inherits from `BaseAgent`
2. Implement the `_perform_task` method to process the PCO
3. Update the orchestrator agent sequence to include the new agent

## Troubleshooting

- **Vector Store Errors**: Ensure the FAISS vector stores are properly initialized
- **API Key Errors**: Check that your `.env` file contains valid API keys
- **Model Errors**: Some operations require specific LLM models - ensure you're using the recommended models 