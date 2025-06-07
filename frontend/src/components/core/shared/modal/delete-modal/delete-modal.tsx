import { styled } from "styled-components";

import { Modal } from "../";
import { DeleteModalProps } from "./delete-modal.props";
import { Button, SecondaryButton } from "../../button";
import { Text } from "../../text";
import { spacing, fontSize} from "theme/utils";

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${spacing("buttonGap")};
  padding-top: ${spacing("small")};;
`;

const StyledText = styled(Text)`
  word-break: break-word;
  white-space: normal;
  font-size: ${fontSize("h6")};
`;

export const DeleteModal: React.FC<DeleteModalProps> = ({
  title,
  isOpen,
  onClose,
  onConfirm,
  className,
}) => {
  return (
    <Modal title={"Confirm deletion"} isOpen={isOpen} onClose={onClose} className={className}>
      {title && <StyledText text={title} />}
      <ButtonContainer>
        <SecondaryButton onClick={onClose} text={"Cancel"} />
        <Button isCautious onClick={onConfirm} text={"Delete"} />
      </ButtonContainer>
    </Modal>
  );
};
