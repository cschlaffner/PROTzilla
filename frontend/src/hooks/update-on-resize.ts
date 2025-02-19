import { useEffect, useState } from "react";

/** Forces a rerender when the window is resized to new dimensions. */
export const useUpdateOnResize = (isActive = true): string | undefined => {
  const [size, setSize] = useState<string | undefined>(undefined);
  useEffect(() => {
    if (!isActive) return;

    const handleResize = () => {
      setSize(`${String(window.innerWidth)}x${String(window.innerHeight)}`);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [isActive]);

  return size;
};
