import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./AppRouter";
import "./index.css";
// import './styles/shared.css';
import { WorkspaceProvider } from "./context/WorkspaceContext.tsx";
import { SchemaProvider } from "./components/schema/SchemaContext";
// Import global governance styles
import "./styles/global.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppRouter />
  </React.StrictMode>
);
