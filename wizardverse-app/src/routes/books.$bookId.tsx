import { createFileRoute, redirect } from "@tanstack/react-router";
import { bookIndex, StoredPost, storedPosts } from "../storedPosts";
import { useEffect, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useInfiniteQuery } from "@tanstack/react-query";
import { addDays, format } from "date-fns";
import { Post } from "../components/Post";

export const Route = createFileRoute("/books/$bookId")({
  component: RouteComponent,
  loader: async ({ params }) => {
    const book = bookIndex[params.bookId];
    if (!book) {
      throw redirect({ statusCode: 404 });
    }
    return { book };
  },
});

const DATE_FORMAT = "yyyy-MM-dd";

const formatDate = (date: Date) => format(date, DATE_FORMAT);

function RouteComponent() {
  const { book } = Route.useLoaderData();
  const { start, end } = book;
  const parentRef = useRef(null);

  const {
    status,
    data,
    error,
    isFetching,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useInfiniteQuery({
    queryKey: ["books", book.id],
    queryFn: async (
      ctx,
    ): Promise<{ posts: StoredPost[]; nextDate: string }> => {
      const postFetcher = storedPosts[ctx.pageParam];

      const { mainPosts, replies } = await postFetcher();
      const posts = mainPosts
        .map((post) => {
          const currentReplies = (replies[post.post.uri] || []).map((post) => ({
            ...post,
            isReply: true,
          }));
          return [post, ...currentReplies];
        })
        .flat();

      var dateParts = ctx.pageParam.split("-").map(Number);
      const nextDate = formatDate(
        addDays(new Date(dateParts[0], dateParts[1] - 1, dateParts[2]), 1),
      );
      return {
        posts,
        nextDate,
      };
    },
    getNextPageParam: ({ nextDate }) =>
      nextDate === end || !(nextDate in storedPosts) ? null : nextDate,
    initialPageParam: start,
  });

  const allRows = data ? data.pages.flatMap((d) => d.posts) : [];

  const virtualizer = useVirtualizer({
    count: hasNextPage ? allRows.length + 1 : allRows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 45,
    overscan: 3,
    gap: 4,
  });

  const virtualItems = virtualizer.getVirtualItems();

  useEffect(() => {
    const lastItem =
      virtualItems.length === 0
        ? undefined
        : virtualItems[virtualItems.length - 1];

    if (!lastItem) {
      return;
    }

    if (lastItem.index >= allRows.length - 1 && hasNextPage && !isFetching) {
      fetchNextPage();
    }
  }, [
    hasNextPage,
    fetchNextPage,
    allRows.length,
    isFetchingNextPage,
    virtualItems,
  ]);

  if (status === "pending") {
    return <p>Loading...</p>;
  }

  if (status === "error") {
    return <span>Error: {error.message}</span>;
  }

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
            const isLoaderRow = virtualRow.index > allRows.length - 1;

            const post = allRows[virtualRow.index];
            return (
              <div
                key={virtualRow.key}
                data-index={virtualRow.index}
                ref={virtualizer.measureElement}
              >
                {isLoaderRow ? (
                  "Loading"
                ) : (
                  <Post
                    key={post.post.uri}
                    post={post}
                    isReply={post.isReply}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
