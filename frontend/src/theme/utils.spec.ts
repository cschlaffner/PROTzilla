import { computeStyleValue, parseNumberFromMetric, parseUnitFromMetric } from "./utils";

describe("theme utilities", () => {
  it("should parse a number from a metric string", () => {
    expect(parseNumberFromMetric("1px")).toBe(1);
    expect(parseNumberFromMetric("1.5 cm")).toBe(1.5);
    expect(parseNumberFromMetric("-20 cm")).toBe(-20);

    expect(parseNumberFromMetric("0")).toBe(0);
  });

  it("should parse a unit from a metric string", () => {
    expect(parseUnitFromMetric("8px")).toBe("px");
    expect(parseUnitFromMetric("-12.3 m")).toBe("m");

    expect(parseUnitFromMetric("0")).toBe("");
  });
});

describe("computeStyleValue", () => {
  it("should return a single style value", () => {
    expect(computeStyleValue("#000", (value) => value)({})).toBe("#000");
    expect(computeStyleValue("1 px", (value) => value)({})).toBe("1px");

    expect(
      computeStyleValue(
        ({ value }) => value as string,
        (value) => value,
      )({ value: "-6.5 px" }),
    ).toBe("-6.5px");

    expect(computeStyleValue(0, (value) => value)({})).toBe("0");
  });

  it("should return reduced style inputs", () => {
    expect(computeStyleValue(["#000", "#fff"], (firstValue) => firstValue)({})).toBe("#000");

    expect(
      computeStyleValue(["1 px", 2, "3 cm"], (...values: number[]) =>
        values.reduce((a, b) => a + b),
      )({}),
    ).toBe("6px");

    expect(
      computeStyleValue([1, 0, () => 3], (...values: number[]) => values.reduce((a, b) => a + b))(
        {},
      ),
    ).toBe("4");

    expect(computeStyleValue([0], (firstValue) => firstValue)({})).toBe("0");
  });
});
