import { useCallback, useState } from "react";

import { useDelay } from "./delay";

/**
 * A boolean flag that disables itself after a given duration.
 * Returns a tuple of the current state and helper functions to enable and
 * disable it.
 *
 * @returns `[isActive, enable, disable]`
 */
export const useVolatileFlag = (duration = 1000): [boolean, () => void, () => void] => {
  const [isActive, setIsActive] = useState(false);
  const [scheduleDismiss, cancelDismiss] = useDelay(
    useCallback(() => {
      setIsActive(false);
    }, []),
    duration,
  );

  const enable = useCallback(() => {
    setIsActive(true);
    scheduleDismiss();
  }, [scheduleDismiss]);

  const disable = useCallback(() => {
    setIsActive(false);
    cancelDismiss();
  }, [cancelDismiss]);

  return [isActive, enable, disable];
};
