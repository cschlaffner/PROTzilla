

export const callApiWithParameters = async (url: string, parameters: Record<string, any>) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/" + url, {
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
    } catch (error) {
      console.error("Error deleting element:", error);
    }
  };
  
export const callApi = (url: string) => {
    fetch("http://127.0.0.1:8000/api/" + url)
      .then((response) => response.json())
      .then((data: any) => {return data})
      .catch((error) => { console.error('Error fetching data:', error); });
};