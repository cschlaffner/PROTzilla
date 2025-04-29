import { styled } from "styled-components";

import { RedButton, SecondaryButton, Text } from "../../../components";
import { Modal } from "../modal";
import { DiscardModalProps } from "./discard-modal.props";

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 8px;
`;

export const DeleteModal: React.FC<DiscardModalProps> = ({
  isOpen,
  onDiscard,
  onClose,
}) => {
  return (
    <Modal title={"Unsaved Changes"} isOpen={isOpen} onClose={onClose}>
      <Text
        text={
          "There are changes that haven't been saved yet. Are you sure you want to discard all changes?"
        }
      />
      <ButtonContainer>
        <SecondaryButton onClick={onDiscard}>Discard Changes</SecondaryButton>
        <RedButton onClick={onClose}>Back</RedButton>
      </ButtonContainer>
    </Modal>
  );
};
