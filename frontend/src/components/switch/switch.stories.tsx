import React, { useState } from "react";

import { Switch } from "./switch";
import { SwitchProps } from "./switch.props";

export default {
  component: Switch,
  title: "Switch",
};

const SwitchWithState: React.FC<SwitchProps> = ({ options, ...args }) => {
  const [selectedOption, setSelectedOption] = useState<string | undefined>(
    undefined,
  );

  return (
    <Switch
      options={options}
      value={selectedOption}
      {...args}
      onChange={setSelectedOption}
    />
  );
};

export const primary = (args: SwitchProps): React.ReactNode => (
  <SwitchWithState {...args} />
);

primary.args = {
  options: [
    { value: "cat", label: "CAT!" },
    { value: "dog", label: "Dog!" },
  ],
  defaultValue: "dog",
  isDisabled: false,
};

export const disabledOption = (args: SwitchProps): React.ReactNode => (
  <SwitchWithState {...args} />
);
disabledOption.args = {
  options: [
    { value: "editor", label: "Editor", isDisabled: false },
    { value: "extra", label: "Extra", isDisabled: true },
    { value: "vorschau", label: "Vorschau", isDisabled: false },
  ],
  isDisabled: false,
};
