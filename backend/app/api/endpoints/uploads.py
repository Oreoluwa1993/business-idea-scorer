import os
import uuid
from typing import List
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.file_processor import process_excel_file, process_csv_file
from app.models.schemas import UploadResponse

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("./uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an Excel or CSV file containing business ideas.
    The file will be processed and the data stored for scoring.
    """
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer after reading
    
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".xlsx", ".xls", ".csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel (.xlsx, .xls) and CSV (.csv) files are supported"
        )
    
    # Create a unique filename for the uploaded file
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Process the file based on its type
    try:
        if file_extension in [".xlsx", ".xls"]:
            # Process Excel file
            data_summary = process_excel_file(file_path)
        else:
            # Process CSV file
            data_summary = process_csv_file(file_path)
            
        return {
            "filename": file.filename,
            "saved_as": unique_filename,
            "size_bytes": file_size,
            "record_count": data_summary.get("record_count", 0),
            "columns": data_summary.get("columns", []),
            "status": "success",
            "message": f"File uploaded and processed successfully with {data_summary.get('record_count', 0)} records"
        }
        
    except Exception as e:
        # Remove the file if processing fails
        if file_path.exists():
            os.remove(file_path)
            
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/files", response_model=List[str])
async def list_uploaded_files():
    """
    List all uploaded files.
    """
    files = []
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file():
            files.append(file_path.name)
    
    return files

@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(filename: str):
    """
    Delete an uploaded file.
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
        
    return None
