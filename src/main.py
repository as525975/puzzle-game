from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import bcrypt
import uvicorn
from typing import List, Optional
import os

from database import SessionLocal, User, Puzzle, Attempt
from models import UserCreate, UserLogin, TokenResponse, PuzzleResponse, AttemptRequest, AttemptResponse, LeaderboardEntry
from logic import validate_maze_solution

app = FastAPI(
    title="Maze Puzzle API",
    description="A REST API for maze puzzle games with authentication, puzzle management, and leaderboards",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_jwt_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(user_id: int = Depends(verify_jwt_token), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/auth/register", response_model=TokenResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token
    token = create_jwt_token(new_user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username
    )

@app.post("/auth/login", response_model=TokenResponse)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    token = create_jwt_token(user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )

@app.get("/puzzles", response_model=List[PuzzleResponse])
def get_puzzles(db: Session = Depends(get_db)):
    """Get all available puzzles"""
    puzzles = db.query(Puzzle).all()
    return [
        PuzzleResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            grid=p.grid,
            start_pos=p.start_pos,
            end_pos=p.end_pos,
            difficulty=len(p.grid) * len(p.grid[0]) // 25  # Simple difficulty calculation
        )
        for p in puzzles
    ]

@app.get("/puzzles/{puzzle_id}", response_model=PuzzleResponse)
def get_puzzle(puzzle_id: int, db: Session = Depends(get_db)):
    """Get a specific puzzle by ID"""
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    
    return PuzzleResponse(
        id=puzzle.id,
        name=puzzle.name,
        description=puzzle.description,
        grid=puzzle.grid,
        start_pos=puzzle.start_pos,
        end_pos=puzzle.end_pos,
        portal_pairs=puzzle.portal_pairs,
        difficulty=len(puzzle.grid) * len(puzzle.grid[0]) // 25
    )

@app.post("/puzzles/{puzzle_id}/attempt", response_model=AttemptResponse)
def submit_attempt(
    puzzle_id: int,
    attempt: AttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    
    # Validate the solution
    is_valid, message = validate_maze_solution(
        puzzle.grid,
        puzzle.start_pos,
        puzzle.end_pos,
        puzzle.portal_pairs,
        attempt.moves
    )
    completion_time = attempt.moves[-1].timestamp - attempt.moves[0].timestamp
    
    # Save attempt to database
    new_attempt = Attempt(
        user_id=current_user.id,
        puzzle_id=puzzle_id,
        moves=[move.action for move in attempt.moves],
        is_valid=is_valid,
        completion_time=completion_time if is_valid else None
    )
    db.add(new_attempt)
    db.commit()
    
    return AttemptResponse(
        is_valid=is_valid,
        message=message,
        completion_time=completion_time if is_valid else None,
        total_moves=len(attempt.moves)
    )

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(puzzle_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get leaderboard for all puzzles or a specific puzzle"""
    
    query = db.query(Attempt, User, Puzzle).join(User).join(Puzzle).filter(
        Attempt.is_valid == True
    )
    
    if puzzle_id:
        query = query.filter(Attempt.puzzle_id == puzzle_id)
    
    attempts = query.order_by(Attempt.completion_time.asc()).limit(10).all()
    
    return [
        LeaderboardEntry(
            username=attempt.User.username,
            puzzle_name=attempt.Puzzle.name,
            completion_time=attempt.Attempt.completion_time,
            total_moves=len(attempt.Attempt.moves),
            completed_at=attempt.Attempt.completed_at
        )
        for attempt in attempts
    ]

@app.get("/")
def root():
    """API health check"""
    return {"message": "Maze Puzzle API is running!", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)