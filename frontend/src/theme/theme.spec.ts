import { getMediaQueriesFromBreakpoints } from "./theme";

describe("getMediaQueriesFromBreakpoints", () => {
  it("should work", () => {
    expect(
      getMediaQueriesFromBreakpoints({
        xs: 0,
        sm: 600,
        md: 900,
        lg: 1200,
        xl: 1536,
      }),
    ).toEqual({
      "lg-down": "@media (max-width: 1200px)",
      "lg-only": "@media (min-width: 901px) and (max-width: 1535px)",
      "lg-up": "@media (min-width: 1200px)",
      "md-down": "@media (max-width: 900px)",
      "md-only": "@media (min-width: 601px) and (max-width: 1199px)",
      "md-up": "@media (min-width: 900px)",
      "sm-down": "@media (max-width: 600px)",
      "sm-only": "@media (min-width: 1px) and (max-width: 899px)",
      "sm-up": "@media (min-width: 600px)",
      "xl-down": "@media (max-width: 1536px)",
      "xl-only": "@media (min-width: 1201px)",
      "xl-up": "@media (min-width: 1536px)",
      "xs-down": "@media (max-width: 0px)",
      "xs-only": "@media (max-width: 599px)",
      "xs-up": "@media (min-width: 0px)",
    });
  });
});
