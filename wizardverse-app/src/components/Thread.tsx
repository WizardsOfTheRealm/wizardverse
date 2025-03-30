import type { Post as PostData } from "../storedPosts";
import { Post } from "./Post";
import classes from "./Thread.module.css";

type Props = {
  post: PostData;
  replies: PostData[];
};

export function Thread({ post, replies }: Props) {
  return (
    <div className={classes.thread}>
      <Post post={post} />
      <div className={classes.replies}>
        {replies.map((reply) => (
          <Post key={reply.post.uri} post={reply} />
        ))}
      </div>
    </div>
  );
}
