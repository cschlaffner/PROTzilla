import { FlexColumn, H1 } from "@protzilla/core/shared"
import { color } from "@protzilla/theme";
import { styled } from "styled-components";

import { baseComponents } from "./base-components";
import { SectionTitleProps } from "./section-title.props";

const Description = styled(H1)`
  color: ${color("gray50")};
`;

export const SectionTitle: React.FC<SectionTitleProps> = ({
  baseComponent = "h1",
  title,
  description,
  ...rest
}) => (
  <FlexColumn {...rest}>
    {title && <H1 as={baseComponents[baseComponent]} text={title} />}
    {description && <Description as={baseComponents[baseComponent]} text={description} />}
  </FlexColumn>
);
