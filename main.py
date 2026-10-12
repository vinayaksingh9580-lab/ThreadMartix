from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
import tempfile

from database import engine, SessionLocal, Base
from models import EmailCase

# Import our pipeline functions from Phases 1-4
from email_parser import parse_email, reconstruct_hop_path
from security_analyzer import analyze_security
from content_classifier import classify_email, calculate_fraud_score
from geolocator import get_originating_ip, geolocate_ip

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIH 2026 - AI Email Threat Intelligence API")

# Enable CORS for React frontend (Phase 6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/analyze")
async def analyze_email(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Ingests a raw .eml file, runs the full threat detection pipeline,
    saves the result to the database, and returns the JSON report.
    """
    if not file.filename.endswith(".eml"):
        raise HTTPException(status_code=400, detail="Only .eml files are supported")
        
    # Save uploaded file to a temporary location to process it
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    try:
        # --- PHASE 1: Parsing & Hop Reconstruction ---
        parsed_data = parse_email(tmp_path)
        if "error" in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data["error"])
            
        hops = reconstruct_hop_path(parsed_data.get('received_headers', []))
        parsed_data['hop_path'] = hops
        parsed_data.pop('received_headers', None)
        
        # --- PHASE 4: Geolocation & Infrastructure ---
        origin_ip = get_originating_ip(hops)
        geo_data = geolocate_ip(origin_ip)
        parsed_data['geo_assessment'] = geo_data
        
        # --- PHASE 2: Security & Authentication ---
        security_results = analyze_security(parsed_data, tmp_path)
        parsed_data['security_analysis'] = security_results
        
        # --- PHASE 3: ML Content Classification & Scoring ---
        text_to_classify = parsed_data.get('body_text') or parsed_data.get('subject') or ""
        ml_result = classify_email(text_to_classify)
        
        anomaly_flags = security_results.get('anomaly_flags', [])
        if geo_data.get('is_tor'):
            anomaly_flags.append("Origin IP is a known Tor exit node")
        elif geo_data.get('is_vpn_or_hosting'):
            anomaly_flags.append("Origin IP is from a VPN/Hosting provider (Non-residential)")
            
        fraud_score_details = calculate_fraud_score(ml_result, anomaly_flags)
        parsed_data['fraud_assessment'] = fraud_score_details
        
        # --- PHASE 5: Database Persistence ---
        db_case = EmailCase(
            filename=file.filename,
            sender=parsed_data.get("sender", "unknown"),
            subject=parsed_data.get("subject", "unknown"),
            fraud_score=fraud_score_details.get("fraud_score", 0.0),
            origin_country=geo_data.get("country", "Unknown"),
            ml_label=fraud_score_details.get("ml_label", "unknown"),
            full_analysis=parsed_data
        )
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        
        # Inject the database ID into the return payload for the frontend
        parsed_data['case_id'] = db_case.id
        
        return parsed_data
        
    finally:
        # Always clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/cases")
def get_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns a summarized list of all analyzed emails (for the dashboard).
    """
    cases = db.query(EmailCase).order_by(EmailCase.id.desc()).offset(skip).limit(limit).all()
    
    # Map to summary dict (excluding the massive full_analysis JSON payload)
    return [{
        "id": c.id,
        "filename": c.filename,
        "sender": c.sender,
        "subject": c.subject,
        "fraud_score": c.fraud_score,
        "origin_country": c.origin_country,
        "ml_label": c.ml_label,
        "timestamp": c.timestamp.isoformat()
    } for c in cases]

@app.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    """
    Returns the full detailed forensic analysis for a specific case ID.
    """
    case = db.query(EmailCase).filter(EmailCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.full_analysis
