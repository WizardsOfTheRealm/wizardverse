import requests
import os
import json
from datetime import datetime

# App password for authentication
APP_PASSWORD = "tld4-3d2m-ocis-7ffc"
BLUESKY_HANDLE = "orboftherealm.bsky.social"

# Create folder for stored posts if it doesn't exist
output_dir = "storedPosts"
os.makedirs(output_dir, exist_ok=True)

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
replies = {}  # Maps parent URI to a list of replies

# Track post date range
oldest_date = None
newest_date = None

# Total posts limit
total_limit = 100
posts_fetched = 0

# Fetch posts
while posts_fetched < total_limit:
    feed_response = requests.get(feed_url, headers=headers, params=feed_params)
    
    if feed_response.status_code == 200:
        feed_data = feed_response.json()
        posts = feed_data.get('feed', [])
        
        if not posts:
            break
        
        for post in posts:
            post_record = post.get('post', {}).get('record', {})
            post_uri = post.get('post', {}).get('uri', 'Unknown URI')
            
            # Capture the post's timestamp
            post_timestamp = post_record.get('createdAt', None)
            if post_timestamp:
                post_date = datetime.strptime(post_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                if oldest_date is None or post_date < oldest_date:
                    oldest_date = post_date
                if newest_date is None or post_date > newest_date:
                    newest_date = post_date

            post['post']['text'] = post_record.get('text', '')  # Store text in post dictionary for later use
            
            if 'reply' in post_record:
                parent_uri = post_record['reply']['parent']['uri']
                replies.setdefault(parent_uri, []).append(post)
            else:
                if posts_fetched < total_limit:
                    main_posts.append(post)
                    posts_fetched += 1
                
                if posts_fetched >= total_limit:
                    break
        
        next_cursor = feed_data.get("cursor", None)
        if next_cursor:
            feed_params["cursor"] = next_cursor
        else:
            break
    else:
        print(f"Error fetching posts: {feed_response.status_code} {feed_response.text}")
        break

# Reverse order (oldest first)
main_posts.reverse()

# Format filename based on post date range
if oldest_date and newest_date:
    date_range_str = f"{oldest_date.strftime('%d%m%y')}_{newest_date.strftime('%d%m%y')}"
else:
    date_range_str = "nodate"

output_file = os.path.join(output_dir, f"{date_range_str}.json")

# Save posts to an HTML file
with open(output_file, "w", encoding="utf-8") as file:
    output = { "mainPosts": main_posts, "replies": replies }
    file.write(json.dumps(output))
