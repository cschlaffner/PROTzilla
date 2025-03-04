import { Modal } from "../modal";
import { styled } from "styled-components";
import { useEffect, useState } from "react";
import { InvisibleButton, ToggleableButton } from "../button";
import { StepSelectionProps } from "./step-selection.props.ts";

type StepItem = {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  input_keys: string[];
  output_keys: string[];
};

type StringStringRecord = Record<string, string>;

const section_modes: StringStringRecord = {
  all: "All available steps",
  importing: "Importing",
  data_preprocessing: "Data Preprocessing",
  data_analysis: "Data Analysis",
  data_integration: "Data Integration",
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

const TestDiv = styled.div`
  height: 80vh;
  width: 60vh;
  overflow: hidden;
  overflow-y: auto;
  gap: 50px;
`;

const StepList = styled.dl`
  display: flex;
  flex-direction: column;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  isOpen,
  onClose,
  addStepToWorkflow,

  ...rest
}) => {
  const [stepList, setStepList] = useState<StepItem[]>([]);

  const [importingStepList, setImportingStepList] = useState<StepItem[]>([]);
  const [dataPreprocessingStepList, setDataPreprocessingStepList] = useState<
    StepItem[]
  >([]);
  const [dataAnalysisStepList, setDataAnalysisStepList] = useState<StepItem[]>(
    [],
  );
  const [dataIntegrationStepList, setDataIntegrationStepList] = useState<
    StepItem[]
  >([]);

  const [listMode, setListMode] = useState<keyof typeof section_modes>("all");

  function sortStepsToLists(step_list: StepItem[]) {
    let importingStepList: StepItem[] = [];
    let dataPreprocessingStepList: StepItem[] = [];
    let dataAnalysisStepList: StepItem[] = [];
    let dataIntegrationStepList: StepItem[] = [];

    for (let i = 0; i < step_list.length; i++) {
      if (step_list[i].section === "importing") {
        importingStepList.push(step_list[i]);
      } else if (step_list[i].section === "data_preprocessing") {
        dataPreprocessingStepList.push(step_list[i]);
      } else if (step_list[i].section === "data_analysis") {
        dataAnalysisStepList.push(step_list[i]);
      } else if (step_list[i].section === "data_integration") {
        dataIntegrationStepList.push(step_list[i]);
      }
    }

    setImportingStepList(importingStepList);
    setDataPreprocessingStepList(dataPreprocessingStepList);
    setDataAnalysisStepList(dataAnalysisStepList);
    setDataIntegrationStepList(dataIntegrationStepList);
  }

  function setCurrentListToDisplay(listMode: string) {
    setListMode(listMode);
    if (listMode === "all") {
      setStepList(
        importingStepList.concat(
          dataPreprocessingStepList,
          dataAnalysisStepList,
          dataIntegrationStepList,
        ),
      );
    } else if (listMode === "importing") {
      setStepList(importingStepList);
    } else if (listMode === "data_preprocessing") {
      setStepList(dataPreprocessingStepList);
    } else if (listMode === "data_analysis") {
      setStepList(dataAnalysisStepList);
    } else if (listMode === "data_integration") {
      setStepList(dataIntegrationStepList);
    }
  }

  useEffect(() => {
    const fetchList = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/step_list/");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data: StepItem[] = await response.json();
        sortStepsToLists(data);
        setStepList(data);
      } catch (error) {
        console.error("Error fetching the list", error);
      }
    };

    fetchList();
  }, []);

  const groupedSteps = stepList.reduce(
    (acc, step) => {
      if (!acc[step.operation]) {
        acc[step.operation] = [];
      }
      acc[step.operation].push(step);
      return acc;
    },
    {} as Record<string, StepItem[]>,
  );

  const handleAddStep = (step: string) => {
    addStepToWorkflow(step);
  };

  return (
    <WideModal
      isOpen={isOpen}
      onClose={onClose}
      className={""}
      title={"Step Selection"}
      {...rest}
    >
      <BorderDiv>
        <MakeRowDiv>
          <SectionSelection>
            {Object.keys(section_modes).map((mode) => (
              <SectionButton
                key={mode}
                isActive={listMode === mode}
                onPress={() => setCurrentListToDisplay(mode)}
              >
                {section_modes[mode]}
              </SectionButton>
            ))}
          </SectionSelection>
          <TestDiv>
            {Object.keys(groupedSteps).map((operation) => (
              <div key={operation}>
                <h2>{operation}</h2>
                <StepList>
                  {groupedSteps[operation].map((item, index) => (
                    <InvisibleButton
                      style={{ justifyContent: "left" }}
                      onPress={() => handleAddStep(item.method_name)}
                      key={index}
                    >
                      {item.display_name}
                    </InvisibleButton>
                  ))}
                </StepList>
              </div>
            ))}
          </TestDiv>
        </MakeRowDiv>
      </BorderDiv>
    </WideModal>
  );
};
