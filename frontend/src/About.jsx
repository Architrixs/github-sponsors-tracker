import React, { useState, useEffect } from 'react';
import './About.css';

const About = () => {
  const [strategySummary, setStrategySummary] = useState(null);

  useEffect(() => {
    // Try to load per-strategy summary if available
    fetch('./strategies/strategies_summary.json')
      .then((res) => res.ok ? res.json() : null)
      .then((data) => setStrategySummary(data))
      .catch(() => {});
  }, []);

  return (
    <div className="about-container">
      <h1>About This Project</h1>
      <div className="last-updated-badge">Last edited: September 15, 2026</div>
      <p>
        I got curious about who's getting sponsored on GitHub and decided to track the top sponsored developers 
        and organizations. Built a scraper, ran it weekly, and found some interesting patterns in the data.
      </p>
      
      <h2>What I Found</h2>
      
      <p>
        <strong>Organizations dominate.</strong> They average {strategySummary ? Math.round(strategySummary.strategies.organizations?.avg_sponsors_per_user || 56) : 56} sponsors 
        each ({strategySummary ? strategySummary.strategies.organizations?.total_sponsors || 272 : 272} orgs found)—nearly double 
        what individual developers get. Makes sense. Projects like Homebrew or Neovim have massive user bases.
      </p>

      <p>
        <strong>More followers doesn't mean more sponsors.</strong> Super popular devs (10K+ followers) average {strategySummary ? Math.round(strategySummary.strategies.stars?.avg_sponsors_per_user || 58) : 58} sponsors 
        each, but I only found {strategySummary ? strategySummary.strategies.stars?.total_sponsors || 46 : 46} of them. Meanwhile, prolific developers with 100+ repos ({strategySummary ? strategySummary.strategies.repos?.total_sponsors || 310 : 310} found) 
        average {strategySummary ? Math.round(strategySummary.strategies.repos?.avg_sponsors_per_user || 29) : 29} sponsors. Smaller audience, better engagement.
      </p>

      <p>
        <strong>Prolific creators win.</strong> People with tons of repositories (100+) have loyal followings. 
        They might not be famous, but they're productive and people notice.
      </p>

      <p>
        <strong>Experience matters.</strong> Accounts that are 2+ years old with consistent output ({strategySummary ? strategySummary.strategies.established?.total_sponsors || 339 : 339} found) 
        average {strategySummary ? Math.round(strategySummary.strategies.established?.avg_sponsors_per_user || 37) : 37} sponsors. People trust developers who stick around.
      </p>

      <p>
        <strong>Being mega-popular is rare.</strong> Only {strategySummary ? strategySummary.strategies.stars?.total_sponsors || 46 : 46} developers with 10K+ followers are sponsorable. 
        At that level you're basically a celebrity and most of your followers are passive.
      </p>
      
      <h2>How It Works</h2>
      <p>
        Every week, a Python script queries GitHub's API using different search strategies. Each strategy 
        fetches up to 10 pages (around 1,000 users):
      </p>
      <ul>
        <li><strong>followers</strong> — popular devs (2K+ followers)</li>
        <li><strong>repos</strong> — prolific creators (100+ repos)</li>
        <li><strong>established</strong> — veterans (2+ years old)</li>
        <li><strong>stars</strong> — the celebrities (10K+ followers)</li>
        <li><strong>active</strong> — balanced maintainers (50+ repos, decent following)</li>
        <li><strong>organizations</strong> — projects like Homebrew, Neovim, etc.</li>
      </ul>

      <p>
        I filter out anyone with fewer than 5 sponsors and merge everything into one ranked list. 
        The site shows followers, repos, and sponsor count for each developer or organization.
      </p>

      <p>
        <strong>Important:</strong> All sponsor counts shown are public sponsors only. GitHub's API doesn't 
        expose private sponsors, so the actual numbers might be higher.
      </p>

      <p>
        <strong>Note:</strong> These strategies have specific constraints (follower counts, repo counts, account age), 
        so some sponsored accounts that don't fit these criteria might not show up in the results.
      </p>

            <h2>Movement Tracking & Badges</h2>
      <p>
        Every weekly run compares current positions against the previous leaderboard to track momentum across the GitHub open-source ecosystem:
      </p>
      <div className="badge-legend">
        <div className="legend-item">
          <span className="badge badge-climbed">▲ 5</span>
          <span><strong>Climbed:</strong> Moved up in overall leaderboard ranking compared to last week.</span>
        </div>
        <div className="legend-item">
          <span className="badge badge-fell">▼ 3</span>
          <span><strong>Fell:</strong> Moved down in overall leaderboard ranking compared to last week.</span>
        </div>
        <div className="legend-item">
          <span className="badge badge-new">NEW</span>
          <span><strong>New:</strong> First time appearing on the top sponsors leaderboard.</span>
        </div>
        <div className="legend-item">
          <span className="badge badge-returned">↩ 2w</span>
          <span><strong>Returned:</strong> Re-entered the top leaderboard after being away.</span>
        </div>
      </div>
      <p>
        <strong>Overall Ranking Note:</strong> Badges reflect movements in the universal global rank. This lets you see if a maintainer is gaining ground worldwide, even when browsing filtered views like Users or Organizations.
      </p>

      <h2>Recent Updates & Bug Fixes</h2>
      <p>
        A few core improvements and bug fixes were recently deployed to make the rankings, strategies, and movement tracking dependable:
      </p>
      <ul>
        <li>
          <strong>Deterministic Ranking (Tie-Breaking):</strong> Fixed an issue where concurrent worker threads returned in arbitrary order, causing accounts with identical sponsor counts to unpredictably swap ranks week-to-week. The scraper now enforces a deterministic multi-key sort (sponsor count, followers, public repos, and username).
        </li>
        <li>
          <strong>Leaderboard-Aligned Registry:</strong> Historical tracking (first seen, last seen, best rank, streak tracker) is now strictly scoped to the public top 1,000 leaderboard, ensuring badges always match what visitors see on the site.
        </li>
      </ul>

      <h2>What's Next</h2>
      <p>
        I might keep adding more data points or visualizations if I find something interesting. 
        For now, this is just a snapshot of who's getting sponsored on GitHub—updated weekly to keep it fresh.
      </p>

      <h2>Get in Touch</h2>
      <p>
        If you have ideas for better search strategies, found something interesting in the data, or just want to 
        connect, feel free to reach out! You can find me on{' '}
        <a href="https://github.com/Architrixs" target="_blank" rel="noopener noreferrer">GitHub</a>.
      </p>
    </div>
  );
};

export default About;
