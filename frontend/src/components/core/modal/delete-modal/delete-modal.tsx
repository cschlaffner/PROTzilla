import { styled } from "styled-components";

import { RedButton, SecondaryButton, Modal } from "@protzilla/core";
import { DeleteModalProps } from "./delete-modal.props";

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 8px;
`;

export const DeleteModal: React.FC<DeleteModalProps> = ({
  title,
  isOpen,
  onClose,
  onConfirm,
  className,
}) => {
  return (
    <Modal title={title} isOpen={isOpen} onClose={onClose} className={className}>
      <ButtonContainer>
        <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
        <RedButton onClick={onConfirm}>Delete</RedButton>
      </ButtonContainer>
    </Modal>
  );
};
