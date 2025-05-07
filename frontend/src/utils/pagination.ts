export interface IPaginationParams {
  limit?: number;
  page?: number;
}

export interface IPaginationMeta {
  /** The amount of items on this specific page. */
  itemCount: number;

  /** The total amount of items. */
  totalItems: number;

  /** The amount of items that were requested per page. */
  itemsPerPage: number;

  /** The total amount of pages in this paginator. */
  totalPages: number;

  /** The current page this paginator "points" to. */
  currentPage: number;
}

export interface IPaginatedResult<T> {
  items: T[];
  meta: IPaginationMeta;
}

export const paginateArray = <T>(array: T[], limit = 10, page = 1): IPaginatedResult<T> => {
  const offset = (page - 1) * limit;
  const items = array.slice(offset, offset + limit);

  const totalPages = Math.ceil(array.length / limit);

  const meta: IPaginationMeta = {
    itemCount: items.length,
    totalItems: array.length,
    itemsPerPage: limit,
    totalPages,
    currentPage: page,
  };

  return { items, meta };
};
