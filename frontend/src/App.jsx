import React, { useState, useEffect, useLayoutEffect } from 'react';
import './App.css';

const ITEMS_PER_PAGE = 25;

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [truncatedBios, setTruncatedBios] = useState({});

  useEffect(() => {
    fetch('./data.json')
      .then((response) => response.json())
      .then((data) => {
        const rankedData = data.map((sponsor, index) => ({
          ...sponsor,
          rank: index + 1,
        }));
        setData(rankedData);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data: ", error);
        setLoading(false);
      });
  }, []);

  const filteredData = data.filter(sponsor =>
    sponsor.login.toLowerCase().includes(filter.toLowerCase())
  );

  const paginatedData = filteredData.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  useLayoutEffect(() => {
    const newTruncatedBios = {};
    const bioElements = document.querySelectorAll('.bio');
    bioElements.forEach(el => {
      if (el.scrollWidth > el.clientWidth) {
        const login = el.dataset.login;
        newTruncatedBios[login] = true;
      }
    });

    // Only update the state if the truncated bios have changed
    if (JSON.stringify(newTruncatedBios) !== JSON.stringify(truncatedBios)) {
      setTruncatedBios(newTruncatedBios);
    }
  }, [paginatedData, truncatedBios]);

  const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);

  return (
    <div className="container">
      <h1>GitHub Top Sponsors</h1>
      <div className="filters">
        <input
          type="text"
          placeholder="Filter by name..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>
      {loading ? (
        <p>Loading data...</p>
      ) : (
        <div className="sponsor-list">
          {paginatedData.map((sponsor) => {
            let cardClassName = 'sponsor-card';
            if (sponsor.rank === 1) cardClassName += ' gold';
            if (sponsor.rank === 2) cardClassName += ' silver';
            if (sponsor.rank === 3) cardClassName += ' bronze';

            return (
              <div key={sponsor.login} className={cardClassName}>
                <div className="rank-number">{sponsor.rank}</div>
                <img src={sponsor.avatar_url} alt={`${sponsor.login} avatar`} className="sponsor-avatar" data-tooltip={sponsor.bio} />
                <div className="sponsor-details">
                    <div className="name-location">
                        <h2><a href={sponsor.html_url} target="_blank" rel="noopener noreferrer">{sponsor.login}</a></h2>
                    </div>
                    {sponsor.location && (
                        <span className="location">
                            📍 {sponsor.location}
                        </span>
                    )}
                </div>
                <div className="sponsor-stats">
                    <div className="stat">
                        <strong>{sponsor.followers}</strong>
                        <span>Followers</span>
                    </div>
                    <div className="stat">
                        <strong>{sponsor.sponsorships_count}</strong>
                        <span>Sponsors</span>
                    </div>
                <a href={`https://github.com/sponsors/${sponsor.login}`} target="_blank" rel="noopener noreferrer" className="sponsor-button">Sponsor</a>
              </div>
            );
          })}
        </div>
      )}
      {totalPages > 1 && (
        <div className="pagination">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
            <button
              key={page}
              className={currentPage === page ? 'active' : ''}
              onClick={() => setCurrentPage(page)}
            >
              {page}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
