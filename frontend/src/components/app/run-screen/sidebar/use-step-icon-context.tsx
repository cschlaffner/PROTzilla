import { createContext, useContext } from "react";

import { IconContextProps } from "./step-icon-context.tsx";

export const IconContext = createContext<IconContextProps | undefined>(undefined);

export const useIconContext = () => {
  const context = useContext(IconContext);
  if (!context) {
    throw new Error("useIconContext must be used within an IconProvider");
  }
  return context;
};
