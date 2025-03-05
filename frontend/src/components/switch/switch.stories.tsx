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
    { value: "list", label: "List" },
    { value: "node", label: "Node" },
  ],
  defaultValue: "list",

  isDisabled: false,
};

export const disabledOption = (args: SwitchProps): React.ReactNode => (
  <SwitchWithState {...args} />
);
disabledOption.args = {
  options: [
    { value: "list", label: "List", isDisabled: false },
    { value: "node", label: "Node", isDisabled: true },
  ],
  isDisabled: false,
};
