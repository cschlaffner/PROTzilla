import { useEffect, useState } from "react";

/** Returns width and height object on resize of a window */
export const useWindowDimensions = (): { width: number; height: number } => {
  const { innerWidth: width, innerHeight: height } = window;

  const [size, setSize] = useState({ width, height });
  const handleResize = () => {
    setSize({ width: window.innerWidth, height: window.innerHeight });
  };

  useEffect(() => {
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return size;
};
