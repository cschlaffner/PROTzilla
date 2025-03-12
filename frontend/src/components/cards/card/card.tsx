import React from "react";
import { styled } from "styled-components";

import { CardProps } from "./card.props";
import { shadow, spacing } from "../../../theme";

const StyledCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: ${shadow("box_shadow")};
  padding: ${spacing("small")};
`;

const CardBody = styled.div<{ hasTitle: boolean }>`
  padding: ${spacing("small")};
  width: auto;
  max-height: ${({ hasTitle }) =>
    hasTitle ? "calc(100vh - 225px)" : "calc(100vh - 178px)"};
  overflow-y: auto;
`;


const CardTitle = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-size: 18px;
  font-weight: bold;
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
