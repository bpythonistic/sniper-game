import { defineConfig } from "eslint-define-config";

export default defineConfig({
    extends: [
        "eslint:recommended",
        "plugin:react/recommended",
        "plugin:react-hooks/recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:import/errors",
        "plugin:import/warnings",
        "plugin:jsx-a11y/recommended",
        "prettier",
    ],
    parser: "@typescript-eslint/parser",
    plugins: [
        "@typescript-eslint",
        "react",
        "react-hooks",
        "import",
        "jsx-a11y",
        "prettier",
    ],
    settings: {
        react: {
            version: "detect",
        },
    },
});
