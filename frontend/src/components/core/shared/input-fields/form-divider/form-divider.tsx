import { styled } from "styled-components";

import { FormDividerProps } from "./form-divider.props";
import { color, size, spacing } from "../../../../../theme";
import { H4 } from "../../text";

const DividerContainer = styled.div`
  padding-top: ${spacing("medium")};
  width: 100%;
  display: flex;
  align-items: center;
`;

const Line = styled.hr`
  flex-grow: 1;
  margin: 0px ${spacing("small")};
  min-width: ${size("lineMinLength")};
  height: ${size("lineThickness")};
  background-color: ${color("primary")};
  border-width: 0;
`;

export const FormDivider: React.FC<FormDividerProps> = ({ label = "" }) => {
  return (
    <DividerContainer>
      <Line />
      {label && <H4>{label}</H4>}
      {label && <Line />}
    </DividerContainer>
  );
};
