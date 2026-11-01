import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    base: process.env.BASE_PATH || env.BASE_PATH || "/",
    plugins: [react()],
    build: { outDir: "dist/client" },
  };
});
