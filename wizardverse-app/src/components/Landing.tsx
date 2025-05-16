import { Link } from "@tanstack/react-router";

import classes from "./Landing.module.css";
import clsx from "clsx";

import globewizard from "../assets/images/globewizard.gif";

export function Landing() {
  return (
    <div className={classes.nightsky}>
      <div className={clsx(classes.stars1, classes.space)}></div>
      <div className={clsx(classes.stars2, classes.space)}></div>
      <div className={clsx(classes.stars3, classes.space)}></div>

      <div className={classes.tree}>
        <Link to="/chapters">
          <img src={globewizard}></img>
        </Link>
      </div>
    </div>
  );
}
