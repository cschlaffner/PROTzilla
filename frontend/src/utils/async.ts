export const isPromise = (maybePromise: unknown): maybePromise is Promise<unknown> =>
  Boolean(
    maybePromise &&
      typeof (maybePromise as Promise<unknown>).catch === "function" &&
      typeof (maybePromise as Promise<unknown>).then === "function",
  );
