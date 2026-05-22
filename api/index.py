"""
FuelGuard AI - FastAPI Backend
Main application entry point with all API routes.

Works both locally (uvicorn api.index:app) and as a Vercel serverless function.
"""

import os
import sys
import json

# Ensure sibling modules are importable regardless of how the app is launched
# (Vercel serverless, local uvicorn from project root, etc.)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from fraud_engine import generate_delivered_fuel, analyze_transaction
from transaction_store import store
from report_generator import generate_pdf_report

# --- App setup ---
app = FastAPI(
    title="FuelGuard AI",
    description="AI-powered petrol fraud detection and fuel verification system",
    version="1.0.0",
)

# CORS — allow all origins for deployment simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / Response models ---
class SimulateRequest(BaseModel):
    requested_fuel: float = Field(
        ..., gt=0, description="Amount of fuel requested in liters"
    )


# --- Routes ---

@app.get("/api/status")
def status():
    """Health-check endpoint."""
    return {"status": "FuelGuard AI Backend Running"}


@app.post("/api/simulate-transaction")
def simulate_transaction(body: SimulateRequest):
    """
    Simulate a single fuel transaction.
    Generates a mock delivered-fuel value, runs fraud analysis,
    and stores the result.
    """
    delivered = generate_delivered_fuel(body.requested_fuel)
    analysis = analyze_transaction(body.requested_fuel, delivered)
    record = store.add(analysis)
    return record


@app.get("/api/transactions")
def get_transactions():
    """Return all stored transactions (newest first)."""
    return store.get_all()


@app.get("/api/analytics")
def get_analytics():
    """Return aggregate analytics across all transactions."""
    return store.get_analytics()


@app.get("/api/export-json")
def export_json():
    """Export all transactions as a downloadable JSON file."""
    transactions = store.get_all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions to export.")

    return JSONResponse(
        content=transactions,
        headers={
            "Content-Disposition": "attachment; filename=fuelguard_transactions.json"
        },
    )


@app.get("/api/generate-report")
def generate_report():
    """Generate a PDF report and return it as a downloadable file."""
    transactions = store.get_all()
    analytics = store.get_analytics()

    if not transactions:
        raise HTTPException(
            status_code=404, detail="No transactions available for report."
        )

    filepath = generate_pdf_report(transactions, analytics)
    if filepath is None:
        raise HTTPException(
            status_code=500,
            detail="PDF generation unavailable. Install reportlab: pip install reportlab",
        )

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath),
    )
