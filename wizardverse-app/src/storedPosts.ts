export type StoredPost = {
  isReply: boolean | undefined;
  post: {
    uri: string;
    text: string;
    author: {
      avatar: string;
      displayName: string;
      handle: string;
    };
    embed?: {
      images: [
        {
          thumb: string;
          fullsize: string;
          alt: string;
          aspectRatio: { height: number; width: number };
        },
      ];
    };
  };
};

type Book = {
  id: string;
  start: string;
  end?: string;
};

async function stableBookIdentifier(message: string) {
  const msgUint8 = new TextEncoder().encode(message); // encode as (utf-8) Uint8Array
  const hashBuffer = await window.crypto.subtle.digest("SHA-256", msgUint8); // hash the message
  const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
  const hashHex = hashArray
    .map((b) => b.toString(16).padStart(2, "0"))
    .join(""); // convert bytes to hex string
  return hashHex;
}

const createBook = async (start: string, end?: string) => ({
  id: await stableBookIdentifier(`${start}-${end}`),
  start,
  end,
});

export const books: Book[] = await Promise.all([
  createBook("2025-03-29", "2025-03-31"),
  // Current (no end defined)
  createBook("2025-04-01"),
]);

export const bookIndex = books.reduce(
  (acc, current) => ({ ...acc, [current.id]: current }),
  {} as Record<string, Book>,
);

type PostIndex = Record<
  string,
  () => Promise<{
    mainPosts: StoredPost[];
    replies: Record<string, StoredPost[]>;
  }>
>;

export const storedPosts = import.meta.glob(
  "../../storedPosts/*.json",
) as PostIndex;

// make the keys url-safe for now
Object.keys(storedPosts).forEach((filePath) => {
  storedPosts[filePath.replace("../../storedPosts/", "").replace(".json", "")] =
    storedPosts[filePath];
  delete storedPosts[filePath];
});

// Sort JSON files by date chronologically
export const postDates = Object.keys(storedPosts).sort((date) =>
  new Date(date).getTime(),
);
