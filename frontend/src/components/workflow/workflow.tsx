import styled from "styled-components";
import { WorkflowProps } from "./workflow.props";
import { BigButton } from "../button";
import { Container } from "react-grid-system";
import { spacing } from "../../theme";
import { H4 } from "../text";

const StyledContainer = styled(Container)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
`;

const FadingText = styled(H4)`
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  
  mask-image: linear-gradient(to right, rgba(0, 0, 0, 1) 80%, rgba(0, 0, 0, 0));
  -webkit-mask-image: linear-gradient(to right, rgba(0, 0, 0, 1) 80%, rgba(0, 0, 0, 0));
`;

export const Workflow: React.FC<WorkflowProps> = ({
  workflow,
  onPress,
  icon,
}) => {

  return (
    <StyledContainer>
        <BigButton
            icon={icon}
            isBig={true}
            onPress={onPress}
            />
        <FadingText 
            text={workflow}
        />
    </StyledContainer>
  );
};