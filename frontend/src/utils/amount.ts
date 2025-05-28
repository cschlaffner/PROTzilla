import { ArrayElement } from "./arrayElement.ts";

/** Currency units. */
export const amountCurrencies = ["EUR"] as const;
export type AmountCurrency = ArrayElement<typeof amountCurrencies>;

export interface Amount<U = AmountCurrency> {
  /** The amount's value. */
  value: number;

  /** The amount's unit. */
  unit: U;
}

/** Returns true if the given value is a `{value, unit}` Amount. */
export const isAmount = <U = unknown>(value: unknown): value is Amount<U> =>
  typeof value === "object" &&
  // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
  typeof (value as Amount<unknown>)?.value === "number";
