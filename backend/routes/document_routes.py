from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Form
from fastapi.responses import Response

from backend.auth import get_current_user,require_admin
from backend.document_service import(
    get_all_documents,
    get_document_count,
    upload_document,
    get_document_bytes,
    delete_document,
    MAX_DOCUMENTS,
)

router=APIRouter(prefix="/api", tags=["documents"])

@router.get("/documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    docs=get_all_documents()
    return {"documents": docs,"count":len(docs), "limit": MAX_DOCUMENTS}

@router.get("/get_document/{document_id}")
async def get_document(document_id:str ,current_user:dict= Depends(get_current_user)):
    try:
        pdf_bytes,filename=get_document_bytes(document_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404,detail="Documents not found")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error retrieving doc:{str(e)}")
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "X-Content-Type-Options": "nosniff",
        }
    )

@router.post("/upload-document")
async def upload_doc(
    title: str=Form(...),
    document_type: str=Form(...),
    file: UploadFile=File(...),
    admin_user:dict=Depends(require_admin),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400,detail="ONLY PDF ALLOWED!!")
    if get_document_count()>=MAX_DOCUMENTS:
        raise HTTPException(status_code=400,detail=f"Document limit of {MAX_DOCUMENTS} reached")
    
    contents=await file.read()

    if len(contents)==0:
        raise HTTPException(status_code=400,detail="Upload empty")
    if len(contents)>20*1024*1024: #20mB limit
        raise HTTPException(status_code=400,detail="File Too large")
    
    try:
        doc=upload_document(title,document_type,contents,file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Upload failed {str(e)}")
    
    return {"message": "Document Uploaded","id":doc["id"]}

@router.delete("/documents/{document_id}")
async def remove_document(document_id: str, admin_user: dict = Depends(require_admin)):
    success = delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document deleted."}