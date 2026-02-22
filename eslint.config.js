import { defineConfig } from "eslint-define-config";
import { react } from "eslint-plugin-react";
import { reacthooks } from "eslint-plugin-react-hooks";

export default defineConfig({
    // extends: [
    //     "eslint:recommended",
    //     "plugin:react/recommended",
    //     "plugin:react-hooks/recommended",
    //     "plugin:@typescript-eslint/recommended",
    //     "plugin:import/errors",
    //     "plugin:import/warnings",
    //     "plugin:jsx-a11y/recommended",
    //     "prettier",
    // ],
    // parser: "@typescript-eslint/parser",
    plugins: {
        react: react,
        reacthooks: reacthooks,
    },
    settings: {
        react: {
            version: "detect",
        },
    },
});
