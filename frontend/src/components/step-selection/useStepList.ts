import { useEffect, useState } from "react";
import { callApi } from "../../utils";

/**
 * Type definition for a step item.
 * Contains relevant fields of step classes from the backend.
 */
export interface StepItem {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  input_keys: string[];
  output_keys: string[];
}

/**
 * Fetches the list of steps from the API aka the backend.
 * @returns {Promise<StepItem[]>} A promise that resolves to an array of StepItem objects.
 * @throws Will throw an error if the network response is not ok.
 */
const fetchStepList = async (): Promise<StepItem[]> => {
  return callApi("step_list/");
};

/**
 * Custom hook to fetch and manage step lists. It returns steps lists sorted by section, and a step list containing all steps.
 * @returns {Object} An object containing all step lists and categorized step lists.
 */
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

    fetchList().then();
  }, []);

  return stepLists;
};
