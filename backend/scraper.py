
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# It's recommended to store your token securely, e.g., in an environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API_URL = "https://api.github.com/graphql"

def get_top_users():
    """
    Fetches the top 100 most followed users on GitHub.
    """
    url = "https://api.github.com/search/users?q=followers:>1000&sort=followers&order=desc&per_page=100"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["items"]

def get_sponsorship_details(login):
    """
    Fetches sponsorship details for a given user using the GraphQL API.
    """
    query = f'''
    query {{
      repositoryOwner(login: "{login}") {{
        ... on User {{
          isSponsoredBy(accountLogin: "github")
          sponsorshipsAsMaintainer(first: 1) {{
            totalCount
          }}
        }}
        ... on Organization {{
          isSponsoredBy(accountLogin: "github")
          sponsorshipsAsMaintainer(first: 1) {{
            totalCount
          }}
        }}
      }}
    }}'''
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"query": query}
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    """
    Main function to fetch top users, get their sponsorship details,
    and save the data to a JSON file.
    """
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set it to your GitHub Personal Access Token with 'read:user' scope.")
        return

    try:
        top_users = get_top_users()
        sponsors_data = []

        for user in top_users:
            login = user["login"]
            print(f"Fetching details for {login}...")
            sponsorship_details = get_sponsorship_details(login)

            if "errors" in sponsorship_details:
                print(f"GraphQL query failed for {login}: {sponsorship_details['errors']}")
                continue

            data = sponsorship_details.get("data", {}).get("repositoryOwner")
            if data and data.get("sponsorshipsAsMaintainer", {}).get("totalCount", 0) > 0:
                print(f"{login} is a sponsor!")
                sponsors_data.append({
                    "login": login,
                    "avatar_url": user["avatar_url"],
                    "html_url": user["html_url"],
                    "followers": user.get("followers", 0),
                    "sponsorships_count": data["sponsorshipsAsMaintainer"]["totalCount"]
                })

        # Sort sponsors by the number of sponsorships
        sponsors_data.sort(key=lambda x: x["sponsorships_count"], reverse=True)

        # Save data to frontend/src/data.json
        output_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data.json")
        with open(output_path, "w") as f:
            json.dump(sponsors_data, f, indent=2)

        print(f"Successfully saved data for {len(sponsors_data)} sponsors to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
