module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ["react", "react-hooks", "@typescript-eslint"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier",
  ],
  settings: {
    react: {
      version: "detect",
    },
  },
  ignorePatterns: ["dist", "node_modules"],
  rules: {
    // 🔥 CRITICAL RULES - Prevent your exact errors
    "no-duplicate-imports": "error",
    "no-redeclare": "error",
    "@typescript-eslint/no-unused-vars": [
      "warn",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      },
    ],

    // React rules
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",

    // Clean code
    "semi": ["error", "always"],
    "quotes": ["error", "double"],

    // Hooks safety
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",

    // Disable TypeScript errors for now (will enable gradually)
    "@typescript-eslint/no-explicit-any": "off",
  },
};
