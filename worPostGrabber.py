import requests
import os
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
            post_text = post_record.get('text', '').replace("\n", "<br>")  # Extract text
            
            # Capture the post's timestamp
            post_timestamp = post_record.get('createdAt', None)
            if post_timestamp:
                post_date = datetime.strptime(post_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                if oldest_date is None or post_date < oldest_date:
                    oldest_date = post_date
                if newest_date is None or post_date > newest_date:
                    newest_date = post_date

            post['post']['text'] = post_text  # Store text in post dictionary for later use
            
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

output_file = os.path.join(output_dir, f"{date_range_str}.html")

def write_post_with_replies(file, post, is_reply=False):
    post_uri = post.get('post', {}).get('uri', 'Unknown URI')
    post_cid = post.get('post', {}).get('cid', 'Unknown CID')
    post_text = post.get('post', {}).get('text', '')  # Get stored text

    if is_reply:
        file.write(f"""
        <div style='display: flex; justify-content: center; align-items: center; width: 100%; max-width: 100%; padding-left: 2px;'>
            <div style='display: flex; align-items: flex-start; width: 100%; max-width: 100%; justify-content: center;'>
                <img src='images/thread.gif' alt='GIF' style='width: 66px; height: auto; margin-right: 2px;'>
                <div style='width: 100%; max-width: 500px; padding-left: 5px;'>
                    <blockquote class='bluesky-embed' data-bluesky-uri='{post_uri}' data-bluesky-cid='{post_cid}'></blockquote>
                    <p style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">{post_text}</p>
                    <script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>
                </div>
            </div>
        </div>
        """)
    else:
        file.write(f"""
        <blockquote class='bluesky-embed' data-bluesky-uri='{post_uri}' data-bluesky-cid='{post_cid}'></blockquote>
        <p style="font-family: Arial, sans-serif; font-size: 16px; color: #000;">{post_text}</p>
        <script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>
        """)

    if post_uri in replies:
        for reply in replies[post_uri]:
            write_post_with_replies(file, reply, is_reply=True)

# Save posts to an HTML file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bluesky Feed - {date_range_str}</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body style="background-color: #f0f0f0;">
        <h1 style="font-family: 'Garamond', sans-serif; text-align: center; font-size: 3em; color: #ff0000;">WIZARDS OF THE REALM</h1>
        <marquee>I'VE HEARD OF "SCROLLS" BUT THIS IS RIDICULOUS</marquee>
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; width: 100%; max-width: 100%;">
    """)

    for post in main_posts:
        write_post_with_replies(file, post)

    file.write("""
        </div>
    </body>
    </html>
    """)

print(f"HTML file created: {output_file}")
