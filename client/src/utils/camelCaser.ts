export function camelize(str: string) {
  return str
    .toLowerCase()
    .replace(/[-_][a-z0-9]/g, (group) => group.slice(-1).toUpperCase());
}

const isJSObject = (value: unknown) =>
  typeof value === "object" && !Array.isArray(value) && value !== null;

export function convertObjectKeysToCamelCase(rawCase: Record<string, unknown>) {
  const converted = {};
  // eslint-disable-next-line prefer-const
  for (let [key, value] of Object.entries(rawCase)) {
    if (isJSObject(value))
      value = convertObjectKeysToCamelCase(value as Record<string, unknown>);
    converted[camelize(key)] = value;
  }
  return converted;
}
