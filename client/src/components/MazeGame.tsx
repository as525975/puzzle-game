import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import './MazeGameStyles.scss';
import '../styles.scss';
import { Move, Puzzle } from '../utils/types';
import axios from 'axios';

const MazeGame = () => {
  const { id } = useParams();
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null);
  const [playerPos, setPlayerPos] = useState([0, 0]);
  const [moves, setMoves] = useState<Move[]>([]);
  const [keysCollected, setKeysCollected] = useState(new Set());
  const [gameStatus, setGameStatus] = useState('playing'); // playing, won, lost
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPuzzle();
  }, []);

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (gameStatus !== 'playing') return;

      switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
          e.preventDefault();
          handleMove('up');
          break;
        case 'ArrowDown':
        case 's':
        case 'S':
          e.preventDefault();
          handleMove('down');
          break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
          e.preventDefault();
          handleMove('left');
          break;
        case 'ArrowRight':
        case 'd':
        case 'D':
          e.preventDefault();
          handleMove('right');
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [gameStatus, playerPos, keysCollected]);

  const fetchPuzzle = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get(`/puzzles/${id}`, { headers });
      setPuzzle(response.data);
      setPlayerPos(response.data.start_pos);
      setLoading(false);
    } catch (error) {
      setMessage('Failed to load puzzle');
      setLoading(false);
    }
  };

  const handleMove = useCallback((direction: string) => {
    if (!puzzle || gameStatus !== 'playing') return;

    const [row, col] = playerPos;
    let newPos = [row, col];

    switch (direction) {
      case 'up':
        newPos = [row - 1, col];
        break;
      case 'down':
        newPos = [row + 1, col];
        break;
      case 'left':
        newPos = [row, col - 1];
        break;
      case 'right':
        newPos = [row, col + 1];
        break;
      default:
        return;
    }

    // Check bounds
    if (newPos[0] < 0 || newPos[0] >= puzzle.grid.length ||
      newPos[1] < 0 || newPos[1] >= puzzle.grid[0].length) {
      setMessage('Cannot move out of bounds!');
      return;
    }

    const newCell = puzzle.grid[newPos[0]][newPos[1]];

    // Check for walls
    if (newCell === '#') {
      setMessage('Cannot move through walls!');
      return;
    }

    // Check for doors
    if (newCell === 'D') {
      if (keysCollected.size === 0) {
        setMessage('You need a key to pass through this door!');
        return;
      }
      // Use a key
      const keyArray = Array.from(keysCollected);
      const newKeys = new Set(keysCollected);
      newKeys.delete(keyArray[0]);
      setKeysCollected(newKeys);
      setMessage('Used a key to open the door!');
    }

    // Update position
    setPlayerPos(newPos);
    setMoves(prevMoves => [...prevMoves, {
      action: direction,
      timestamp: Date.now()
    }]);

    // Handle special cells
    if (newCell === 'K') {
      const keyPos = `${newPos[0]},${newPos[1]}`;
      if (!keysCollected.has(keyPos)) {
        setKeysCollected(prev => new Set([...prev, keyPos]));
        setMessage('Collected a key!');
      }
    } else if (newCell.startsWith('P')) {
      // Find the other portal
      const otherPortal = puzzle.portal_pairs[parseInt(newCell.substring(1))]?.find(
        ([r, c]) => r !== newPos[0] || c !== newPos[1]
      );

      if (otherPortal) {
        setPlayerPos(otherPortal);
        setMessage('Teleported through portal!');
      }
    } else {
      setMessage('');
    }

    // Check if reached the goal
    if (newPos[0] === puzzle.end_pos[0] && newPos[1] === puzzle.end_pos[1]) {
      setGameStatus('won');
      setMessage('Congratulations! You completed the maze!');
      submitSolution([...moves, { action: direction, timestamp: Date.now() }]);
    }
  }, [puzzle, playerPos, keysCollected, gameStatus, moves]);

  const submitSolution = async (finalMoves: Move[]) => {
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setMessage('You must be logged in to submit your solution');
        return;
      }
      const response = await axios.post(`/puzzles/${id}/attempt`, {
        moves: finalMoves,
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json' 
        },
        withCredentials: true,
      });

      if (response.data.is_valid) {
        setGameStatus('won');
        setMessage(
          `${response.data.message} Time: ${(response.data.completion_time / 1000).toFixed(2)}s`
        );
      } else {
        setGameStatus('lost');
        setMessage(response.data.message);
      }
    } catch (error) {
      console.error(error);
      if (error.response?.status === 401 || error.response?.status === 403) {
        setMessage('Authentication failed. Please log in again.');
      } else {
        setMessage('Failed to submit solution. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const resetGame = () => {
    if (!puzzle) return;
    setPlayerPos(puzzle.start_pos);
    setMoves([]);
    setKeysCollected(new Set());
    setGameStatus('playing');
    setMessage('');
  };

  const getCellDisplay = (cell: string, rowIndex: number, colIndex: number) => {
    const isPlayer = rowIndex === playerPos[0] && colIndex === playerPos[1];

    if (isPlayer) {
      return { content: '😊', className: 'player' };
    }

    switch (cell) {
      case 'S':
        return { content: 'S', className: 'start' };
      case 'E':
        return { content: 'E', className: 'end' };
      case '#':
        return { content: '', className: 'wall' };
      case 'K':
        const keyPos = `${rowIndex},${colIndex}`;
        return keysCollected.has(keyPos)
          ? { content: '', className: 'empty' }
          : { content: '🗝️', className: 'key' };
      case 'D':
        return { content: '🚪', className: 'door' };
      default:
        if (cell.startsWith('P')) {
          // Check if it's any P followed by a number (P1, P2, P3, etc.)
          return { content: '🌀', className: 'portal' };
        }
        return { content: '', className: 'empty' };
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading puzzle...</p>
      </div>
    );
  }

  if (!puzzle) {
    return (
      <div className="error-message" style={{ maxWidth: '600px', margin: '2rem auto' }}>
        Puzzle not found
      </div>
    );
  }

  return (
    <div className="maze-container">
      <div className="maze-header">
        <h1 className="maze-title">{puzzle.name}</h1>
        <p className="maze-description">{puzzle.description}</p>

        <div className="maze-stats">
          <span>Moves: {moves.length}</span>
          <span>Keys: {keysCollected.size}</span>
          <span>Status: {gameStatus}</span>
        </div>
      </div>

      {message && (
        <div className={gameStatus === 'won' ? 'success-message' : 'error-message'}>
          {message}
        </div>
      )}

      <div
        className="maze-grid"
        style={{
          gridTemplateColumns: `repeat(${puzzle.grid[0].length}, 1fr)`
        }}
      >
        {puzzle.grid.map((row, rowIndex) =>
          row.map((cell, colIndex) => {
            const { content, className } = getCellDisplay(cell, rowIndex, colIndex);
            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`maze-cell ${className}`}
              >
                {content}
              </div>
            );
          })
        )}
      </div>

      <div className="controls">
        <p>Use arrow keys or WASD to move, or click the buttons below:</p>

        <div className="movement-controls">
          <button
            className="control-btn"
            onClick={() => handleMove('up')}
            disabled={gameStatus !== 'playing'}
          >
            ↑
          </button>
          <button
            className="control-btn"
            onClick={() => handleMove('left')}
            disabled={gameStatus !== 'playing'}
          >
            ←
          </button>
          <button
            className="control-btn"
            onClick={() => handleMove('right')}
            disabled={gameStatus !== 'playing'}
          >
            →
          </button>
          <button
            className="control-btn"
            onClick={() => handleMove('down')}
            disabled={gameStatus !== 'playing'}
          >
            ↓
          </button>
        </div>

        <div className="footer-container">
          <button
            className="btn btn-secondary"
            onClick={resetGame}
          >
            Reset
          </button>
          <Link to="/puzzles" className="btn btn-primary">
            Back to Puzzles
          </Link>
          {gameStatus === 'won' && (
            <Link to="/leaderboard" className="btn btn-primary">
              View Leaderboard
            </Link>
          )}
        </div>

        {moves.length > 0 && (
          <div className="move-history">
            <strong>Move History:</strong> {moves.map(move => move.action).join(' → ')}
          </div>
        )}
      </div>

      {submitting && (
        <div className="submitting-container">
          Submitting solution...
        </div>
      )}
    </div>
  );
};

export default MazeGame;