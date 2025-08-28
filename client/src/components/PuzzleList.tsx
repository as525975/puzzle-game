import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import { Puzzle } from '../utils/types';

const PuzzleList = () => {
  const [puzzles, setPuzzles] = useState<Puzzle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPuzzles();
  }, []);

  const fetchPuzzles = async () => {
    try {
      const response = await api.get('/puzzles');
      setPuzzles(response.data);
    } catch (error) {
      setError('Failed to load puzzles. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 3) return '#4CAF50'; // Easy - Green
    if (difficulty <= 6) return '#FF9800'; // Medium - Orange
    return '#F44336'; // Hard - Red
  };

  const getDifficultyText = (difficulty) => {
    if (difficulty <= 3) return 'Easy';
    if (difficulty <= 6) return 'Medium';
    return 'Hard';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading puzzles...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message" style={{ maxWidth: '600px', margin: '2rem auto' }}>
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ textAlign: 'center', color: 'white', marginBottom: '2rem' }}>
        Choose Your Puzzle
      </h1>
      
      <div className="puzzle-grid">
        {puzzles.map(puzzle => (
          <div key={puzzle.id} className="puzzle-card">
            <div className="puzzle-title">{puzzle.name}</div>
            <div className="puzzle-description">{puzzle.description}</div>
            
            <div className="puzzle-meta">
              <span>Size: {puzzle.grid.length}x{puzzle.grid[0].length}</span>
              <span 
                style={{ 
                  color: getDifficultyColor(puzzle.difficulty),
                  fontWeight: 'bold'
                }}
              >
                {getDifficultyText(puzzle.difficulty)}
              </span>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              {/* Show mini preview of maze elements */}
              <span>Elements:</span>
              {puzzle.grid.some(row => row.includes('K')) && 
                <span style={{ background: '#FFD700', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem' }}>
                  🗝️ Keys
                </span>
              }
              {puzzle.grid.some(row => row.includes('D')) && 
                <span style={{ background: '#8B4513', color: 'white', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem' }}>
                  🚪 Doors
                </span>
              }
              {puzzle.grid.some(row => row.includes('P')) && 
                <span style={{ background: '#9C27B0', color: 'white', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem' }}>
                  🌀 Portals
                </span>
              }
            </div>
            
            <Link 
              to={`/puzzle/${puzzle.id}`} 
              className="btn btn-primary btn-full"
            >
              Play Puzzle
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PuzzleList;