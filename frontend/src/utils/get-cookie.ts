/**
 * Function to get the value of a cookie by its name.
 * @param {string} tokenName - The name of the cookie.
 * @returns {string | null} The value of the cookie or null if not found.
 */
export const getCookie = (tokenName: string): string | null => {
  let value = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, tokenName.length + 1) === tokenName + "=") {
        value = decodeURIComponent(cookie.substring(tokenName.length + 1));
        break;
      }
    }
  }
  return value as string;
};
