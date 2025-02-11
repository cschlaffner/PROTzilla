import React, { useState } from "react";
import { TextInputField } from "../components/input-fields/text-input-field";
import { NumberInputField } from "../components/input-fields/number-input-field";
import { SearchInputField } from "../components/input-fields/search-input-field";
import { CheckboxSelectInputField } from "../components/input-fields/checkbox-select-input-field";
import { RadioSelectInputField } from "../components/input-fields/radio-select-input-field";
import { DropdownInputField } from "../components/input-fields/dropdown-input-field";
import { MultiSelectInputField } from "../components/input-fields/multi-select-input-field";

// ++++++++++++++++++++++++++++++++++++++
// SPIELWIESE 
// wird vorm Mergen gelöscht
// ++++++++++++++++++++++++++++++++++++++

export const InputFieldTestScreen: React.FC = () => {
  const [values, setValues] = useState<{ [key: string]: any }>({
    textinput1: "",
    multiselect: [],
    numberinput1: Number,
    search: "",
    checkboxes: [],
    radio: "",
    dropdown: "",
  });

  const [tooltip, setTooltip] = useState<string | null>(null);

  const handleChange = (field: string, value: any) => {
    setValues((prev) => ({ ...prev, [field]: value }));

    setTooltip(`${field} geändert zu: ${value}`);

    setTimeout(() => {
      setTooltip(null);
    }, 2000);
  };

  return (
    <div className="flex flex-col p-4">
      <h1 className="font-bold mb-4">Test-Page for Input-Fields</h1>

      <div className="border-top border-bottom p-2 m-2">
        Änderung~
        {tooltip}
      </div>

      <div
        style={{width: "700px", border: "2px solid black", padding: "10px",  display: "flex", flexDirection: "column" }}
      >
        <TextInputField
          label="Gib mal was ein"
          labelPosition="side"
          value={values.textinput1}
          onChange={(e) => handleChange("textinput1", e)}
          placeholder="Was steht hier?"
          subscript="Hallo"
          optional={true}
        />

        <MultiSelectInputField 
        options={[
            { label: "Blue", value: "blue" },
            { label: "Red", value: "red" },
            { label: "Orange", value: "orange" },
            { label: "Green", value: "green" },
            { label: "Yellow", value: "yellow" },
          ]}
          onChange={(e) => handleChange("multiselect", e)}
          label="Wähle die richtigen Farben aus"
        />

        <NumberInputField
          value={values.numberinput1}
          onChange={(e) => handleChange("numberinput1", e)}
          optional={true}
          subscript="Dieser Zähler springt irgendwie komisch was ist wenn dieser Text immer länger wird, weißst du, dass das beste Getränk Spezi ist"
        />

        <SearchInputField
          value={values.search}
          onChange={(e) => handleChange("search", e)}
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
        onChange={(e) => handleChange("checkboxes", e)}
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
        onChange={(e) => handleChange("radio", e)}
        label="Wähle eine Farbe aus"
        subscript="Was hast du ausgewählt?"
        separatePrefix=":)"
        />

        <DropdownInputField 
        label="Wer hat die meisten Spezis getrunken?"
        options={["max", "jannes", "jonas", "sarah", "ronja", "philipp"]}
        onClick={(e) => handleChange("dropdown", e)}
        />
      </div>
    </div>
  );
};
