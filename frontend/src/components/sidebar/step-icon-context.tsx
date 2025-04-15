import React, { createContext, useContext, useState } from "react";

interface IconContextProps {
  icons: Record<string, string>;
  setIcon: (stepId: string, icon: string) => void;
}

interface IconProviderProps {
  children: React.ReactNode;
}

const IconContext = createContext<IconContextProps | undefined>(undefined);

export const IconProvider: React.FC<IconProviderProps> = ({ children }) => {
  const [icons, setIcons] = useState<Record<string, string>>({});

  const setIcon = (stepId: string, icon: string) => {
    setIcons((prevIcons) => ({ ...prevIcons, [stepId]: icon }));
  };

  return (
    <IconContext.Provider value={{ icons, setIcon }}>
      {children}
    </IconContext.Provider>
  );
};

export const useIconContext = () => {
  const context = useContext(IconContext);
  if (!context) {
    throw new Error("useIconContext must be used within an IconProvider");
  }
  return context;
};
