import { StepItem } from "./useStepList.ts";

/**
 * Fetches the list of steps from the API aka the backend.
 * @returns {Promise<StepItem[]>} A promise that resolves to an array of StepItem objects.
 * @throws Will throw an error if the network response is not ok.
 */
export const fetchStepList = async (): Promise<StepItem[]> => {
  const response = await fetch("http://127.0.0.1:8000/api/step_list/");
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response.json();
};

export function getCookie(tokenName: string) {
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

/**
 * Adds a new step to the workflow via POST request to the backend.
 * Connection to the backend is tested with this function, csrftoken management works here.
 * @param {string} run_name - The name of the run.
 * @param {string} new_step - The new step to be added.
 * @param {string} csrftoken - The CSRF token for authentication.
 * @returns {Promise<any>} A promise that resolves to the response of the API call.
 * @throws Will throw an error if the network response is not ok.
 */
export const addStepToWorkflow = async (run_name: string, new_step: string) => {
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
