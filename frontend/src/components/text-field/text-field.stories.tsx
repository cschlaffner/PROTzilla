import { useState } from "react";

import { MultilineTextField, SmallTextField, TextField } from "./text-field";
import { MultilineTextFieldProps, TextFieldProps } from "./text-field.props";
import { useForwardCall } from "../../hooks";

export default {
  component: TextField,
  title: "Text Field",
  argTypes: {
    onConfirm: { action: "confirmed" },
    onCancel: { action: "cancelled" },
  },
};

const TextFieldWithState: React.FC<TextFieldProps> = ({
  onConfirm,
  ...args
}) => {
  const [value, setValue] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const confirm = useForwardCall(onConfirm, setValue);

  return (
    <TextField
      {...args}
      value={value}
      onConfirm={confirm}
      tags={tags}
      setTags={setTags}
    />
  );
};
export const primary = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
primary.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Text Field",
  placeholder: "Type something...",
  isRequired: false,
  isOptional: false,
};

export const characterLimit = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
characterLimit.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Text Field",
  placeholder: "Type something...",
  isRequired: false,
  isOptional: false,
  maxCharacters: 10,
};

export const subscript = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
subscript.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Text Field",
  placeholder: "Type something...",
  isRequired: false,
  isOptional: false,
  maxCharacters: 10,
  subscript: "Fancy subscript text",
};

export const password = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
password.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Password",
  placeholder: "Password",
  type: "password",
  defaultValue: "password",
};

const SmallTextFieldWithState: React.FC<TextFieldProps> = ({
  onConfirm,
  ...args
}) => {
  const [value, setValue] = useState("");
  const confirm = useForwardCall(onConfirm, setValue);

  return <SmallTextField {...args} value={value} onConfirm={confirm} />;
};
export const small = (args: TextFieldProps): React.ReactNode => (
  <SmallTextFieldWithState {...args} />
);
small.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Small Text Field",
  placeholder: "Type something...",
};

const MultilineTextFieldWithState: React.FC<MultilineTextFieldProps> = ({
  onConfirm,
  ...args
}) => {
  const [value, setValue] = useState("");
  const confirm = useForwardCall(onConfirm, setValue);

  return <MultilineTextField {...args} value={value} onConfirm={confirm} />;
};
export const multiline = (args: MultilineTextFieldProps): React.ReactNode => (
  <MultilineTextFieldWithState {...args} />
);
multiline.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Multiline Text Field",
  placeholder: "Type something...",
};

export const tagged = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
tagged.args = {
  label: "Tagged Textfield",
  placeholder: "Add Tag",
  type: "tag",
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  isRequired: false,
  isOptional: false,
};

export const taggedLimited = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
taggedLimited.args = {
  label: "Limited Tagged Textfield",
  placeholder: "Add Tag",
  type: "tag",
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  isRequired: false,
  isOptional: false,
  maxCharacters: 10,
  maxTags: 5,
};

export const taggedSubscript = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
taggedSubscript.args = {
  label: "Limited Tagged Textfield",
  placeholder: "Add Tag",
  type: "tag",
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  isRequired: false,
  isOptional: false,
  maxCharacters: 10,
  subscript: "Subscript text",
};

export const info = (args: TextFieldProps): React.ReactNode => (
  <TextFieldWithState {...args} />
);
info.args = {
  isDisabled: false,
  hasSuccess: false,
  hasError: false,
  label: "Text Field",
  placeholder: "Type something...",
  isRequired: false,
  isOptional: false,
  maxCharacters: 10,
  subscript: "Fancy subscript text",
  subscriptInfo: {
    text: "Subscript Info",
    title: "Info",
  },
  labelInfo: {
    text: "Label Info",
  },
};
