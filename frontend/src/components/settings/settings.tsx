import { styled } from "styled-components";
import { Modal } from "../modal";
import { spacing } from "../../theme";
import { ToggleableButton } from "../button";
import { SettingsProps } from "./settings.props.ts";
import { useState } from "react";

const WideModal = styled(Modal)`
  width: fit-content;
  max-width: 100%;
  height: fit-content;
  max-height: 100vh;
`;

const BorderDiv = styled.div`
  height: fit-content;
`;

const MakeRowDiv = styled.div`
  width: fit-content;
  display: flex;
  height: 90%;
  max-height: 90vh;
  flex-direction: row;
  padding: ${spacing("medium")};
  gap: ${spacing("medium")};
`;

const SectionSelection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("smallButtonGap")};
`;

const SectionButton = styled(ToggleableButton)`
  color: ${(props) => (props.isActive ? "white" : "black")};
  justify-content: left;
`;

export const Settings: React.FC<SettingsProps> = ({}) => {
  //const [selectedSetting, setSelectedSetting] = useState("General");

  return (
    <WideModal isOpen={true} onClose={() => {}} title="Settings">
      <BorderDiv>
        <MakeRowDiv>
          <SectionSelection>
            <SectionButton isActive={false}>General</SectionButton>
            <SectionButton isActive={false}>Advanced</SectionButton>
          </SectionSelection>
        </MakeRowDiv>
      </BorderDiv>
    </WideModal>
  );
};
