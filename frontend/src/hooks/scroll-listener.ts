import { useEffect } from "react";

/**
 * Registers a document scroll listener on mount and takes care of the clean up
 * on unmount.
 */
export const useScrollListener = (handleScroll?: (event: Event) => void, isActive = true): void => {
  useEffect(() => {
    if (!isActive || !handleScroll) return;

    document.addEventListener("scroll", handleScroll, true);
    return () => {
      document.removeEventListener("scroll", handleScroll);
    };
  }, [handleScroll, isActive]);
};
