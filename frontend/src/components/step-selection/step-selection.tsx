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
  isOpen,
  onClose,

  ...rest
}) => {
  // - - - step lists and sorting - - -

  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);

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

  function showSelectedListByListMode(listMode: string) {
    setListMode(listMode);
    if (listMode === "all") {
      setActiveStepList(
        importingStepList.concat(
          dataPreprocessingStepList,
          dataAnalysisStepList,
          dataIntegrationStepList,
        ),
      );
    } else if (listMode === "importing") {
      setActiveStepList(importingStepList);
    } else if (listMode === "data_preprocessing") {
      setActiveStepList(dataPreprocessingStepList);
    } else if (listMode === "data_analysis") {
      setActiveStepList(dataAnalysisStepList);
    } else if (listMode === "data_integration") {
      setActiveStepList(dataIntegrationStepList);
    }
  }

  const stepsGroupedByOperation = activeStepList.reduce(
    (acc, step) => {
      if (!acc[step.operation]) {
        acc[step.operation] = [];
      }
      acc[step.operation].push(step);
      return acc;
    },
    {} as Record<string, StepItem[]>,
  );

  // - - - API calls - - -

  useEffect(() => {
    const fetchList = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/step_list/");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data: StepItem[] = await response.json();
        sortStepsToLists(data);
        setActiveStepList(data);
      } catch (error) {
        console.error("Error fetching the list", error);
      }
    };

    fetchList();
  }, []);

  function getCookie(tokenName: string) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, tokenName.length + 1) === tokenName + "=") {
          cookieValue = decodeURIComponent(
            cookie.substring(tokenName.length + 1),
          );
          break;
        }
      }
    }
    return cookieValue as string;
  }

  const addStepToWorkflow = async (run_name: string, new_step: string) => {
    const csrftoken = getCookie("csrftoken");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/add_step/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
          run_name: run_name,
          method: new_step,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log("Step added to workflow:", data);
    } catch (error) {
      console.error("Error adding step to workflow:", error);
    }
  };

  // DEBUG - should be deleted before merge
  const continueRunForDebugging = async (run_name: string) => {
    const csrftoken = getCookie("csrftoken");

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
  continueRunForDebugging("runrun");

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
                onPress={() => showSelectedListByListMode(mode)}
              >
                {section_modes[mode]}
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
                        addStepToWorkflow("runrun", item.method_name)
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
  );
};
