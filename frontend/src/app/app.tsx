import { IndexScreen, MainScreen, NotificationCenter, RunScreen } from "@protzilla/app";
import { ModalRoot } from "@protzilla/core/shared";
import { getTheme, GlobalStyles, ThemeProvider } from "@protzilla/theme";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { RootStore } from "../models";
import { AutomaticErrorNotification } from "./automatic-error-notification";
import { setupRootStore, StoreProvider } from "./store";

function App() {
  const [isReady, setIsReady] = useState(false);
  const rootStoreRef = useRef<RootStore | null>(null);
  useEffect(() => {
    Promise.all([setupRootStore()])
      .then(([store]) => {
        rootStoreRef.current = store;
        setIsReady(true);
      })
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      .catch(() => {});
  }, []);

  const theme = useMemo(() => getTheme(), []);

  return (
    <ThemeProvider theme={theme}>
      <StoreProvider value={rootStoreRef.current}>
        <NotificationCenter>
          <GlobalStyles theme={theme} />
          {isReady && (
            <Suspense fallback={null}>
              <ModalRoot />
              <AutomaticErrorNotification />
              <Routes>
                <Route path="/" element={<MainScreen />}>
                  <Route path="/" element={<IndexScreen />} />
                  <Route path="/run" element={<RunScreen />} />
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          )}
        </NotificationCenter>
      </StoreProvider>
    </ThemeProvider>
  );
}

export default App;
