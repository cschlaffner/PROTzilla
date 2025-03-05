import { getCookie } from "./get-cookie.ts";

export const callApiWithParameters = async (
  url: string,
  parameters: Record<string, string>,
) => {
  try {
    const csrfToken = getCookie("csrftoken")!;
    const response = await fetch("http://127.0.0.1:8000/api/" + url, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(parameters),
    });

    const data = await response.json();

    if (response.ok) {
      alert(data.message);
    } else {
      alert(data.message);
    }
  } catch (error) {
    console.error("Error deleting element:", error);
  }
};

export const callApi = (url: string) => {
  fetch("http://127.0.0.1:8000/api/" + url)
    .then((response) => response.json())
    .then((data: string) => {
      return data;
    })
    .catch((error: unknown) => {
      if (error instanceof Error) {
        console.error("Error fetching data:", error.message);
      } else {
        console.error("An unknown error occurred", error);
      }
    });
};
