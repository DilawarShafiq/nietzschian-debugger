import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { backendOrigin } from "./shared/backend-chat.js";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = process.env.VITE_API_BASE_URL || env.VITE_API_BASE_URL;
  if (apiBase) backendOrigin(apiBase);
  return {
    base: process.env.BASE_PATH || env.BASE_PATH || "/",
    plugins: [react()],
    build: { outDir: "dist/client" },
  };
});
