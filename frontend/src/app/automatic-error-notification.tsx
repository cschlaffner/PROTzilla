import { observer } from "mobx-react-lite";
import { useRef } from "react";
import { styled } from "styled-components";

import { useStore } from "../app/store";
import { I18nMessage } from "../components";

const Container = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
`;

export const AutomaticErrorNotification = observer(() => {
  const store = useStore();

  const cachedError = useRef<I18nMessage>();
  if (store.error) {
    cachedError.current = store.error;
  }
/*   const dismissError = useCallback(() => {
    store.setError();
  }, [store]); */

  return (
    <Container>
{/*       <ErrorNotification
        isShown={Boolean(store.error)}
        {...(cachedError.current ?? {})}
        onClose={dismissError}
      /> */}
    </Container>
  );
});
