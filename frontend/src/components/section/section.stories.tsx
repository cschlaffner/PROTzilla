import { Section } from "./section";
import { SectionProps } from "./section.props";

export default {
  component: Section,
  title: "Section",
};

export const primary = (args: SectionProps): React.ReactNode => (
  <Section {...args} />
);
primary.args = {
  title: "Title",
  description: "Description",
};
