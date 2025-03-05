import { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { CircularButton, InvisibleButton, ToggleableButton } from "../button";
import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { StepItem, useStepLists } from "./useStepList.ts";
import { useOutsidePress, useToggleableState } from "../../hooks";
import { callApiWithParameters } from "../../utils";
import { getCookie } from "../../utils/get-cookie.ts";

enum SectionModes {
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

export const StepSelection: React.FC<StepSelectionProps> = ({
  runName,

  ...rest
}) => {
  // - - - step lists and sorting - - -
  const {
    allStepsList,
    importingStepList,
    dataPreprocessingStepList,
    dataAnalysisStepList,
    dataIntegrationStepList,
  } = useStepLists();

  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);
  useEffect(() => {
    setActiveStepList(allStepsList);
  }, [allStepsList]);

  const [listMode, setListMode] = useState<SectionModes>(SectionModes.All);

  const stepsGroupedByOperation = useMemo(() => {
    return activeStepList.reduce<Record<string, StepItem[]>>(
      (acc, step) => {
        if (!acc[step.operation]) {
          acc[step.operation] = [];
        }
        acc[step.operation].push(step);
        return acc;
      },
      {},
    );
  }, [activeStepList]);

  const showSelectedListByListMode = (mode: SectionModes) => {
    setListMode(mode);
    if (mode === SectionModes.All) {
      setActiveStepList(allStepsList);
    } else if (mode === SectionModes.Importing) {
      setActiveStepList(importingStepList);
    } else if (mode === SectionModes.DataPreprocessing) {
      setActiveStepList(dataPreprocessingStepList);
    } else if (mode === SectionModes.DataAnalysis) {
      setActiveStepList(dataAnalysisStepList);
    } else if (mode === SectionModes.DataIntegration) {
      setActiveStepList(dataIntegrationStepList);
    }
  };

  // - - - API calls - - -
  //const addStepToWorkflow = useAddStepToWorkflow();
  const handleAddStep = async (run_name: string, method_name: string) => {
    callApiWithParameters("add_step/", {
      run_name: run_name,
      method: method_name,
    });
  };

  // DEBUG - should be deleted before merge
  const continueRunForDebugging = async (run_name: string) => {
    const csrftoken = getCookie("csrftoken")!;

    try {
      const response = await fetch("http://127.0.0.1:8000/api/continue_run/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
          run_name: run_name,
        }),
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
    } catch (error) {
      console.error("Error adding step to workflow:", error);
    }
  };

  // DEBUG - should be deleted before merge
  continueRunForDebugging(runName);

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
        }}
      />
      <div ref={refModal}>
        <WideModal
          isOpen={isModalOpen}
          onClose={closeModal}
          className={""}
          title={"Step Selection"}
          {...rest}
        >
          <BorderDiv>
            <MakeRowDiv>
              <SectionSelection>
                {Object.keys(sectionModes).map((mode) => (
                  <SectionButton
                    key={mode}
                    isActive={listMode === mode}
                    onPress={() =>
                      { showSelectedListByListMode(mode as SectionModes); }
                    }
                  >
                    {sectionModes[mode as SectionModes]}
                  </SectionButton>
                ))}
              </SectionSelection>
              <StepList>
                {Object.keys(stepsGroupedByOperation).map((operation) => (
                  <div key={operation}>
                    <h2>{operation}</h2>
                    <OperationStepList>
                      {stepsGroupedByOperation[operation].map((item, index) => (
                        <StepButton
                          onPress={() =>
                            handleAddStep(runName, item.method_name)
                          }
                          key={index}
                        >
                          {item.display_name}
                        </StepButton>
                      ))}
                    </OperationStepList>
                  </div>
                ))}
              </StepList>
            </MakeRowDiv>
          </BorderDiv>
        </WideModal>
      </div>
    </div>
  );
};
