import React from 'react';
import './About.css';

const About = () => {
  return (
    <div className="about-container">
      <h1>About This Project</h1>
      <p>This project was born out of curiosity about the GitHub sponsorship ecosystem. I wanted to see who the top sponsored developers and organizations are, and what kind of projects they are working on.</p>
      <p>The data is collected using the GitHub API, and the frontend is built with React. The list is updated weekly to provide a fresh look at the top sponsors.</p>
      
      <h2>Interesting Findings</h2>
      <p>One of the most interesting findings from this data is that there is not always a direct correlation between the number of followers a user has and the number of sponsors they have. Some developers with a smaller, but highly engaged, community have more sponsors than some of the most followed users on the platform.</p>
      <p>This suggests that building a strong community and providing value to a niche audience can be more effective for gaining financial support than simply having a large number of followers.</p>

      <h2>Future Plans</h2>
      <p>I plan to continue improving this project by adding more data visualizations and historical data to track trends over time. If you have any suggestions, feel free to reach out!</p>
    </div>
  );
};

export default About;
