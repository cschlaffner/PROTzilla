import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./app/app.tsx";
import { IconProvider } from "./components/sidebar/step-icon-context.tsx";

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <IconProvider>
        <App />
      </IconProvider>
    </BrowserRouter>
  </StrictMode>,
);
