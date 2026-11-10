import logging
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware

from .models import LeadCreate, LeadResponse, HealthResponse
from .database import init_db, insert_lead, get_leads, get_lead_by_id, count_leads

# Configure safe logging without PII leakage
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Mock-CRM] %(message)s"
)
logger = logging.getLogger("mock_crm")

app = FastAPI(
    title="Mock CRM API",
    description="Local synthetic CRM backed by SQLite for PORTFOLIO-024",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Mock CRM database initialized.")

def mask_email(email: str) -> str:
    if "@" in email:
        user, domain = email.split("@", 1)
        masked_user = user[0] + "***" if len(user) > 0 else "***"
        return f"{masked_user}@{domain}"
    return "***"

@app.get("/health", response_model=HealthResponse)
def health():
    try:
        total = count_leads()
        return HealthResponse(
            status="healthy",
            database="connected",
            total_leads=total,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Database unreachable")

@app.post("/api/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, response: Response):
    masked = mask_email(lead_in.email)
    logger.info(f"Received lead ingestion request | submission_id={lead_in.submission_id} | email={masked} | service={lead_in.service_required}")
    try:
        result = insert_lead(lead_in.dict())
        if result.get("is_duplicate"):
            response.status_code = status.HTTP_200_OK
            logger.info(f"Duplicate submission detected | submission_id={lead_in.submission_id} -> Returning existing record ID={result['id']}")
        else:
            logger.info(f"New lead committed to SQLite | ID={result['id']} | submission_id={lead_in.submission_id}")
        return result
    except Exception as e:
        logger.error(f"Error persisting lead: {e}")
        raise HTTPException(status_code=500, detail="Internal CRM persistence failure")

@app.get("/api/leads", response_model=List[LeadResponse])
def list_leads(limit: int = 50, offset: int = 0):
    return get_leads(limit=limit, offset=offset)

@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
def read_lead(lead_id: int):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
