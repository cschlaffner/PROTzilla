import { styled } from "styled-components";

import { DeleteModalProps } from "./delete-modal.props";
import { Modal } from "../";
import { RedButton, SecondaryButton } from "../../button";

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
