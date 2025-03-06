import type { Post } from "../storedPosts";
import classes from "./Post.module.scss";

type Props = {
  post: Post;
};

/**
 * TODO
 * embedded tags
 * profile links
 *
 * embed.images[]
 */

// const handle = https://bsky.app/profile/thegreenwizard.bsky.social

const urlForHandle = (handle: string) => `https://bsky.app/profile/${handle}`;

export function Post({ post }: Props) {
  const { author, text, embed } = post.post;
  const images = embed?.images;
  // const formattedText = text.replace(/<br\s*\\?>/g, "\r\n");
  return (
    <div className={classes.post}>
      <img className={classes.avatar} src={author.avatar} />
      <div className={classes.content}>
        <div className={classes.header}>
          <span className={classes.authorName}>{author.displayName}</span>
          <a className={classes.handle} href={urlForHandle(author.handle)}>
            @{author.handle}
          </a>
        </div>
        <span className={classes.text}>{text}</span>
        {images &&
          images.map((image) => (
            <img className={classes.image} src={image.fullsize}></img>
          ))}
      </div>
    </div>
  );
}
