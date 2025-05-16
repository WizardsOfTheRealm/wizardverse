export type StoredPost = Post & {
  isReply: true;
};

export type Post = {
  post: {
    uri: string;
    record: {
      text: string;
      createdAt: string; // date
    };
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

type ChapterIndex = Record<
  string,
  () => Promise<{
    mainPosts: StoredPost[];
    replies: Record<string, StoredPost[]>;
  }>
>;

export const chapterFileIndex = import.meta.glob(
  "./../generated/*.json",
) as ChapterIndex;

export const chapterIndex = Object.entries(chapterFileIndex).reduce(
  (acc, [key, value]) => {
    const sanitizedFileName = key.split("/").pop()!.split(".")[0];
    return { ...acc, [sanitizedFileName]: value };
  },
  {} as ChapterIndex,
);

export const chapters = Object.keys(chapterIndex);
