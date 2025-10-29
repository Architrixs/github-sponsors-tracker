import React, { useState } from 'react';
import './App.css';
import Tooltip from './Tooltip';

const ITEMS_PER_PAGE = 30;

function Home({ sponsors, loading }) {
  const [filter, setFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [typeFilter, setTypeFilter] = useState('user'); // 'user', 'organization', 'all'

  const filteredData = sponsors
    .filter(sponsor => {
      // Type filter
      if (typeFilter === 'user' && sponsor.type === 'organization') return false;
      if (typeFilter === 'organization' && sponsor.type !== 'organization') return false;
      // Name filter
      return sponsor.login.toLowerCase().includes(filter.toLowerCase());
    })
    .map((sponsor, index) => ({
      ...sponsor,
      filteredRank: index + 1 // Re-rank based on filtered results
    }));

  const paginatedData = filteredData.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);

  return (
    <div className="container">
      <div className="filters">
        <div className="filter-chips">
          <button 
            className={`chip ${typeFilter === 'user' ? 'active' : ''}`}
            onClick={() => { setTypeFilter('user'); setCurrentPage(1); }}
          >
            Users
          </button>
          <button 
            className={`chip ${typeFilter === 'organization' ? 'active' : ''}`}
            onClick={() => { setTypeFilter('organization'); setCurrentPage(1); }}
          >
            Organizations
          </button>
          <button 
            className={`chip ${typeFilter === 'all' ? 'active' : ''}`}
            onClick={() => { setTypeFilter('all'); setCurrentPage(1); }}
          >
            All
          </button>
        </div>
        <input
          type="text"
          placeholder="Filter by name..."
          value={filter}
          onChange={(e) => { setFilter(e.target.value); setCurrentPage(1); }}
        />
      </div>
      {loading ? (
        <p>Loading data...</p>
      ) : (
        <div className="sponsor-list">
          {paginatedData.map((sponsor) => {
            let cardClassName = 'sponsor-card';
            if (sponsor.filteredRank === 1) cardClassName += ' gold';
            if (sponsor.filteredRank === 2) cardClassName += ' silver';
            if (sponsor.filteredRank === 3) cardClassName += ' bronze';

            return (
              <div key={sponsor.login} className={cardClassName}>
                <div className="rank-number">{sponsor.filteredRank}</div>
                <Tooltip text={sponsor.bio}>
                  <img src={sponsor.avatar_url} alt={`${sponsor.login} avatar`} className="sponsor-avatar" />
                </Tooltip>
                <div className="sponsor-details">
                    <div className="name-location">
                        <h2>
                          <a href={sponsor.html_url} target="_blank" rel="noopener noreferrer">
                            {sponsor.login}
                          </a>
                          {sponsor.type === 'organization' && <span className="org-badge">ORG</span>}
                        </h2>
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

export default Home;

