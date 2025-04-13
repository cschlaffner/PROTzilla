import { useState } from "react";
import { styled } from "styled-components";

import { SettingsProps } from "./settings.props.ts";
import { Modal, ToggleableButton } from "../../components";
import { spacing } from "../../theme";
import { DatabaseSettings, GitHub, PlotSettings } from "./specific-settings/";

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
  position: relative;
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

const SpecificSettings = styled.div`
  height: 80vh;
  width: 120vh;
  overflow: hidden;
  overflow-y: auto;
`;

export const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [selectedSetting, setSelectedSetting] = useState("plot");

  return (
    <WideModal isOpen={isOpen} onClose={onClose} title="Settings">
      <BorderDiv>
        <MakeRowDiv>
          <SectionSelection>
            <SectionButton
              id={"plot"}
              isActive={selectedSetting === "plot"}
              icon={"data_analysis"}
              text={"Plot Export"}
              onPress={() => {
                setSelectedSetting("plot");
              }}
            />
            <SectionButton
              id={"database"}
              isActive={selectedSetting === "database"}
              icon={"database"}
              text={"Database Upload"}
              onPress={() => {
                setSelectedSetting("database");
              }}
            />
            <SectionButton
              id={"github"}
              isActive={selectedSetting === "github"}
              text={"About Us"}
              icon={"info"}
              onPress={() => {
                setSelectedSetting("github");
              }}
            />
          </SectionSelection>
          <SpecificSettings>
            {selectedSetting === "plot" && (
              <PlotSettings isOpen={isOpen} onClose={onClose} />
            )}
            {selectedSetting === "database" && <DatabaseSettings />}
            {selectedSetting === "github" && <GitHub />}
          </SpecificSettings>
        </MakeRowDiv>
      </BorderDiv>
    </WideModal>
  );
};
