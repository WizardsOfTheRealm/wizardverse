import { createRootRoute, Outlet, useMatch } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";
import clsx from "clsx";

import classes from "./__root.module.css";

export const Route = createRootRoute({
  component: () => {
    const isLanding = useMatch({ from: "/" });
    return (
      <div
        className={clsx(classes.root, { [classes.wandBackground]: !isLanding })}
      >
        {!isLanding && (
          <>
            <h1 className={classes.headerText}>WIZARDS OF THE REALM</h1>
            <span className={classes.marquee}>
              I'VE HEARD OF "SCROLLS" BUT THIS IS RIDICULOUS
            </span>
            <hr />
          </>
        )}
        <Outlet />
        <TanStackRouterDevtools />
      </div>
    );
  },
});
