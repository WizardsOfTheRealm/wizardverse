import { createFileRoute } from "@tanstack/react-router";
import { storedPosts } from "../storedPosts";
import { Thread } from "../components/Thread";

export const Route = createFileRoute("/books/$bookId")({
  component: RouteComponent,
  loader: async ({ params }) => {
    const postDataAsync = storedPosts[params.bookId];
    const { mainPosts, replies } = await postDataAsync();
    return { mainPosts, replies };
  },
});

function RouteComponent() {
  const { mainPosts, replies } = Route.useLoaderData();
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "8px",
      }}
    >
      {mainPosts.map((post) => (
        <Thread
          key={post.post.uri}
          post={post}
          replies={replies[post.post.uri] || []}
        />
      ))}
    </div>
  );
}
