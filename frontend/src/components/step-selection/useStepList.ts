import { useState, useEffect } from "react";
import { fetchStepList } from "./api";

export type StepItem = {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  input_keys: string[];
  output_keys: string[];
};

export const useStepLists = () => {
  const [stepLists, setStepLists] = useState({
    allStepsList: [] as StepItem[],
    importingStepList: [] as StepItem[],
    dataPreprocessingStepList: [] as StepItem[],
    dataAnalysisStepList: [] as StepItem[],
    dataIntegrationStepList: [] as StepItem[],
  });

  useEffect(() => {
    const fetchList = async () => {
      try {
        const data = await fetchStepList();
        const importingStepList = data.filter(
          (step) => step.section === "importing",
        );
        const dataPreprocessingStepList = data.filter(
          (step) => step.section === "data_preprocessing",
        );
        const dataAnalysisStepList = data.filter(
          (step) => step.section === "data_analysis",
        );
        const dataIntegrationStepList = data.filter(
          (step) => step.section === "data_integration",
        );

        setStepLists({
          allStepsList: data,
          importingStepList,
          dataPreprocessingStepList,
          dataAnalysisStepList,
          dataIntegrationStepList,
        });
      } catch (error) {
        console.error("Error fetching the list", error);
      }
    };

    fetchList();
  }, []);

  return stepLists;
};
