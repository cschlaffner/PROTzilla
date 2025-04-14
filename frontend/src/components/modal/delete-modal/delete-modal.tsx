import { RedButton, SecondaryButton } from "../../button";
import { Modal } from "../modal";
import { DeleteModalProps } from "./delete-modal.props";



export const DeleteModal: React.FC<DeleteModalProps> = ({
  title,
  isOpen,
  onClose,
  onConfirm,
  className
}) => { 
    return(
        <Modal title={title} isOpen={isOpen} onClose={onClose} className={className}>
            <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
            <RedButton onClick={onConfirm}>
                Delete
            </RedButton>
        </Modal>
    )
}