import { styled } from "styled-components";

import { InfoFieldProps } from "./info-field.props.ts";
import { InfoText } from "../../text";

const DividerContainer = styled.div`
  display: inline-block;
  position: relative;
  width: 100%;
`;

export const InfoField: React.FC<InfoFieldProps> = ({ label = "" }) => {
  return <DividerContainer>{label && <InfoText>{label}</InfoText>}</DividerContainer>;
};
