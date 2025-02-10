import requests

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
    "list": "at://did:plc:tsrqneix4sgsbvrhz6arbuci/app.bsky.graph.list/3lbq3w3xvpx2d",  # Replace with your actual list URI
    "limit": 100  # Limit for the feed request (adjust as needed)
}

# Initialize structures to store posts
main_posts = []  # Stores main posts
replies = {}  # Maps parent URI to a list of replies

# Start pagination
while True:
    # Make the request to fetch the feed (get the posts)
    feed_response = requests.get(feed_url, headers=headers, params=feed_params)
    
    if feed_response.status_code == 200:
        feed_data = feed_response.json()
        
        # Check if 'data' exists and if there are posts
        posts = feed_data.get('feed', [])
        
        if not posts:
            break
        
        # Process each post
        for post in posts:
            post_record = post.get('post', {}).get('record', {})
            post_uri = post.get('post', {}).get('uri', 'Unknown URI')
            
            # Check if the post is a reply
            if 'reply' in post_record:
                parent_uri = post_record['reply']['parent']['uri']
                if parent_uri not in replies:
                    replies[parent_uri] = []
                replies[parent_uri].append(post)
            else:
                main_posts.append(post)
        
        # Check if there's a next page (nextCursor) and update parameters accordingly
        next_cursor = feed_data.get("cursor", None)
        if next_cursor:
            feed_params["cursor"] = next_cursor
        else:
            break
    else:
        print(f"Error fetching posts: {feed_response.status_code} {feed_response.text}")
        break

# Reverse the order of the main posts to be oldest to newest
main_posts.reverse()

def write_post_with_replies(file, post, is_reply=False):
    post_uri = post.get('post', {}).get('uri', 'Unknown URI')
    post_cid = post.get('post', {}).get('cid', 'Unknown CID')
    
    if is_reply:
        file.write("""
        <div style='display: flex; justify-content: center; align-items: center; width: 100%; max-width: 100%; padding-left: 40px;'>
            <div style='display: flex; align-items: flex-start; width: 100%; max-width: 100%; justify-content: center;'>
                <img src='images/thread.gif' alt='GIF' style='width: 66px; height: auto; margin-right: 5px;'>
                <div style='width: 100%; max-width: 500px; padding-left: 5px;'>
                    <blockquote class='bluesky-embed' data-bluesky-uri='{}' data-bluesky-cid='{}'></blockquote>
                    <script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>
                </div>
            </div>
        </div>
        """.format(post_uri, post_cid))
    else:
        file.write(f"<blockquote class='bluesky-embed' data-bluesky-uri='{post_uri}' data-bluesky-cid='{post_cid}'></blockquote>\n")
        file.write("<script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>\n")
    
    # Check if this post has replies and process them
    if post_uri in replies:
        for reply in replies[post_uri]:
            write_post_with_replies(file, reply, is_reply=True)

# Save the posts to an HTML file
with open("postsWReply.html", "w", encoding="utf-8") as file:
    # Write the basic HTML structure
    file.write("<html>\n<head>\n<title>Bluesky Posts</title>\n</head>\n<body>\n")
    
    # Iterate through the main posts and write them with replies
    for post in main_posts:
        write_post_with_replies(file, post)
    
    # Close the HTML tags
    file.write("</body>\n</html>\n")

print("HTML file created: postsWReply.html")