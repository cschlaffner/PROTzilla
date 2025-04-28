import { styled } from "styled-components";

const isValidHtmlProp = (prop: string) => {
  return prop in document.createElement("div");
};

//This component is to ensure only properties which React recognizes on a DOM Element are passed down to divs.
//We need this so we dont get a warning and dont need to specify a Config everytime we use a styled div

export const styledDiv = new Proxy(styled, {
  get(target, component) {
    return (...args: unknown[]) =>
      (target as any)[component].withConfig({
        shouldForwardProp: (prop: string) => isValidHtmlProp(prop),
      })(...args);
  },
});
