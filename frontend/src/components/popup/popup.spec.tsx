import { render } from "@testing-library/react";
import { ThemeProvider } from "styled-components";

import { PopUp } from "./popup";
import { getTheme } from "../../theme";

describe("PopUp", () => {
  it("should render successfully", () => {
    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <PopUp />
      </ThemeProvider>,
    );
    expect(baseElement).toBeTruthy();
  });
});
