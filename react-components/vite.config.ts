import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  plugins: [react()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  build: {
    lib: {
      entry: "./src/main.ts",
      name: "react_vtk",
      formats: ["umd"],
      fileName: () => "trame-vtk-react.js",
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
        },
      },
    },
    // js/ also holds the vue bundle (trame-vtk.js)
    emptyOutDir: false,
    outDir: "../src/trame_vtk/modules/common/serve",
    assetsDir: ".",
  },
});
