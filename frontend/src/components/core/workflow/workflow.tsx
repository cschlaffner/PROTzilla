import { BigButton } from "@protzilla/core";
import { H5, Tooltip, useTooltipScheduling } from "@protzilla/core/shared";
import { spacing } from "@protzilla/theme";
import { Container } from "react-grid-system";
import { styled } from "styled-components";

import { WorkflowProps } from "./workflow.props";

const StyledContainer = styled(Container)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
`;

const NameText = styled(H5)`
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
`;

export const Workflow: React.FC<WorkflowProps> = ({ workflow, onPress, icon }) => {
  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true);
  return (
    <StyledContainer>
      <BigButton icon={icon} isBig={true} onPress={onPress} />
      <NameText
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
      </NameText>
    </StyledContainer>
  );
};
