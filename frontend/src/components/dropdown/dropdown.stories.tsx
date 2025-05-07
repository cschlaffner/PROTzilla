import React, { useCallback, useState } from "react";

import { Dropdown } from "./dropdown";
import { DropdownProps } from "./dropdown.props";

export default {
  component: Dropdown,
  title: "Dropdown",
};

const DropdownWithState: React.FC<DropdownProps> = ({
  options,
  onChange,
  onOtherChange,
  ...args
}) => {
  const [selectedOption, setSelectedOption] = useState<string | undefined>(undefined);
  const [otherOption, setOtherOption] = useState<string | undefined>(undefined);

  const setStandardSelectedOption = useCallback(
    (value: string) => {
      setSelectedOption(value);
      setOtherOption(undefined);
      onChange?.(value);
    },
    [onChange],
  );
  const setOtherSelectedOption = useCallback(
    (value: string) => {
      setOtherOption(value);
      setSelectedOption(undefined);
      onOtherChange?.(value);
    },
    [onOtherChange],
  );

  return (
    <Dropdown
      options={options}
      value={otherOption ?? selectedOption}
      onChange={setStandardSelectedOption}
      isOtherSelected={otherOption !== undefined}
      onOtherChange={setOtherSelectedOption}
      style={{ width: "320px" }}
      {...args}
    />
  );
};

export const primary = (args: DropdownProps): React.ReactNode => <DropdownWithState {...args} />;
primary.args = {
  options: [
    { value: "option1", label: "Option 1" },
    { value: "option2", label: "Option 2" },
    { value: "option3", label: "Option 3" },
    {
      value: "option4",
      label: "option4 option4 option4 option4 option4 option4",
    },
  ],
  isDisabled: false,
  marqueeTextLength: 20,
  placeholder: "Click to select",
};

export const searchable = ({ options, ...args }: DropdownProps): React.ReactNode => {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [search, setSearch] = useState("");

  return (
    <DropdownWithState
      {...args}
      options={options.filter((option) => (option.label as string | undefined)?.includes(search))}
      onSearch={setSearch}
    />
  );
};
searchable.args = {
  options: [
    { value: "option1", label: "Option 1" },
    { value: "option2", label: "Option 2" },
    { value: "option3", label: "Option 3" },
  ],
  isDisabled: false,
  isSearchable: true,
  placeholder: "Click to select",
};

export const withLabel = (args: DropdownProps): React.ReactNode => <DropdownWithState {...args} />;

withLabel.args = {
  options: [
    { value: "cat", label: "CAT!! ..duh" },
    { value: "dog", label: "Dog" },
    { value: "tiger", label: "I'm the tiger king" },
    { value: "none", label: "I don't like pets" },
  ],
  isDisabled: false,
  labelTx: "What is your favorite pet?",
  defaultOther: "Fish.. they're so quiet",
  defaultValue: "dog",
  isOtherAllowed: true,
};
