import { getCookie } from "./get-cookie.ts";
import { API_ROOT } from "../constants";

export async function ensureCSRFToken() {
  const response = await fetch(`${API_ROOT}get_csrf_token/`, {
    method: "GET",
    credentials: "include",
  });
  if (!response.ok) throw new Error("Failed to fetch CSRF token");
  return response;
}

export const callApiWithParameters = async (
  url: string,
  parameters: Record<string, string | string[] | number | File>,
) => {
  try {
    await ensureCSRFToken();

    const csrfToken = getCookie("csrftoken");
    if (!csrfToken) {
      throw new Error("CSRF token not found.");
    }
    const response = await fetch(`${API_ROOT}${url}`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(parameters),
    });

    const data = await response.json();

    return data;

  } catch (error) {
    console.error("Error:", error);
  }
};

export const callApi = async (url: string) => {
  try {
    const response = await fetch(`${API_ROOT}${url}`);

    const data = await response.json();

    return data;
    
  } catch (error) {
    console.error("Error:", error);
  }
};
