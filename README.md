# Maze Puzzle Application

A full-stack maze puzzle game with FastAPI backend, PostgreSQL database, and React frontend.

## Features

- **User Authentication**: JWT-based registration and login
- **Maze Puzzles**: Navigate through mazes collecting keys to unlock doors
- **Special Elements**: Portals for teleportation, walls to avoid
- **Leaderboard**: Track successful attempts and completion times
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Architecture

### Backend (FastAPI)
- JWT authentication with user registration/login
- Maze validation logic with keys, doors, portals, and walls
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive API documentation via FastAPI's automatic OpenAPI generation

### Frontend (React)
- Puzzle selection and gameplay interface
- Visual maze representation
- Real-time move submission and validation
- Leaderboard and user statistics

### Database (PostgreSQL)
- Users table with authentication data
- Puzzles table with maze configurations
- Attempts table tracking user progress and results

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+

### Backend Setup

1. **Install dependencies**:
```bash
cd src
pip install -r requirements.txt
```

2. **Set up PostgreSQL**:
```bash
# Create database
createdb maze_puzzles

# Set environment variables
export DATABASE_URL="postgresql://postgres:5571@localhost/maze_puzzles"
export JWT_SECRET_KEY="your-secret-key-here"
```

3. **Initialize database**:
```bash
python database.py
```

4. **Run the server**:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies**:
```bash
cd client
npm install
```

2. **Start development server**:
```bash
npm start
```

The app will be available at `http://localhost:3000`

### Testing

**Backend tests**:
```bash
cd src
pytest
```

**Frontend tests**:
```bash
cd client
npm test
```

## Gameplay

### Maze Elements
- `S`: Start position
- `E`: End/Goal position  
- `#`: Wall (impassable)
- `K`: Key (must collect to unlock doors)
- `D`: Door (requires key to pass through)
- `P`: Portal (teleports to another portal)
- `.`: Empty space

### How to Play
1. Register/Login to track your progress
2. Select a puzzle from the available list
3. Navigate using arrow keys or click controls
4. Collect all keys before attempting to reach doors
5. Use portals strategically to traverse the maze
6. Reach the goal to complete the puzzle

### API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication  
- `GET /puzzles` - List available puzzles
- `GET /puzzles/{id}` - Get specific puzzle details
- `POST /puzzles/{id}/attempt` - Submit solution attempt
- `GET /leaderboard` - View top completions

## Database Schema

### Users
- id, username, email, hashed_password, created_at

### Puzzles  
- id, name, description, grid, start_pos, end_pos, created_at

### Attempts
- id, user_id, puzzle_id, moves, is_valid, completed_at, completion_time

## Development Approach

1. **API-First Design**: Used FastAPI's automatic documentation generation to define clear contracts
2. **Separation of Concerns**: Clean separation between authentication, game logic, and data persistence
3. **Validation**: Server-side validation ensures game integrity
4. **Testing**: Unit tests for critical game logic and API endpoints
5. **User Experience**: Intuitive React interface with visual feedback

## Future Enhancements

- Multiple difficulty levels
- Real-time multiplayer competitions
- Puzzle editor for user-created content
- Advanced statistics and analytics
- Mobile-responsive design improvements