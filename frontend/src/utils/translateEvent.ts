export const translateEvent = (event: string, dictionary: Record<string, string>): string => {
  if (!event) return event;

  const sortedKeys = Object.keys(dictionary).sort((a, b) => b.length - a.length);

  let result = event;
  for (const key of sortedKeys) {
    const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escaped, 'gi');
    result = result.replace(regex, dictionary[key]);
  }

  return result;
};
