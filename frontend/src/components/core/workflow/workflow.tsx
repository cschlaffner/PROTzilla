import { useNotification } from "@protzilla/app";
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
import { callApiWithParameters } from "@protzilla/utils";
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

export const Workflow: React.FC<WorkflowProps> = ({
  workflow,
  onPress,
  icon,
  refreshWorkflowList,
}) => {
  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true);

  const notify = useNotification();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const handleDeleteWorkflow = async (workflow: string) => {
    const response = await callApiWithParameters("delete_workflow/", { workflow_name: workflow });
    if (response.success) {
      notify({
        title: "Delete Workflow",
        message: `Workflow "${workflow}" deleted successfully.`,
        type: "info",
      });
      await refreshWorkflowList();
    } else {
      notify({
        title: "Delete Workflow Failed",
        message: `Failed to delete workflow "${workflow}": ${String(response.message)}`,
        type: "error",
      });
    }
    setIsDeleteModalOpen(false);
  };

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
        <Icon icon={"trash"} style={{ height: "15px" }} />
      </StyledCircularButton>
      <DeleteModal
        title={`Delete workflow "${workflow ?? ""}"?`}
        isOpen={isDeleteModalOpen}
        onConfirm={() => {
          if (workflow) {
            void handleDeleteWorkflow(workflow);
          }
        }}
        onClose={() => {
          setIsDeleteModalOpen(false);
        }}
      />
    </StyledContainer>
  );
};
