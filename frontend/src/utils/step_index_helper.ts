import {
  Section,
  Sections,
  SelectedStep,
} from "../components/sidebar/types.ts";

export const translateGlobalToSectionIndex = (
  globalIndex: number,
  sectionsData: Section[],
): SelectedStep => {
  let i = globalIndex;
  console.log(sectionsData);
  for (const section of sectionsData) {
    console.log(section);
    if (i < section.steps.length) {
      return { section: section.id, index: i };
    }
    i -= section.steps.length;
  }
  return { section: Sections.Importing, index: 0 };
};
