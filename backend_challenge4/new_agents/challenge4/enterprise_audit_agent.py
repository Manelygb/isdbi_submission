import os
import json
import pandas as pd
import io
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from ..custom_chat_models.chat_openrouter import ChatOpenRouter
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv()

MODEL_NAME = "deepseek/deepseek-chat-v3-0324"

class AuditSummary(BaseModel):
    average_score: float = Field(description="Average financial score across years")
    risk_distribution: Dict[str, int] = Field(description="Distribution of risk levels across years")
    verdict: str = Field(description="Final recommendation: APPROVE, MODIFY, or REJECT")
    justification: str = Field(description="Detailed explanation of the audit conclusion")

class EnterpriseAuditAgent(BaseAgent):
    agent_name = "EnterpriseAuditAgent"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenRouter(model_name=MODEL_NAME, temperature=0.3)
        self.structured_llm = self.llm.with_structured_output(AuditSummary)
        
        print(f"{self.agent_name} initialized.")

    def _perform_task(self, pco: dict):
        pco["processing_log"][-1]["message"] = "Starting enterprise financial audit..."
        
        client_details = pco.get("client_details", {})
        client_type = client_details.get("client_type")
        
        if client_type != "company":
            pco["enterprise_audit_results"] = {
                "score": None, 
                "summary": "Not a company, audit skipped.",
                "key_ratios": {},
                "warnings": ["Client is not a company; financial audit not applicable."]
            }
            pco["processing_log"][-1]["message"] = "Audit skipped, client not a company."
            pco["current_status"] = "pending_project_evaluation"
            return
        
        try:
            # Get financial data from client_details
            financial_data_csv = client_details.get("financial_data_csv")
            
            # If financial data is not provided in client_details, try to use the default mock data as fallback
            if not financial_data_csv:
                script_dir = os.path.dirname(__file__)
                mock_financials_path = os.path.join(script_dir, "../../../data/input/mock_full_financials.csv")
                
                if os.path.exists(mock_financials_path):
                    with open(mock_financials_path, 'r') as f:
                        financial_data_csv = f.read()
                        pco["processing_log"][-1]["message"] += " Using mock financial data file."
                else:
                    raise FileNotFoundError("No financial data provided in client_details and mock file not found.")
            
            # Parse the CSV data
            df = pd.read_csv(io.StringIO(financial_data_csv))
            
            # Process and analyze financials
            ratios_by_year = self._compute_all_ratios(df)
            company_summary = self._summarize_company(ratios_by_year)
            
            # Update PCO with audit results
            pco["enterprise_audit_results"] = {
                "score": company_summary["average_score"],
                "summary": company_summary["llm_summary"],
                "key_ratios": {year_data["year"]: year_data["ratios"] for year_data in ratios_by_year},
                "risk_level": company_summary["risk_distribution"],
                "verdict": company_summary["verdict"],
                "warnings": []
            }
            
            pco["processing_log"][-1]["message"] = "Company financial audit completed successfully."
            pco["current_status"] = "pending_project_evaluation"
            
        except Exception as e:
            error_message = f"Error during enterprise audit: {str(e)}"
            pco["enterprise_audit_results"] = {
                "score": 0,
                "summary": "Error during financial analysis.",
                "key_ratios": {},
                "warnings": [error_message]
            }
            pco["processing_log"][-1]["message"] = error_message
            pco["current_status"] = "error_enterprise_audit"
            print(f"Critical error in EnterpriseAuditAgent: {e}")
    
    def _compute_all_ratios(self, df):
        results = []
        for i in range(len(df)):
            year_data = df.iloc[i]
            year = year_data['Year']
            prev_data = df.iloc[i - 1] if i > 0 else None

            current_assets = year_data['CurrentAssets']
            current_liabilities = year_data['CurrentLiabilities']
            inventory = year_data['StocksAndRelief']
            equity = year_data['IssuedCapital']
            total_liabilities = year_data['TotalLiabilities']
            total_assets = year_data['TotalAssets']
            net_income = year_data['NetIncome']
            revenue = year_data.get('Revenue', 1e6)
            permanent_capital = year_data.get('PermanentCapital', equity + total_liabilities)
            fixed_assets = year_data.get('FixedAssets', year_data['NonCurrentAssets'])

            ratios = {}
            ratios['Current Ratio'] = current_assets / current_liabilities if current_liabilities else None
            ratios['Quick Ratio'] = (current_assets - inventory) / current_liabilities if current_liabilities else None
            ratios['Equity Ratio'] = equity / total_liabilities if total_liabilities else None
            ratios['Debt Ratio'] = total_liabilities / total_assets if total_assets else None
            ratios['Net Debt Ratio'] = total_liabilities / equity if equity else None
            ratios['General Solvency Ratio'] = total_assets / total_liabilities if total_liabilities else None
            ratios['Return on Assets'] = net_income / total_assets if total_assets else None
            ratios['Return on Equity'] = net_income / equity if equity else None
            ratios['Net Margin'] = net_income / revenue if revenue else None

            if prev_data is not None:
                prev_revenue = prev_data.get('Revenue', 1e6)
                ratios['Revenue Growth'] = (revenue - prev_revenue) / prev_revenue if prev_revenue else None
            else:
                ratios['Revenue Growth'] = None

            working_capital = permanent_capital - fixed_assets
            bfr = current_assets - current_liabilities
            cash_position = working_capital - bfr
            ratios['ROE'] = net_income / equity if equity else None
            ratios['ROA'] = net_income / total_assets if total_assets else None
            ratios['Working Capital'] = working_capital
            ratios['BFR'] = bfr
            ratios['Cash Position'] = cash_position

            score = self._score_ratios(ratios)

            results.append({
                "year": int(year) if isinstance(year, int) else int(year.item()) if hasattr(year, 'item') else int(year),
                "ratios": {k: round(float(v), 4) if v is not None else None for k, v in ratios.items()},
                "score": score
            })

        return results
    
    def _score_ratios(self, ratios):
        score_details = {}
        total_score = 0.0
        max_possible_score = 2.0

        def apply_threshold(value, thresholds):
            for rule in thresholds:
                if "range" in rule:
                    x = value
                    try:
                        if eval(rule["range"].replace("x", str(x))):
                            return rule["points"]
                    except:
                        continue
                elif "condition" in rule:
                    if rule["condition"] == "positive" and value > 0:
                        return rule["points"]
                    elif rule["condition"] == "negative" and value < 0:
                        return rule["points"]
            return 0

        scoring_system = {
            "GENERAL_LIQUIDITY": {
                "source": "Current Ratio",
                "thresholds": [
                    {"range": "x<1", "points": 0},
                    {"range": "1<x<1.5 or x>2", "points": 1},
                    {"range": "1.5<x<2", "points": 2},
                ],
                "weight": 0.10
            },
            "NET_DEBT": {
                "source": "Net Debt Ratio",
                "thresholds": [
                    {"range": "x>1", "points": 0},
                    {"range": "0.6<x<1", "points": 1},
                    {"range": "x<0.6", "points": 2},
                ],
                "weight": 0.10
            },
            "GENERAL_SOLVENCY_RATIO": {
                "source": "General Solvency Ratio",
                "thresholds": [
                    {"range": "x<1", "points": 0},
                    {"range": "x>1", "points": 2}
                ],
                "weight": 0.10
            },
            "NET_MARGIN": {
                "source": "Net Margin",
                "thresholds": [
                    {"range": "x<0.05", "points": 0},
                    {"range": "0.05<x<0.10", "points": 1},
                    {"range": "x>0.10", "points": 2},
                ],
                "weight": 0.05
            },
            "REVENUE_GROWTH": {
                "source": "Revenue Growth",
                "thresholds": [
                    {"condition": "negative", "points": 0},
                    {"condition": "positive", "points": 1}
                ],
                "weight": 0.05
            }
        }

        for key, config in scoring_system.items():
            value = ratios.get(config["source"])
            if value is None:
                points = 0
                weighted = 0
            else:
                points = apply_threshold(value, config["thresholds"])
                weighted = (points / 2) * config["weight"]
                total_score += weighted

            score_details[key] = {
                "value": value,
                "points": points,
                "weighted": round(weighted, 4)
            }

        return {
            "total_score": round(total_score, 4),
            "maximum_possible": max_possible_score,
            "risk_level": (
                "Low" if total_score >= 1.5 else
                "Moderate" if total_score >= 1.0 else
                "High"
            ),
            "category_scores": score_details
        }
    
    def _summarize_company(self, results):
        avg_score = sum(year['score']['total_score'] for year in results) / len(results)
        risk_counts = {"Low": 0, "Moderate": 0, "High": 0}
        for year in results:
            risk_counts[year['score']['risk_level']] += 1

        if avg_score >= 1.5:
            verdict = "APPROVE"
        elif avg_score >= 1.0:
            verdict = "MODIFY"
        else:
            verdict = "REJECT"

        prompt = self._build_summary_prompt(results, avg_score, risk_counts, verdict)
        
        # Use the LLM to generate a detailed summary
        response = self.llm.invoke(prompt)

        return {
            "average_score": round(avg_score, 4),
            "risk_distribution": risk_counts,
            "verdict": verdict,
            "llm_summary": response.content
        }
    
    def _build_summary_prompt(self, results, avg_score, risk_counts, verdict):
        model_input = {
            "scores_by_year": [{"year": r["year"], "score": r["score"]} for r in results],
            "average_score": avg_score,
            "risk_distribution": risk_counts,
            "verdict": verdict
        }
        
        return f"""You are a senior financial auditor. Based on multi-year scoring data and risk analysis, write a final audit opinion about this company.

**Financial Audit Data:**
```json
{json.dumps(model_input, indent=2)}
```

Provide an overall audit summary with justification and financial advice. Focus on the company's financial health, 
trends over time, key strengths and weaknesses, and specific recommendations based on the data.

Your assessment should be professional, balanced, and data-driven. If the verdict is MODIFY or REJECT, 
be specific about what financial aspects would need improvement.
""" 