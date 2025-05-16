import { getTheme, ThemeProvider } from "@protzilla/theme";
import { render } from "@testing-library/react";

import { Button } from "./button";

describe("Button", () => {
  it("should render successfully", () => {
    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <Button />
      </ThemeProvider>,
    );
    expect(baseElement).toBeTruthy();
  });
});
