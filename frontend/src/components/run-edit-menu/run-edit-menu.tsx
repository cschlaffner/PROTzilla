import { forwardRef } from "react";
import { RunEditMenuProps } from "./run-edit-menu.props.ts";
import { styled } from "styled-components";
import { fontSize, spacing } from "../../theme";
import { Card } from "../card";

const WrapperCard = styled(Card)`
  position: absolute;
  top: ${spacing("navbarHeight")};
  left: 0;
  font-size: ${fontSize("small")};
`;

export const RunEditMenu = forwardRef<HTMLDivElement, RunEditMenuProps>(
  (props, ref) => {
    return (
      <div ref={ref}>
        <WrapperCard>
          <h2>Run Edit Menu for run {props.runName}</h2>
          <p>Here you can edit your run settings.</p>
          {/* Add your run edit functionality here */}
        </WrapperCard>
      </div>
    );
  },
);
