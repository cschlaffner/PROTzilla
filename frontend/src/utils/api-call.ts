import { API_ROOT } from "../constants";


export const callApiWithParameters = async (url: string, parameters: Record<string, string>) => {
    try {
      const response = await fetch(API_ROOT + url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          //"X-CSRFToken": csrfToken, // Include CSRF token here
        },
        body: JSON.stringify(parameters),
      });

      const data = await response.json();

      if (response.ok) {
        alert(data.message);
      } else {
        alert(data.message);
      }
      return data
    } catch (error) {
      console.error("Error:", error);
    }
  };
  
export const callApi = async (url: string) => {
  try {
    const response = await fetch(API_ROOT + url)

    const data = await response.json();

    if (response.ok) {
      alert(data.message);
    } else {
      alert(data.message);
    }
    return data
  } catch (error) {
    console.error("Error:", error);
  }
};