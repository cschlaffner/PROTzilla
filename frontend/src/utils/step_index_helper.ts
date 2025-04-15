import { Section } from "../components/sidebar/types.ts";

export const translateGlobalToSectionIndex = (
  globalIndex: number,
  currentSection: string,
  sectionsData: Section[],
): number | undefined => {
  let i = globalIndex;
  for (const section of sectionsData) {
    if (section.id === currentSection) {
      return i;
    }
    i -= section.steps.length;
  }
  return undefined;
};
