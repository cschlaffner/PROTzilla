import React, { forwardRef } from "react";
import { NumberFieldProps } from "./number-field.props";
import { InputLabel } from "../text";
import { FlexRow } from "../box";
import styled from "styled-components";


const LabelRow = styled(FlexRow)`
  align-items: flex-end;
`;

export const NumberField = forwardRef<HTMLInputElement, NumberFieldProps>(
    ({ label, value, placeholder, min, max, step, onChange }, ref) => {
      const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const numValue = event.target.value ? parseFloat(event.target.value) : undefined;
        if (onChange && numValue !== undefined) {
          onChange(numValue);
        }
      };
  
      return (
        <LabelRow>
          <InputLabel 
                className="label"
                text={label} />
          <input
            type="number"
            value={value}
            placeholder={placeholder}
            min={min}
            max={max}
            step={step}
            onChange={handleChange}
            ref={ref}
            style={{ padding: "8px", fontSize: "16px", width: "100px" }}
          />
        </LabelRow>
      );
    }
  );