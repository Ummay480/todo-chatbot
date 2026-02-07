from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Petrol Pump Ledger Automation API",
    description="API for digitizing handwritten petrol pump ledgers with OCR, AI structure detection, and RAG chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Petrol Pump Ledger Automation API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routers
from .api.v1.ledger_upload_endpoint import router as ledger_router
from .api.v1.auth_api import router as auth_router
from .api.v1.health_api import router as health_router

app.include_router(ledger_router, prefix="/api/v1/ledger", tags=["ledger"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)