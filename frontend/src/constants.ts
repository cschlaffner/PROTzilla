const fetchApiRoot = () => {
  const currentHost = window.location.hostname;
  const currentPort = window.location.port;
  if (currentPort === "6006") {
    if (currentHost === "localhost") {
      return "http://localhost:8000/api/";
    } else if (currentHost === "127.0.0.1") {
      return "http://127.0.0.1:8000/api/";
    } else if (currentHost === "0.0.0.0") {
      return "http://0.0.0.0:8000/api/";
    }
  }

  return "/api/";
};

export const API_ROOT = fetchApiRoot();
export const DOCUMENTATION_URL = "http://localhost:5174/PROTzilla/";

export const PROTZILLA_VERSION = "1.0.0";
export const PROTZILLA_LASTUPDATE = "2026-03-18";
