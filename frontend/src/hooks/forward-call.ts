import { useCallback } from "react";

/**
 * Returns a function that, when called, calls a passed callback functions with
 * the same arguments.
 */
export const useForwardCall = <A extends unknown[]>(
  ...callbacks: (((...args: A) => void) | null | undefined)[]
): ((...args: A) => void) =>
  useCallback((...args) => {
    callbacks.forEach((callback) => {
      callback?.(...args);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, callbacks);
