import { createFileRoute, Link } from "@tanstack/react-router";
import { chapters } from "../storedPosts";
import bookQuill from "../assets/images/bookquil.gif";

export const Route = createFileRoute("/chapters/")({
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
      {chapters.map((chapterName, index) => (
        <Link
          key={chapterName}
          to="/chapters/$chapterId"
          params={{
            chapterId: chapterName,
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
            {chapterName}
          </span>
        </Link>
      ))}
    </div>
  );
}
