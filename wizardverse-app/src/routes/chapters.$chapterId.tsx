import { createFileRoute, redirect } from "@tanstack/react-router";
import { chapterIndex } from "../storedPosts";
import { useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { Post } from "../components/Post";

export const Route = createFileRoute("/chapters/$chapterId")({
  component: RouteComponent,
  loader: async ({ params }) => {
    const chapterFetcher = chapterIndex[params.chapterId];
    if (!chapterFetcher) {
      throw redirect({ statusCode: 404 });
    }
    const { mainPosts, replies } = await chapterFetcher();
    const chapter = mainPosts
      .map((post) => {
        const currentReplies = (replies[post.post.uri] || []).map((post) => ({
          ...post,
          isReply: true as const,
        }));
        return [post, ...currentReplies];
      })
      .flat();

    return { chapter };
  },
});

function RouteComponent() {
  const { chapter } = Route.useLoaderData();
  const parentRef = useRef(null);

  const virtualizer = useVirtualizer({
    count: chapter.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 45,
    overscan: 3,
    gap: 4,
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
            const post = chapter[virtualRow.index];
            return (
              <div
                key={virtualRow.key}
                data-index={virtualRow.index}
                ref={virtualizer.measureElement}
              >
                <Post key={post.post.uri} post={post} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
