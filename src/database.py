from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from puzzle_create import generate_puzzle
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:5571@localhost:5433/maze_puzzles")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=func.now())

class Puzzle(Base):
    __tablename__ = "puzzles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    grid = Column(JSON, nullable=False)  # 2D array representing the maze
    start_pos = Column(JSON, nullable=False)  # [row, col] position
    end_pos = Column(JSON, nullable=False)    # [row, col] position
    created_at = Column(DateTime, default=func.now())

class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, )
    puzzle_id = Column(Integer, ForeignKey("puzzles.id", ondelete="CASCADE"), nullable=False)
    moves = Column(JSON, nullable=False)  # Array of move strings
    is_valid = Column(Boolean, nullable=False)
    completion_time = Column(Float)  # Time in seconds (only for valid attempts)
    completed_at = Column(DateTime, default=func.now())

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def seed_puzzles():
    """Seed the database with initial puzzles"""
    db = SessionLocal()
    
    # If puzzles already exist, then clear
    existing_puzzles = db.query(Puzzle).count()
    if existing_puzzles > 0:
        try:
            db.query(Puzzle).delete()
            db.commit()
        except:
            db.rollback()
            print("Failed to clear existing puzzles")
    
    puzzles = [
        generate_puzzle("easy", "Easy Adventure"),
        generate_puzzle("easy", "Simple Maze Puzzle"),
        generate_puzzle("medium", "Medium Challenge"),
        generate_puzzle("hard", "Hard Labyrinth"),
        generate_puzzle("hard", "Ultimate Puzzle"),
    ]
    
    for puzzle_data in puzzles:
        puzzle = Puzzle(**puzzle_data)
        db.add(puzzle)
    
    db.commit()
    print(f"Seeded {len(puzzles)} puzzles")
    db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Seeding puzzles...")
    seed_puzzles()
    print("Database setup complete!")