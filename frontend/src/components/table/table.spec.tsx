import { render } from "@testing-library/react";

import { Table } from "./table";
import { getTheme, ThemeProvider } from "../../theme";

describe("Table", () => {
  it("should render successfully", () => {
    const columns = [
      {
        name: "name" as const,
        titleTx: "Name",
      },
      {
        name: "birthDate" as const,
        titleTx: "Birth Date",
        formatCell: (value: string | Date) =>
          value instanceof Date ? value.toLocaleDateString() : value,
      },
    ];
    const rows = [
      { name: "John", birthDate: new Date("1980-09-08") },
      { name: "Mary", birthDate: new Date("2000-11-26") },
    ];

    const { baseElement } = render(
      <ThemeProvider theme={getTheme()}>
        <Table columns={columns} rows={rows} />
      </ThemeProvider>,
    );

    expect(baseElement).toBeTruthy();
  });

  it("should display column titles and rows", () => {
    const columns = [
      {
        name: "name" as const,
        titleTx: "Name",
      },
      {
        name: "birthDate" as const,
        titleTx: "Birth Date",
        formatCell: (value: string | Date) =>
          value instanceof Date ? value.toLocaleDateString() : value,
      },
    ];
    const rows = [
      { name: "John", birthDate: new Date("1980-09-08") },
      { name: "Mary", birthDate: new Date("2000-11-26") },
    ];

    const { getByText } = render(
      <ThemeProvider theme={getTheme()}>
        <Table columns={columns} rows={rows} />
      </ThemeProvider>,
    );

    expect(getByText("Name")).toBeTruthy();
    expect(getByText("Birth Date")).toBeTruthy();

    expect(getByText("John")).toBeTruthy();
    expect(getByText("Mary")).toBeTruthy();
    expect(getByText("9/8/1980")).toBeTruthy();
    expect(getByText("11/26/2000")).toBeTruthy();
  });
});
