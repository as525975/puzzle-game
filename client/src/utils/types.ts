export type Puzzle = {
    grid: string[][];
    name: string;
    description: string;
    difficulty: number;
    id: number;
    end_pos: [number, number];
    start_pos: [number, number];
}

export type LeaderboardEntry = {
    username: string,
    puzzle_name: string,
    total_moves: number,
    completion_time: number,
    completed_at: string,
}

export type Move = {
    action: string;
    timestamp: number;
}