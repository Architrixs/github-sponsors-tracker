// Header component
import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header>
      <h1>GitHub Top Sponsored</h1>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
      </nav>
      <a href="https://github.com/sponsors/Architrixs" target="_blank" rel="noopener noreferrer" title="Go on, you know you want to!" className="sponsor-me-link">Sponsor Me</a>
    </header>
  );
};

export default Header;
