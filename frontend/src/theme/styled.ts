import styledComponents from 'styled-components';

const isValidHtmlProp = (prop: string) => 
    prop in document.createElement("div"); 

//importing styled from here instead from "styled-components" directly makes sure only properties which React recognizes on a DOM Element are passed down


export const styled = new Proxy(styledComponents, {
  get(target, prop) {
    return (...args: any[]) =>
      (target as any)[prop].withConfig({
        shouldForwardProp: (prop:any) => isValidHtmlProp(prop),
      })(...args);
  },
}) as typeof styledComponents;