import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { MainScreen, ModalRoot } from "../components";
import { initI18nApp } from "../i18n";
import { RootStore } from "../models";
import { getTheme, GlobalStyles, ThemeProvider } from "../theme";
import { AutomaticErrorNotification } from "./automatic-error-notification";
import { setupRootStore, StoreProvider } from "./store";
import { CountersScreen, IndexScreen, InputFieldTestScreen } from "../screens";

function App() {
  const [isReady, setIsReady] = useState(false);
  const rootStoreRef = useRef<RootStore | null>(null);
  useEffect(() => {
    Promise.all([setupRootStore(), initI18nApp()])
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
        <GlobalStyles theme={theme} />
        {isReady && (
          <Suspense fallback={null}>
            <ModalRoot>
              <AutomaticErrorNotification />
            </ModalRoot>
            <Routes>
              <Route path="/" element={<MainScreen />}>
                <Route path="/" element={<IndexScreen />} />
                <Route path="/counters" element={<CountersScreen />} />
                <Route path="/input" element={<InputFieldTestScreen />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        )}
      </StoreProvider>
    </ThemeProvider>
  );
}

export default App;
