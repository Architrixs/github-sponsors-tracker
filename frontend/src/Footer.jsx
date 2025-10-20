import React from 'react';
import './Footer.css';

const Footer = ({ lastUpdated }) => {
  return (
    <footer>
      <p>Made with 💜 by <a href="https://github.com/Architrixs" target="_blank" rel="noopener noreferrer">architrixs</a></p>
      {lastUpdated && <p>Last updated: {new Date(lastUpdated).toLocaleString()} UTC</p>}
    </footer>
  );
};

export default Footer;
