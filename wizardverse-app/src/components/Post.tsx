import clsx from "clsx";
import type { StoredPost } from "../storedPosts";
import classes from "./Post.module.css";
import butterfly from "../assets/images/blubutterfly.gif";

type Props = {
  post: StoredPost;
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
  const { author, embed, uri, record } = post.post;
  const images = embed?.images;
  const formattedUri = uri
    .replace("at://", "https://bsky.app/profile/")
    .replace("/app.bsky.feed.post/", "/post/");
  // const formattedText = text.replace(/<br\s*\\?>/g, "\r\n");
  return (
    <div className={clsx(classes.post, { [classes.reply]: post.isReply })}>
      <a href={formattedUri} target="_blank" rel="noopener noreferrer">
        <img className={classes.topRightImage} src={butterfly} alt="Bluesky" />
      </a>
      <img className={classes.avatar} src={author.avatar} />
      <div className={classes.content}>
        <div className={classes.header}>
          <div className={classes.authorName}>{author.displayName}</div>
          <div>
            <a className={classes.handle} href={urlForHandle(author.handle)}>
              @{author.handle}
            </a>
          </div>
        </div>
        <span className={classes.text}>{record.text}</span>
        {images &&
          images.map((image) => (
            <img
              key={image.fullsize}
              className={classes.image}
              src={image.fullsize}
            ></img>
          ))}
      </div>
    </div>
  );
}
