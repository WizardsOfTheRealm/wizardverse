export type Post = {
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
        }
      ];
    };
  };
};

type PostIndex = Record<
  string,
  () => Promise<{
    mainPosts: Post[];
    replies: Record<string, Post[]>;
  }>
>;

export const storedPosts = import.meta.glob(
  "../../storedPosts/*.json"
) as PostIndex;

// make the keys url-safe for now
Object.keys(storedPosts).forEach((filePath) => {
  storedPosts[filePath.replace("../../storedPosts/", "").replace(".json", "")] =
    storedPosts[filePath];
  delete storedPosts[filePath];
});

export const bookIdentifiers = Object.keys(storedPosts);
