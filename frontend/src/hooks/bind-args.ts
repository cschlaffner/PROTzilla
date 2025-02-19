import { useCallback } from "react";

export const useBindArgs = <T extends readonly unknown[], R>(
  fn: ((...args: T) => R) | undefined,
  ...args: T
) =>
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useCallback(() => fn?.(...args), [...args]);
