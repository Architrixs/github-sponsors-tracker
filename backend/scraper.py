
import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

# ... (rest of the imports)

# ... (rest of the code)

        # Create the final data structure
        output_data = {
            "sponsors": sponsors_data,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        # Save data to frontend/public/data.json
        output_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "data.json")
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"Successfully saved data for {len(sponsors_data)} sponsors to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
