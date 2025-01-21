import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "styled-components";

import { ErrorNotification } from "./error-notification";
import { getTheme } from "../../theme";

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={getTheme("light")}>{component}</ThemeProvider>);

describe("ErrorNotification", () => {
  const defaultProps = {
    isShown: true,
    title: "Error",
    description: "An error has occurred.",
  };

  it("should render successfully when shown", () => {
    renderWithTheme(<ErrorNotification {...defaultProps} />);

    const title = screen.queryByText("Error");
    const description = screen.queryByText("An error has occurred.");

    expect(title).not.toBeNull();
    expect(description).not.toBeNull();
  });
});
