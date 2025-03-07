const fetch_API_ROOT = () => {
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

export const API_ROOT = fetch_API_ROOT();
