import os
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import from modules
from .database import engine, get_db, settings, Base
from . import models
from . import schemas
from .utils import watermark_pdf, save_upload_file

# Create tables
models.Base.metadata.create_all(bind=engine)

# Ensure static directory exists
os.makedirs(settings.STATIC_PDF_DIR, exist_ok=True)

# --- App Setup ---
app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount PDF files
app.mount("/pdfs", StaticFiles(directory=settings.STATIC_PDF_DIR), name="pdfs")

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to Teacher's Batch-Vault API"}

@app.post("/api/batches/", response_model=schemas.BatchOut)
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):
    db_batch = models.Batch(name=batch.name)
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@app.get("/api/batches/", response_model=List[schemas.BatchOut])
def list_batches(db: Session = Depends(get_db)):
    return db.query(models.Batch).all()

@app.get("/api/batches/{batch_id}", response_model=schemas.BatchOut)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@app.post("/api/batches/{batch_id}/students/", response_model=schemas.StudentOut)
def add_student(batch_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    db_student = models.Student(**student.dict(), batch_id=batch_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.post("/api/batches/{batch_id}/upload_pdf")
async def upload_pdf(batch_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if not batch.students:
        return JSONResponse(status_code=400, content={"message": "No students in this batch to generate PDFs for."})

    # Save uploaded file temporarily
    temp_filename = f"temp_{batch_id}_{file.filename}"
    save_upload_file(file, temp_filename)
    
    generated_count = 0
    
    try:
        for student in batch.students:
            # Create unique filename
            # format: OriginalFilename (StudentName).pdf
            original_filename = os.path.splitext(file.filename)[0]
            safe_original_filename = "".join([c for c in original_filename if c.isalnum() or c in (' ', '_', '-')]).strip()
            safe_student_name = "".join([c for c in student.name if c.isalnum() or c in (' ', '_', '-')]).strip()
            
            filename = f"{safe_original_filename} ({safe_student_name}).pdf"
            output_path = os.path.join(settings.STATIC_PDF_DIR, filename)
            
            # Watermark
            if watermark_pdf(temp_filename, output_path, student.name):
                pdf_url = f"/pdfs/{filename}"
                student.pdf_url = pdf_url
                generated_count += 1
        
        db.commit()
    finally:
        # Cleanup temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
    return {"message": f"Successfully generated {generated_count} PDFs", "count": generated_count}
