import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles.scss';
import './LeaderboardStyles.scss'
import { LeaderboardEntry, Puzzle } from '../utils/types';

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
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.get('/puzzles', { headers });
      setPuzzles(response.data);
    } catch (error) {
      setError('Failed to load puzzles');
    }
  };

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const url = selectedPuzzle === 'all' 
        ? '/leaderboard' 
        : `/leaderboard?puzzle_id=${selectedPuzzle}`;
      
      const response = await axios.get(url, { headers });
      setLeaderboard(response.data);
    } catch (error) {
      setError('Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (milliseconds: number) => {
    return `${(milliseconds / 1000).toFixed(2)}s`;
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
      <h1 className="leaderboard-text">
        🏆 Leaderboard
      </h1>

      <div className="leaderboard-text">
        <label htmlFor="puzzle-select" className="label-text">
          Filter by Puzzle:
        </label>
        <select
          id="puzzle-select"
          value={selectedPuzzle}
          onChange={(e) => setSelectedPuzzle(e.target.value)}
          className="select-input"
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
        <div className="empty-text-container">
          {`No completed attempts yet. Be the first to complete ${!isNaN(Number(selectedPuzzle)) ? puzzles.filter(puzzle => puzzle.id === Number(selectedPuzzle))[0].name : 'a puzzle'}!`}
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
                <td className="username-text">{entry.username}</td>
                <td>{entry.puzzle_name}</td>
                <td>{formatTime(entry.completion_time)}</td>
                <td>{entry.total_moves}</td>
                <td>{formatDate(entry.completed_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="explainer-container">
        <p className="explainer-paragraph">
          Rankings are based on completion time. Faster times rank higher!
        </p>
      </div>
    </div>
  );
};

export default Leaderboard;