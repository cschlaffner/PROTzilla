import { useEffect, useState } from "react";

/** Forces a rerender when the given element is resized to new dimensions. */
export const useUpdateOnElementResize = (
  element?: HTMLElement | null,
  isActive = true,
): string | undefined => {
  const [size, setSize] = useState<string | undefined>(undefined);
  useEffect(() => {
    if (!isActive || !element) return;

    const handleResize = () => {
      setSize(`${String(element.offsetWidth)}x${String(element.offsetHeight)}`);
    };
    new ResizeObserver(handleResize).observe(element);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [element, isActive]);

  return size;
};
