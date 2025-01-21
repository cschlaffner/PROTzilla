import {
  ID,
  ILocalStorageAdapter,
  Snapshot,
  StorageCommand,
  StorageTransaction,
} from "./types";

export class StorageLogger<M> implements ILocalStorageAdapter<M> {
  public read<E extends keyof M>(
    entity: E,
    id: ID,
  ): Promise<Snapshot<M[E]> | undefined> {
    console.log("Read:", entity, id);
    return Promise.resolve(undefined);
  }

  public readAll<E extends keyof M>(
    entity: E,
    query?: unknown,
  ): Promise<Snapshot<M[E]>[]> {
    console.log("Read all:", entity, JSON.stringify(query));
    return Promise.resolve([]);
  }

  public write<E extends keyof M>(
    entity: E,
    newValue: Snapshot<M[E]>,
  ): Promise<void> {
    console.log("Write:", entity, JSON.stringify(newValue));
    return Promise.resolve();
  }

  public writeAll<E extends keyof M>(
    entity: E,
    query: unknown,
    newValues: Snapshot<M[E]>[],
  ): Promise<void> {
    console.log(
      "Write all:",
      entity,
      JSON.stringify(query),
      JSON.stringify(newValues),
    );
    return Promise.resolve();
  }

  public clear(): Promise<void> {
    console.log("Clear");
    return Promise.resolve();
  }

  public dispatch<E extends keyof M>(
    command: StorageCommand<E, M> | StorageTransaction<E, M>,
  ): Promise<void> {
    console.log("Command:", JSON.stringify(command));
    return Promise.resolve();
  }
}
