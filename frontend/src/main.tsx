import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { Callback } from "./CallBack.tsx";
import { LogtoProvider, type LogtoConfig } from "@logto/react";
import { LOGTO_SCOPES } from "./logtoScopes.ts";

const router = createBrowserRouter([
  {
    path: "/",
    Component: App,
  },
  {
    path: "callback",
    Component: Callback,
  },
]);

const config: LogtoConfig = {
  endpoint: "https://y9fivj.logto.app/",
  appId: "994bq29s02bwqwawpg7yl",
  resources: ["https://dev.punchedn.com/api"],
  scopes: LOGTO_SCOPES,
};

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LogtoProvider config={config}>
      <RouterProvider router={router} />,
    </LogtoProvider>
  </StrictMode>,
);
