import { useCallback, useRef } from "react";

export const useShortTap = <T extends Element>(
  handleShortTap: (event: React.PointerEvent<T>) => void,
  maxDuration = 300,
  canActivate = true,
): [
  (event: React.PointerEvent<T>) => void,
  (event: React.PointerEvent<T>) => void,
] => {
  const timeRefs = useRef<Record<number, number | undefined>>({});

  const startTap = useCallback(
    (event: React.PointerEvent<T>) => {
      if (!canActivate) return;
      timeRefs.current[event.pointerId] = Date.now();
    },
    [canActivate],
  );
  const stopTap = useCallback(
    (event: React.PointerEvent<T>) => {
      const lastStart = timeRefs.current[event.pointerId];
      if (lastStart === undefined) return;
      if (Date.now() - lastStart <= maxDuration) handleShortTap(event);
      timeRefs.current[event.pointerId] = undefined;
    },
    [handleShortTap, maxDuration],
  );

  return [startTap, stopTap];
};
