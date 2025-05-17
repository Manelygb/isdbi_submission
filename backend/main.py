from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.forensic_agent import create_forensic_agent
from ch1_onsite import process_finance_scenario

app = FastAPI()

origins = [
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ROUTES ===
class InputData(BaseModel):
    input: str

agent = create_forensic_agent()

@app.post("/api/challenge2/analyze")
async def analyze(data: InputData):
    response = agent.invoke({"input": data.input})
    return {"output": response["output"]}


class ScenarioInput(BaseModel):
    scenario: str

@app.post("/api/usecase/analyze")
def usecase_analyze(data: ScenarioInput):
    result = process_finance_scenario(data.scenario)
    return result
