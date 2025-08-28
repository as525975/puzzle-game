from typing import List, Tuple

def validate_maze_solution(
    grid: List[List[str]], 
    start_pos: Tuple[int, int], 
    end_pos: Tuple[int, int], 
    moves: List[str]
) -> Tuple[bool, str]:
    """
    Validate a maze solution by simulating the player's moves.
    
    Args:
        grid: 2D array representing the maze
        start_pos: Starting position (row, col)
        end_pos: Goal position (row, col)  
        moves: List of move commands ('up', 'down', 'left', 'right')
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    
    if not moves:
        return False, "No moves provided"
    
    rows, cols = len(grid), len(grid[0])
    current_pos = list(start_pos)
    keys_collected = set()
    visited_positions = set()
    
    # Find all portals in the grid
    portals = {}
    portal_positions = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'P':
                portal_positions.append((r, c))
    
    # Map portals to each other (assuming pairs)
    for i in range(0, len(portal_positions), 2):
        if i + 1 < len(portal_positions):
            pos1, pos2 = portal_positions[i], portal_positions[i + 1]
            portals[pos1] = pos2
            portals[pos2] = pos1
    
    def is_valid_position(pos: List[int]) -> bool:
        """Check if position is within bounds"""
        return 0 <= pos[0] < rows and 0 <= pos[1] < cols
    
    def can_move_to(pos: List[int]) -> Tuple[bool, str]:
        """Check if player can move to this position"""
        if not is_valid_position(pos):
            return False, "Position out of bounds"
        
        cell = grid[pos[0]][pos[1]]
        
        if cell == '#':
            return False, "Cannot move through walls"
        
        if cell == 'D':
            # Check if we have at least one key
            if not keys_collected:
                return False, "Need a key to pass through door"
            # Use one key
            keys_collected.pop()
            return True, "Used key to pass through door"
        
        return True, "Valid move"
    
    # Simulate each move
    for i, move in enumerate(moves):
        visited_positions.add(tuple(current_pos))
        
        # Calculate new position based on move
        new_pos = current_pos.copy()
        if move == 'up':
            new_pos[0] -= 1
        elif move == 'down':
            new_pos[0] += 1
        elif move == 'left':
            new_pos[1] -= 1
        elif move == 'right':
            new_pos[1] += 1
        else:
            return False, f"Invalid move '{move}' at step {i + 1}"
        
        # Check if move is valid
        can_move, move_message = can_move_to(new_pos)
        if not can_move:
            return False, f"Invalid move at step {i + 1}: {move_message}"
        
        # Update position
        current_pos = new_pos
        cell = grid[current_pos[0]][current_pos[1]]
        
        # Handle special cells
        if cell == 'K':
            keys_collected.add((current_pos[0], current_pos[1]))
        elif cell == 'P':
            # Teleport through portal
            portal_pos = tuple(current_pos)
            if portal_pos in portals:
                destination = portals[portal_pos]
                current_pos = [destination[0], destination[1]]
        
        # Check if we've reached the goal
        if tuple(current_pos) == end_pos:
            return True, f"Congratulations! Maze completed in {len(moves)} moves!"
    
    # If we finish all moves but haven't reached the goal
    if tuple(current_pos) == end_pos:
        return True, f"Congratulations! Maze completed in {len(moves)} moves!"
    else:
        return False, f"Did not reach the goal. Final position: ({current_pos[0]}, {current_pos[1]}), Goal: {end_pos}"

def get_maze_info(grid: List[List[str]]) -> dict:
    """
    Get information about a maze including key positions, doors, and portals.
    
    Args:
        grid: 2D array representing the maze
        
    Returns:
        Dictionary with maze information
    """
    rows, cols = len(grid), len(grid[0])
    keys = []
    doors = []
    portals = []
    walls = []
    
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell == 'K':
                keys.append((r, c))
            elif cell == 'D':
                doors.append((r, c))
            elif cell == 'P':
                portals.append((r, c))
            elif cell == '#':
                walls.append((r, c))
    
    return {
        'dimensions': (rows, cols),
        'keys': keys,
        'doors': doors,
        'portals': portals,
        'walls': walls,
        'total_keys': len(keys),
        'total_doors': len(doors)
    }