from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Todo App Chatbot API",
    description="AI-powered todo management chatbot with natural language interface using OpenAI",
    version="1.0.0"
)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Todo App Chatbot API",
        "version": "1.0.0",
        "description": "AI-powered task management with natural language interface"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "todo-app-chatbot"}

# Include API routers
from .api.v1.chat_api import router as chat_router
from .api.v1.auth_api import router as auth_router
from .api.v1.health_api import router as health_router

app.include_router(chat_router, tags=["chat"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)