from datetime import datetime, timezone, timedelta
import requests
import os
import json
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API_URL = "https://api.github.com/graphql"
REST_API_URL = "https://api.github.com"

# Rate limiting configuration
MAX_WORKERS = 8  # Parallel requests
RATE_LIMIT_DELAY = 0.4  # Seconds between requests
FETCH_TOP_REPOS = False  # Set to True to fetch popular repos (uses more API calls)
FETCH_SPONSOR_DETAILS = False  # Set to True to fetch individual sponsor list (uses more API calls)

def make_graphql_request(query, variables=None, max_retries=3):
    """Make a GraphQL request with error handling and retry logic."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"query": query}
    if variables:
        data["variables"] = variables
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                print(f"  ⏱️  Request timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Request timed out after {max_retries} attempts")
                raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [502, 503, 504]:  # Gateway errors
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 3, 6, 9 seconds for server errors
                    print(f"  ⏱️  Server error {e.response.status_code}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Server error {e.response.status_code} after {max_retries} attempts")
                    raise
            else:
                raise  # Other HTTP errors (auth, rate limit, etc.) - don't retry

def search_sponsorable_users(cursor=None, search_type="followers"):
    """
    Search for sponsorable users with multiple strategies.
    search_type: 'followers', 'repos', 'established', 'stars', 'organizations', 'active'
    """
    # Calculate date filters dynamically (only for established strategy)
    two_years_ago = (datetime.now(timezone.utc) - timedelta(days=730)).strftime("%Y-%m-%d")
    
    search_queries = {
        "followers": "type:user followers:>2000 repos:>5 is:sponsorable",  # Popular developers
        "repos": "type:user repos:>100 followers:>500 is:sponsorable",  # Prolific creators (high output)
        "established": f"type:user followers:>1000 repos:>20 is:sponsorable created:<{two_years_ago}",  # Veterans (2+ years old)
        "stars": "type:user followers:>10000 is:sponsorable",  # Super popular (celebrities)
        "organizations": "type:org repos:>10 is:sponsorable",
        "active": "type:user repos:>50 followers:>800 is:sponsorable"  # Active maintainers (balanced)
    }
    
    after_clause = f', after: "{cursor}"' if cursor else ""
    
    query = f'''
    query {{
      search(query: "{search_queries[search_type]}", type: USER, first: 100{after_clause}) {{
        pageInfo {{
          hasNextPage
          endCursor
        }}
        nodes {{
          ... on User {{
            login
            name
            avatarUrl
            url
            bio
            location
            company
            twitterUsername
            websiteUrl
            createdAt
            followers {{
              totalCount
            }}
            following {{
              totalCount
            }}
            repositories(privacy: PUBLIC) {{
              totalCount
            }}
            sponsoring {{
              totalCount
            }}
            sponsorshipsAsMaintainer {{
              totalCount
            }}
            isGitHubStar
            status {{
              message
            }}
          }}
          ... on Organization {{
            login
            name
            avatarUrl
            url
            description
            location
            twitterUsername
            websiteUrl
            createdAt
            repositories(privacy: PUBLIC) {{
              totalCount
            }}
            sponsorshipsAsMaintainer {{
              totalCount
            }}
          }}
        }}
      }}
      rateLimit {{
        remaining
        resetAt
      }}
    }}'''
    
    return make_graphql_request(query)

def get_user_top_repos(login, count=5):
    """Get user's most starred repositories (excluding forks)."""
    query = f'''
    query {{
      repositoryOwner(login: "{login}") {{
        ... on User {{
          repositories(first: {count}, orderBy: {{field: STARGAZERS, direction: DESC}}, isFork: false, privacy: PUBLIC) {{
            nodes {{
              name
              stargazerCount
              description
              url
              isFork
              primaryLanguage {{
                name
              }}
              forkCount
              watchers {{
                totalCount
              }}
            }}
          }}
        }}
        ... on Organization {{
          repositories(first: {count}, orderBy: {{field: STARGAZERS, direction: DESC}}, isFork: false, privacy: PUBLIC) {{
            nodes {{
              name
              stargazerCount
              description
              url
              isFork
              primaryLanguage {{
                name
              }}
              forkCount
              watchers {{
                totalCount
              }}
            }}
          }}
        }}
      }}
    }}'''
    
    try:
        result = make_graphql_request(query)
        return result.get("data", {}).get("repositoryOwner", {}).get("repositories", {}).get("nodes", [])
    except:
        return []

