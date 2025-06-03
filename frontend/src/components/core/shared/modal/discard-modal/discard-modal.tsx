import { styled } from "styled-components";

import { Modal } from "../";
import { DiscardModalProps } from "./discard-modal.props";
import { Button, SecondaryButton } from "../../button";
import { Text } from "../../text";

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
`;

export const DiscardModal: React.FC<DiscardModalProps> = ({ isOpen, onDiscard, onClose }) => {
  return (
    <Modal title={"Unsaved Changes"} isOpen={isOpen} onClose={onClose}>
      <Text
        text={
          "There are changes that haven't been saved yet. Are you sure you want to discard all changes?"
        }
      />
      <ButtonContainer>
        <SecondaryButton onClick={onDiscard} text={"Discard Changes"} />
        <Button onClick={onClose} text={"Back"} />
      </ButtonContainer>
    </Modal>
  );
};
