import { defineConfig } from "eslint/config";

export default defineConfig({
  files: ["**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"],
  env: {
    browser: true,
  },
  parserOptions: {
    ecmaVersion: 12,
    sourceType: "module",
  },
  extends: ["eslint:recommended"],
  rules: {
    "no-console": "warn",
    "prefer-const": "error",
  },
});
