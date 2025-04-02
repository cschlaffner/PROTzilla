import { Section } from "../components/sidebar/types.ts";

export const translateGlobalToSectionIndex = (
  globalIndex: number,
  sections: Section[],
): [Section, number] | undefined => {
  let i = 0;
  for (const section of sections) {
    i = i + section.steps.length;
    if (i >= globalIndex) {
      return [section, globalIndex - (i - section.steps.length)];
    }
  }
  return undefined;
};
