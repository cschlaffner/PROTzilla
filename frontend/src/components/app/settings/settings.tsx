import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import { useState } from "react";
import { styled } from "styled-components";

import {
  CrosslinkColors,
  CrosslinkDefaultUpload,
  DatabaseSettings,
  GitHub,
  MonomerStructureUpload,
  MultimerStructureUpload,
  PTMVisSettings,
} from "./other-settings/";
import { PlotSettingsModal } from "./plot-settings";
import { SettingsProps } from "./settings.props.ts";
import { DiscardModal, Modal, ToggleableButton } from "../../core/";

const WideModal = styled(Modal)`
  width: fit-content;
  max-width: 100vw;
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
  width: 65vw;
  overflow: hidden;
  overflow-y: auto;
`;

export const Settings: React.FC<SettingsProps> = ({
  isOpen,
  onClose,
  hasChanges,
  setHasChanges,
}) => {
  const [pendingSetting, setPendingSetting] = useState<string | null>(null);
  const [selectedSetting, setSelectedSetting] = useState<string | null>("plot");

  const [isDiscardModalOpen, openDiscardModal, closeDiscardModal] = useToggleableState(false);
  const handleSwitchSection = (section: string) => {
    if (hasChanges) {
      setPendingSetting(section);
      openDiscardModal();
    } else {
      setSelectedSetting(section);
    }
  };
  const handleDiscard = () => {
    closeDiscardModal();
    setSelectedSetting(pendingSetting);
    setPendingSetting(null);
    setHasChanges(false);
  };
  return (
    <WideModal
      isOpen={isOpen}
      onClose={() => {
        onClose(hasChanges);
      }}
      title="Settings"
    >
      <BorderDiv>
        <MakeRowDiv>
          <SectionSelection>
            <SectionButton
              id={"plot"}
              isActive={selectedSetting === "plot"}
              icon={"data_analysis"}
              text={"Plot Export"}
              onPress={() => {
                handleSwitchSection("plot");
              }}
            />
            <SectionButton
              id={"database"}
              isActive={selectedSetting === "database"}
              icon={"database"}
              text={"Database Upload"}
              onPress={() => {
                handleSwitchSection("database");
              }}
            />
            <SectionButton
              id={"ptm-vis"}
              isActive={selectedSetting === "ptm-vis"}
              icon={"barChartSteps"}
              text={"PTM Visualizations"}
              onPress={() => {
                handleSwitchSection("ptm-vis");
              }}
            />
            <SectionButton
              id={"monomer-structure-upload"}
              isActive={selectedSetting === "monomer-structure-upload"}
              icon={"prot_structure"}
              text={"Monomer Structure Upload"}
              onPress={() => {
                handleSwitchSection("monomer-structure-upload");
              }}
            />
            <SectionButton
              id={"multimer-structure-upload"}
              isActive={selectedSetting === "multimer-structure-upload"}
              icon={"prot_structure"}
              text={"Multimer Structure Upload"}
              onPress={() => {
                handleSwitchSection("multimer-structure-upload");
              }}
            />
            <SectionButton
              id={"crosslink-defaults"}
              isActive={selectedSetting === "crosslink-defaults"}
              icon={"handleCrosslinkingIcon"}
              text={"Crosslinks Defaults"}
              onPress={() => {
                handleSwitchSection("crosslink-defaults");
              }}
            />
            <SectionButton
              id={"crosslink-colors"}
              isActive={selectedSetting === "crosslink-colors"}
              icon={"colorBrush"}
              text={"Crosslink Colours"}
              onPress={() => {
                handleSwitchSection("crosslink-colors");
              }}
            />
            <SectionButton
              id={"github"}
              isActive={selectedSetting === "github"}
              text={"About Us"}
              icon={"info"}
              onPress={() => {
                handleSwitchSection("github");
              }}
            />
          </SectionSelection>
          <SpecificSettings>
            {selectedSetting === "plot" && (
              <PlotSettingsModal isOpen={isOpen} onClose={onClose} setHasChanges={setHasChanges} />
            )}
            {selectedSetting === "database" && <DatabaseSettings />}
            {selectedSetting === "ptm-vis" && <PTMVisSettings />}
            {selectedSetting === "monomer-structure-upload" && <MonomerStructureUpload />}
            {selectedSetting === "multimer-structure-upload" && <MultimerStructureUpload />}
            {selectedSetting === "crosslink-defaults" && <CrosslinkDefaultUpload />}
            {selectedSetting === "crosslink-colors" && <CrosslinkColors />}
            {selectedSetting === "github" && <GitHub />}
          </SpecificSettings>
          <DiscardModal
            isOpen={isDiscardModalOpen}
            onDiscard={handleDiscard}
            onClose={closeDiscardModal}
          />
        </MakeRowDiv>
      </BorderDiv>
    </WideModal>
  );
};
