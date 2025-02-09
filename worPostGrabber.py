import requests
from collections import defaultdict

# App password for authentication
APP_PASSWORD = "tld4-3d2m-ocis-7ffc"
BLUESKY_HANDLE = "orboftherealm.bsky.social"

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
    "list": "at://did:plc:tsrqneix4sgsbvrhz6arbuci/app.bsky.graph.list/3lbq3w3xvpx2d",  # Replace with actual list URI
    "limit": 100
}

# Initialize storage
main_posts = []
replies = defaultdict(list)  # Store replies under their parent post URI

# Start pagination
while True:
    feed_response = requests.get(feed_url, headers=headers, params=feed_params)
    if feed_response.status_code != 200:
        print(f"Error fetching posts: {feed_response.status_code} {feed_response.text}")
        break
    
    feed_data = feed_response.json()
    posts = feed_data.get('feed', [])
    if not posts:
        break
    
    for post in posts:
        post_record = post.get('post', {}).get('record', {})
        post_uri = post.get('post', {}).get('uri', 'Unknown URI')
        post_cid = post.get('post', {}).get('cid', 'Unknown CID')
        
        # Check if it's a reply
        reply_parent = post_record.get('reply', {}).get('parent', {}).get('uri')
        if reply_parent:
            replies[reply_parent].append((post_uri, post_cid))
        else:
            main_posts.append((post_uri, post_cid))
    
    next_cursor = feed_data.get("cursor")
    if next_cursor:
        feed_params["cursor"] = next_cursor
    else:
        break

# Reverse main_posts to be in chronological order
main_posts.reverse()

# Save to HTML
with open("postsWReplyThreaded.html", "w", encoding="utf-8") as file:
    file.write("<html>\n<head>\n<title>Bluesky Posts</title>\n</head>\n<body>\n")
    
    for post_uri, post_cid in main_posts:
        file.write(f"<blockquote class='bluesky-embed' data-bluesky-uri='{post_uri}' data-bluesky-cid='{post_cid}'></blockquote>\n")
        file.write("<script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>\n")
        
        # Add replies in original order (chronological)
        if post_uri in replies:
            for reply_uri, reply_cid in replies[post_uri]:
                file.write("""
                <div style='display: flex; justify-content: center; align-items: center; width: 100%; max-width: 100%; padding-left: 40px;'>
                    <div style='display: flex; align-items: flex-start; width: 100%; max-width: 100%; justify-content: center;'>
                        <img src='images/thread.gif' alt='GIF' style='width: 100px; height: auto; margin-right: 20px;'>
                        <div style='width: 100%; max-width: 500px; padding-left: 20px;'>
                            <blockquote class='bluesky-embed' data-bluesky-uri='{}' data-bluesky-cid='{}'></blockquote>
                            <script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>
                        </div>
                    </div>
                </div>
                """.format(reply_uri, reply_cid))
    
    file.write("</body>\n</html>\n")

print("HTML file created: postsWReplyThreaded.html")