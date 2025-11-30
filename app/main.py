#!/usr/bin/env python3
"""
IPMS Web Application
Modern Intellectual Property Management System with migration capabilities
"""

from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get project root
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "app" / "templates"
STATIC_DIR = ROOT / "app" / "static"
DATA_DIR = ROOT / "data" / "legacy_csv"
VALIDATION_REPORTS_DIR = ROOT / "data" / "validation_reports"

# Create directories if they don't exist
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="IPMS - Intellectual Property Management System",
    description="Modern IPMS with legacy data migration capabilities",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Import ETL modules
import sys
sys.path.append(str(ROOT / "etl"))

try:
    from generate_mock_data import main as generate_data
    from validate import IPMSDataValidator
    from transform_utils import validate_data_quality
except ImportError as e:
    logger.warning(f"Could not import ETL modules: {e}")
    generate_data = None
    IPMSDataValidator = None

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    # Get data statistics
    stats = await get_data_statistics()
    
    # Get latest validation report
    latest_validation = await get_latest_validation_report()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "validation": latest_validation,
        "title": "IPMS Dashboard"
    })

@app.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    """Clients management page"""
    clients_data = await load_csv_data("clients.csv")
    
    return templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": clients_data.to_dict('records') if clients_data is not None else [],
        "title": "Client Management"
    })

@app.get("/patents", response_class=HTMLResponse)
async def patents_page(request: Request):
    """Patents management page"""
    patents_data = await load_csv_data("patents.csv")
    
    return templates.TemplateResponse("patents.html", {
        "request": request,
        "patents": patents_data.to_dict('records') if patents_data is not None else [],
        "title": "Patent Portfolio"
    })

@app.get("/trademarks", response_class=HTMLResponse)
async def trademarks_page(request: Request):
    """Trademarks management page"""
    trademarks_data = await load_csv_data("trademarks.csv")
    
    return templates.TemplateResponse("trademarks.html", {
        "request": request,
        "trademarks": trademarks_data.to_dict('records') if trademarks_data is not None else [],
        "title": "Trademark Portfolio"
    })

@app.get("/deadlines", response_class=HTMLResponse)
async def deadlines_page(request: Request):
    """Deadlines management page"""
    deadlines_data = await load_csv_data("deadlines.csv")
    
    # Filter upcoming deadlines
    if deadlines_data is not None:
        # Sort by due date
        deadlines_data = deadlines_data.sort_values('due_date')
        
        # Add urgency classification
        today = datetime.now().date()
        deadlines_records = []
        
        for _, row in deadlines_data.iterrows():
            record = row.to_dict()
            try:
                due_date = pd.to_datetime(record['due_date']).date()
                days_until = (due_date - today).days
                
                if days_until < 0:
                    record['urgency'] = 'overdue'
                elif days_until <= 7:
                    record['urgency'] = 'critical'
                elif days_until <= 30:
                    record['urgency'] = 'high'
                elif days_until <= 90:
                    record['urgency'] = 'medium'
                else:
                    record['urgency'] = 'low'
                
                record['days_until'] = days_until
            except:
                record['urgency'] = 'unknown'
                record['days_until'] = None
            
            deadlines_records.append(record)
    else:
        deadlines_records = []
    
    return templates.TemplateResponse("deadlines.html", {
        "request": request,
        "deadlines": deadlines_records,
        "title": "Deadlines & Renewals"
    })

@app.get("/migration", response_class=HTMLResponse)
async def migration_page(request: Request):
    """Migration management page"""
    return templates.TemplateResponse("migration.html", {
        "request": request,
        "title": "Data Migration"
    })

