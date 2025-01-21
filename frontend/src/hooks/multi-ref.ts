import { useCallback } from "react";
import type React from "react";

/** Returns a function ref that updates all passed refs when called. */
export const useMultiRef = <T>(...refs: React.Ref<T>[]): React.RefCallback<T> =>
  useCallback((element: T | null) => {
    refs.forEach((ref) => {
      if (typeof ref === "function") {
        ref(element);
      } else if (ref) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (ref as any).current = element;
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, refs);
