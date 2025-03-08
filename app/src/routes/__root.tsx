import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";
import classes from "./__root.module.scss";

export const Route = createRootRoute({
  component: () => (
    <div className={classes.root}>
      <h1 className={classes.headerText}>WIZARDS OF THE REALM</h1>
      <span className={classes.marquee}>
        I'VE HEARD OF "SCROLLS" BUT THIS IS RIDICULOUS
      </span>
      <hr />
      <Outlet />
      <TanStackRouterDevtools />
    </div>
  ),
});
