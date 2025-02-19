import { createGlobalStyle } from "styled-components";

import { color, font, fontSize, fontWeight } from "./utils";

export interface GlobalStylesProps {
  backgroundColor?: string;
  color?: string;
}

export const GlobalStyles = createGlobalStyle`
  html {
    height: 100%;
    margin: 0;
    padding: 0;
  }
  body {
    background-color: ${color("background")};
    color: ${color("text")};
    font-family: ${font("defaultWithFallbacks")};
    font-size: ${fontSize("default")};
    font-weight: ${fontWeight("default")};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    height: 100%;
    margin: 0;
    max-height: 100%;
    overflow: hidden;
    padding: 0;
  }
  main,
  p,
  h1,
  h2,
  h3,
  h4,
  h5,
  h6,
  hr {
    margin: 0;
  }

  b {
    font-weight: ${fontWeight("bold")};
  }

  input {
    border-radius: 0;
  }

  #root {
    height: 100%;
    max-height: 100%;
    overflow: hidden;
  }

  ::-webkit-scrollbar {
    width: 16px;
  }

  ::-webkit-scrollbar-thumb {
    background-color: #B9B9B9;
    border-radius: 16px;
    border: 4px solid rgba(0, 0, 0, 0);
    background-clip: padding-box;

    :hover {
      background-color: #999999;
    }
  }

  ::-webkit-scrollbar-button {
    display:none;
  }

  .gm-style iframe + div { border:none!important; }
`;
