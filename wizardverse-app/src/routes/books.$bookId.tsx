import { createFileRoute } from "@tanstack/react-router";
import { storedPosts } from "../storedPosts";
import { Thread } from "../components/Thread";
import { useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

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
  const parentRef = useRef(null);

  const virtualizer = useVirtualizer({
    count: mainPosts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 45,
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  return (
    <div
      ref={parentRef}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "8px",
      }}
    >
      <div
        style={{
          height: virtualizer.getTotalSize(),
          width: "100%",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            transform: `translateY(${virtualItems[0]?.start ?? 0}px)`,
          }}
        >
          {virtualItems.map((virtualRow) => {
            const post = mainPosts[virtualRow.index];
            return (
              <div
                key={virtualRow.key}
                data-index={virtualRow.index}
                ref={virtualizer.measureElement}
              >
                <Thread
                  key={post.post.uri}
                  post={post}
                  replies={replies[post.post.uri] || []}
                />
              </div>
            );
          })}
        </div>

        {mainPosts.map((post) => (
          <Thread
            key={post.post.uri}
            post={post}
            replies={replies[post.post.uri] || []}
          />
        ))}
      </div>
    </div>
  );
}
