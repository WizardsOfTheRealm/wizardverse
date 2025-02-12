const postContainer = document.getElementById("post-container");
const prevPageBtn = document.getElementById("prev-page");
const nextPageBtn = document.getElementById("next-page");

const listUri = "at://did:plc:tsrqneix4sgsbvrhz6arbuci/app.bsky.graph.list/3lbq3w3xvpx2d";

// Adjust this date to start from a specific point (ISO 8601 format)
const customStartDate = "2025-01-01T00:00:00Z";  // Example: January 1st, 2025

let currentPage = 0;
let allPosts = [];  // Store all posts across pages

// Ensure the post container is left-aligned
postContainer.style.textAlign = "left";  // Apply this style to ensure left-alignment

async function fetchPosts(pageIndex) {
    let url = `https://public.api.bsky.app/xrpc/app.bsky.feed.getListFeed?list=${encodeURIComponent(listUri)}&limit=100`;
    
    try {
        const response = await fetch(url, { headers: { "Content-Type": "application/json" } });
        if (!response.ok) throw new Error(`Error: ${response.status} ${await response.text()}`);

        const data = await response.json();
        const posts = data.feed;

        // Filter posts by custom start date
        const filteredPosts = posts.filter(post => new Date(post.post.record.createdAt) >= new Date(customStartDate));

        // Sort posts by date (oldest to newest)
        const sortedPosts = filteredPosts.sort((a, b) => new Date(a.post.record.createdAt) - new Date(b.post.record.createdAt));

        // Paginate sorted posts manually
        const postsPerPage = 20;
        const totalPages = Math.ceil(sortedPosts.length / postsPerPage);
        const startIndex = pageIndex * postsPerPage;
        const endIndex = startIndex + postsPerPage;
        const pagePosts = sortedPosts.slice(startIndex, endIndex);

        allPosts = sortedPosts;  // Store sorted posts globally
        currentPage = pageIndex;
        renderPosts(pagePosts);  // Render posts for the current page
        updateButtons(totalPages);  // Update pagination buttons

    } catch (error) {
        console.error("Failed to fetch posts:", error);
    }
}

function renderPosts(posts) {
    postContainer.innerHTML = ""; // Clear old posts
    console.log("Rendering posts:", posts);

    // Filter posts by custom start date
    const filteredPosts = posts.filter(post => new Date(post.post.record.createdAt) >= new Date(customStartDate));
    console.log("Filtered posts:", filteredPosts);

    // Sort posts by date (oldest to newest)
    const sortedPosts = filteredPosts.sort((a, b) => new Date(a.post.record.createdAt) - new Date(b.post.record.createdAt));
    console.log("Sorted posts:", sortedPosts);

    // Iterate over sorted posts and render them
    sortedPosts.forEach(post => {
        const uri = post.post.uri;
        const record = post.post.record;
        const parentUri = record.reply?.parent?.uri || null;

        // Skip rendering replies as main posts
        if (parentUri) {
            return;  // This is a reply, so we don't render it as a main post
        }

        // Main post: Render normally and append replies under it
        const postElement = createPostElement(post);
        postElement.dataset.uri = uri;
        postContainer.appendChild(postElement);
        console.log("Main post rendered:", postElement);

        // Now, append all replies under the main post
        const replies = getRepliesForPost(uri, sortedPosts); // Get all replies for the current main post
        console.log("Replies for this post:", replies);
        renderReplies(postElement, replies);
    });
}


function createPostElement(post) {
    const postDiv = document.createElement("div");
    postDiv.innerHTML = `
        <blockquote class="bluesky-embed" data-bluesky-uri="${post.post.uri}" data-bluesky-cid="${post.post.cid}"></blockquote>
    `;
    postContainer.appendChild(postDiv);

    // Add embed script for each post
    const script = document.createElement("script");
    script.src = "https://embed.bsky.app/static/embed.js";
    script.async = true;
    script.charset = "utf-8";
    document.body.appendChild(script);  // Appending the script after each post to make it work

    return postDiv;
}

function renderReplies(parentElement, replies) {
    if (replies.length === 0) return;  // No replies to render

    replies.sort((a, b) => new Date(a.post.record.createdAt) - new Date(b.post.record.createdAt));

    replies.forEach(reply => {
        const replyDiv = document.createElement("div");
        replyDiv.style.marginTop = "8px";  // Adds space between replies
        replyDiv.style.marginLeft = "20px";  // Consistent indentation for all replies
        replyDiv.style.textAlign = "left";  // Left-align text inside the reply container

        const flexContainer = document.createElement("div");
        flexContainer.style.display = "flex";  // Aligns the thread indicator and content horizontally
        flexContainer.style.alignItems = "flex-start";  // Ensures the thread image and content are aligned to the left

        const threadIndicator = document.createElement("img");
        threadIndicator.src = "images/thread.gif";
        threadIndicator.alt = "Reply Indicator";
        threadIndicator.style.width = "66px";  // Fixed width for the gif
        threadIndicator.style.height = "auto";  // Maintain the aspect ratio of the gif
        threadIndicator.style.marginRight = "8px";  // Space between the gif and reply content
        threadIndicator.style.verticalAlign = "top";  // Ensures the gif aligns with the top of the text
        threadIndicator.style.objectFit = "contain";  // Ensures the image doesn't stretch or scale

        const replyContent = document.createElement("div");
        replyContent.style.maxWidth = "500px";
        replyContent.innerHTML = `
            <blockquote class="bluesky-embed" data-bluesky-uri="${reply.post.uri}" data-bluesky-cid="${reply.post.cid}"></blockquote>
        `;

        flexContainer.appendChild(threadIndicator);
        flexContainer.appendChild(replyContent);

        replyDiv.appendChild(flexContainer);

        parentElement.appendChild(replyDiv);

        const script = document.createElement("script");
        script.src = "https://embed.bsky.app/static/embed.js";
        script.async = true;
        script.charset = "utf-8";
        document.body.appendChild(script);

        const childReplies = getRepliesForPost(reply.post.uri, allPosts);
        if (childReplies.length > 0) {
            renderReplies(replyDiv, childReplies);  // Recursively render child replies under this reply
        }
    });
}

function getRepliesForPost(postUri, allPosts) {
    return allPosts.filter(post => post.post.record.reply?.parent?.uri === postUri);
}

function updateButtons(totalPages) {
    prevPageBtn.disabled = currentPage === 0;
    nextPageBtn.disabled = currentPage === totalPages - 1;
}

// Event listeners for pagination
prevPageBtn.addEventListener("click", () => {
    if (currentPage > 0) fetchPosts(currentPage - 1);
});

nextPageBtn.addEventListener("click", () => {
    fetchPosts(currentPage + 1);
});

// Load first page
fetchPosts(0);
