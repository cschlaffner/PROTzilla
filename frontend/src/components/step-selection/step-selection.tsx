import { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { CircularButton, InvisibleButton, ToggleableButton } from "../button";
import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { StepItem, useStepLists } from "./useStepList.ts";
import { useOutsidePress, useToggleableState } from "../../hooks";
import { callApiWithParameters } from "../../utils";
import { shadow } from "../../theme";

export const enum SectionModes {
  All = "all",
  Importing = "importing",
  DataPreprocessing = "data_preprocessing",
  DataAnalysis = "data_analysis",
  DataIntegration = "data_integration",
}

const sectionModes = {
  [SectionModes.All]: "All available steps",
  [SectionModes.Importing]: "Importing",
  [SectionModes.DataPreprocessing]: "Data Preprocessing",
  [SectionModes.DataAnalysis]: "Data Analysis",
  [SectionModes.DataIntegration]: "Data Integration",
};

const all_steps = "All steps";

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
  padding: 5px;
  gap: 15px;
`;

const SectionSelection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 3px;
`;

const SectionButton = styled(ToggleableButton)`
  color: ${(props) => (props.isActive ? "white" : "black")};
  justify-content: left;
`;

const StepList = styled.div`
  height: 80vh;
  width: 60vh;
  overflow: hidden;
  overflow-y: auto;
  gap: 50px;
`;

const OperationStepList = styled.dl`
  display: flex;
  flex-direction: column;
`;

const StepButton = styled(InvisibleButton)`
  justify-content: left;
  text-align: left;
`;

const StepDescriptionDropdown = styled.div`
  box-shadow: ${shadow("tooltip")};
  padding: 10px;
  max-width: 95%;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  runName,
  section,

  ...rest
}) => {
  // - - - step lists and sorting - - -
  const {
    allStepsList, //TODO maybe remove
    importingStepList,
    dataPreprocessingStepList,
    dataAnalysisStepList,
    dataIntegrationStepList,
  } = useStepLists();

  // step list only to distingusih between sections
  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);
  useEffect(() => {
    if (section === SectionModes.All) {
      // todo maybe dont allow all here?
      setActiveStepList(allStepsList);
    } else if (section === SectionModes.Importing) {
      setActiveStepList(importingStepList);
    } else if (section === SectionModes.DataPreprocessing) {
      setActiveStepList(dataPreprocessingStepList);
    } else if (section === SectionModes.DataAnalysis) {
      setActiveStepList(dataAnalysisStepList);
    } else if (section === SectionModes.DataIntegration) {
      setActiveStepList(dataIntegrationStepList);
    }
  }, [allStepsList]);

  const [activeOperationStepList, setActiveOperationStepList] = useState<
    StepItem[]
  >([]);
  useEffect(() => {
    setActiveOperationStepList(activeStepList); //visible list set on "all" for the active section list
  }, [activeStepList]);

  const [listMode, setListMode] = useState<string>(); // now for operations
  useEffect(() => {
    setListMode(all_steps);
  }, [activeStepList]);

  const stepsGroupedByOperation = useMemo(() => {
    return activeStepList.reduce<Record<string, StepItem[]>>((acc, step) => {
      if (!acc[all_steps]) {
        acc[all_steps] = [];
      }
      if (!acc[step.operation]) {
        acc[step.operation] = [];
      }
      acc[step.operation].push(step);
      acc[all_steps].push(step);
      return acc;
    }, {});
  }, [activeStepList]);

  const operationModes: string[] = useMemo(
    () => Object.keys(stepsGroupedByOperation),
    [stepsGroupedByOperation],
  );

  //todo
  const showSelectedListByListMode = (mode: string) => {
    setListMode(mode);

    setActiveOperationStepList(stepsGroupedByOperation[mode] || []);
  };

  const [visibleDescription, setVisibleDescription] = useState<string | null>(
    null,
  );

  // - - - API calls - - -
  const handleAddStep = async (run_name: string, method_name: string) => {
    await callApiWithParameters("add_step/", {
      run_name: run_name,
      method: method_name,
    });
  };

  // DEBUG - should be deleted before merge
  const continueRunForDebugging = async (run_name: string) => {
    try {
      await callApiWithParameters("continue_run/", { run_name: run_name });
    } catch (error) {
      console.error("Error adding step to workflow:", error);
    }
  };

  // Modal handling
  const [isModalOpen, openModal, closeModal] = useToggleableState(false);
  const refModal = useRef<HTMLDivElement>(null);
  useOutsidePress(refModal, closeModal, isModalOpen, false);

  return (
    <div>
      <CircularButton
        icon={"add"}
        onPress={() => {
          openModal();
          continueRunForDebugging(runName);
        }}
        tooltip={"meep"}
      />
      <div ref={refModal}>
        <WideModal
          isOpen={isModalOpen}
          onClose={() => {
            closeModal();
            showSelectedListByListMode(all_steps);
          }}
          className={""}
          title={"Step Selection"}
          {...rest}
        >
          <BorderDiv>
            <MakeRowDiv>
              <SectionSelection>
                {operationModes.map((mode: string) => (
                  <SectionButton
                    key={mode}
                    isActive={listMode === mode}
                    onPress={() => {
                      showSelectedListByListMode(mode);
                    }}
                  >
                    {mode}
                  </SectionButton>
                ))}
              </SectionSelection>
              <StepList>
                <h1>{sectionModes[section]}</h1>
                {listMode === all_steps ? (
                  Object.keys(stepsGroupedByOperation)
                    .filter((op) => op !== all_steps)
                    .map((operation) => (
                      <div key={operation}>
                        <h2>{operation}</h2>
                        <OperationStepList>
                          {stepsGroupedByOperation[operation].map(
                            (item, index) => (
                              <div>
                                <StepButton
                                  onPress={() =>
                                    handleAddStep(runName, item.method_name)
                                  }
                                  key={index}
                                  // tooltip={item.method_description}
                                  // tooltipPosition={"top"}
                                >
                                  {item.display_name}
                                </StepButton>
                                <CircularButton
                                  icon={"help"}
                                  onPress={() =>
                                    setVisibleDescription(
                                      visibleDescription === item.method_name
                                        ? null
                                        : item.method_name,
                                    )
                                  }
                                />
                                {visibleDescription === item.method_name && (
                                  <StepDescriptionDropdown>
                                    {item.method_description}
                                  </StepDescriptionDropdown>
                                )}
                              </div>
                            ),
                          )}
                        </OperationStepList>
                      </div>
                    ))
                ) : (
                  <OperationStepList>
                    {activeOperationStepList.map((item, index) => (
                      <StepButton
                        onPress={() => handleAddStep(runName, item.method_name)}
                        key={index}
                        tooltip={item.method_description}
                      >
                        {item.display_name}
                      </StepButton>
                    ))}
                  </OperationStepList>
                )}
              </StepList>
            </MakeRowDiv>
          </BorderDiv>
        </WideModal>
      </div>
    </div>
  );
};
