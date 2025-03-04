import { StepItem } from "./useStepList.ts";

export const fetchStepList = async (): Promise<StepItem[]> => {
  const response = await fetch("http://127.0.0.1:8000/api/step_list/");
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response.json();
};

export const addStepToWorkflow = async (
  run_name: string,
  new_step: string,
  csrftoken: string,
) => {
  const response = await fetch("http://127.0.0.1:8000/api/add_step/", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ run_name, method: new_step }),
  });

  if (!response.ok) {
    throw new Error("Network response was not ok");
  }

  return response.json();
};
