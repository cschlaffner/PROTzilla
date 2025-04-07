import { observer } from "mobx-react-lite";
import { useCallback, useEffect, useRef } from "react";
import { useStore } from "../app/store";
import { useNotification } from "../components";
import { useTranslation } from "react-i18next";

export const AutomaticErrorNotification = observer(() => {
  const store = useStore();
  const notify = useNotification();
  const { t } = useTranslation();

  const cachedKey = useRef<string | undefined>(undefined);

  const dismissError = useCallback(() => {
    store.setError();
    cachedKey.current = undefined;
  }, [store]);

  useEffect(() => {
    const error = store.error;

    const currentKey = error?.descriptionTx ?? String(error?.description ?? "");

    if (error && currentKey !== cachedKey.current) {
      cachedKey.current = currentKey;

      notify({
        type: "error",
        title: error.titleTx
          ? t(error.titleTx, error.titleData)
          : typeof error.title === "string"
            ? error.title
            : t("Fehler"),
        message: error.descriptionTx
          ? t(error.descriptionTx, error.descriptionData)
          : typeof error.description === "string"
            ? error.description
            : t("Ein unbekannter Fehler ist aufgetreten."),
        onClose: dismissError,
      });
    }
  }, [store.error, notify, t, dismissError]);

  return null;
});
