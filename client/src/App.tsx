import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './styles.scss';

// Components
import Login from './components/Login';
import Register from './components/Register';
import PuzzleList from './components/PuzzleList';
import MazeGame from './components/MazeGame';
import Leaderboard from './components/Leaderboard';
import Navigation from './components/Navigation';

axios.defaults.baseURL = 'http://localhost:8000';
function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token is still valid by trying to fetch puzzles
      axios.get('/puzzles')
        .then(() => {
          const userData = JSON.parse(localStorage.getItem('user') || '{}');
          setUser(userData);
        })
        .catch(() => {
          // Token is invalid
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', JSON.stringify(userData));
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Navigation user={user} onLogout={logout} />
        <main className="main-content">
          <Routes>
            <Route 
              path="/login" 
              element={!user ? <Login onLogin={login} /> : <Navigate to="/puzzles" />} 
            />
            <Route 
              path="/register" 
              element={!user ? <Register onLogin={login} /> : <Navigate to="/puzzles" />} 
            />
            <Route 
              path="/puzzles" 
              element={user ? <PuzzleList /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/puzzle/:id" 
              element={user ? <MazeGame /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/leaderboard" 
              element={user ? <Leaderboard /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/" 
              element={<Navigate to={user ? "/puzzles" : "/login"} />} 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;