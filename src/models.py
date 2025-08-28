from pydantic import BaseModel, EmailStr
from typing import List, Optional, Tuple
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

class PuzzleResponse(BaseModel):
    id: int
    name: str
    description: str
    grid: List[List[str]]
    start_pos: Tuple[int, int]
    end_pos: Tuple[int, int]
    difficulty: int

class AttemptRequest(BaseModel):
    moves: List[str]  # List of moves: 'up', 'down', 'left', 'right'

class AttemptResponse(BaseModel):
    is_valid: bool
    message: str
    completion_time: Optional[float]
    total_moves: int

class LeaderboardEntry(BaseModel):
    username: str
    puzzle_name: str
    completion_time: float
    total_moves: int
    completed_at: datetime