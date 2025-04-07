import { SingleCheckboxInputField } from "./single-checkbox-input-field.tsx";
import { SingleCheckboxInputFieldProps } from "./single-checkbox-input-field.props.ts";

export default {
  component: "SingleCheckboxInputField",
  title: "Input Fields / Single Checkbox Input Field",
  argTypes: { onChange: { action: "changed" } },
};

export const primary = (args: SingleCheckboxInputFieldProps) => (
  <SingleCheckboxInputField {...args} />
);
primary.args = {
  label: "Do you like this single checkbox?",
  text: "It is amazing!",
  value: true,
};
