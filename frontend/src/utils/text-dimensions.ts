export const getRenderedTextDimensions = (text: string, style?: Partial<CSSStyleDeclaration>) => {
  const element = document.createElement("span");
  const textNode = document.createTextNode(text);
  element.appendChild(textNode);

  if (style) {
    Object.keys(style).forEach((key) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      element.style[key as any] = style[key as any] as any;
    });
  }

  element.style.position = "absolute";
  element.style.left = "-999px";
  element.style.top = "-999px";
  element.style.visibility = "hidden";

  document.body.appendChild(element);
  const size = {
    height: element.offsetHeight,
    width: element.offsetWidth,
  };
  element.parentNode?.removeChild(element);

  return size;
};
