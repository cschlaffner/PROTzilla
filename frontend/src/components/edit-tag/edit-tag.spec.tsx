import { render } from "@testing-library/react";

import { EditTag } from "./edit-tag";
import { getTheme, ThemeProvider } from "../../theme";

describe("Tag", () => {
  it("should render successfully", () => {
    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <EditTag />
      </ThemeProvider>,
    );
    expect(baseElement).toBeTruthy();
  });
});
