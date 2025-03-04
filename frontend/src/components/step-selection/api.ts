import { useCookie } from "../../hooks/use-cookie.ts";

/**
 * Hook to add a new step to the workflow via POST request to the backend. Accesses the CSRF token from the cookie via useCookie hook.
 * Connection to the backend is tested with this function, csrftoken management works here.
 * @param {string} run_name - The name of the run.
 * @param {string} new_step - The new step to be added.
 * @param {string} csrftoken - The CSRF token for authentication.
 * @returns {Promise<any>} A promise that resolves to the response of the API call.
 * @throws Will throw an error if the network response is not ok.
 */
export const useAddStepToWorkflow = () => {
  const csrftoken = useCookie("csrftoken");

  const addStepToWorkflow = async (run_name: string, new_step: string) => {
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

  return addStepToWorkflow;
};
