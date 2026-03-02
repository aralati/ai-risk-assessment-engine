import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Risk Assessment Engine",
    description="Microservice for AI-driven financial transaction risk scoring.",
    version="1.0.0"
)

class TransactionData(BaseModel):
    transaction_id: str = Field(..., example="TXN-987654")
    user_id: str = Field(..., example="USR-10293")
    amount: float = Field(..., gt=0, example=2500.50)
    currency: str = Field(..., min_length=3, max_length=3, example="USD")
    merchant_category: str = Field(..., example="electronics")
    is_international: bool = Field(default=False)

class RiskScoreResponse(BaseModel):
    transaction_id: str
    risk_score: float
    risk_level: str
    ai_behavioral_flag: bool
    details: Optional[str] = None

def mock_ml_risk_scoring(tx: TransactionData) -> float:
    base_risk = 0.1
    if tx.amount > 10000:
        base_risk += 0.3
    if tx.is_international:
        base_risk += 0.2
    if tx.merchant_category.lower() in ["crypto", "gambling"]:
        base_risk += 0.35
    return min(base_risk, 0.99)

def call_llm_behavioral_analysis(tx: TransactionData) -> bool:
    logger.info(f"Sending context to LLM for transaction {tx.transaction_id}...")
    if tx.amount > 5000 and tx.is_international:
        return True
    return False

@app.post("/api/v1/assess-risk", response_model=RiskScoreResponse)
async def assess_transaction_risk(transaction: TransactionData):
    try:
        logger.info(f"Processing risk assessment for TXN: {transaction.transaction_id}")
        ml_score = mock_ml_risk_scoring(transaction)
        llm_flag = call_llm_behavioral_analysis(transaction)
        
        final_risk_level = "HIGH" if (ml_score > 0.7 or llm_flag) else ("MEDIUM" if ml_score > 0.4 else "LOW")
        
        return RiskScoreResponse(
            transaction_id=transaction.transaction_id,
            risk_score=round(ml_score, 2),
            risk_level=final_risk_level,
            ai_behavioral_flag=llm_flag,
            details="Assessment completed successfully."
        )

    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during risk assessment.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
