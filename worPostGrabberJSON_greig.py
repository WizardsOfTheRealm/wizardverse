import requests
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup # added by G

# altered code from AG and IC by GO 2025-04-04
# reads old 'episodes by G' to get post IDs by date
# input: html files corresponding to 'episodes'
# output: daily json files storing all posts and replies
# to-do: only ran once for ep 1: check with ian and if working do rest


# OLD - DELETE
# start_date_str = "2024-10-30"  # inclusive
# end_date_str = "2024-10-31"
# # Parse date range into datetime objects
# start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
# end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()


# App password for authentication
APP_PASSWORD = "tld4-3d2m-ocis-7ffc"
BLUESKY_HANDLE = "orboftherealm.bsky.social"

################ parsing old episode html manually done by G ##################
# read episode file
oldep_dir = "episodes by G"  # TO DO: make loop over all eps
# oldep_html = "_prologue.html" # weird htmls created manually by G
# epnum = "prlg"
# oldep_html = "episode 1 - the symposium.html" # weird htmls created manually by G
# epnum = "ep1"
oldep_html = "episode 2 - the whistleblower.html" # weird htmls created manually by G
epnum = "ep2"
# oldep_html = "episode 3 - the apprentice.html" # weird htmls created manually by G
# epnum = "ep3"
# oldep_html = "episode 4 - the kettles p1.html" # weird htmls created manually by G
# epnum = "ep41"
# oldep_html = "episode 4 - the kettles p2.html" # weird htmls created manually by G
# epnum = "ep42"
# oldep_html = "episode 5 - Frankleskas.html" # weird htmls created manually by G
# epnum = "ep5"
# oldep_html = "episode 6 - the bugs.html" # weird htmls created manually by G
# epnum = "ep6"
# oldep_html = "episode 7 - Roy up to Jan 27.html" # weird htmls created manually by G
# epnum = "ep7"


# Create folder for stored posts if it doesn't exist
output_dir = f"storedPosts/test_greig/{epnum}"
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



# loop over cid and uri's
#data-bluesky-uri="" or data-bluesky-cid="
# use above to see if post or reply
# Load and parse the HTML
with open(oldep_dir + "//" + oldep_html, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")


# Find all blockquotes with class 'bluesky-embed'
embeds = soup.find_all("blockquote", class_="bluesky-embed")

# Set up headers
headers = {
    "Authorization": f"Bearer {session_token}",
    "Content-Type": "application/json"
}
post_url = "https://gomphus.us-west.host.bsky.network/xrpc/app.bsky.feed.getPostThread"


# Loop through embeds and fetch each post
# for each 'embed' bit, get the actual post from bsky api
# check if it's a post and not a reply
# if it's a post from same day as previous, add to running json var
# if new day, then write json var to file and continue to end of file

# --- Tracking ---
seen_uris = set()
current_date = None
current_posts = []
last_seen_date = None

i = 0 # debug - delete me
for embed in embeds:

    #if i > 5:
    #    exit()

    uri = embed.get("data-bluesky-uri")
    cid = embed.get("data-bluesky-cid")

    print(f"Fetching post:\n  URI: {uri}\n  CID: {cid}")

    # Call the API to get the post
    params = {"uri": uri}
    response = requests.get(post_url, headers=headers, params=params)

    if response.status_code == 200:
        post_data = response.json()
        # Pretty-print the post JSON (or do whatever you need)
        print(json.dumps(post_data, indent=2))
    else:
        print(f"Failed to fetch post {uri}: {response.status_code} - {response.text}")

    # Get top-level post (can be nested in thread)
    post = post_data.get("thread", {}).get("post")
    if not post:
        print(f"No top-level post found for {uri}")
        #i += 1 # debug
        continue

    record = post.get("record", {})
    if "reply" in record:
        print(f"Skipping reply post: {post.get('uri')}")
        #i += 1  # debug
        continue

    created_at_str = record.get("createdAt")
    if not created_at_str:
        print(f"No createdAt timestamp for {uri}")
        #i += 1
        continue

    # Parse and check date
    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    post_date = created_at.date()

    # --- Check chronological order ---
    if last_seen_date and post_date < last_seen_date:
        print(f"⚠️ Warning: post date moved backward from {last_seen_date} to {post_date}")
        exit()

    # --- New day? Write previous day's data ---
    if current_date and post_date != current_date:
        filename = f"{epnum}_{current_date.strftime('%Y%m%d')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(current_posts, f, indent=2)
        print(f"Wrote {len(current_posts)} posts to {filename}")

        current_posts = []

    # Accumulate post
    current_date = post_date
    last_seen_date = post_date
    current_posts.append(post_data)


    print("##################")
    print("##################")

    i += 1

# for date range, each day





# old code



# # URL to fetch the feed from Bluesky
# feed_url = "https://gomphus.us-west.host.bsky.network/xrpc/app.bsky.feed.getListFeed"
#
# # Set up headers
# headers = {
#     "Authorization": f"Bearer {session_token}",
#     "Content-Type": "application/json"
# }
#
# # Set up parameters for the feed request
# feed_params = {
#     "list": "at://did:plc:tsrqneix4sgsbvrhz6arbuci/app.bsky.graph.list/3lbq3w3xvpx2d",
#     "limit": 100
# }
#
# # Initialize structures to store posts
# main_posts = []  # Stores main posts
# replies = {}  # Maps parent URI to a list of replies
#
# # Track post date range
# oldest_date = None
# newest_date = None
#
# # Total posts limit
# total_limit = 100
# posts_fetched = 0
#
# # Fetch posts
# while posts_fetched < total_limit:
#     feed_response = requests.get(feed_url, headers=headers, params=feed_params)
#
#     if feed_response.status_code == 200:
#         feed_data = feed_response.json()
#         posts = feed_data.get('feed', [])
#
#         if not posts:
#             break
#
#         for post in posts:
#             post_record = post.get('post', {}).get('record', {})
#             post_uri = post.get('post', {}).get('uri', 'Unknown URI')
#
#             # Capture the post's timestamp
#             post_timestamp = post_record.get('createdAt', None)
#             if post_timestamp:
#                 post_date = datetime.strptime(post_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").date()
#                 if oldest_date is None or post_date < oldest_date:
#                     oldest_date = post_date
#                 if newest_date is None or post_date > newest_date:
#                     newest_date = post_date
#
#             post['post']['text'] = post_record.get('text', '')  # Store text in post dictionary for later use
#
#             if 'reply' in post_record:
#                 parent_uri = post_record['reply']['parent']['uri']
#                 replies.setdefault(parent_uri, []).append(post)
#             else:
#                 if posts_fetched < total_limit:
#                     main_posts.append(post)
#                     posts_fetched += 1
#
#                 if posts_fetched >= total_limit:
#                     break
#
#         next_cursor = feed_data.get("cursor", None)
#         if next_cursor:
#             feed_params["cursor"] = next_cursor
#         else:
#             break
#     else:
#         print(f"Error fetching posts: {feed_response.status_code} {feed_response.text}")
#         break
#
# # Reverse order (oldest first)
# main_posts.reverse()
#
# # Format filename based on post date range
# if oldest_date and newest_date:
#     date_range_str = f"{oldest_date.strftime('%d%m%y')}_{newest_date.strftime('%d%m%y')}"
# else:
#     date_range_str = "nodate"
#
# output_file = os.path.join(output_dir, f"{date_range_str}.json")
#
# # Save posts to an HTML file
# with open(output_file, "w", encoding="utf-8") as file:
#     output = { "mainPosts": main_posts, "replies": replies }
#     file.write(json.dumps(output))
