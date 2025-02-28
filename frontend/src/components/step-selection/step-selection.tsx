import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { styled } from "styled-components";

const WideModal = styled(Modal)`
  width: 100%;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  isOpen,
  onClose,
}) => {
    all_steps =
  return (
    <WideModal
      isOpen={isOpen}
      onClose={onClose}
      className={""}
      title={"Step Selection"}
    >
      <div>
        <p>
          Step 1: Select your favorite run Select your favorite runSelect your
          favorite runSelect your favorite runSelect your favorite runrite run
          Srite run Srite run Srite run Srite run Srite run Srite run Srite run
          Srite run S
        </p>
        <p>Step 2: Select your favorite shoes</p>
        <p>Step 3: Select your favorite time</p>
      </div>
    </WideModal>
  );
};
