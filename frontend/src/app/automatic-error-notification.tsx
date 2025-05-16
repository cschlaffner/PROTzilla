import { observer } from "mobx-react-lite";
import { useCallback, useEffect, useRef } from "react";

import { useStore } from "../app/store";
import { useNotification } from "@protzilla/app";

export const AutomaticErrorNotification = observer(() => {
  const store = useStore();
  const notify = useNotification();

  const cachedMessage = useRef<string | undefined>(undefined);

  const dismissError = useCallback(() => {
    store.setError();
    cachedMessage.current = undefined;
  }, [store]);

  useEffect(() => {
    const error = store.error;

    const message = typeof error?.description === "string" ? error.description : "";

    if (error && message !== cachedMessage.current) {
      cachedMessage.current = message;

      notify({
        type: "error",
        title: typeof error.title === "string" ? error.title : "Error",
        message: message || "An unknown error has occurred.",
        onClose: dismissError,
      });
    }
  }, [store.error, notify, dismissError]);

  return null;
});
