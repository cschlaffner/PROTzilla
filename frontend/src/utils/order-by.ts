import { Amount, isAmount } from "./amount";
import { ArrayElement } from "./arrayElement.ts";

export const orderKinds = ["ASC", "DESC"] as const;
export type OrderKind = ArrayElement<typeof orderKinds>;

export type SortableValue = Date | number | Amount | string;

export type SortableAttributesOf<T> = {
  [K in keyof T as T[K] extends SortableValue ? K : never]: T[K];
};

export const sortCompare = <T extends SortableValue>(a: T, b: T) =>
  typeof a === "string"
    ? a.localeCompare(b as string)
    : typeof a === "number" || a instanceof Date || isAmount(a)
      ? Number(isAmount(a) ? a.value : a) - Number(isAmount(b) ? b.value : b)
      : 0;

export const orderByArray = <T extends object>(
  array: T[],
  orderBy: keyof SortableAttributesOf<T>,
  order: OrderKind = "ASC",
) =>
  array.sort(
    (a, b) =>
      sortCompare(a[orderBy] as SortableValue, b[orderBy] as SortableValue) *
      (order === "DESC" ? -1 : 1),
  );
