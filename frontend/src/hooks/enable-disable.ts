import { useCallback } from "react";

/**
 * Returns a tuple of `[enable, disable]` functions that, when called, call
 * `setState` with `true` or `false` as an argument respectively.
 */
export const useEnableDisable = (
  setState: (value: boolean) => void,
): [() => void, () => void] => [
  useCallback(() => {
    setState(true);
  }, [setState]),
  useCallback(() => {
    setState(false);
  }, [setState]),
];
