import { SectionTitle } from "@protzilla/core";
import { styled } from "styled-components";

export const Container = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
`;

export const CanvasWrapper = styled.div`
  flex: 1;
  position: relative;
  top: 86px;
`;

console.log(SectionTitle);
export const LoadingTitle = styled(SectionTitle)`
  margin: 15px;
`;
