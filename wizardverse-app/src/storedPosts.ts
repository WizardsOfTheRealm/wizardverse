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

export const storedPosts = import.meta.glob(
  "../../storedPosts/*.json"
) as Record<
  string,
  () => Promise<{
    mainPosts: Post[];
    replies: Record<string, Post[]>;
  }>
>;

export const bookIdentifiers = Object.keys(storedPosts);
