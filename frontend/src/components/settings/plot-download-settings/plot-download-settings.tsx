import { styled } from "styled-components";

import { PlotDownloadSettingsProps } from "./plot-download-settings.props.ts";
import { Modal } from "../../../components";

const StyledModal = styled(Modal)`
  width: fit-content;
  max-width: 100%;
  height: fit-content;
  max-height: 100vh;
`;

export const PlotDownloadSettings: React.FC<PlotDownloadSettingsProps> = ({
  isOpen,
  onClose,
}) => {
  return (
    <StyledModal isOpen={isOpen} onClose={onClose} title="Download Plots">
      <div>Testing</div>
    </StyledModal>
  );
};
