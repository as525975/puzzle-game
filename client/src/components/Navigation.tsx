import React from 'react';
import './NavigationStyles.scss';
import { Link } from 'react-router-dom';

const Navigation = ({ user, onLogout }) => {
  return (
    <nav className="navigation">
      <div className="nav-brand">
        🧩 Maze Puzzles
      </div>
      
      {user ? (
        <div className="nav-links">
          <Link to="/puzzles" className="nav-link">
            Puzzles
          </Link>
          <Link to="/leaderboard" className="nav-link">
            Leaderboard
          </Link>
          <span className="nav-user">
            Welcome, {user.username}!
          </span>
          <button 
            onClick={onLogout}
            className="btn btn-secondary"
          >
            Logout
          </button>
        </div>
      ) : (
        <div className="nav-links">
          <Link to="/login" className="nav-link">
            Login
          </Link>
          <Link to="/register" className="nav-link">
            Register
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navigation;