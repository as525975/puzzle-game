
import random
from collections import deque

def generate_puzzle(difficulty, name):
    """
    Generate a maze puzzle based on difficulty level.
    
    Args:
        difficulty (str): "easy", "medium", or "hard"
    
    Returns:
        dict: A puzzle dictionary with name, description, grid, start_pos, and end_pos
    """
    
    # Define difficulty parameters
    if difficulty.lower() == "easy":
        size = 5
        wall_density = 0.3
        num_keys = 1
        num_doors = 1
        num_portals = 0
        description = "A gentle introduction to maze solving. Find the key and reach the exit!"
    elif difficulty.lower() == "medium":
        size = 6
        wall_density = 0.35
        num_keys = 2
        num_doors = 2
        num_portals = 2
        description = "Navigate portals and collect keys to unlock your path to freedom!"
    elif difficulty.lower() == "hard":
        size = 7
        wall_density = 0.4
        num_keys = 3
        num_doors = 3
        num_portals = 4
        description = "A complex maze with multiple keys, doors, and portals. Master the challenge!"
    else:
        raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'")
    
    max_attempts = 100
    for attempt in range(max_attempts):
        # Initialize grid with empty spaces
        grid = [["." for _ in range(size)] for _ in range(size)]
        
        # Place start and end positions
        start_pos = (0, 0)
        end_pos = (size - 1, size - 1)
        grid[0][0] = "S"
        grid[size - 1][size - 1] = "E"
        
        # Generate walls randomly
        wall_positions = set()
        total_cells = size * size
        num_walls = int(total_cells * wall_density)
        
        # Get all possible positions except start and end
        available_positions = [(r, c) for r in range(size) for c in range(size) 
                             if (r, c) not in [start_pos, end_pos]]
        
        # Place walls
        wall_candidates = random.sample(available_positions, min(num_walls, len(available_positions)))
        for r, c in wall_candidates:
            grid[r][c] = "#"
            wall_positions.add((r, c))
        
        # Update available positions (remove walls)
        available_positions = [(r, c) for r, c in available_positions if (r, c) not in wall_positions]
        
        # Check if basic path exists from S to E (ignoring keys/doors for now)
        if not has_basic_path(grid, start_pos, end_pos, size):
            continue
        
        # Place keys
        if len(available_positions) < num_keys + num_doors + num_portals:
            continue
            
        key_positions = random.sample(available_positions, num_keys)
        for r, c in key_positions:
            grid[r][c] = "K"
        available_positions = [pos for pos in available_positions if pos not in key_positions]
        
        # Place doors
        door_positions = random.sample(available_positions, num_doors)
        for r, c in door_positions:
            grid[r][c] = "D"
        available_positions = [pos for pos in available_positions if pos not in door_positions]
        
        # Place portals
        if num_portals > 0:
            portal_positions = random.sample(available_positions, num_portals)
            for r, c in portal_positions:
                grid[r][c] = "P"
        
        # Verify the puzzle is solvable
        if is_solvable(grid, start_pos, end_pos, size, key_positions, door_positions):
            return {
                "name": name,
                "description": description,
                "grid": grid,
                "start_pos": start_pos,
                "end_pos": end_pos
            }
    
    # If we couldn't generate a valid puzzle, create a simple guaranteed solvable one
    return create_fallback_puzzle(difficulty)

def has_basic_path(grid, start, end, size):
    """Check if there's a basic path from start to end, ignoring doors."""
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        r, c = queue.popleft()
        
        if (r, c) == end:
            return True
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < size and 0 <= nc < size and 
                (nr, nc) not in visited and grid[nr][nc] != "#"):
                visited.add((nr, nc))
                queue.append((nr, nc))
    
    return False

def is_solvable(grid, start, end, size, key_positions, door_positions):
    """Check if the puzzle is solvable by simulating gameplay."""
    # State: (row, col, keys_collected, doors_opened)
    start_state = (start[0], start[1], frozenset(), frozenset())
    visited = set()
    queue = deque([start_state])
    visited.add(start_state)
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        r, c, keys, opened_doors = queue.popleft()
        
        # Check if we reached the end
        if (r, c) == end:
            return True
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            if not (0 <= nr < size and 0 <= nc < size):
                continue
            
            cell = grid[nr][nc]
            
            # Can't move through walls
            if cell == "#":
                continue
            
            # Can't move through doors without enough keys
            if cell == "D" and (nr, nc) not in opened_doors:
                if len(keys) == 0:
                    continue
                # Use a key to open this door
                new_keys = set(keys)
                if new_keys:
                    new_keys.pop()  # Remove one key
                new_opened = opened_doors | {(nr, nc)}
                new_state = (nr, nc, frozenset(new_keys), new_opened)
            else:
                # Collect key if present
                new_keys = keys
                if cell == "K" and (nr, nc) in [(kp[0], kp[1]) for kp in key_positions]:
                    new_keys = keys | {(nr, nc)}
                
                new_state = (nr, nc, new_keys, opened_doors)
            
            if new_state not in visited:
                visited.add(new_state)
                queue.append(new_state)
    
    return False

def create_fallback_puzzle(difficulty):
    """Create a simple, guaranteed solvable puzzle as fallback."""
    if difficulty.lower() == "easy":
        return {
            "name": "Simple Path",
            "description": "A straightforward maze to get you started!",
            "grid": [
                ["S", ".", ".", ".", "K"],
                ["#", ".", "#", "#", "."],
                [".", ".", ".", "#", "D"],
                ["#", ".", "#", ".", "."],
                [".", ".", ".", ".", "E"]
            ],
            "start_pos": (0, 0),
            "end_pos": (4, 4)
        }
    elif difficulty.lower() == "medium":
        return {
            "name": "Portal Adventure",
            "description": "Use portals and collect keys to reach the exit!",
            "grid": [
                ["S", "#", "K", "#", "."],
                [".", ".", ".", "#", "P"],
                ["#", ".", "#", "#", "."],
                ["P", ".", ".", "#", "D"],
                [".", "#", "K", "D", "E"]
            ],
            "start_pos": (0, 0),
            "end_pos": (4, 4)
        }
    else:  # hard
        return {
            "name": "Ultimate Challenge",
            "description": "A complex maze with multiple keys, doors, and portals!",
            "grid": [
                ["S", ".", "K", "#", ".", "#", "K"],
                ["#", ".", ".", ".", ".", "#", "."],
                [".", "#", "#", "D", "#", ".", "P"],
                ["K", ".", ".", ".", ".", ".", "D"],
                [".", "#", "P", ".", "P", "#", "."],
                [".", ".", "#", "D", "#", ".", "P"],
                [".", ".", ".", ".", ".", ".", "E"]
            ],
            "start_pos": (0, 0),
            "end_pos": (6, 6)
        }