import React, { useState } from "react";

import { IconContext } from "./use-step-icon-context";

export interface IconContextProps {
  icons: Record<string, string>;
  setIcon: (stepId: string, icon: string) => void;
}

interface IconProviderProps {
  children: React.ReactNode;
}

export const IconProvider: React.FC<IconProviderProps> = ({ children }) => {
  const [icons, setIcons] = useState<Record<string, string>>({});

  const setIcon = (stepId: string, icon: string) => {
    setIcons((prevIcons) => ({ ...prevIcons, [stepId]: icon }));
  };

  return <IconContext.Provider value={{ icons, setIcon }}>{children}</IconContext.Provider>;
};
