import { Container } from "react-grid-system";
import { styled } from "styled-components";

import { WorkflowProps } from "./workflow.props";
import { spacing } from "../../theme";
import { BigButton } from "../button";
import { H5 } from "../text";
import { Tooltip, useTooltipScheduling } from "../tooltip";

const StyledContainer = styled(Container)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
`;

const CutoffText = styled(H5)`
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
`;

export const Workflow: React.FC<WorkflowProps> = ({
  workflow,
  onPress,
  icon,
}) => {
  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true)
  return (
    <StyledContainer>
        <BigButton
            icon={icon}
            isBig={true}
            onPress={onPress}
            />
        <CutoffText
            text={workflow}
            onPointerEnter={handlePointerEnter}
            onPointerLeave={handlePointerLeave}
        >
          <Tooltip
            text={workflow}
            isShown={showTooltip}
            anchor={mouseAnchor}
            position="bottomRight"
            distance={13}
          />
        </CutoffText>
    </StyledContainer>
  );
};