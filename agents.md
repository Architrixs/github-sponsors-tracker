# Project: GitHub Top Sponsors Showcase

## 1. Project Goal

To create a web application that identifies, tracks, and showcases the top-sponsored users and organizations on GitHub. The application will maintain an updated list of these top sponsors for display on a website.

## 2. Core Functionality: Data Acquisition

- **Method**: The primary method for data collection will be the GitHub API (likely the GraphQL API, which provides detailed sponsorship information). Direct web scraping will be avoided as it is less reliable and against GitHub's terms of service.
- **Data Points**: For each user/organization, we will aim to collect:
    - Username/Organization name.
    - Sponsorship tier information.
    - Number of sponsors (if publicly available).
    - Follower count.
    - Number of public repositories.
    - Account creation date.

## 3. Data Storage

- **Initial Choice**: **SQLite** is recommended for the initial phase. It is lightweight, serverless, and easy to manage for a focused dataset like the "top N" sponsors.
- **Future Scalability**: **MongoDB** can be considered in the future if the scope expands to store historical data, trends, or a much larger set of user information.
- **Scope**: The database will only store data for the top `N` (e.g., top 100) most sponsored entities, plus any metadata required for the application, like the total number of accounts scanned.

## 4. Update Strategy

- **Frequency**: A **weekly batch process** is the most viable and recommended approach.
- **Rationale**:
    - **API Rate Limits**: Continuous scraping would quickly exhaust GitHub API rate limits.
    - **Data Stability**: Sponsorship numbers do not change so rapidly as to require real-time updates. A weekly snapshot is sufficient to show trends.
    - **Resource Efficiency**: A scheduled task is significantly more efficient than a continuously running process.

## 5. Account Filtering and Constraints

To ensure data quality and relevance, the scraping process will apply constraints to determine which accounts to analyze. Accounts may be skipped if they meet certain criteria, such as:

- **New Accounts**: Accounts created very recently.
- **Inactive or Empty Accounts**: Accounts with zero public repositories or very low activity.
- **Low Follower Count**: A minimum follower threshold could be used as a proxy for community engagement.

## 6. Website and Display

- The ultimate goal is a website that displays the curated list of top sponsors.
- The site should also display metadata from the scraping process, such as:
    - The total number of GitHub accounts scanned/processed to date.
    - The timestamp of the last update.
  
  new changes to be made:
  1. Project Restructure for Multi-Page Navigation: To add an "About" page, I'll need to
      introduce a routing library (react-router-dom) to the project. This will allow users
      to navigate between different pages. it will decribe the project, its purpose (it was fun for me, just curious about the data), and any interesting findings.
   2. New Components: I'll create several new components:
       * A Header component with a "Sponsor Me" button and navigation links.
       * A Footer component with your "Made with ❤️ by Architrixs" message and a link to your profile.
       * An About page component to house the project write-up.
   3. Scraper and Data Enhancements:
       * I'll modify the scraper to add a last_updated timestamp to the data.json file.
       * I'll add this "Last Updated" date to the footer.
       * I'll add a section to the "About" page discussing the interesting finding that
         "most followers doesn't mean most sponsors" and other potential data insights.
