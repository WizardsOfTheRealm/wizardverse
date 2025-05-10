# created: Apr 19 2025 by Blue Wizard
# Purpose: process daily files produced by worPostGrabberJSON_greig.py
#          which returns daily files, formatted as 'threads'
# input:   daily files in wizardverse\storedPosts\test_greig
# output:  daily files formatted as the CTO requires, as 'List' 
#          i.e., as 'MainPosts' and 'Replies' in flat format 
import os
import json
from datetime import datetime, timedelta

# ========== CONFIGURABLE PARAMETERS ==========
INPUT_FOLDER = "storedPosts/test_greig/prlg"
OUTPUT_FOLDER = os.path.join(INPUT_FOLDER, "converted")
INPUT_PREFIX = "prlg_"
INPUT_SUFFIX = ".json"
DATE_FORMAT_INPUT = "%Y%m%d"
DATE_FORMAT_OUTPUT = "%Y-%m-%d"
# =============================================

def flatten_replies(thread_view_post, parent_uri=None):
    replies_dict = {}
    post = thread_view_post.get("post")
    if not post:
        return replies_dict

    # Inject 'text' at top level
    if "record" in post and isinstance(post["record"], dict) and "text" in post["record"]:
        post["text"] = post["record"]["text"]

    if parent_uri:
        replies_dict.setdefault(parent_uri, []).append({"post": post})

    for reply in thread_view_post.get("replies", []):
        if isinstance(reply, dict) and reply.get("$type") == "app.bsky.feed.defs#threadViewPost":
            nested_uri = post.get("uri")
            nested = flatten_replies(reply, parent_uri=nested_uri)
            for k, v in nested.items():
                replies_dict.setdefault(k, []).extend(v)

    return replies_dict

def convert_threads_to_main_posts_and_replies(threads):
    result = {
        "mainPosts": [],
        "replies": {}
    }

    for item in threads:
        thread = item.get("thread")
        if thread and thread.get("$type") == "app.bsky.feed.defs#threadViewPost":
            top_post = thread.get("post")
            if top_post:
                # Inject 'text' at top level
                if "record" in top_post and isinstance(top_post["record"], dict) and "text" in top_post["record"]:
                    top_post["text"] = top_post["record"]["text"]

                result["mainPosts"].append({"post": top_post})

                for reply in thread.get("replies", []):
                    if reply.get("$type") == "app.bsky.feed.defs#threadViewPost":
                        reply_map = flatten_replies(reply, parent_uri=top_post.get("uri"))
                        for uri, reply_list in reply_map.items():
                            result["replies"].setdefault(uri, []).extend(reply_list)

    return result

def process_date_range(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    current = start_date
    while current <= end_date:
        input_filename = f"{INPUT_PREFIX}{current.strftime(DATE_FORMAT_INPUT)}{INPUT_SUFFIX}"
        input_path = os.path.join(INPUT_FOLDER, input_filename)

        if os.path.exists(input_path):
            with open(input_path, "r", encoding="utf-8") as f:
                try:
                    threads = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️ Could not decode JSON in file: {input_filename}")
                    current += timedelta(days=1)
                    continue

            converted = convert_threads_to_main_posts_and_replies(threads)

            output_filename = f"{current.strftime(DATE_FORMAT_OUTPUT)}.json"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(converted, f_out, indent=2)

            print(f"✅ Processed {input_filename} → {output_filename}")
        else:
            print(f"⛔ File not found: {input_filename}")

        current += timedelta(days=1)

# ========== USER INPUT ==========
if __name__ == "__main__":
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    process_date_range(start_date, end_date)