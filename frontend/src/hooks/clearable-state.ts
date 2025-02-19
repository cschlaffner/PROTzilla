import { useCallback, useState } from "react";

/** Returns a tuple of `[state, setState, clearState]`. */
export const useClearableState = <T>(defaultValue?: T) => {
  const [state, setState] = useState<T>(defaultValue as T);
  const clearState = useCallback(() => {
    setState(undefined as T);
  }, []);

  return [state, setState, clearState] as const;
};
