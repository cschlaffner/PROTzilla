import { action, observable } from "mobx";

import { CacheMissError, NoIdError } from "./errors";
import {
  EntityStore,
  ID,
  IRemoteObject,
  IStorageCache,
  QueryStore,
  Snapshot,
  StorageCommand,
  StorageCommandKind,
  StorageTransaction,
} from "./types";
import { handleTransaction } from "./utils";

export class StorageCache<M> implements IStorageCache<M> {
  @observable protected accessor store: Partial<EntityStore<M>> = {};
  @observable protected accessor queries: Partial<QueryStore<M>> = {};

  constructor(
    protected mapEntity: <E extends keyof M>(entity: E, value: Snapshot<M[E]>) => M[E] = <
      E extends keyof M,
    >(
      value: E,
    ) => value as M[E],
  ) {}

  @action
  public create<E extends keyof M>(entity: E, value: Snapshot<M[E]>): void {
    if ((value as Partial<IRemoteObject>).id === undefined) {
      throw new NoIdError();
    }

    this.store[entity] = this.store[entity] ?? {};
    this.store[entity][(value as IRemoteObject).id] = this.mapEntity(entity, value);
  }

  @action
  public update<E extends keyof M>(entity: E, id: ID, newValue: Snapshot<Partial<M[E]>>): void {
    this.store[entity] = this.store[entity] ?? {};
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const previousValue = this.store[entity]![id];
    if (previousValue === undefined || previousValue === null) {
      this.create(entity, newValue as Snapshot<M[E]>);
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (typeof (previousValue as any).hydrate === "function") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (previousValue as any).hydrate(newValue);
    } else {
      Object.keys(previousValue).forEach((key) => {
        if (!(key in (previousValue as object))) return;
        previousValue[key as never] = newValue[key as never];
      });
    }
  }

  @action
  public delete<E extends keyof M>(entity: E, id: ID): void {
    if (!this.store[entity]) return;
    this.store[entity][id] = null;
  }

  public get<E extends keyof M>(entity: E, id: ID): M[E] | undefined {
    const value = this.store[entity]?.[id];
    if (value === undefined) throw new CacheMissError();
    return value ?? undefined;
  }

  public getAll<E extends keyof M>(entity: E, query?: unknown): M[E][] {
    if (!this.store[entity]) throw new CacheMissError();

    if (query) {
      if (!this.queries[entity]) throw new CacheMissError();
      const queryResult = this.queries[entity][JSON.stringify(query)];
      if (!queryResult) throw new CacheMissError();
      return queryResult.map((id) => this.get(entity, id)).filter((value) => value !== undefined);
    }

    return Object.values(this.store[entity]).filter(
      (value) => value !== null && value !== undefined,
    );
  }

  public read<E extends keyof M>(entity: E, id: ID): Promise<M[E] | undefined> {
    return Promise.resolve(this.get(entity, id));
  }

  public readAll<E extends keyof M>(entity: E, query: unknown): Promise<M[E][]> {
    return Promise.resolve(this.getAll(entity, query));
  }

  @action
  public write<E extends keyof M>(entity: E, newValue: Snapshot<M[E]>): Promise<void> {
    this.create(entity, newValue);
    return Promise.resolve();
  }

  @action
  public writeAll<E extends keyof M>(
    entity: E,
    query: unknown,
    newValues: Snapshot<M[E]>[],
  ): Promise<void> {
    newValues.forEach((value) => {
      this.create(entity, value);
    });
    this.queries[entity] = this.queries[entity] ?? {};
    this.queries[entity][JSON.stringify(query)] = newValues.map((value) => {
      if ((value as Partial<IRemoteObject>).id === undefined) {
        throw new NoIdError();
      }
      return (value as IRemoteObject).id;
    });
    return Promise.resolve();
  }

  @action
  public clear(): Promise<void> {
    this.store = {};
    this.queries = {};
    return Promise.resolve();
  }

  public dispatch<E extends keyof M>(
    transaction: StorageCommand<E, M> | StorageTransaction<E, M>,
  ): Promise<void> {
    return handleTransaction(transaction, (command) => {
      switch (command.kind) {
        case StorageCommandKind.CREATE:
          this.create(command.entity, command.data as Snapshot<M[E]>);
          break;

        case StorageCommandKind.UPDATE:
          this.update(command.entity, command.id, command.data as Snapshot<Partial<M[E]>>);
          break;

        case StorageCommandKind.DELETE:
          this.delete(command.entity, command.id);
          break;
      }
      return Promise.resolve();
    });
  }
}
