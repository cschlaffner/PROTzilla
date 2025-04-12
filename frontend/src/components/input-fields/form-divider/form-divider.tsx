import { styled } from "styled-components";

import { FormDividerProps } from "./form-divider.props";
import { spacing } from "../../../theme";

const DividerContainer = styled.div`
  padding-top: ${spacing("medium")};
  width: 100%;
  display: flex;
  align-items: center;
`;

const Line = styled.hr`
  flex-grow: 1;
  border-top: 2px solid black;
  margin: 0px ${spacing("small")};
  min-width: 10px;
`;

const Label = styled.h3``;

export const FormDivider: React.FC<FormDividerProps> = ({ label = "" }) => {
  return (
    <DividerContainer>
      <Line />
      <Label>{label}</Label>
      <Line />
    </DividerContainer>
  );
};
