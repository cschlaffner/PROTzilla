import { useEffect, useState } from "react";

/** Returns how much a user scrolled from top */
export const useScrollPosition = (): number => {
  const [scrollValue, setScrollValue] = useState(0);

  const handleScroll = (e: Event): void => {
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    setScrollValue(e && (e.target as HTMLElement).scrollTop);
  };

  useEffect(() => {
    document.addEventListener("scroll", handleScroll, true);

    return () => {
      document.removeEventListener("scroll", handleScroll, true);
    };
  }, []);

  return scrollValue;
};
