import { createFileRoute, Link } from "@tanstack/react-router";
import { bookIdentifiers } from "../storedPosts";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "16px",
        marginTop: "16px",
      }}
    >
      {bookIdentifiers.map((bookId, index) => (
        <Link
          key={bookId}
          to="/books/$bookId"
          params={{
            bookId,
          }}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <img width={600} src="src/assets/bookquill.gif" alt="Enter"></img>
          <span
            style={{
              color: "yellow",
              fontSize: "32px",
            }}
          >
            Book {index + 1}
          </span>
        </Link>
      ))}
    </div>
  );
}
