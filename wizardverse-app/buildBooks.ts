import { Glob } from "bun";
import { basename } from "node:path";

const glob = new Glob("../storedPosts/chapters/*");

// Scans the current working directory and each of its sub-directories recursively
const bookPaths: string[] = [];
for await (const file of glob.scan({ cwd: ".", onlyFiles: false })) {
  console.log(file);
  bookPaths.push(file);
}

bookPaths.forEach(async (bookPath) => {
  const jsonGlob = new Glob(`${bookPath}/*.json`);
  const result = jsonGlob.scanSync({ cwd: "." });

  const jsonFiles: string[] = [];
  for await (const file of jsonGlob.scan({ cwd: "." })) {
    console.log(file);
    jsonFiles.push(file);
  }

  const contentPromises = jsonFiles.map(
    async (
      filePath,
    ): Promise<{ mainPosts: Post[]; replies: Record<string, Post[]> }> => {
      const file = Bun.file(filePath);
      const textContent = await file.text();
      return JSON.parse(textContent);
    },
  );

  type Post = {
    post: {
      uri: string;
      record: {
        text: string;
        createdAt: string; // date
      };
    };
  };

  // TODO order by date

  const allContents = await Promise.all(contentPromises);

  const merged = allContents.reduce(
    (acc, current) => {
      const replies = Object.keys(current.replies).reduce(
        (repliesAcc, mainPostId) => {
          console.log(acc);
          // repliesAcc
          if (repliesAcc[mainPostId]) {
            repliesAcc[mainPostId] = [
              ...repliesAcc[mainPostId],
              ...current.replies[mainPostId],
            ];
          } else {
            repliesAcc[mainPostId] = current.replies[mainPostId];
          }
          return repliesAcc;
        },
        acc.replies,
      );

      Object.keys(replies).forEach((mainPostKey) => {
        replies[mainPostKey].sort(
          (a, b) =>
            new Date(a.post.record.createdAt).getTime() -
            new Date(b.post.record.createdAt).getTime(),
        );
      });

      return {
        mainPosts: [...acc.mainPosts, ...current.mainPosts],
        replies: replies,
      };
    },
    { mainPosts: [], replies: {} },
  );

  // get all json file names for that book
  // const jsonFiles =
  // read all json files

  const bookName = basename(bookPath);

  // merge json contents (insert by date)
  await Bun.write(`./generated/${bookName}.json`, JSON.stringify(merged));
});
