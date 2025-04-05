import requests
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+

# App password for authentication
APP_PASSWORD = "tld4-3d2m-ocis-7ffc"
BLUESKY_HANDLE = "orboftherealm.bsky.social"

# Create folder for stored posts if it doesn't exist
output_dir = "storedPosts"
os.makedirs(output_dir, exist_ok=True)

# Set PST timezone
pst = ZoneInfo("America/Los_Angeles")

# Calculate yesterday's date based on current PST time.
# Midnight (00:00:00) is the cutoff.
yesterday = (datetime.now(tz=pst) - timedelta(days=1)).date()
TARGET_DATE_STR = yesterday.strftime("%Y-%m-%d")
TARGET_DATE = yesterday

print(f"Fetching posts for {TARGET_DATE_STR} (PST)")

# --- LOGIN: Get session token ---
login_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
login_data = {"identifier": BLUESKY_HANDLE, "password": APP_PASSWORD}

session = requests.Session()
response = session.post(login_url, json=login_data)

if response.status_code != 200:
    print("Login failed:", response.status_code, response.text)
    exit()

session_token = response.json()["accessJwt"]

# URL to fetch the feed from Bluesky
feed_url = "https://gomphus.us-west.host.bsky.network/xrpc/app.bsky.feed.getListFeed"

# Set up headers
headers = {
    "Authorization": f"Bearer {session_token}",
    "Content-Type": "application/json"
}

# Set up parameters for the feed request
feed_params = {
    "list": "at://did:plc:tsrqneix4sgsbvrhz6arbuci/app.bsky.graph.list/3lbq3w3xvpx2d",
    "limit": 100
}

# Initialize structures to store posts
main_posts = []  # Stores main posts
replies = {}     # Maps parent URI to a list of replies

# Fetch posts only for the target day (yesterday, PST)
while True:
    feed_response = requests.get(feed_url, headers=headers, params=feed_params)
    
    if feed_response.status_code != 200:
        print(f"Error fetching posts: {feed_response.status_code} {feed_response.text}")
        break

    feed_data = feed_response.json()
    posts = feed_data.get('feed', [])
    
    # Break out if no posts are returned.
    if not posts:
        break

    for post in posts:
        post_record = post.get('post', {}).get('record', {})
        post_timestamp = post_record.get('createdAt', None)
        if not post_timestamp:
            continue

        try:
            post_date = datetime.strptime(post_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        except ValueError:
            continue  # Skip posts with unparseable timestamps

        if post_date == TARGET_DATE:
            # Process this post
            post['post']['text'] = post_record.get('text', '')
            if 'reply' in post_record:
                parent_uri = post_record['reply']['parent']['uri']
                replies.setdefault(parent_uri, []).append(post)
            else:
                main_posts.append(post)
        elif post_date < TARGET_DATE:
            # Once we hit posts older than TARGET_DATE, stop fetching further.
            posts = []
            break

    if not posts:
        break

    next_cursor = feed_data.get("cursor", None)
    if next_cursor:
        feed_params["cursor"] = next_cursor
    else:
        break

# Optionally, reverse the list for chronological order (oldest first)
main_posts.reverse()

# Save the collected posts to a JSON file named by the target date
output_file = os.path.join(output_dir, f"{TARGET_DATE_STR}.json")
with open(output_file, "w", encoding="utf-8") as file:
    output = { "mainPosts": main_posts, "replies": replies }
    file.write(json.dumps(output, indent=2))

print(f"Saved posts from {TARGET_DATE_STR} (PST) to {output_file}")
