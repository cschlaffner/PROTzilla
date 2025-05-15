export const formatDate = (dateString: string) => {
  const date = /^\d{2} \d{2} \d{4}$/.test(dateString)
    ? new Date(dateString.split(" ").reverse().join("-"))
    : /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(dateString)
      ? new Date(dateString.replace(" ", "T"))
      : new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};
