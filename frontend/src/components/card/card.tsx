import React from "react";
import styled from "styled-components";
import { CardProps } from "./card.props";

const StyledCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px;
`;

const CardBody = styled.div`
  padding: 8px 0;
`;

const CardTitle = styled.h5`
  font-size: 1.25rem;
  margin-bottom: 12px;
`;

export const Card: React.FC<CardProps> = ({ title, children, className }) => {
  return (
    <StyledCard className={className}>
      {title && <CardTitle>{title}</CardTitle>}
      <CardBody>{children}</CardBody>
    </StyledCard>
  );
};