def get_sponsor_details(login):
    """Get detailed sponsorship information."""
    query = f'''
    query {{
      repositoryOwner(login: "{login}") {{
        ... on User {{
          sponsorshipsAsMaintainer(first: 1) {{
            totalCount
          }}
          sponsorshipsAsSponsor(first: 1) {{
            totalCount
          }}
          sponsors(first: 100) {{
            totalCount
            nodes {{
              ... on User {{
                login
                followers {{
                  totalCount
                }}
              }}
              ... on Organization {{
                login
              }}
            }}
          }}
        }}
        ... on Organization {{
          sponsorshipsAsMaintainer(first: 1) {{
            totalCount
          }}
          sponsors(first: 100) {{
            totalCount
            nodes {{
              ... on User {{
                login
                followers {{
                  totalCount
                }}
              }}
              ... on Organization {{
                login
              }}
            }}
          }}
        }}
      }}
    }}'''
    
    try:
        result = make_graphql_request(query)
        return result.get("data", {}).get("repositoryOwner", {})
    except:
        return None

def process_user(user_data):
    """Process a single user and gather all relevant data."""
    login = user_data.get("login")
    if not login:
        return None
    
    # Detect if this is an organization (orgs don't have followers/following fields in the same way)
    is_organization = user_data.get("following") is None
    
    print(f"Processing {login}...")
    
    # Get sponsor count from initial query
    sponsorships_count = user_data.get("sponsorshipsAsMaintainer", {}).get("totalCount", 0)
    
    # Only include users with sponsors
    if sponsorships_count == 0:
        return None
    
    # Filter: Only users with meaningful sponsor base (at least 5 sponsors)
    if sponsorships_count < 5:
        print(f"  Skipping {login}: only {sponsorships_count} sponsors")
        return None
    
    # Optional: Get detailed sponsor information (individual sponsor list)
    sponsor_details = None
    sponsor_followers_total = 0
    sponsor_logins = set()
    sponsoring_count = user_data.get("sponsoring", {}).get("totalCount", 0)
    
    if FETCH_SPONSOR_DETAILS:
        time.sleep(RATE_LIMIT_DELAY)
        sponsor_details = get_sponsor_details(login)
        if sponsor_details:
            sponsors = sponsor_details.get("sponsors", {})
            sponsor_list = sponsors.get("nodes", [])
            
            # Calculate sponsor metrics
            sponsor_followers_total = sum(
                s.get("followers", {}).get("totalCount", 0) 
                for s in sponsor_list 
                if "followers" in s
            )
            sponsor_logins = {s.get("login") for s in sponsor_list if s.get("login")}
            
            # Get sponsoring count if available
            if "sponsorshipsAsSponsor" in sponsor_details:
                sponsoring_count = sponsor_details.get("sponsorshipsAsSponsor", {}).get("totalCount", 0)
    
    # Get top repositories (optional - can be disabled to save API calls)
    top_repos = []
    if FETCH_TOP_REPOS:
        time.sleep(RATE_LIMIT_DELAY)
        top_repos = get_user_top_repos(login)
    
    return {
        "login": login,
        "type": "organization" if is_organization else "user",
        "name": user_data.get("name"),
        "avatar_url": user_data.get("avatarUrl"),
        "html_url": user_data.get("url"),
        "bio": user_data.get("bio") or user_data.get("description"),
        "location": user_data.get("location"),
        "company": user_data.get("company"),
        "twitter_username": user_data.get("twitterUsername"),
        "website_url": user_data.get("websiteUrl"),
        "created_at": user_data.get("createdAt"),
        "is_github_star": user_data.get("isGitHubStar", False),
        
        # Counts
        "followers": user_data.get("followers", {}).get("totalCount", 0),
        "following": user_data.get("following", {}).get("totalCount", 0),
        "public_repos": user_data.get("repositories", {}).get("totalCount", 0),
        "sponsorships_count": sponsorships_count,
        "sponsoring_count": sponsoring_count,
        
        # Sponsor metrics (only available if FETCH_SPONSOR_DETAILS is True)
        "sponsors_total": sponsorships_count,  # Using count from first query
        "sponsor_followers_total": sponsor_followers_total,
        "sponsor_follower_ratio": round(sponsor_followers_total / max(user_data.get("followers", {}).get("totalCount", 1), 1), 4) if sponsor_followers_total > 0 else 0,
        
        # Top repositories
        "top_repos": [
            {
                "name": repo.get("name"),
                "stars": repo.get("stargazerCount", 0),
                "description": repo.get("description"),
                "url": repo.get("url"),
                "language": repo.get("primaryLanguage", {}).get("name") if repo.get("primaryLanguage") else None,
                "forks": repo.get("forkCount", 0),
                "watchers": repo.get("watchers", {}).get("totalCount", 0)
            }
            for repo in top_repos
            if not repo.get("isFork", False)  # Double-check no forks
        ],
        
        # Calculated metrics
        "sponsor_conversion_rate": round(sponsorships_count / max(user_data.get("followers", {}).get("totalCount", 1), 1) * 100, 4),
        "engagement_score": round(
            (sponsorships_count * 10 + 
             user_data.get("repositories", {}).get("totalCount", 0) +
             user_data.get("followers", {}).get("totalCount", 0) * 0.01) / 100, 2
        )
    }

