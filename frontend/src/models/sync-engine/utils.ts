import { toJS } from "mobx";
import { v4 } from "uuid";

import type { Snapshot, StorageCommand, StorageTransaction } from "./types";

export const MAX_HISTORY_STEPS = 128;

export const generateId = (): string => v4();
export const ensureId = <T>(value: T): T =>
  typeof value === "object" && value !== null ? { ...value, id: generateId() } : value;

export const defaultMapEntityToRoute = (entity: unknown) => {
  const base = String(entity).toLowerCase();
  return base.endsWith("s") ? base : `${base}s`;
};

/* eslint-disable @typescript-eslint/no-explicit-any */
export const toSnapshot = <T>(data: T): Snapshot<T> => {
  if (data === null || typeof data !== "object") {
    return (data instanceof Date ? data.toISOString() : data) as Snapshot<T>;
  }

  if (typeof (data as any).toJSON === "function") {
    return (data as any).toJSON() as Snapshot<T>;
  }

  const snapshot = toJS(data);

  if (Array.isArray(snapshot)) {
    return snapshot.map(toSnapshot) as unknown as Snapshot<T>;
  }

  Object.keys(snapshot).forEach((key) => {
    if (snapshot[key as keyof T] !== null && typeof snapshot[key as keyof T] === "object") {
      snapshot[key as keyof T] = toSnapshot(snapshot[key as keyof T]) as any;
      return;
    }

    if (snapshot[key as keyof T] instanceof Date) {
      snapshot[key as keyof T] = (snapshot[key as keyof T] as Date).toISOString() as any;
    }
  });

  return snapshot as Snapshot<T>;
};
/* eslint-enable */

export const pickProperties = <T extends object, K extends keyof T>(
  object: T,
  keys: K[],
): Pick<T, K> =>
  keys
    .filter((key) => key in object)
    .reduce((result, key) => ((result[key] = object[key]), result), {} as Pick<T, K>);

export const handleTransaction = async <E extends keyof M, M>(
  command: StorageCommand<E, M> | StorageTransaction<E, M>,
  execute: (command: StorageCommand<E, M>) => Promise<void>,
) => {
  if (command.kind === "TRANSACTION") {
    for (const subCommand of command.commands) {
      await execute(subCommand);
    }
    return;
  }

  return execute(command);
};
