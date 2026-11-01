import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = process.env.VITE_API_BASE_URL || env.VITE_API_BASE_URL;
  if (apiBase) {
    const url = new URL(apiBase);
    const local = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
    if (url.protocol !== "https:" && !(local && url.protocol === "http:")) {
      throw new Error("VITE_API_BASE_URL must use HTTPS, except for a local backend.");
    }
    if (url.username || url.password || url.search || url.hash || url.pathname !== "/") {
      throw new Error("VITE_API_BASE_URL must be a backend origin, without credentials, query, or path.");
    }
  }
  return {
    base: process.env.BASE_PATH || env.BASE_PATH || "/",
    plugins: [react()],
    build: { outDir: "dist/client" },
  };
});
