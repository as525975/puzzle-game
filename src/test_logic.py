import pytest
from logic import validate_maze_solution
from unittest.mock import MagicMock

### Unit Tests for the Logic Module

def test_validate_maze_solution_success():
    """Test a successful solution for a simple maze."""
    grid = [["S", ".", "E"]]
    start_pos = (0, 0)
    end_pos = (0, 2)
    moves = [MagicMock(action="right", timestamp=1000), MagicMock(action="right", timestamp=2000)]
    portal_pairs = {}
    
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, portal_pairs, moves)
    assert is_valid is True
    assert "Congratulations!" in message

def test_validate_maze_solution_fail_no_moves():
    """Test a solution with no moves."""
    grid = [["S", "E"]]
    start_pos = (0, 0)
    end_pos = (0, 1)
    moves = []
    portal_pairs = {}
    
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, portal_pairs, moves)
    assert is_valid is False
    assert "No moves provided" in message

def test_validate_maze_solution_hit_wall():
    """Test a solution that moves into a wall."""
    grid = [["S", "#", "E"]]
    start_pos = (0, 0)
    end_pos = (0, 2)
    moves = [MagicMock(action="right", timestamp=1000)]
    portal_pairs = {}
    
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, portal_pairs, moves)
    assert is_valid is False
    assert "Invalid move" in message
def test_validate_maze_solution_out__of_bounds():
    """Test a solution that goes out of bounds."""
    grid = [["S", ".", "E"]]
    start_pos = (0, 0)
    end_pos = (0, 2)
    
    # Solution with key
    moves_valid = [
        MagicMock(action="up", timestamp=1000), # Move out of bounds
    ]
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, {}, moves_valid)
    assert is_valid is False
    assert "Position out of bounds" in message

    # Solution without key
    moves_invalid = [
        MagicMock(action="right", timestamp=1000), # Move to K
        MagicMock(action="down", timestamp=2000),  # Not valid
    ]
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, {}, moves_invalid)
    assert is_valid is False
def test_validate_maze_solution_collect_key():
    """Test a solution that must collect a key to proceed."""
    grid = [["S", "K", "D", "E"]]
    start_pos = (0, 0)
    end_pos = (0, 3)
    
    # Solution with key
    moves_valid = [
        MagicMock(action="right", timestamp=1000), # Move to K
        MagicMock(action="right", timestamp=2000), # Move to D
        MagicMock(action="right", timestamp=3000)  # Move to E
    ]
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, {}, moves_valid)
    assert is_valid is True

    # Solution without key
    moves_invalid = [
        MagicMock(action="right", timestamp=1000), # Move to K
        MagicMock(action="down", timestamp=2000),  # Not valid
    ]
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, {}, moves_invalid)
    assert is_valid is False

def test_validate_maze_solution_door_without_key():
    """Test a solution that gets to a door without a key."""
    grid = [["S", "D", "K", "E"]]
    start_pos = (0, 0)
    end_pos = (0, 3)
    
    # Solution with key
    moves_valid = [
        MagicMock(action="right", timestamp=1000), # Move to D
        MagicMock(action="right", timestamp=2000), # Move to K
        MagicMock(action="right", timestamp=3000)  # Move to E
    ]
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, {}, moves_valid)
    assert is_valid is False
    assert "Need a key to pass through door" in message

    # Solution without key
    moves_invalid = [
        MagicMock(action="right", timestamp=1000), # Move to K
        MagicMock(action="down", timestamp=2000),  # Not valid
    ]
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, {}, moves_invalid)
    assert is_valid is False

def test_validate_maze_solution_with_portals():
    """Test a solution that uses a portal."""
    grid = [
        ["S", ".", "P1"],
        ["#", "#", "#"],
        ["P1", ".", "E"]
    ]
    start_pos = (0, 0)
    end_pos = (2, 2)
    portal_pairs = {1: [[0, 2], [2, 0]]}

    moves = [
        MagicMock(action="right", timestamp=1000), # S -> .
        MagicMock(action="right", timestamp=2000), # . -> P1 (teleports to P1 at (2,0))
        MagicMock(action="right", timestamp=3000), # .
        MagicMock(action="right", timestamp=4000)  # . -> E
    ]
    
    is_valid, message = validate_maze_solution(grid, start_pos, end_pos, portal_pairs, moves)
    print(is_valid, message)
    assert is_valid is True
    assert "Congratulations!" in message