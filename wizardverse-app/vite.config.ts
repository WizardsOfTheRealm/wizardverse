import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";

// https://vite.dev/config/
export default defineConfig(({ command }) => {
  return {
    base: command === "serve" ? "" : "/wizardverse/",
    css: {
      transformer: "lightningcss",
    },
    build: {
      cssMinify: "lightningcss",
      localsConvention: "camelCaseOnly",
      target: "es2022",
    },
    plugins: [react(), TanStackRouterVite({ autoCodeSplitting: true })],
  };
});
