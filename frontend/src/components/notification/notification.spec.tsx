import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "styled-components";

import { getTheme } from "../../theme";
import { Notification } from "./notification";

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={getTheme("light")}>{component}</ThemeProvider>);

describe("Notification", () => {
  const defaultProps = {
    isShown: true,
    title: "Error",
    message: "An error has occurred.",
    type: 'error' | 'success' | 'warning' | 'info',
  };

  it("should render successfully when shown", () => {
    renderWithTheme(<Notification {...defaultProps} />);

    const title = screen.queryByText("Error");
    const message = screen.queryByText("An error has occurred.");

    expect(title).not.toBeNull();
    expect(message).not.toBeNull();
  });
});
