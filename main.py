from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
from models import QueryRequest, QueryResponse
from database import init_db, get_db
from database_models import DocumentModel
from schemas import DocumentCreate, DocumentResponse
from agent import triage_ticket, process_query
from summariser import generate_account_brief
from eval_harness import run_evaluation
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TicketRequest(BaseModel):
    ticket_text: str

class AccountRequest(BaseModel):
    account_id: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"status": "running"}

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    answer = process_query(request.query)
    return {"answer": answer}

@app.post("/documents", response_model=DocumentResponse)
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    db_doc = DocumentModel(title=doc.title, content=doc.content)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@app.get("/documents", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.query(DocumentModel).all()

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    db_doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(db_doc)
    db.commit()
    return {"message": "Document deleted successfully"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")
    db_doc = DocumentModel(title=file.filename, content=text_content)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return {"filename": file.filename, "id": db_doc.id, "message": "File uploaded successfully"}

@app.post("/triage")
def triage_support_ticket(request: TicketRequest):
    result = triage_ticket(request.ticket_text)
    return result

@app.post("/account-brief")
def account_health_brief(request: AccountRequest):
    result = generate_account_brief(request.account_id)
    return result

@app.post("/run-eval")
def trigger_evaluation():
    results = run_evaluation()
    return {"message": "Evaluation completed successfully", "results": results}