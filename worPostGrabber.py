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

# Initialize the list to store posts
all_posts = []

# Start pagination
while True:
    # Make the request to fetch the feed (get the posts)
    feed_response = requests.get(feed_url, headers=headers, params=feed_params)
    
    # Print the raw response data for debugging
    print("Feed Response Text:", feed_response.text)  # Debugging output
    
    if feed_response.status_code == 200:
        feed_data = feed_response.json()
        
        # Check if 'data' exists and if there are posts
        posts = feed_data.get('feed', [])
        print("Posts found:", len(posts))  # Print number of posts to see if we have any data
        
        if not posts:
            print("No posts found in the feed response.")
            break
        
        # Append the posts to the all_posts list
        all_posts.extend(posts)
        
        # Check if there's a next page (nextCursor) and update parameters accordingly
        next_cursor = feed_data.get("cursor", None)
        if next_cursor:
            feed_params["cursor"] = next_cursor
            print(f"Fetching next page with cursor: {next_cursor}")
        else:
            print("No more pages to fetch.")
            break
        
        # Check if we've reached the desired limit
        if len(all_posts) >= 100:  # Adjust this limit as needed
            all_posts = all_posts[:100]  # Truncate the list to the desired limit
            print(f"Reached limit of {len(all_posts)} posts.")
            break
    else:
        print(f"Error fetching posts: {feed_response.status_code} {feed_response.text}")
        break

# Save the posts to an HTML file
with open("posts.html", "w", encoding="utf-8") as file:
    # Write the basic HTML structure
    file.write("<html>\n<head>\n<title>Bluesky Posts</title>\n</head>\n<body>\n")
    
    # Iterate through the posts and write each one in the desired format
    for post in all_posts:
        post_record = post.get('post', {}).get('record', {})
        post_uri = post.get('post', {}).get('uri', 'Unknown URI')
        post_cid = post.get('post', {}).get('cid', 'Unknown CID')
        
        # Write each post as a blockquote
        file.write(f"<blockquote class='bluesky-embed' ")
        file.write(f"data-bluesky-uri='{post_uri}' ")
        file.write(f"data-bluesky-cid='{post_cid}'>\n")
        
        file.write(f"</blockquote>\n")
        file.write(f"<script async src='https://embed.bsky.app/static/embed.js' charset='utf-8'></script>\n")
    
    # Close the HTML tags
    file.write("</body>\n</html>\n")

print("HTML file created: posts.html")
