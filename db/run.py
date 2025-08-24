#!/usr/bin/env python3
"""
Startup script for the Insurance Management API.
"""
import uvicorn
from db.main import app

if __name__ == "__main__":
    uvicorn.run(
        "db.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
