import { Counter } from "./counter";

declare module "./sync-engine/main" {
  export interface DefaultEntityMap {
    Counter: Counter;
  }
}

export * from "./counter";
export * from "./root-store";
