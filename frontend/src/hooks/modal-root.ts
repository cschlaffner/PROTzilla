import { MutableRefObject, useEffect, useRef } from "react";

import { useTheme } from "@protzilla/theme";
import { useForceUpdate } from "./force-update";

/**
 * Returns a ref to an element that is part of the modal root (if there is one)
 * to render to using a ReactDOM portal.
 */
export const useModalRoot: () => MutableRefObject<HTMLElement | undefined> = () => {
  // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
  const modalRootId = useTheme()?.modalRootId;
  const modalRoot = document.getElementById(modalRootId);

  const modalRootRef = useRef<HTMLElement>();
  const forceUpdate = useForceUpdate();
  useEffect(() => {
    if (modalRoot) {
      modalRootRef.current = document.createElement("div");
      modalRoot.appendChild(modalRootRef.current);
      forceUpdate();

      return () => {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        modalRoot.removeChild(modalRootRef.current!);
        modalRootRef.current = undefined;
      };
    }
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modalRootId, Boolean(modalRoot)]);

  return modalRootRef;
};
