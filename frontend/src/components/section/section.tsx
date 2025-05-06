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
  description,
  children,
  ...rest
}) => (
  <SectionContainer {...rest}>
    {(title ?? description) && (
      <SectionTitle
        baseComponent="h3"
        title={title}
        description={description}
      />
    )}
    {children}
  </SectionContainer>
);

export const DenseSection = styled(Section)`
  gap: ${spacing("small")};
`;
