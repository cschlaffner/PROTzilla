import { useCallback, useRef } from "react";

export const useLongPress = <T extends Element>(
  handleLongPress: (event: React.PointerEvent<T>) => void,
  minDuration = 500,
  canActivate = true,
): [
  (event: React.PointerEvent<T>) => void,
  (event: React.PointerEvent<T>) => void,
] => {
  const timerRefs = useRef<Record<number, number | undefined>>({});

  const startPress = useCallback(
    (event: React.PointerEvent<T>) => {
      if (!canActivate) return;
      timerRefs.current[event.pointerId] = setTimeout(() => {
        handleLongPress(event);
      }, minDuration) as unknown as number;
    },
    [canActivate, handleLongPress, minDuration],
  );
  const stopPress = useCallback((event: React.PointerEvent<T>) => {
    const timer = timerRefs.current[event.pointerId];
    if (timer === undefined) return;
    clearTimeout(timer);
    timerRefs.current[event.pointerId] = undefined;
  }, []);

  return [startPress, stopPress];
};
