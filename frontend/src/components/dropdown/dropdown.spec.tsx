import { render } from "@testing-library/react";

import { Dropdown } from "./dropdown";
import { getTheme, ThemeProvider } from "../../theme";

describe("Dropdown", () => {
  it("should render successfully", () => {
    const options = [
      { value: "option1", labelTx: "option1" },
      { value: "option2", labelTx: "option2" },
      { value: "option3", labelTx: "option3" },
    ];
    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <Dropdown options={options} />
      </ThemeProvider>,
    );
    expect(baseElement).toBeTruthy();
  });
});
