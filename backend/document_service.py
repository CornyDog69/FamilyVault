import os
import uuid # for unique identifiers it hides real name of docs and give encrypted words
from datetime import datetime
from pathlib import Path
from backend.database import documents_col
from backend.encryption import save_encrypted_file,load_decrypted_file

SECURE_DOCS_DIR=os.path.join(os.path.dirname(os.path.dirname(__file__)),"secure_docs")
MAX_DOCUMENTS=60
ALLOWED_EXTENSIONS={".pdf"}

def get_all_documents():
    docs=list(documents_col.find({},{"_id":1,"title":1,"document_type":1,"uploaded_At":1}))
    for doc in docs:
        doc["id"] =str(doc["_id"])
        doc["_id"]=str(doc["_id"])
    return docs

def get_document_count()->int:
    return documents_col.count_documents({})


def upload_document(title:str,document_type:str,file_bytes:bytes,original_filename:str)-> dict:
    ext=Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF")
    if get_document_count()>= MAX_DOCUMENTS:
        raise ValueError(f"LIMIT REACHED OF {MAX_DOCUMENTS}")
    
    unique_name=f"{uuid.uuid4().hex}.enc"
    filepath=os.path.join(SECURE_DOCS_DIR,unique_name)
    os.makedirs(SECURE_DOCS_DIR,exist_ok=True)
    save_encrypted_file(file_bytes,filepath)
    doc={
        "title":title,
        "document_type": document_type,
        "file_path": filepath,
        "original_name": original_filename,
        "uploaded_at": datetime.utcnow(),
    }
    result= documents_col.insert_one(doc)
    doc["id"]=str(result.inserted_id)
    return doc

def get_document_bytes(document_id:str)-> tuple[bytes,str]:
    from bson import ObjectId
    doc= documents_col.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise FileNotFoundError("NOT FOUND")
    decrypted=load_decrypted_file(doc["file_path"])
    return decrypted,doc.get("original_filename","document.pdf")

def delete_document(document_id: str)-> bool:
    from bson import ObjectId
    doc=documents_col.find_one({"_id": ObjectId(document_id)})
    if not doc:
        return False
    try:
        os.remove(doc["file_path"])
    except FileNotFoundError:
        pass
    documents_col.delete_one({"_id": ObjectId(document_id)})
    return True