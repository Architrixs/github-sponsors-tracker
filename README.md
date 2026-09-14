# GitHub Top Sponsors Tracker

Ever wondered who the most sponsored developers on GitHub are? This project tracks and showcases the top sponsored users and organizations, with some interesting findings along the way.

## What I Found

After collecting data using different search strategies, here's what stood out:

- **More followers ≠ more sponsors**: Developers with massive followings don't always have the most sponsors. Quality beats quantity.
- **Sustained output wins**: People who maintain lots of projects (100+ repos) tend to attract more sponsors than those chasing popularity.
- **Niche matters**: Focused developers with smaller, engaged communities often get better support than generalists with huge audiences.
- **Being a GitHub Star helps, but isn't everything**: Only 4-8% of top sponsored devs are official GitHub Stars. The rest earned it through their work.

The data updates weekly and you can filter by users, organizations, or view all together.

## How It Works

The scraper uses GitHub's API with multiple strategies to find sponsorable accounts:
- **followers**: Popular developers (2K+ followers)
- **repos**: Prolific creators (100+ repositories)
- **established**: Veterans (2+ year old accounts)
- **stars**: The celebrities (10K+ followers)
- **active**: Balanced maintainers (solid output + moderate following)

Each strategy captures different types of developers, giving a well-rounded picture of who's getting sponsored and why.

## Movement Tracking

The tracker monitors changes between weekly snapshots:
- **`▲ N` / `▼ N`**: Climbed or fell N positions in universal overall rank compared to the prior week.
- **`NEW`**: First time appearing on the top sponsors leaderboard.
- **`↩ Nw`**: Returned to the leaderboard after N weeks away.
- **Deterministic Ranking**: Uses multi-key tie-breaking (sponsors, followers, repos, username) to prevent thread race conditions from causing phantom rank swaps among maintainers with equal sponsor counts.
- **Respectful Tracking**: Maintains an internal history registry without publicly displaying dropped accounts.

## Tech Stack

- **Backend**: Python scraper using GitHub GraphQL API
- **Frontend**: React (Vite) for the website
- **Data**: JSON files updated weekly with per-strategy breakdowns

## Setup: GitHub Token

The scraper needs a GitHub personal access token (PAT) to call the API.

1. Create a token at https://github.com/settings/tokens → "Generate new token (classic)".
   Required scopes: `read:user` + `read:org` (the query fetches Organization fields; without `read:org` every strategy fails).
2. Local run — pick one:
   - `.env` file: `Copy-Item backend\.env.example backend\.env` (PowerShell) or `cp backend/.env.example backend/.env`, then set `GITHUB_TOKEN=ghp_...` inside. The scraper loads `backend/.env` whether you run from the repo root or `backend/`.
   - Env var: `$env:GITHUB_TOKEN="ghp_..."` (PowerShell) or `GITHUB_TOKEN=ghp_... python backend/scraper.py` (Bash).
3. Run it:
   ```
   pip install -r backend/requirements.txt
   python backend/scraper.py
   ```
4. CI (weekly workflow in `.github/workflows/update-data.yml`): save the same token as the `GH_TOKEN` repository secret (Settings → Secrets → Actions). The workflow maps it to `GITHUB_TOKEN` for the scraper.

## Check It Out

Visit the live site to explore the rankings, filter by type, and see who's leading in each category.

---

Made with 💜 by [architrixs](https://github.com/Architrixs) • Curious about the sponsorship economy on GitHub
