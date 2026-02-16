import os
import shutil
import fitz  # PyMuPDF
from fastapi import UploadFile

def watermark_pdf(input_path: str, output_path: str, student_name: str) -> bool:
    try:
        doc = fitz.open(input_path)
        for page in doc:
            # Adds student name at the bottom of every page
            # Color is RGB (0.7, 0.7, 0.7) which is light gray
            page.insert_text((50, page.rect.height - 30), 
                             f"Property of: {student_name}", 
                             fontsize=11, color=(0.7, 0.7, 0.7))
        doc.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"Error watermarking PDF: {e}")
        return False

def save_upload_file(upload_file: UploadFile, destination: str) -> None:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
