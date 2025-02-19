import React from "react";

import { RootStore } from "../models";

// eslint-disable-next-line react-refresh/only-export-components, @typescript-eslint/require-await
export const setupRootStore = async (): Promise<RootStore> => {
  const store = new RootStore();
  // TODO: Hydrate
  return store;
};

// eslint-disable-next-line react-refresh/only-export-components
export const storeContext = React.createContext<RootStore | null>(null);
export const StoreProvider = storeContext.Provider;
// eslint-disable-next-line react-refresh/only-export-components
export const useStore = (): RootStore =>
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  React.useContext(storeContext)!;
