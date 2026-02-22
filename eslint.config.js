import { defineConfig } from "eslint-define-config";
import react from "eslint-plugin-react";
import reacthooks from "eslint-plugin-react-hooks";

export default defineConfig({
    files: ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"],
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
