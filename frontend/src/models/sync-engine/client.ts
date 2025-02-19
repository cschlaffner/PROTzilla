import { action, observable, runInAction } from "mobx";

import { StorageCache } from "./cache";
import { StorageController } from "./controller";
import { CacheMissError, RollbackUnsupportedError } from "./errors";
import { StorageHistory } from "./history";
import {
  ConstructorMap,
  ID,
  ILocalStorageAdapter,
  IStorageAdapter,
  IStorageClient,
  IStorageController,
  Snapshot,
  StorageCommand,
  StorageTransaction,
} from "./types";

export class StorageClient<M> implements IStorageClient<M> {
  @observable protected accessor transaction:
    | StorageTransaction<keyof M, M>
    | undefined = undefined;
  @observable protected accessor transactionCounter = 0;

  public cache = new StorageCache<M>(this.mapEntity.bind(this));
  public history = new StorageHistory<M>((command) =>
    this.dispatch(command, { history: false }),
  );

  public entityMap: Partial<ConstructorMap<M>> = {};

  constructor(
    public local?: ILocalStorageAdapter<M> | undefined,
    public remote?: IStorageAdapter<M> | undefined,
    public handleError: (error: Error) => void = (error) => {
      throw error;
    },
  ) {}

  public mapEntity<E extends keyof M>(entity: E, value: Snapshot<M[E]>): M[E] {
    const Model = this.entityMap[entity];
    if (!Model) return value as M[E];

    const object = new Model();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (typeof (object as any).hydrate === "function") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (object as any).hydrate(value);
    } else {
      Object.keys(object).forEach((key) => {
        if (!(key in (object as object))) return;
        object[key as never] = value[key as never];
      });
    }
    return object;
  }

  public getController<E extends keyof M>(entity: E): IStorageController<E, M> {
    return new StorageController<E, M>(entity, this);
  }

  @action
  public beginTransaction(): void {
    if (this.transactionCounter) return;
    this.transaction = { kind: "TRANSACTION", commands: [] };
    this.transactionCounter += 1;
  }

  public async commitTransaction(): Promise<void> {
    if (!this.transactionCounter) return;

    runInAction(() => {
      this.transactionCounter -= 1;
    });
    if (this.transactionCounter || !this.transaction) return;

    await this.dispatch(this.transaction);
    runInAction(() => {
      this.transaction = undefined;
    });
  }

  public async abortTransaction(): Promise<void> {
    if (!this.transaction) return;

    if (this.transaction.commands.find((subCommand) => !subCommand.rollback)) {
      throw new RollbackUnsupportedError();
    }
    for (const subCommand of [...this.transaction.commands].reverse()) {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      await this.dispatch(subCommand.rollback!, { history: false });
    }

    runInAction(() => {
      this.transaction = undefined;
      this.transactionCounter = 0;
    });
  }

  public async read<E extends keyof M>(
    entity: E,
    id: ID,
    { cache = true, local = true } = {},
  ): Promise<M[E] | undefined> {
    try {
      try {
        if (!cache) throw new CacheMissError();
        return this.cache.get(entity, id);
      } catch (error) {
        if (!(error instanceof CacheMissError)) throw error;

        let value: Snapshot<M[E]> | undefined = undefined;
        if (local && this.local) {
          try {
            value = await this.local.read(entity, id);
          } catch (error) {
            if (!(error instanceof CacheMissError)) throw error;
            value = await this.remote?.read(entity, id);
          }
        } else {
          value = await this.remote?.read(entity, id);
        }

        if (value === undefined) {
          this.cache.delete(entity, id);
        } else {
          await this.cache.write(entity, value);
        }
        return this.cache.get(entity, id);
      }
    } catch (error) {
      this.handleError(error as Error);
    }
  }

  public async readAll<E extends keyof M>(
    entity: E,
    query?: unknown,
    { cache = true, local = true } = {},
  ): Promise<M[E][]> {
    try {
      try {
        if (!cache) throw new CacheMissError();
        return this.cache.getAll(entity, query);
      } catch (error) {
        if (!(error instanceof CacheMissError)) throw error;

        let values: Snapshot<M[E]>[] = [];
        if (local && this.local) {
          try {
            values = await this.local.readAll(entity, query);
          } catch (error) {
            if (!(error instanceof CacheMissError)) throw error;
            values = (await this.remote?.readAll(entity, query)) ?? [];
            await this.local.writeAll(entity, query, values);
          }
        } else {
          values = (await this.remote?.readAll(entity, query)) ?? [];
        }

        await this.cache.writeAll(entity, query, values);
        return this.cache.getAll(entity, query);
      }
    } catch (error) {
      this.handleError(error as Error);
      return [];
    }
  }

  public get<E extends keyof M>(entity: E, id: ID): M[E] | undefined {
    try {
      return this.cache.get(entity, id);
    } catch (error) {
      if (!(error instanceof CacheMissError)) throw error;
      void this.read(entity, id).catch();
    }
  }

  public getAll<E extends keyof M>(entity: E, query?: unknown): M[E][] {
    try {
      return this.cache.getAll(entity, query);
    } catch (error) {
      if (!(error instanceof CacheMissError)) throw error;
      void this.readAll(entity, query).catch();
    }
    return [];
  }

  public async write<E extends keyof M>(
    entity: E,
    newValue: Snapshot<M[E]>,
  ): Promise<void> {
    await this.cache.write(entity, newValue);
    await this.local?.write(entity, newValue);
  }

  public async writeAll<E extends keyof M>(
    entity: E,
    query: unknown,
    newValues: Snapshot<M[E]>[],
  ): Promise<void> {
    await this.cache.writeAll(entity, query, newValues);
    await this.local?.writeAll(entity, query, newValues);
  }

  public async clear(): Promise<void> {
    await this.cache.clear();
    await this.local?.clear();
  }

  public async dispatch<E extends keyof M>(
    command: StorageCommand<E, M> | StorageTransaction<E, M>,
    { cache = true, history = true, local = true, remote = true } = {},
  ): Promise<void> {
    if (cache) await this.cache.dispatch(command);

    if (this.transaction) {
      runInAction(() => {
        if (command.kind === "TRANSACTION") {
          this.transaction?.commands.push(...command.commands);
        } else {
          this.transaction?.commands.push(command);
        }
      });
    } else {
      if (history) await this.history.dispatch(command);

      let hasLocalPassed = false;
      try {
        if (local) await this.local?.dispatch(command);
        hasLocalPassed = true;
        if (remote) await this.remote?.dispatch(command);
      } catch (error) {
        this.handleError(error as Error);

        // Rollback
        if (command.kind === "TRANSACTION") {
          await Promise.all(
            command.commands.map((subCommand) =>
              this.read(subCommand.entity, subCommand.id, {
                cache: false,
                local: !hasLocalPassed,
              }),
            ),
          );
        } else {
          await this.read(command.entity, command.id, {
            cache: false,
            local: !hasLocalPassed,
          });
        }
      }
    }
  }
}
