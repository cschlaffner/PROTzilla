import { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import {
  Button,
  CircularButton,
  InvisibleButton,
  ToggleableButton,
} from "../button";
import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { useOutsidePress, useToggleableState } from "../../hooks";
import { callApi, callApiWithParameters } from "../../utils";
import { shadow } from "../../theme";
import { iconColor } from "../icon";

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

export interface StepItem {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  input_keys: string[];
  output_keys: string[];
}

const fetchStepList = async (): Promise<StepItem[]> => {
  return callApi("step_list/");
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

const HelpButton = styled(Button)`
  background: none;
  width: fit-content;
  &:hover {
    background-color: transparent;
  }

  .icon {
    width: 12px;
    height: 12px;
    ${iconColor("protzillaGray")}
  }
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
  // - - - Step list handling - - -
  const [allStepsList, setAllStepsList] = useState<StepItem[]>([]);
  useEffect(() => {
    const fetchSteps = async () => {
      const data = await fetchStepList();
      const list = data.filter((step) => step.section === section);
      setAllStepsList(list);
    };

    fetchSteps().then();
  }, []);

  const [listMode, setListMode] = useState<string>(); // now for operations
  useEffect(() => {
    setListMode(all_steps);
  }, [allStepsList]);
  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);
  useEffect(() => {
    setActiveStepList(allStepsList);
  }, [allStepsList]);

  const selectList = (mode: string) => {
    setListMode(mode);
    setActiveStepList(stepsGroupedByOperation[mode] || []);
  };

  // - - - Step grouping - - -
  const stepsGroupedByOperation = useMemo(() => {
    return allStepsList.reduce<Record<string, StepItem[]>>((acc, step) => {
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
  }, [allStepsList]);

  const operationModes: string[] = useMemo(
    () => Object.keys(stepsGroupedByOperation),
    [stepsGroupedByOperation],
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

  // - - - Modal handling - - -
  const [isModalOpen, openModal, closeModal] = useToggleableState(false);
  const refModal = useRef<HTMLDivElement>(null);
  useOutsidePress(refModal, closeModal, isModalOpen, false);

  // - - - Step description dropdown - - -
  const [visibleDescription, setVisibleDescription] = useState<string | null>(
    null,
  );

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
            selectList(all_steps);
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
                      selectList(mode);
                    }}
                  >
                    {mode}
                  </SectionButton>
                ))}
              </SectionSelection>
              <StepList>
                <h2>{sectionModes[section]}</h2>
                {listMode === all_steps ? (
                  Object.keys(stepsGroupedByOperation)
                    .filter((op) => op !== all_steps)
                    .map((operation) => (
                      <div key={operation}>
                        <h3>{operation}</h3>
                        <div>
                          {stepsGroupedByOperation[operation].map(
                            (item, index) => (
                              <div>
                                <InvisibleButton
                                  style={{
                                    textAlign: "left",
                                    justifyContent: "left",
                                  }}
                                  onPress={() =>
                                    handleAddStep(runName, item.method_name)
                                  }
                                  key={index}
                                >
                                  {item.display_name}
                                </InvisibleButton>
                                <HelpButton
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
                        </div>
                      </div>
                    ))
                ) : (
                  <div>
                    {activeStepList.map((item, index) => (
                      <div>
                        <InvisibleButton
                          style={{ textAlign: "left", justifyContent: "left" }}
                          onPress={() =>
                            handleAddStep(runName, item.method_name)
                          }
                          key={index}
                          tooltip={item.method_description}
                        >
                          {item.display_name}
                        </InvisibleButton>
                        <HelpButton
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
                    ))}
                  </div>
                )}
              </StepList>
            </MakeRowDiv>
          </BorderDiv>
        </WideModal>
      </div>
    </div>
  );
};
