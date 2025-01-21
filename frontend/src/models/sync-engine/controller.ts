import {
  ID,
  IRemoteObject,
  IStorageCache,
  IStorageController,
  Snapshot,
  StorageCommand,
  StorageCommandKind,
  StorageTransaction,
} from "./types";
import { ensureId, pickProperties, toSnapshot } from "./utils";

export class StorageController<E extends keyof M, M>
  implements IStorageController<E, M>
{
  constructor(
    public readonly entity: E,
    protected storageAdapter: IStorageCache<M>,
  ) {}

  public async create(value: Partial<M[E]>): Promise<M[E]> {
    const normalizedValue = ensureId(value);

    await this.storageAdapter.dispatch({
      kind: StorageCommandKind.CREATE,
      entity: this.entity,
      id: (normalizedValue as unknown as IRemoteObject).id,
      data: toSnapshot(normalizedValue),
      rollback: {
        kind: StorageCommandKind.DELETE,
        entity: this.entity,
        id: (normalizedValue as unknown as IRemoteObject).id,
      },
    });
    return this.storageAdapter.read(
      this.entity,
      (normalizedValue as unknown as IRemoteObject).id,
    ) as M[E];
  }

  public async update(
    id: ID,
    newValue: Partial<M[E]>,
    previousValue?: Partial<M[E]>,
  ): Promise<void> {
    const value = previousValue === undefined ? await this.read(id) : undefined;

    return this.storageAdapter.dispatch({
      kind: StorageCommandKind.UPDATE,
      entity: this.entity,
      id: id,
      data: toSnapshot(newValue),
      rollback:
        previousValue === undefined && value === undefined
          ? undefined
          : {
              kind: StorageCommandKind.UPDATE,
              entity: this.entity,
              id,
              data: (previousValue === undefined
                ? pickProperties(
                    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                    toSnapshot(value!) as object,
                    Object.keys(newValue) as never[],
                  )
                : toSnapshot(previousValue)) as Snapshot<M[E]>,
            },
    });
  }

  public async delete(id: ID): Promise<void> {
    const value = await this.read(id);

    return this.storageAdapter.dispatch({
      kind: StorageCommandKind.DELETE,
      entity: this.entity,
      id: id,
      rollback:
        value === undefined
          ? undefined
          : {
              kind: StorageCommandKind.CREATE,
              entity: this.entity,
              id,
              data: toSnapshot(value),
            },
    });
  }

  public read(id: ID): Promise<M[E] | undefined> {
    return this.storageAdapter.read(this.entity, id);
  }
  public readAll(query?: unknown): Promise<M[E][]> {
    return this.storageAdapter.readAll(this.entity, query);
  }

  public get(id: ID): M[E] | undefined {
    return this.storageAdapter.get(this.entity, id);
  }
  public getAll(query?: unknown): M[E][] {
    return this.storageAdapter.getAll(this.entity, query);
  }

  public clear(): Promise<void> {
    return this.storageAdapter.clear();
  }

  public dispatch<E extends keyof M>(
    command: StorageCommand<E, M> | StorageTransaction<E, M>,
  ): Promise<void> {
    return this.storageAdapter.dispatch(command);
  }
}
