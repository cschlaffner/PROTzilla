import { forwardRef, useState } from "react";
import { RunEditMenuProps } from "./run-edit-menu.props.ts";
import { styled } from "styled-components";
import { fontSize, size, spacing } from "../../theme";
import { Card } from "../card";
import { TextInputField } from "../input-fields/text-input-field";
import { SecondaryButton } from "../button";
import { callApiWithParameters } from "../../utils";
import { SectionTitle } from "../section-title";

const WrapperCard = styled(Card)`
  position: absolute;
  top: ${spacing("navbarHeight")};
  left: 0;
  font-size: ${fontSize("small")};
  width: ${size("navigationItemWidth")};
`;

export const RunEditMenu = forwardRef<HTMLDivElement, RunEditMenuProps>(
  (props, ref) => {
    const [newRunName, setNewRunName] = useState(props.runName);

    const onSave = async () => {
      await callApiWithParameters("update_run_name/", {
        run_name: props.runName,
        new_run_name: newRunName,
      });
    };

    return (
      <div ref={ref}>
        <WrapperCard>
          <SectionTitle baseComponent={"h5"} title={"Run menu"} />
          <TextInputField
            onChange={(value) => setNewRunName(value)}
            value={newRunName}
            label="Edit run name"
          />
          <SecondaryButton text={"Save"} onClick={onSave} />
        </WrapperCard>
      </div>
    );
  },
);
