import { styled } from "styled-components";

import { baseComponents } from "./base-components";
import { color } from "../../theme";
import { FlexColumn } from "../box";
import { H1 } from "../text";
import { SectionTitleProps } from "./section-title.props";

const Description = styled(H1)`
  color: ${color("gray50")};
`;

export const SectionTitle: React.FC<SectionTitleProps> = ({
  baseComponent = "h1",
  title,
  titleTx,
  titleData,
  titleComponents,
  description,
  descriptionTx,
  descriptionData,
  descriptionComponents,
  ...rest
}) => (
  <FlexColumn {...rest}>
    {(title ?? titleTx) && (
      <H1
        as={baseComponents[baseComponent]}
        text={title}
        tx={titleTx}
        txData={titleData}
        txComponents={titleComponents}
      />
    )}
    {(description ?? descriptionTx) && (
      <Description
        as={baseComponents[baseComponent]}
        text={description}
        tx={descriptionTx}
        txData={descriptionData}
        txComponents={descriptionComponents}
      />
    )}
  </FlexColumn>
);
