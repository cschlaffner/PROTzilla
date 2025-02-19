import { useCallback, useState } from "react";

/**
 * Returns a function that, when called, triggers a re-render of the current
 * component.
 */
export const useForceUpdate = (): (() => void) => {
  const [, setHelperValue] = useState({});
  return useCallback(() => {
    setHelperValue({});
  }, []);
};
