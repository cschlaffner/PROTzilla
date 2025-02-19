import { useCallback, useState } from "react";

/**
 * Returns a tuple of the current state and helper functions to enable,
 * disable, and toggle it.
 *
 * @param initialValue The initial state
 * @returns A tuple of `[isActive, enable, disable, toggle]`
 */
export const useToggleableState = (
  initialValue = false,
): [boolean, () => void, () => void, () => void] => {
  const [isActive, setIsActive] = useState(initialValue);
  const enable = useCallback(() => {
    setIsActive(true);
  }, []);
  const disable = useCallback(() => {
    setIsActive(false);
  }, []);
  const toggle = useCallback(() => {
    setIsActive(!isActive);
  }, [isActive]);

  return [isActive, enable, disable, toggle];
};