def main():
  """Main function to fetch and process sponsorable users."""
  if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set.")
    return

  all_sponsors = []
  seen_logins = set()
  # Collect per-strategy results independently for insight/analysis
  strategy_results = {}

  try:
    print("=" * 60)
    print("Starting GitHub Sponsors data collection")
    print("=" * 60)

    # Use multiple search strategies to get diverse results
    strategies = ["followers", "repos", "established", "stars", "active", "organizations"]

    for strategy in strategies:
      print(f"\n🔍 Strategy: {strategy.upper()}")
      print("-" * 60)
      strategy_results[strategy] = []
      per_strategy_seen = set()

      cursor = None
      pages_fetched = 0
      max_pages = 10  # 10 pages per strategy = up to 1000 users per strategy

      while pages_fetched < max_pages:
        try:
          result = search_sponsorable_users(cursor, strategy)
        except Exception as e:
          print(f"  ❌ Error fetching page {pages_fetched + 1}: {e}")
          print(f"  Skipping to next strategy...")
          break

        if "errors" in result:
          print(f"  GraphQL error: {result['errors']}")
          # Check if it's a rate limit or timeout issue
          error_msg = str(result['errors'])
          if 'timeout' in error_msg.lower() or 'rate limit' in error_msg.lower():
            print(f"  Waiting 10 seconds before continuing...")
            time.sleep(10)
          break

        data = result.get("data", {})
        search_results = data.get("search", {})
        users = search_results.get("nodes", [])

        if not users:
          print("  No more users found")
          break

        # Process users with ThreadPoolExecutor
        print(f"  Found {len(users)} users in page {pages_fetched + 1}")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
          futures = {executor.submit(process_user, user): user for user in users}

          for future in as_completed(futures):
            try:
              processed_data = future.result()
              if processed_data:
                # Add to per-strategy list (dedupe within strategy)
                login = processed_data["login"]
                if login not in per_strategy_seen:
                  strategy_results[strategy].append(processed_data)
                  per_strategy_seen.add(login)
                # Add to global list (dedupe globally)
                if login not in seen_logins:
                  all_sponsors.append(processed_data)
                  seen_logins.add(login)
            except Exception as e:
              print(f"Error processing user: {e}")

        # Check rate limit
        rate_limit = data.get("rateLimit", {})
        print(f"  Rate limit remaining: {rate_limit.get('remaining', 'unknown')}")
        print(f"  Total unique sponsors so far: {len(all_sponsors)}")

        # Pagination
        page_info = search_results.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
          print("  No more pages available")
          break

        cursor = page_info.get("endCursor")
        pages_fetched += 1
        time.sleep(1)  # Be nice to the API
      
      # Brief pause between strategies to avoid overwhelming the API
      if strategy != strategies[-1]:  # Don't pause after the last strategy
        print(f"  Pausing 3 seconds before next strategy...")
        time.sleep(3)

    # Sort by sponsorships count
    all_sponsors.sort(key=lambda x: x["sponsorships_count"], reverse=True)

    # Calculate statistics
    stats = {
      "total_sponsors": len(all_sponsors),
      "total_sponsorships": sum(s["sponsorships_count"] for s in all_sponsors),
      "avg_sponsors_per_user": round(sum(s["sponsorships_count"] for s in all_sponsors) / max(len(all_sponsors), 1), 2),
      "avg_follower_count": round(sum(s["followers"] for s in all_sponsors) / max(len(all_sponsors), 1), 2),
      "avg_conversion_rate": round(sum(s["sponsor_conversion_rate"] for s in all_sponsors) / max(len(all_sponsors), 1), 4),
      "github_stars_count": sum(1 for s in all_sponsors if s.get("is_github_star")),
    }

    output_data = {
      "sponsors": all_sponsors[:1000],  # Top 1000
      "statistics": stats,
      "last_updated": datetime.now(timezone.utc).isoformat()
    }

    # Save data
    public_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public")
    output_path = os.path.join(public_dir, "data.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
      json.dump(output_data, f, indent=2)

    # Also write per-strategy JSONs for deeper insight
    strategies_dir = os.path.join(public_dir, "strategies")
    os.makedirs(strategies_dir, exist_ok=True)

    strategies_summary = {
      "last_updated": output_data["last_updated"],
      "strategies": {}
    }

    for strat, items in strategy_results.items():
      # Sort each strategy's results by sponsorships_count desc
      items_sorted = sorted(items, key=lambda x: x.get("sponsorships_count", 0), reverse=True)

      strat_stats = {
        "total_sponsors": len(items_sorted),
        "total_sponsorships": sum(s.get("sponsorships_count", 0) for s in items_sorted),
        "avg_sponsors_per_user": round(
          (sum(s.get("sponsorships_count", 0) for s in items_sorted) / max(len(items_sorted), 1)), 2
        ),
        "avg_follower_count": round(
          (sum(s.get("followers", 0) for s in items_sorted) / max(len(items_sorted), 1)), 2
        ),
        "avg_conversion_rate": round(
          (sum(s.get("sponsor_conversion_rate", 0) for s in items_sorted) / max(len(items_sorted), 1)), 4
        ),
        "github_stars_count": sum(1 for s in items_sorted if s.get("is_github_star")),
      }

      strat_payload = {
        "strategy": strat,
        "sponsors": items_sorted,  # keep full per-strategy list
        "statistics": strat_stats,
        "last_updated": output_data["last_updated"]
      }

      with open(os.path.join(strategies_dir, f"strategy_{strat}.json"), "w") as sf:
        json.dump(strat_payload, sf, indent=2)

      strategies_summary["strategies"][strat] = strat_stats

    # Write a compact summary file for quick comparison in the frontend or docs
    with open(os.path.join(strategies_dir, "strategies_summary.json"), "w") as ssf:
      json.dump(strategies_summary, ssf, indent=2)

    print(f"\n✅ Successfully saved data for {len(all_sponsors)} sponsors to {output_path}")
    print(f"\n📊 Statistics:")
    print(f"   Total sponsorships: {stats['total_sponsorships']}")
    print(f"   Avg sponsors per user: {stats['avg_sponsors_per_user']}")
    print(f"   Avg conversion rate: {stats['avg_conversion_rate']}%")
    print(f"   GitHub Stars: {stats['github_stars_count']}")
    print(f"\n🧩 Per-strategy files written to: {strategies_dir}")
    print(f"\n⚙️  Configuration:")
    print(f"   Fetching top repos: {'✅ Enabled' if FETCH_TOP_REPOS else '❌ Disabled (faster)'}")
    print(f"   Fetching sponsor details: {'✅ Enabled' if FETCH_SPONSOR_DETAILS else '❌ Disabled (faster)'}")
    print(f"   Max workers: {MAX_WORKERS}")
    print(f"   Rate limit delay: {RATE_LIMIT_DELAY}s")

  except Exception as e:
    print(f"An unexpected error occurred: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    main()