import { useCallback, useEffect, useMemo } from "react";

/**
 * Returns a function that, when called, opens a file picker.
 * Once a file is selected, the `callback` will be called with the change
 * event.
 */
export const useFilePicker = (
  callback: (arg: Event) => void,
  accept = "image/png, image/jpeg, application/pdf",
  multiple = true,
): (() => void) => {
  const inputElement: HTMLInputElement = useMemo(
    () => document.createElement("input"),
    [],
  );
  useEffect(() => {
    inputElement.addEventListener("change", callback);
    return () => {
      inputElement.removeEventListener("change", callback);
    };
  }, [callback, inputElement]);

  return useCallback(() => {
    inputElement.value = "";
    inputElement.type = "file";
    inputElement.accept = accept;
    inputElement.multiple = multiple;
    inputElement.dispatchEvent(new MouseEvent("click"));
  }, [accept, inputElement, multiple]);
};
