#!/usr/bin/env python3
"""
Minimal test server to verify FastAPI works
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Simple Test Server")

@app.get("/")
async def root():
    return {"message": "Server is working!", "status": "ok"}

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

if __name__ == "__main__":
    print("🧪 Starting minimal test server...")
    print("📖 Visit: http://localhost:8080/")
    print("📖 Docs: http://localhost:8080/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
        log_level="debug"
    )