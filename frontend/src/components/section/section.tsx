import { styled } from "styled-components";

import { SectionProps } from "./section.props";
import { spacing } from "../../theme";
import { SectionTitle } from "../section-title";

const SectionContainer = styled.section`
  align-items: flex-start;
  align-self: stretch;
  display: flex;
  flex-direction: column;
  gap: ${spacing("medium")};
`;

export const Section: React.FC<SectionProps> = ({
  title,
  titleTx,
  titleData,
  titleComponents,
  description,
  descriptionTx,
  descriptionData,
  descriptionComponents,
  children,
  ...rest
}) => (
  <SectionContainer {...rest}>
    {(title ?? titleTx ?? description ?? descriptionTx) && (
      <SectionTitle
        baseComponent="h3"
        title={title}
        titleTx={titleTx}
        titleData={titleData}
        titleComponents={titleComponents}
        description={description}
        descriptionTx={descriptionTx}
        descriptionData={descriptionData}
        descriptionComponents={descriptionComponents}
      />
    )}
    {children}
  </SectionContainer>
);

export const DenseSection = styled(Section)`
  gap: ${spacing("small")};
`;
