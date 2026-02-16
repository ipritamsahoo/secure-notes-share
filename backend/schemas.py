from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    phone: str

class StudentOut(BaseModel):
    id: int
    name: str
    phone: str
    pdf_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class BatchCreate(BaseModel):
    name: str

class BatchOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    students: List[StudentOut] = []

    class Config:
        from_attributes = True
