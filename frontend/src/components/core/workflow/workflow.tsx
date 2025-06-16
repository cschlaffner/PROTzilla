import {
  BigButton,
  CircularButton,
  DeleteModal,
  H5,
  Icon,
  Tooltip,
  useTooltipScheduling,
} from "@protzilla/core";
import { color, size, spacing } from "@protzilla/theme";
import { useState } from "react";
import { Container } from "react-grid-system";
import { styled } from "styled-components";

import { WorkflowProps } from "./workflow.props";

const StyledContainer = styled(Container)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
  align-items: center;
  width: ${size("bigButtonContainerDimension")};
  position: relative;
`;

const NameText = styled(H5)`
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
`;

const StyledCircularButton = styled(CircularButton)`
  position: absolute;
  top: 0;
  right: 0;
  width: ${size("smallButtonHeight")};
  background: ${color("secondary")};
  z-index: 1;
`;

const SytledIcon = styled(Icon)`
  height: calc(${size("smallButtonHeight")} - ${spacing("small")});
`;

export const Workflow: React.FC<WorkflowProps> = ({
  workflow,
  onPress,
  icon,
  handleDeleteWorkflow,
}) => {
  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <StyledContainer
      onMouseEnter={() => {
        setIsHovered(true);
      }}
      onMouseLeave={() => {
        setIsHovered(false);
      }}
    >
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
      {isHovered && (
        <StyledCircularButton
          isSmall
          isCautious
          isShy
          onClick={(e) => {
            if (workflow) {
              setIsDeleteModalOpen(true);
            }
            e.stopPropagation();
          }}
        >
          <SytledIcon icon={"trash"} />
        </StyledCircularButton>
      )}
      <DeleteModal
        title={`Delete workflow "${workflow ?? ""}"?`}
        isOpen={isDeleteModalOpen}
        onConfirm={() => {
          if (workflow) {
            handleDeleteWorkflow(workflow);
            setIsDeleteModalOpen(false);
          }
        }}
        onClose={() => {
          setIsDeleteModalOpen(false);
        }}
      />
    </StyledContainer>
  );
};
