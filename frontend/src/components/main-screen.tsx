import { Outlet } from "react-router-dom";
import { styled } from "styled-components";

import { Screen, ScreenProps, SubScreen } from "./screen";
import { color, spacing } from "../theme";

const StyledScreen = styled(Screen)`
  background: ${color("backgroundOffset")};
  flex-direction: row;
`;

const MainContent = styled(SubScreen)`
  flex: 1;
  gap: ${spacing("large")};
  min-width: 0;
  overflow-y: auto;
  overflow-x: auto;
  width: 100%;
`;

export const MainScreen: React.FC<ScreenProps> = ({ children, ...rest }) => (
  <StyledScreen {...rest}>
    <MainContent>{children ?? <Outlet />}</MainContent>
  </StyledScreen>
);
