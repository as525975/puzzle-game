from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import bcrypt
import uvicorn
from typing import List, Optional
import os

app = FastAPI(
    title="Maze Puzzle API",
    description="A REST API for maze puzzle games with authentication, puzzle management, and leaderboards",
    version="1.0.0"
)

@app.get("/")
def root():
    """API health check"""
    return {"message": "Maze Puzzle API is running!", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)