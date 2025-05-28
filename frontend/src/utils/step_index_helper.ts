import { Section, Sections, SelectedStep } from "@protzilla/utils";

export const translateGlobalToSectionIndex = (
  globalIndex: number,
  sectionsData: Section[],
): SelectedStep => {
  let i = globalIndex;
  for (const section of sectionsData) {
    if (i < section.steps.length) {
      return { section: section.id, index: i };
    }
    i -= section.steps.length;
  }
  return { section: Sections.Importing, index: 0 };
};