@app.get("/validation", response_class=HTMLResponse)
async def validation_page(request: Request):
    """Data validation page"""
    validation_reports = await get_validation_reports()
    latest_report = await get_latest_validation_report()
    
    return templates.TemplateResponse("validation.html", {
        "request": request,
        "reports": validation_reports,
        "latest": latest_report,
        "title": "Data Validation"
    })

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports and analytics page"""
    stats = await get_data_statistics()
    analytics = await get_analytics_data()
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "stats": stats,
        "analytics": analytics,
        "title": "Reports & Analytics"
    })

# API Endpoints
@app.get("/api/stats")
async def api_get_stats():
    """Get system statistics"""
    return await get_data_statistics()

@app.get("/api/validation/latest")
async def api_get_latest_validation():
    """Get latest validation report"""
    return await get_latest_validation_report()

@app.post("/api/validation/run")
async def api_run_validation(background_tasks: BackgroundTasks):
    """Run data validation"""
    if IPMSDataValidator is None:
        raise HTTPException(status_code=500, detail="Validation system not available")
    
    background_tasks.add_task(run_validation_background)
    return {"message": "Validation started", "status": "running"}

@app.post("/api/data/generate")
async def api_generate_data(background_tasks: BackgroundTasks):
    """Generate mock data"""
    if generate_data is None:
        raise HTTPException(status_code=500, detail="Data generator not available")
    
    background_tasks.add_task(run_data_generation_background)
    return {"message": "Data generation started", "status": "running"}

@app.get("/api/clients")
async def api_get_clients(limit: int = 100, offset: int = 0):
    """Get clients data"""
    clients_data = await load_csv_data("clients.csv")
    if clients_data is None:
        return {"clients": [], "total": 0}
    
    total = len(clients_data)
    clients = clients_data.iloc[offset:offset+limit].to_dict('records')
    
    return {"clients": clients, "total": total, "limit": limit, "offset": offset}

@app.get("/api/patents")
async def api_get_patents(limit: int = 100, offset: int = 0):
    """Get patents data"""
    patents_data = await load_csv_data("patents.csv")
    if patents_data is None:
        return {"patents": [], "total": 0}
    
    total = len(patents_data)
    patents = patents_data.iloc[offset:offset+limit].to_dict('records')
    
    return {"patents": patents, "total": total, "limit": limit, "offset": offset}

@app.get("/api/trademarks")
async def api_get_trademarks(limit: int = 100, offset: int = 0):
    """Get trademarks data"""
    trademarks_data = await load_csv_data("trademarks.csv")
    if trademarks_data is None:
        return {"trademarks": [], "total": 0}
    
    total = len(trademarks_data)
    trademarks = trademarks_data.iloc[offset:offset+limit].to_dict('records')
    
    return {"trademarks": trademarks, "total": total, "limit": limit, "offset": offset}

@app.get("/api/deadlines")
async def api_get_deadlines(limit: int = 100, offset: int = 0, urgency: Optional[str] = None):
    """Get deadlines data"""
    deadlines_data = await load_csv_data("deadlines.csv")
    if deadlines_data is None:
        return {"deadlines": [], "total": 0}
    
    # Filter by urgency if specified
    if urgency:
        # This would require processing urgency in real-time
        pass
    
    total = len(deadlines_data)
    deadlines = deadlines_data.iloc[offset:offset+limit].to_dict('records')
    
    return {"deadlines": deadlines, "total": total, "limit": limit, "offset": offset}

# Helper functions
async def load_csv_data(filename: str) -> Optional[pd.DataFrame]:
    """Load CSV data"""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return None
    
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return None

async def get_data_statistics() -> Dict[str, Any]:
    """Get data statistics"""
    stats = {
        "clients": 0,
        "patents": 0,
        "trademarks": 0,
        "deadlines": 0,
        "last_updated": None
    }
    
    for entity in ["clients", "patents", "trademarks", "deadlines"]:
        data = await load_csv_data(f"{entity}.csv")
        if data is not None:
            stats[entity] = len(data)
    
    # Get last modification time
    files = list(DATA_DIR.glob("*.csv"))
    if files:
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        stats["last_updated"] = datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
    
    return stats

async def get_latest_validation_report() -> Optional[Dict[str, Any]]:
    """Get the latest validation report"""
    if not VALIDATION_REPORTS_DIR.exists():
        return None
    
    report_files = list(VALIDATION_REPORTS_DIR.glob("validation_report_*.json"))
    if not report_files:
        return None
    
    # Get the most recent report
    latest_file = max(report_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading validation report: {e}")
        return None

async def get_validation_reports() -> List[Dict[str, Any]]:
    """Get all validation reports"""
    if not VALIDATION_REPORTS_DIR.exists():
        return []
    
    reports = []
    report_files = sorted(
        VALIDATION_REPORTS_DIR.glob("validation_report_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    for report_file in report_files[:10]:  # Get last 10 reports
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
                report['filename'] = report_file.name
                reports.append(report)
        except Exception as e:
            logger.error(f"Error loading report {report_file}: {e}")
    
    return reports

async def get_analytics_data() -> Dict[str, Any]:
    """Get analytics data for reports"""
    analytics = {
        "patent_status_distribution": {},
        "trademark_status_distribution": {},
        "deadlines_by_priority": {},
        "clients_by_type": {},
        "filing_trends": {}
    }
    
    # Patent status distribution
    patents_data = await load_csv_data("patents.csv")
    if patents_data is not None:
        status_counts = patents_data['status'].value_counts().to_dict()
        analytics["patent_status_distribution"] = status_counts
    
    # Trademark status distribution
    trademarks_data = await load_csv_data("trademarks.csv")
    if trademarks_data is not None:
        status_counts = trademarks_data['status'].value_counts().to_dict()
        analytics["trademark_status_distribution"] = status_counts
    
    # Deadlines by priority
    deadlines_data = await load_csv_data("deadlines.csv")
    if deadlines_data is not None:
        priority_counts = deadlines_data['priority'].value_counts().to_dict()
        analytics["deadlines_by_priority"] = priority_counts
    
    # Clients by type
    clients_data = await load_csv_data("clients.csv")
    if clients_data is not None:
        type_counts = clients_data['client_type'].value_counts().to_dict()
        analytics["clients_by_type"] = type_counts
    
    return analytics

async def run_validation_background():
    """Run validation in background"""
    try:
        validator = IPMSDataValidator()
        validator.validate_all()
        logger.info("Background validation completed")
    except Exception as e:
        logger.error(f"Background validation failed: {e}")

async def run_data_generation_background():
    """Run data generation in background"""
    try:
        generate_data()
        logger.info("Background data generation completed")
    except Exception as e:
        logger.error(f"Background data generation failed: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
