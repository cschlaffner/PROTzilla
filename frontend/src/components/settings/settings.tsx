import { styled } from "styled-components";
import { Modal } from "../modal";
import { spacing } from "../../theme";
import { ToggleableButton } from "../button";
import { SettingsProps } from "./settings.props.ts";
import { useState } from "react";
import { DatabaseSettings } from "./specific-settings/database-settings/database-settings.tsx";

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

const SpecificSettings = styled.div`
  height: 80vh;
  width: 70vh;
  overflow: hidden;
  overflow-y: auto;
`;

//const settingsSections = ["plot", "database"];

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
              text={"Plot Settings"}
              onPress={() => {
                setSelectedSetting("plot");
              }}
            />
            <SectionButton
              id={"database"}
              isActive={selectedSetting === "database"}
              text={"Database Upload"}
              onPress={() => {
                setSelectedSetting("database");
              }}
            />
            <SectionButton
              id={"github"}
              isActive={selectedSetting === "github"}
              text={"Github"}
              onPress={() => {
                setSelectedSetting("github");
              }}
            />
          </SectionSelection>
          <SpecificSettings>
            {selectedSetting === "plot" && (
              <div>
                <p>Plot settings content goes here.</p>
              </div>
            )}
            {selectedSetting === "database" && <DatabaseSettings />}
            {selectedSetting === "github" && (
              <div>
                <p>Github settings content goes here.</p>
              </div>
            )}
          </SpecificSettings>
        </MakeRowDiv>
      </BorderDiv>
    </WideModal>
  );
};
