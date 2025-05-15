import { getTheme, ThemeProvider } from "@protzilla/theme";
import { render } from "@testing-library/react";

import { Tooltip } from "./tooltip";

describe("Tooltip", () => {
  it("should render successfully", () => {
    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <Tooltip />
      </ThemeProvider>,
    );
    expect(baseElement).toBeTruthy();
  });
});
