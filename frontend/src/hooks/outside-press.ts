import { useCallback, useEffect } from "react";

import { useDelay } from "./delay";

const outsideCondition = <T extends HTMLElement>(
  ref: React.RefObject<T>,
  event: PointerEvent,
): boolean =>
  Boolean(
    ref.current &&
      !ref.current.contains(event.target as Node) &&
      document.body.contains(event.target as Node) &&
      // eslint-disable-next-line @typescript-eslint/no-deprecated
      !event.cancelBubble,
  );

/**
 * Hook to catch pointerdown events outside one or more elements.
 * @param ref Ref(s) to one or more elements.
 * @param callback The callback for a pointerdown event outside the element(s).
 * @param activateHandler Whether or not the handler is active.
 * @param shouldHandleBlur Whether or not the handler should fire on a blur event.
 */
export const useOutsidePress = <T extends HTMLElement>(
  ref: React.RefObject<T> | React.RefObject<T>[],
  callback?: (event: PointerEvent | FocusEvent) => void,
  activateHandler?: boolean,
  shouldHandleBlur = true,
): void => {
  const handleOutsidePress = useCallback(
    (event: PointerEvent) => {
      if (
        Array.isArray(ref)
          ? ref.every((singleRef) => outsideCondition(singleRef, event))
          : outsideCondition(ref, event)
      ) {
        callback?.(event);
      }
    },
    [callback, ref],
  );
  const handleBlur = useCallback(
    (event: FocusEvent) => {
      if (shouldHandleBlur) callback?.(event);
    },
    [callback, shouldHandleBlur],
  );

  const [schedule, cancel] = useDelay(
    useCallback(() => {
      document.addEventListener("pointerdown", handleOutsidePress);
      window.addEventListener("blur", handleBlur);
    }, [handleBlur, handleOutsidePress]),
    35,
  );

  useEffect(() => {
    if (activateHandler) {
      schedule();

      return () => {
        cancel();
        document.removeEventListener("pointerdown", handleOutsidePress);
        window.removeEventListener("blur", handleBlur);
      };
    }

    cancel();
    document.removeEventListener("pointerdown", handleOutsidePress);
    window.removeEventListener("blur", handleBlur);
    return () => {
      // Intentionally left blank
    };
  }, [activateHandler, cancel, schedule, handleBlur, handleOutsidePress]);
};
