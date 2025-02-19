import React, { useEffect } from "react";
import { styled } from "styled-components";

import { ScreenProps } from "./screen.props";

export const SubScreen = styled.div`
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  height: 100%;
  position: relative;
  width: 100%;
`;

const StyledDiv = styled(SubScreen)`
  max-height: 100%;
  max-width: 100%;
  min-width: 100%;
`;

export const Screen: React.FC<ScreenProps> = ({
  title,
  ...rest
}: ScreenProps) => {
  useEffect(() => {
    if (title) document.title = title;
  }, [title]);

  return <StyledDiv {...rest} />;
};

export default Screen;
