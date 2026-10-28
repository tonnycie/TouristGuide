export function formatError(err) {
  if (!err.response) return "Няма връзка със сървъра.";
  const data = err.response.data;
  if (data && data.detail) return data.detail;
  if (data && typeof data === "object") {
    return Object.entries(data)
      .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(" ") : msgs}`)
      .join(" | ");
  }
  return "Възникна грешка.";
}