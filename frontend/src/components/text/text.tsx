import { color, font, fontSize, fontWeight, mediaQuery } from "@protzilla/theme";
import { motion } from "framer-motion";
import { css, styled } from "styled-components";

import { CollapsibleLabelProps, LinkProps, TextProps } from "./text.props";

const StyledSpan = styled.span<Pick<TextProps, "isDisabled">>`
  color: ${(props) => color(props.isDisabled ? "textDisabled" : "text")};
  font-family: ${font("defaultWithFallbacks")};
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("default")};
  white-space: pre-line;
`;

const UnderlinedText = styled.span`
  text-decoration-line: underline;
`;

const ThinText = styled.span`
  font-weight: ${fontWeight("light")};
`;

// eslint-disable-next-line react-refresh/only-export-components
export const defaultTxComponents = {
  b: <b />,
  i: <i />,
  u: <UnderlinedText />,
  thin: <ThinText />,
  p: <p />,
  ul: <ul />,
  ol: <ol />,
  li: <li />,
};

export const Text: React.FC<
  TextProps & { as?: "span" | "a" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6" }
> = ({ children, text, ...rest }) => {
  return (
    <StyledSpan {...rest}>
      {text}
      {children}
    </StyledSpan>
  );
};

export const SmallText = styled(Text)`
  font-size: ${fontSize("small")};
`;

export const ContentText = styled(Text)`
  font-size: ${fontSize("h6")};
`;

export const Link = styled(({ ...rest }: LinkProps) => (
  <Text as="a" target="_blank" rel="noreferrer" {...rest} />
))`
  color: ${(props) => color(props.isDisabled ? "linkDisabled" : "link")};
  cursor: pointer;
  text-decoration: underline;
`;

export const H1 = styled(({ ...rest }: TextProps) => <Text as="h1" {...rest} />)`
  font-size: ${fontSize("h1Mobile")};
  line-height: ${fontSize("h1Mobile")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};

  ${mediaQuery(
    "md-up",
    css`
      font-size: ${fontSize("h1")};
      line-height: ${fontSize("h1")};
    `,
  )}
`;

export const H2 = styled(({ ...rest }: TextProps) => <Text as="h2" {...rest} />)`
  font-size: ${fontSize("h2Mobile")};
  line-height: ${fontSize("h2Mobile")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};

  ${mediaQuery(
    "md-up",
    css`
      font-size: ${fontSize("h2")};
      line-height: ${fontSize("h2")};
    `,
  )}
`;

export const H3 = styled(({ ...rest }: TextProps) => <Text as="h3" {...rest} />)`
  font-size: ${fontSize("h3")};
  line-height: ${fontSize("h3")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const H4 = styled(({ ...rest }: TextProps) => <Text as="h4" {...rest} />)`
  font-size: ${fontSize("h4")};
  line-height: ${fontSize("h4")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const H5 = styled(({ ...rest }: TextProps) => <Text as="h5" {...rest} />)`
  font-size: ${fontSize("h5")};
  line-height: ${fontSize("h5")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const H6 = styled(({ ...rest }: TextProps) => <Text as="h6" {...rest} />)`
  font-size: ${fontSize("h6")};
  line-height: ${fontSize("h6")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const InputLabel = styled(Text)`
  font-size: ${fontSize("h6")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
  margin: 4px 0;
`;

const CollapsibleContainer = styled(motion.div)`
  overflow: hidden;
  white-space: nowrap;
  padding-bottom: 1px;
`;

export const CollapsibleLabel: React.FC<CollapsibleLabelProps> = ({
  width,
  collapsedWidth = 0,
  isCollapsed,
  children,
}: CollapsibleLabelProps) => {
  return (
    <CollapsibleContainer
      initial={{ width: isCollapsed ? collapsedWidth : width }}
      animate={{ width: isCollapsed ? collapsedWidth : width }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      {children}
    </CollapsibleContainer>
  );
};
