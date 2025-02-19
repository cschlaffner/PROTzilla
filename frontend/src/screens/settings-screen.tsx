import { observer } from "mobx-react-lite";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { useStore } from "../app/store";
import { Button, Switch } from "../components";
import { size, spacing } from "../theme";

const FlexColumn = styled.div`
  align-items: stretch;
  align-self: center;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: ${spacing("small")};
  justify-content: center;
  width: ${size("navigationItemWidth")};
`;

export const SettingsScreen = observer(() => {
  const store = useStore();
  const navigate = useNavigate();

  return (
    <FlexColumn>
      <Switch
        options={[
          { value: "de", label: "Deutsch" },
          { value: "en", label: "English" },
        ]}
        value={store.language}
        onChange={(language) => void store.setLanguage(language)}
      />
      <Button tx="open" onPress={() => void navigate("/counters")} />
    </FlexColumn>
  );
});
