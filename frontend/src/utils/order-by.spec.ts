import { orderByArray } from "./order-by";

describe("orderByArray", () => {
  it("should work", () => {
    expect(orderByArray([{ a: 0 }, { a: 3 }, { a: 2 }], "a", "DESC")).toEqual([
      { a: 3 },
      { a: 2 },
      { a: 0 },
    ]);
  });
});
