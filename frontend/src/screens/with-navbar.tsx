import { observer } from "mobx-react-lite";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { Navbar } from "../components/navbar/navbar.tsx";
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

export const WithNavbar = observer(() => {
  const navigate = useNavigate();

  return (
    <div>
      <Navbar
        onNavigateHome={() => {
          void navigate("/");
        }}
        isDetailsPage={true}
        title={"my_runnnnnnn"}
      />
      <FlexColumn>Put PROTzilla content here</FlexColumn>
    </div>
  );
});
