import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import Home from './Home';
import About from './About';
import './App.css';

function App() {
  const [sponsors, setSponsors] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('./data.json')
      .then((response) => response.json())
      .then((data) => {
        const rankedData = data.sponsors.map((sponsor, index) => ({
          ...sponsor,
          rank: index + 1,
        }));
        setSponsors(rankedData);
        setLastUpdated(data.last_updated);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data: ", error);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <Header />
      <Routes>
        <Route path="/" element={<Home sponsors={sponsors} loading={loading} />} />
        <Route path="/about" element={<About />} />
      </Routes>
      <Footer lastUpdated={lastUpdated} />
    </div>
  );
}

export default App;


