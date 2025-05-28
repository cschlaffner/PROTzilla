import { SectionTitle } from "./section-title";
import { SectionTitleProps } from "./section-title.props";

export default {
  component: SectionTitle,
  title: "Section Title",
};

export const screenTitle = (args: SectionTitleProps): React.ReactNode => <SectionTitle {...args} />;
screenTitle.args = {
  title: "Title",
  description: "Description",
};

export const cardTitle = (args: SectionTitleProps): React.ReactNode => <SectionTitle {...args} />;
cardTitle.args = {
  baseComponent: "h2",
  title: "Title",
  description: "Description",
};

export const sectionTitle = (args: SectionTitleProps): React.ReactNode => (
  <SectionTitle {...args} />
);
sectionTitle.args = {
  baseComponent: "h3",
  title: "Title",
  description: "Description",
};
