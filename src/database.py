from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/maze_puzzles")

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
    
    # Relationship with attempts
    attempts = relationship("Attempt", back_populates="user")

class Puzzle(Base):
    __tablename__ = "puzzles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    grid = Column(JSON, nullable=False)  # 2D array representing the maze
    start_pos = Column(JSON, nullable=False)  # [row, col] position
    end_pos = Column(JSON, nullable=False)    # [row, col] position
    created_at = Column(DateTime, default=func.now())
    
    # Relationship with attempts
    attempts = relationship("Attempt", back_populates="puzzle")

class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    puzzle_id = Column(Integer, nullable=False)
    moves = Column(JSON, nullable=False)  # Array of move strings
    is_valid = Column(Boolean, nullable=False)
    completion_time = Column(Float)  # Time in seconds (only for valid attempts)
    completed_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="attempts")
    puzzle = relationship("Puzzle", back_populates="attempts")

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def seed_puzzles():
    """Seed the database with initial puzzles"""
    db = SessionLocal()
    
    # Check if puzzles already exist
    existing_puzzles = db.query(Puzzle).count()
    if existing_puzzles > 0:
        print("Puzzles already seeded")
        db.close()
        return
    
    puzzles = [
        {
            "name": "Simple Start",
            "description": "A basic maze to get you started. Collect the key to open the door!",
            "grid": [
                ["S", ".", ".", "#", "K"],
                ["#", ".", "#", ".", "."],
                [".", ".", ".", "#", "D"],
                ["#", ".", "#", ".", "."],
                [".", ".", ".", ".", "E"]
            ],
            "start_pos": (0, 0),
            "end_pos": (4, 4)
        },
        {
            "name": "Portal Challenge",
            "description": "Use the portals wisely! They can teleport you across the maze.",
            "grid": [
                ["S", "#", "K", "#", "."],
                [".", "#", ".", "#", "P"],
                ["#", ".", ".", ".", "#"],
                ["P", "#", ".", "#", "D"],
                [".", ".", ".", ".", "E"]
            ],
            "start_pos": (0, 0),
            "end_pos": (4, 4)
        },
        {
            "name": "Multiple Keys",
            "description": "This maze requires collecting multiple keys. Plan your route carefully!",
            "grid": [
                ["S", ".", "K", "#", ".", "#", "K"],
                ["#", ".", ".", ".", ".", "#", "."],
                [".", "#", "#", "D", "#", ".", "."],
                ["K", ".", ".", "#", ".", ".", "D"],
                [".", "#", ".", ".", ".", "#", "."],
                [".", ".", "#", "D", "#", ".", "."],
                [".", ".", ".", ".", ".", ".", "E"]
            ],
            "start_pos": (0, 0),
            "end_pos": (6, 6)
        }
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