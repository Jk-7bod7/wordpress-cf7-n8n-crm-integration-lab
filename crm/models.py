from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class LeadCreate(BaseModel):
    submission_id: str = Field(..., description="Unique idempotency key from WordPress Contact Form 7", min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Lead contact email address")
    phone: Optional[str] = Field(None, max_length=30)
    company: Optional[str] = Field(None, max_length=100)
    service_required: str = Field(..., min_length=2, max_length=100)
    message: str = Field(..., min_length=5, max_length=2000)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v_clean):
            raise ValueError("Invalid email address format")
        return v_clean

class LeadResponse(BaseModel):
    id: int
    submission_id: str
    full_name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    service_required: str
    message: str
    created_at: str
    is_duplicate: bool = False

class HealthResponse(BaseModel):
    status: str
    database: str
    total_leads: int
    timestamp: str
