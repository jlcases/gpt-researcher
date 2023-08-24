from pydantic import BaseModel

class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str
    language: str
    openai_api_key: str
