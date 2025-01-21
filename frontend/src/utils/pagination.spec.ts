import { paginateArray } from "./pagination";

describe("paginateArray", () => {
  it("should work", () => {
    expect(paginateArray([1, 2, 3, 4, 5], 2, 2)).toEqual({
      items: [3, 4],
      meta: {
        itemCount: 2,
        totalItems: 5,
        itemsPerPage: 2,
        totalPages: 3,
        currentPage: 2,
      },
    });
  });
});
