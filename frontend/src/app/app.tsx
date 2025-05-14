import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { ModalRoot, NotificationCenter } from "../components";
import { RootStore } from "../models";
import { getTheme, GlobalStyles, ThemeProvider } from "../theme";
import { setupRootStore, StoreProvider } from "./store";
import { IndexScreen, MainScreen, RunScreen } from "../screens";
import { AutomaticErrorNotification } from "./automatic-error-notification";

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
