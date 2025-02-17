import React, { useState } from "react";

import { CheckboxSelectInputField } from "../components/input-fields/checkbox-select-input-field";
import { DropdownInputField } from "../components/input-fields/dropdown-input-field";
import { MultiSelectInputField } from "../components/input-fields/multi-select-input-field";
import { NumberInputField } from "../components/input-fields/number-input-field";
import { RadioSelectInputField } from "../components/input-fields/radio-select-input-field";
import { SearchInputField } from "../components/input-fields/search-input-field";
import { TextInputField } from "../components/input-fields/text-input-field";

// ++++++++++++++++++++++++++++++++++++++
// SPIELWIESE
// wird vorm Mergen gelöscht
// ++++++++++++++++++++++++++++++++++++++

export const InputFieldTestScreen: React.FC = () => {
  const [values, setValues] = useState<{
    textinput1: string;
    multiselect: string[];
    numberinput1: number;
    search: string;
    checkboxes: string[];
    radio: string;
    dropdown: string;
  }>({
    textinput1: "",
    multiselect: [],
    numberinput1: 0,
    search: "",
    checkboxes: [],
    radio: "",
    dropdown: "",
  });

  const [tooltip, setTooltip] = useState<string | null>(null);

  const handleChange = (
    field: keyof typeof values,
    value: string | number | string[],
  ) => {
    setValues((prev) => ({ ...prev, [field]: value }));

    setTooltip(`${field} geändert zu: ${String(value)}`);

    setTimeout(() => {
      setTooltip(null);
    }, 2000);
  };

  return (
    <div className="flex flex-col p-4">
      <h1 className="font-bold mb-4">Spielwiese für Input-Fields</h1>

      <div className="border-top border-bottom p-2 m-2">
        Änderung~
        {tooltip}
      </div>

      <div
        style={{
          width: "400px",
          border: "2px solid black",
          padding: "10px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <TextInputField
          label="Gib mal was ein"
          labelPosition="side"
          defaultValue={values.textinput1}
          onChange={(e) => {
            handleChange("textinput1", e);
          }}
          placeholder="Was steht hier?"
          subscript="Hallo"
          optional={true}
        />

        <MultiSelectInputField
          options={colorOptions}
          onChange={(selectedOptions) => {
            handleChange("multiselect", selectedOptions);
          }}
          label="Wähle die richtigen Farben aus"
        />

        <NumberInputField
          defaultValue={values.numberinput1}
          onChange={(e) => {
            handleChange("numberinput1", e);
          }}
          optional={true}
          subscript="Dieser Zähler springt irgendwie komisch was ist wenn dieser Text immer länger wird, weißst du, dass das beste Getränk Spezi ist"
        />

        <SearchInputField
          defaultValue={values.search}
          onChange={(e) => {
            handleChange("search", e);
          }}
        />

        <CheckboxSelectInputField
          options={[
            { label: "Blue", value: "blue" },
            { label: "Red", value: "red" },
            { label: "Orange", value: "orange" },
            { label: "Green", value: "green" },
            { label: "Yellow", value: "yellow" },
          ]}
          selectedValues={values.checkboxes}
          onChange={(e) => {
            handleChange("checkboxes", e);
          }}
          label="Wähle eine Farbe aus"
          subscript="Was hast du ausgewählt?"
          separatePrefix=":)"
        />

        <RadioSelectInputField
          options={[
            { label: "Blue", value: "blue" },
            { label: "Red", value: "red" },
            { label: "Orange", value: "orange" },
            { label: "Green", value: "green" },
            { label: "Yellow", value: "yellow" },
          ]}
          selectedValue={values.radio}
          onChange={(e) => {
            handleChange("radio", e);
          }}
          label="Wähle eine Farbe aus"
          subscript="Was hast du ausgewählt?"
          separatePrefix=":)"
        />

        <DropdownInputField
          label="Wer hat die meisten Spezis getrunken?"
          options={["max", "jannes", "jonas", "sarah", "ronja", "philipp"]}
          onChange={(e) => {
            handleChange("dropdown", e);
          }}
        />
      </div>
    </div>
  );
};

const colorOptions = [
  { label: "Blue", value: "blue" },
  { label: "Red", value: "red" },
  { label: "Orange", value: "orange" },
  { label: "Green", value: "green" },
  { label: "Yellow", value: "yellow" },
  { label: "Purple", value: "purple" },
  { label: "Pink", value: "pink" },
  { label: "Brown", value: "brown" },
  { label: "Black", value: "black" },
  { label: "White", value: "white" },
  { label: "Gray", value: "gray" },
  { label: "Cyan", value: "cyan" },
  { label: "Magenta", value: "magenta" },
  { label: "Lime", value: "lime" },
  { label: "Teal", value: "teal" },
  { label: "Indigo", value: "indigo" },
  { label: "Maroon", value: "maroon" },
  { label: "Beige", value: "beige" },
  { label: "Turquoise", value: "turquoise" },
  { label: "Lavender", value: "lavender" },
  { label: "Gold", value: "gold" },
  { label: "Silver", value: "silver" },
  { label: "Coral", value: "coral" },
  { label: "Peach", value: "peach" },
  { label: "Olive", value: "olive" },
];
