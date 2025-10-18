import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In development, Vite serves from the root, so the path is correct.
    // In the built version, data.json will be in the same directory as index.html.
    fetch('./data.json')
      .then((response) => response.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data: ", error);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>GitHub Top Sponsors</h1>
      {loading ? (
        <p>Loading data...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Avatar</th>
              <th>Login</th>
              <th>Followers</th>
              <th>Sponsorships</th>
              <th>Profile</th>
            </tr>
          </thead>
          <tbody>
            {data && data.map(sponsor => (
              <tr key={sponsor.login}>
                <td><img src={sponsor.avatar_url} alt={`${sponsor.login} avatar`} /></td>
                <td>{sponsor.login}</td>
                <td>{sponsor.followers}</td>
                <td>{sponsor.sponsorships_count}</td>
                <td><a href={sponsor.html_url} target="_blank" rel="noopener noreferrer">View Profile</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;

