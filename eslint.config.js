import { defineConfig } from "eslint-define-config";
import react from "eslint-plugin-react";
import reacthooks from "eslint-plugin-react-hooks";

export default defineConfig({
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
