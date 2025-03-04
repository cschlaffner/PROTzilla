import { useState, useEffect } from "react";

/**
 * Custom hook to get the value of a cookie by its name.
 * @param {string} tokenName - The name of the cookie.
 * @returns {string} The value of the cookie.
 */
export const useCookie = (tokenName: string): string => {
  const [cookieValue, setCookieValue] = useState<string>("");

  useEffect(() => {
    const getCookie = (name: string): string | null => {
      let value = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            value = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return value;
    };

    setCookieValue(getCookie(tokenName) || "");
  }, [tokenName]);

  return cookieValue;
};
