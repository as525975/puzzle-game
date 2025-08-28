import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { LeaderboardEntry, Puzzle } from '../../utils/types';

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPuzzle, setSelectedPuzzle] = useState('all');
  const [puzzles, setPuzzles] = useState<Puzzle[]>([]);

  useEffect(() => {
    fetchPuzzles();
    fetchLeaderboard();
  }, []);

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedPuzzle]);

  const fetchPuzzles = async () => {
    try {
      const response = await api.get('/puzzles');
      setPuzzles(response.data);
    } catch (error) {
      console.error('Failed to load puzzles');
    }
  };

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const url = selectedPuzzle === 'all' 
        ? '/leaderboard' 
        : `/leaderboard?puzzle_id=${selectedPuzzle}`;
      
      const response = await api.get(url);
      setLeaderboard(response.data);
    } catch (error) {
      setError('Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = (seconds % 60).toFixed(1);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading leaderboard...</p>
      </div>
    );
  }

  return (
    <div className="leaderboard-container">
      <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>
        🏆 Leaderboard
      </h1>

      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <label htmlFor="puzzle-select" style={{ marginRight: '1rem', fontWeight: '500' }}>
          Filter by Puzzle:
        </label>
        <select
          id="puzzle-select"
          value={selectedPuzzle}
          onChange={(e) => setSelectedPuzzle(e.target.value)}
          style={{
            padding: '0.5rem',
            borderRadius: '8px',
            border: '2px solid #e1e5e9',
            fontSize: '1rem'
          }}
        >
          <option value="all">All Puzzles</option>
          {puzzles.map(puzzle => (
            <option key={puzzle.id} value={puzzle.id}>
              {puzzle.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {leaderboard.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#666', fontSize: '1.1rem' }}>
          No completed attempts yet. Be the first to complete a puzzle!
        </div>
      ) : (
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Puzzle</th>
              <th>Time</th>
              <th>Moves</th>
              <th>Completed</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, index) => (
              <tr key={index}>
                <td>
                  <strong>
                    {index + 1}
                    {index === 0 && ' 🥇'}
                    {index === 1 && ' 🥈'}
                    {index === 2 && ' 🥉'}
                  </strong>
                </td>
                <td style={{ fontWeight: '500' }}>{entry.username}</td>
                <td>{entry.puzzle_name}</td>
                <td>{formatTime(entry.completion_time)}</td>
                <td>{entry.total_moves}</td>
                <td>{formatDate(entry.completed_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <p style={{ color: '#666' }}>
          Rankings are based on completion time. Faster times rank higher!
        </p>
      </div>
    </div>
  );
};

export default Leaderboard;