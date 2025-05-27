import { H3 } from "../../text";
import { color, fontSize, fontWeight, shadow, spacing, styledDiv } from "@protzilla/theme";
import React from "react";
import { styled } from "styled-components";

import { CardProps } from "./card.props";

const StyledCard = styledDiv.div`
  background: white;
  border-radius: 8px;
  box-shadow: ${shadow("box_shadow")};
  padding: ${spacing("small")};
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const CardBody = styledDiv.div<{ hasTitle: boolean }>`
  padding: ${spacing("small")};
  flex: 1;
  overflow-y: auto;
  
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
`;

const CardTitle = styled(H3)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-size: ${fontSize("h3")};
  line-height: ${fontSize("h3")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  padding: ${spacing("small")};
`;

export const Card: React.FC<CardProps> = ({ title, children, className }) => {
  return (
    <StyledCard className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardBody hasTitle={Boolean(title)}>{children}</CardBody>
    </StyledCard>
  );
};
