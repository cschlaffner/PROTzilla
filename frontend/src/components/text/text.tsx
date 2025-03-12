import { css, styled } from "styled-components";

import { LinkProps, TextProps } from "./text.props";
import { Trans, useTranslation } from "../../i18n";
import { color, font, fontSize, fontWeight, mediaQuery } from "../../theme";

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
> = ({ children, txData, text, tx, txComponents, ...rest }) => {
  const { t } = useTranslation();

  return (
    <StyledSpan {...rest}>
      {tx ? (
        txComponents ? (
          <Trans i18nKey={tx} components={txComponents} values={txData} />
        ) : (
          t(tx, txData)
        )
      ) : (
        text
      )}
      {children}
    </StyledSpan>
  );
};

export const SmallText = styled(Text)`
  font-size: ${fontSize("small")};
`;

export const ContentText = styled(Text)`
  font-size: ${fontSize("h5")};
`

export const Link = styled(({ ...rest }: LinkProps) => (
  <Text as="a" target="_blank" rel="noreferrer" {...rest} />
))`
  color: ${(props) => color(props.isDisabled ? "linkDisabled" : "link")};
  cursor: pointer;
  text-decoration: underline;
`;

export const H1 = styled(({ ...rest }: TextProps) => (
  <Text as="h1" {...rest} />
))`
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

export const H2 = styled(({ ...rest }: TextProps) => (
  <Text as="h2" {...rest} />
))`
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

export const H3 = styled(({ ...rest }: TextProps) => (
  <Text as="h3" {...rest} />
))`
  font-size: ${fontSize("h3")};
  line-height: ${fontSize("h3")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const H4 = styled(({ ...rest }: TextProps) => (
  <Text as="h4" {...rest} />
))`
  font-size: ${fontSize("h4")};
  line-height: ${fontSize("h4")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const H5 = styled(({ ...rest }: TextProps) => (
  <Text as="h5" {...rest} />
))`
  font-size: ${fontSize("h5")};
  line-height: ${fontSize("h5")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isDisabled ? "primaryDisabled" : "primary")};
`;

export const H6 = styled(({ ...rest }: TextProps) => (
  <Text as="h6" {...rest} />
))`
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
