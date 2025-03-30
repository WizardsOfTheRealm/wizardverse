import { Link } from "@tanstack/react-router";

import classes from "./Landing.module.css";
import clsx from "clsx";

export function Landing() {
  return (
    <div className={classes.nightsky}>
      <div className={clsx(classes.stars1, classes.space)}></div>
      <div className={clsx(classes.stars2, classes.space)}></div>
      <div className={clsx(classes.stars3, classes.space)}></div>

      <div className={classes.tree}>
        <Link to="/books">
          <img src="src/assets/images/globewizard.gif"></img>
        </Link>
      </div>
    </div>
  );
}
