export const formatDate = (rawDate: string) => {
  if (!rawDate) return "";
  return new Date(rawDate).toLocaleDateString();
};
