import styledComponents from 'styled-components';

// const isValidHtmlProp = (prop: string,component:string|symbol) =>  {
//   console.log(String(component))
//   console.log(document.createElement(String(component)))
//   console.log(prop,prop in document.createElement(String(component)))
//   return (prop in document.createElement(String(component))); 
// }
    

//importing styled from here instead from "styled-components" directly makes sure only properties which React recognizes on a DOM Element are passed down


export const styled = new Proxy(styledComponents, {
  get(target, component) {
    return (...args: any[]) =>
      (target as any)[component].withConfig({
        //shouldForwardProp: (prop:string) => isValidHtmlProp(prop, component),
      })(...args);
  },
}) as typeof styledComponents;