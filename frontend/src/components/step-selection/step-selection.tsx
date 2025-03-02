import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { styled } from "styled-components";
import { useEffect, useState } from "react";
import { GrayButton, InvisibleButton } from "../button";

type StepItem = {
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  input_keys: string[];
  output_keys: string[];
};

const WideModal = styled(Modal)`
  width: fit-content;
  max-width: 100%;
  height: fit-content;
  max-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 10px;
`;

const MakeRowDiv = styled.div`
  width: fit-content;
  display: flex;
  flex-direction: row;
`;

const SectionSelection = styled.div`
  display: flex;
  flex-direction: column;
`;

const SectionButton = styled(GrayButton)``;

const TestDiv = styled.div`
  height: 100%;
  max-height: 80vh;
  overflow: hidden;
  overflow-y: auto;
`;

const StepList = styled.dl`
  display: flex;
  flex-direction: column;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  isOpen,
  onClose,
}) => {
  const [stepList, setStepList] = useState<StepItem[]>([]);

  const [importingStepList, setImportingStepList] = useState<StepItem[]>([]);
  const [dataAnalysisStepList, setDataAnalysisStepList] = useState<StepItem[]>(
    [],
  );
  const [dataIntegrationStepList, setDataIntegrationStepList] = useState<
    StepItem[]
  >([]);
  const [dataPreprocessingStepList, setDataPreprocessingStepList] = useState<
    StepItem[]
  >([]);

  function sortStepsToLists(step_list: StepItem[]) {
    let importingStepList: StepItem[] = [];
    let dataAnalysisStepList: StepItem[] = [];
    let dataIntegrationStepList: StepItem[] = [];
    let dataPreprocessingStepList: StepItem[] = [];

    for (let i = 0; i < step_list.length; i++) {
      if (step_list[i].section === "importing") {
        importingStepList.push(step_list[i]);
      } else if (step_list[i].section === "data_analysis") {
        dataAnalysisStepList.push(step_list[i]);
      } else if (step_list[i].section === "data_integration") {
        dataIntegrationStepList.push(step_list[i]);
      } else if (step_list[i].section === "data_preprocessing") {
        dataPreprocessingStepList.push(step_list[i]);
      }
    }

    setImportingStepList(importingStepList);
    setDataAnalysisStepList(dataAnalysisStepList);
    setDataIntegrationStepList(dataIntegrationStepList);
    setDataPreprocessingStepList(dataPreprocessingStepList);
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

  return (
    <WideModal
      isOpen={isOpen}
      onClose={onClose}
      className={""}
      title={"Step Selection"}
    >
      <MakeRowDiv>
        <SectionSelection>
          <SectionButton>Importing</SectionButton>
          <SectionButton>Data Analysis</SectionButton>
          <SectionButton>Data Integration</SectionButton>
          <SectionButton>Data Preprocessing</SectionButton>
        </SectionSelection>
        <TestDiv>
          {Object.keys(groupedSteps).map((operation) => (
            <div key={operation}>
              <h2>{operation}</h2>
              <StepList>
                {groupedSteps[operation].map((item, index) => (
                  <GrayButton key={index}>{item.display_name}</GrayButton>
                ))}
              </StepList>
            </div>
          ))}
        </TestDiv>
        {/*<TestDiv>*/}
        {/*  <span>Importing</span>*/}
        {/*  <StepList>*/}
        {/*    {importingStepList.map((item, index) => (*/}
        {/*      <>*/}
        {/*        <dt>*/}
        {/*          <GrayButton key={index}>{item.display_name}</GrayButton>*/}
        {/*        </dt>*/}
        {/*        <dd>{item.operation}</dd>*/}
        {/*      </>*/}
        {/*    ))}*/}
        {/*  </StepList>*/}
        {/*  <span>Data Analysis</span>*/}
        {/*  <StepList>*/}
        {/*    {dataAnalysisStepList.map((item, index) => (*/}
        {/*      <InvisibleButton key={index}>{item.display_name}</InvisibleButton>*/}
        {/*    ))}*/}
        {/*  </StepList>*/}
        {/*  <span>Data Integration</span>*/}
        {/*  <StepList>*/}
        {/*    {dataIntegrationStepList.map((item, index) => (*/}
        {/*      <li key={index}>{item.display_name}</li>*/}
        {/*    ))}*/}
        {/*  </StepList>*/}
        {/*  <span>Data Preprocessing</span>*/}
        {/*  <StepList>*/}
        {/*    {dataPreprocessingStepList.map((item, index) => (*/}
        {/*      <li key={index}>{item.display_name}</li>*/}
        {/*    ))}*/}
        {/*  </StepList>*/}
        {/*</TestDiv>*/}
      </MakeRowDiv>
    </WideModal>
  );
};
