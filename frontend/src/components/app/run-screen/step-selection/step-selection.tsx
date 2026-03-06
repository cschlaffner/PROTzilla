import {
  Button,
  GrayButton,
  IconButton,
  iconColor,
  Modal,
  SectionTitle,
  ToggleableButton,
} from "@protzilla/core";
import { useOutsidePress, useToggleableState } from "@protzilla/hooks";
import { color, shadow, size, spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters, SectionIDs } from "@protzilla/utils";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { StepSelectionProps } from "./step-selection.props.ts";

const sectionModes = {
  [SectionIDs.Importing]: "Importing",
  [SectionIDs.DataPreprocessing]: "Data Preprocessing",
  [SectionIDs.DataAnalysis]: "Data Analysis",
  [SectionIDs.DataIntegration]: "Data Integration",
};

const allSteps = "All steps";

export interface StepItem {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  calculation_status: string;
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

const StepList = styled.div`
  height: 80vh;
  width: 60vh;
  overflow: hidden;
  overflow-y: auto;
`;

const StepWrapper = styled.div`
  padding: ${spacing("listButtonPadding")};
`;

const LightGrayButton = styled(GrayButton)`
  background-color: ${color("backgroundOffset")};
`;

const HelpButton = styled(Button)`
  background: none;
  width: fit-content;
  &:hover {
    background-color: transparent;
    .icon {
      ${iconColor("protzillaDarkBlue")}
    }
  }

  .icon {
    width: ${size("smallIcon")};
    height: ${size("smallIcon")};
    ${iconColor("protzillaGray")}
  }
`;

const StepDescriptionDropdown = styled.div`
  box-shadow: ${shadow("tooltip")};
  margin-top: ${spacing("verySmall")};
  padding: ${spacing("small")};
  background-color: ${color("backgroundOffset")};
  max-width: 95%;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  runName,
  section,
  isSmallButton = false,
  onAddStep,
  handlePosition = { top: 0, left: 0 },
  setShowHandle = () => undefined,
  ModalTrigger,

  ...rest
}) => {
  // - - -
  const [selectedSection, setSelectedSection] = useState<SectionIDs | null>(null);

  // - - - Step list handling - - -
  const [allStepsList, setAllStepsList] = useState<StepItem[]>([]);
  const [listMode, setListMode] = useState<string>(); // now for operations
  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);

  useEffect(() => {
    if (!selectedSection) return;
    const fetchSteps = async () => {
      const data = await fetchStepList();
      const list = data.filter((step) => (step.section as SectionIDs) === section);
      list.sort((a, b) => a.display_name.localeCompare(b.display_name));
      setAllStepsList(list);
    };

    void fetchSteps();
  }, [selectedSection, section]);

  useEffect(() => {
    setActiveStepList(allStepsList);
  }, [allStepsList, section]);

  useEffect(() => {
    setListMode(allSteps);
  }, [allStepsList]);

  const selectList = (mode: string) => {
    setListMode(mode);
    setActiveStepList(stepsGroupedByOperation[mode]);
  };

  // - - - Step grouping - - -
  const stepsGroupedByOperation = useMemo(() => {
    const result: Record<string, StepItem[]> = {
      [allSteps]: [],
    };

    const sortedSteps = allStepsList.sort((a, b) => {
      if (a.operation === b.operation) {
        return a.display_name.localeCompare(b.display_name);
      }
      return a.operation.localeCompare(b.operation);
    });
    for (const step of sortedSteps) {
      if (!Object.prototype.hasOwnProperty.call(result, step.operation)) {
        result[step.operation] = [];
      }
      result[step.operation].push(step);
      result[allSteps].push(step);
    }

    return result;
  }, [allStepsList]);

  const operationModes: string[] = useMemo(
    () => Object.keys(stepsGroupedByOperation).sort(),
    [stepsGroupedByOperation],
  );

  // - - - API calls - - -
  const handleAddStep = async (run_name: string, method_name: string) => {
    await callApiWithParameters("add_step/", {
      run_name: run_name,
      method: method_name,
    }).then(() => {
      onAddStep();
    });
  };

  // - - - Modal handling - - -
  const [isModalOpen, openModal, closeModal] = useToggleableState(false);
  const refModal = useRef<HTMLDivElement>(null);
  useOutsidePress(refModal, closeModal, isModalOpen, false);

  const handleOpenModal = () => {
    openModal();
    setSelectedSection(section);
  };

  // - - - Step description dropdown - - -
  const [visibleDescription, setVisibleDescription] = useState<string | null>(null);

  // - - - Render - - -
  return (
    <div style={{ display: "flex", flexDirection: "column", margin: "0 5px" }}>
      {ModalTrigger ? (
        ModalTrigger(handleOpenModal)
      ) : isSmallButton ? (
        <IconButton
          icon={"add"}
          onPointerDown={isModalOpen ? undefined : handleOpenModal}
          style={{
            position: "absolute",
            left: handlePosition.left,
            top: handlePosition.top,
            transform: "translateX(-50%) translateY(-50%)",
          }}
          onMouseEnter={() => {
            setShowHandle(true);
          }}
        />
      ) : (
        <GrayButton
          color={"protzillaDarkBlue"}
          isShy={true}
          icon={"add"}
          text={"Add steps"}
          onPointerDown={() => {
            openModal();
            handleOpenModal();
          }}
          style={{
            display: "flex",
          }}
        />
      )}
      <div ref={refModal}>
        <WideModal
          isOpen={isModalOpen}
          onClose={() => {
            closeModal();
            selectList(allSteps);
          }}
          className={""}
          title={"Add steps"}
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
                      setVisibleDescription(null);
                    }}
                    text={mode}
                  ></SectionButton>
                ))}
              </SectionSelection>
              <div>
                {allStepsList.length === 0 ? (
                  <SectionTitle baseComponent={"h2"} title={"Loading..."} />
                ) : (
                  <SectionTitle
                    baseComponent={"h2"}
                    title={sectionModes[section]}
                    // style={{ paddingLeft: "100px" }}
                  />
                )}
                <StepList>
                  {listMode === allSteps ? (
                    Object.keys(stepsGroupedByOperation)
                      .filter((op) => op !== allSteps)
                      .map((operation) => (
                        <div key={operation}>
                          <SectionTitle baseComponent={"h3"} description={operation}></SectionTitle>
                          <div style={{ padding: "10px 10px 10px 20px" }}>
                            {stepsGroupedByOperation[operation].map((item, index) => (
                              <StepWrapper key={`step_${String(index)}`}>
                                <LightGrayButton
                                  style={{
                                    textAlign: "left",
                                    justifyContent: "left",
                                  }}
                                  onPress={() => void handleAddStep(runName, item.method_name)}
                                  key={index}
                                  text={item.display_name}
                                />
                                <HelpButton
                                  icon={"help"}
                                  onPress={() => {
                                    setVisibleDescription(
                                      visibleDescription === item.method_name
                                        ? null
                                        : item.method_name,
                                    );
                                  }}
                                />
                                {visibleDescription === item.method_name && (
                                  <StepDescriptionDropdown>
                                    {item.method_description}
                                  </StepDescriptionDropdown>
                                )}
                              </StepWrapper>
                            ))}
                          </div>
                        </div>
                      ))
                  ) : (
                    <div>
                      <SectionTitle baseComponent={"h3"} description={listMode}></SectionTitle>
                      <div style={{ padding: "10px 10px 10px 20px" }}>
                        {activeStepList.map((item, index) => (
                          <StepWrapper key={`step_${String(index)}`}>
                            <LightGrayButton
                              style={{
                                textAlign: "left",
                                justifyContent: "left",
                              }}
                              onPress={() => void handleAddStep(runName, item.method_name)}
                              key={index}
                              text={item.display_name}
                            />
                            <HelpButton
                              icon={"help"}
                              onPress={() => {
                                setVisibleDescription(
                                  visibleDescription === item.method_name ? null : item.method_name,
                                );
                              }}
                            />
                            {visibleDescription === item.method_name && (
                              <StepDescriptionDropdown>
                                {item.method_description}
                              </StepDescriptionDropdown>
                            )}
                          </StepWrapper>
                        ))}
                      </div>
                    </div>
                  )}
                </StepList>
              </div>
            </MakeRowDiv>
          </BorderDiv>
        </WideModal>
      </div>
    </div>
  );
};
