// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type MixinConstructor<T extends object> = new (...args: any[]) => T;

export type ID = string;

export type Snapshot<T> = T extends Date
  ? string
  : {
      [P in keyof T]: T[P] extends Date
        ? string
        : T[P] extends object
          ? Snapshot<T[P]>
          : T[P] extends () => void
            ? never
            : T[P];
    };

export interface IRemoteObject {
  id: ID;
}

export type EntityStore<M> = {
  [E in keyof M]: Partial<Record<ID, M[E] | null>>;
};

export type QueryStore<M> = {
  [E in keyof M]: Partial<Record<string, ID[]>>;
};

export type ConstructorMap<M> = {
  [E in keyof M]: MixinConstructor<M[E] & object>;
};

export enum StorageCommandKind {
  CREATE = "CREATE",
  UPDATE = "UPDATE",
  DELETE = "DELETE",
}

export interface StorageCommand<E extends keyof M, M> {
  kind: StorageCommandKind;
  entity: E;
  id: ID;
  data?: Snapshot<Partial<M[E]>>;

  rollback?: StorageCommand<E, M>;
}

export interface StorageTransaction<E extends keyof M, M> {
  kind: "TRANSACTION";
  commands: StorageCommand<E, M>[];
}

export interface IStorageAdapter<M> {
  read<E extends keyof M>(
    entity: E,
    id: ID,
  ): Promise<Snapshot<M[E]> | undefined>;
  readAll<E extends keyof M>(
    entity: E,
    query?: unknown,
  ): Promise<Snapshot<M[E]>[]>;

  dispatch<E extends keyof M>(
    command: StorageCommand<E, M> | StorageTransaction<E, M>,
  ): Promise<void>;
}

export interface ILocalStorageAdapter<M> extends IStorageAdapter<M> {
  write<E extends keyof M>(entity: E, newValue: Snapshot<M[E]>): Promise<void>;
  writeAll<E extends keyof M>(
    entity: E,
    query: unknown,
    newValues: Snapshot<M[E]>[],
  ): Promise<void>;

  clear(): Promise<void>;
}

export interface IStorageCache<M>
  extends Omit<ILocalStorageAdapter<M>, "read" | "readAll" | "get" | "getAll"> {
  read<E extends keyof M>(entity: E, id: ID): Promise<M[E] | undefined>;
  readAll<E extends keyof M>(entity: E, query?: unknown): Promise<M[E][]>;

  get<E extends keyof M>(entity: E, id: ID): M[E] | undefined;
  getAll<E extends keyof M>(entity: E, query?: unknown): M[E][];
}

export interface IStorageHistory<M> extends IStorageAdapter<M> {
  canUndo: boolean;
  canRedo: boolean;

  undo(): Promise<void>;
  redo(): Promise<void>;
}

export interface IStorageController<E extends keyof M, M>
  extends Omit<
    ILocalStorageAdapter<M>,
    "read" | "readAll" | "write" | "writeAll"
  > {
  entity: E;

  create(value: Partial<M[E]>): Promise<M[E]>;
  update(
    id: ID,
    newValue: Partial<M[E]>,
    previousValue?: Partial<M[E]>,
  ): Promise<void>;
  delete(id: ID): Promise<void>;

  read(id: ID): Promise<M[E] | undefined>;
  readAll(query?: unknown): Promise<M[E][]>;

  get(id: ID): M[E] | undefined;
  getAll(query?: unknown): M[E][];
}

export interface IStorageClient<M> extends IStorageCache<M> {
  cache: IStorageCache<M>;
  history: IStorageHistory<M>;
  local?: ILocalStorageAdapter<M>;
  remote?: IStorageAdapter<M>;

  mapEntity<E extends keyof M>(entity: E, value: Snapshot<M[E]>): M[E];
  getController<E extends keyof M>(entity: E): IStorageController<E, M>;

  beginTransaction(): void;
  commitTransaction(): Promise<void>;
  abortTransaction(): Promise<void>;
}

export interface IClientModel<T> {
  isDirty: boolean;

  save(): Promise<void>;
  delete(): Promise<void>;
  hydrate(data: Partial<T>): void;

  toJSON(): Snapshot<T>;
}
