import { render } from "@testing-library/react";

import { Switch } from "./switch";
import { getTheme, ThemeProvider } from "@protzilla/theme";

describe("Switch", () => {
  it("should render successfully", () => {
    const options = [
      { value: "option1", labelTx: "option1" },
      { value: "option2", labelTx: "option2" },
      { value: "option3", labelTx: "option3" },
    ];
    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <Switch options={options} />
      </ThemeProvider>,
    );
    expect(baseElement).toBeTruthy();
  });
});
