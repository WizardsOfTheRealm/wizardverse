import { createFileRoute, Link } from "@tanstack/react-router";
import { books } from "../storedPosts";
import bookQuill from "../assets/images/bookquil.gif";

export const Route = createFileRoute("/books/")({
  component: RouteComponent,
});

function RouteComponent() {
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
      {books.map(({ id: bookId }, index) => (
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
          <img width={600} src={bookQuill} alt="Enter"></img>
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
