import { useCallback, useState } from "react";

import { isPromise } from "../utils";

export interface TextFieldPreviewConfig<T = string> {
  /** The persisted value, updated on confirm. */
  value: T;

  /**
   * Any preprocessing that should be applied to the preview and before
   * persisting a new value.
   */
  transformValue?: (value: T, previousValue?: T) => T;

  /** The setter that persists a new value. */
  onChangeValue?: (value: T) => void | Promise<void>;
}

/**
 * Handles the live preview for a stateful text field.
 *
 * @returns A tuple of: `[previewValue, onChangeValue, onConfirm, onCancel]`
 */
export const useTextFieldPreview = <T = string>({
  value,
  transformValue,
  onChangeValue,
}: TextFieldPreviewConfig<T>): [T, (value: T) => void, (value: T) => void, () => void] => {
  const [preview, setPreview] = useState<T>();

  const handleChangeValue = useCallback((newValue: T) => {
    setPreview(newValue);
  }, []);

  const handleConfirmEdit = useCallback(
    (newValue: T) => {
      const result = onChangeValue?.(transformValue ? transformValue(newValue, value) : newValue);
      if (isPromise(result)) {
        result
          .then(() => {
            setPreview(undefined);
          })
          // eslint-disable-next-line @typescript-eslint/no-empty-function
          .catch(() => {});
      } else {
        setPreview(undefined);
      }
    },
    [onChangeValue, transformValue, value],
  );

  const handleCancelEdit = useCallback(() => {
    setPreview(undefined);
  }, []);

  return [
    preview === undefined ? value : transformValue ? transformValue(preview, value) : preview,
    handleChangeValue,
    handleConfirmEdit,
    handleCancelEdit,
  ];
};
