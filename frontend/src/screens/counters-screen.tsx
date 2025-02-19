import { observer } from "mobx-react-lite";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { useStore } from "../app/store";
import { Button, H3, RedButton } from "../components";
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
const FlexRow = styled.div`
  align-items: center;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;
export const CountersScreen = observer(() => {
  const store = useStore();
  const counters = store.client.getController("Counter");

  const navigate = useNavigate();

  return (
    <FlexColumn>
      <FlexRow>
        <H3 text="Counters" />
        <Button text="Add counter" onPress={() => void counters.create({})} />
      </FlexRow>
      {counters.getAll().map((counter) => (
        <Button
          key={counter.id}
          text={String(counter.count)}
          onPress={() => {
            if (counter.count === 10) {
              void counter.delete();
            } else {
              counter.increment();
              void counter.save();
            }
          }}
        />
      ))}
      <RedButton
        text="Go back"
        onPress={() => {
          void navigate("/");
        }}
      />
    </FlexColumn>
  );
});
