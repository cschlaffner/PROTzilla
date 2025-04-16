import React from "react";
import { styled } from "styled-components";

import { CardProps } from "./card.props";
import { color, fontSize, fontWeight, shadow, spacing } from "../../theme";

const StyledCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: ${shadow("box_shadow")};
  padding: ${spacing("small")};
`; //${border("defaultRadius")}

const CardBody = styled.div`
  padding: ${spacing("small")};
`;

const CardTitle = styled.div`
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
      <CardBody>{children}</CardBody>
    </StyledCard>
  );
};
