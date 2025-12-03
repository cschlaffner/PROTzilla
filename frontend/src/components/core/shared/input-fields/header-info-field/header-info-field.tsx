import { styled } from "styled-components";

import { HeaderInfoFieldProps } from "./header-info-field.props.ts";
import { HeaderInfoText } from "../../text";

const DividerContainer = styled.div`
  position: relative;
  width: 100%;
  margin: 8px 0;
`;

export const HeaderInfoField: React.FC<HeaderInfoFieldProps> = ({ label = "" }) => {
  return <DividerContainer>{label && <HeaderInfoText>{label}</HeaderInfoText>}</DividerContainer>;
};
