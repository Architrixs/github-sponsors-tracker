// Header component
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header>
      <h1>GitHub Top Sponsored</h1>
      <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)}>
        &#9776;
      </button>
      <nav className={`nav-links ${menuOpen ? 'open' : ''}`}>
        <Link to="/" onClick={() => setMenuOpen(false)}>Home</Link>
        <Link to="/about" onClick={() => setMenuOpen(false)}>About</Link>
      </nav>
      <a href="https://github.com/sponsors/Architrixs" target="_blank" rel="noopener noreferrer" title="Go on, you know you want to!" className="sponsor-me-link">Get me on the List!</a>
    </header>
  );
};

export default Header;
