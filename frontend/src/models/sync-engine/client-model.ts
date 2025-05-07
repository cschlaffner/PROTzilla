import { action, computed, observable, runInAction } from "mobx";

import { StorageClient } from "./client";
import { defaultStorageClient } from "./main";
import { IClientModel, IRemoteObject, MixinConstructor, Snapshot } from "./types";
import { pickProperties, toSnapshot } from "./utils";

export const ClientModel =
  <M>(
    entity?: string,
    storageClient: StorageClient<M> = defaultStorageClient as unknown as StorageClient<M>,
  ) =>
  <T extends IRemoteObject>(constructor: MixinConstructor<T>, { kind, name }: DecoratorContext) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const resolvedEntity = entity ?? (name as any);

    if (kind === "class") {
      const Model = class extends (constructor as MixinConstructor<IRemoteObject>) {
        @observable protected accessor dirtyKeys: PropertyKey[] = [];
        protected accessor previousValues: Record<PropertyKey, unknown> = {};
        protected sync = true;

        @computed
        public get isDirty(): boolean {
          return Boolean(this.dirtyKeys.length);
        }

        public async save(): Promise<void> {
          await storageClient
            .getController(resolvedEntity)
            .update(
              this.id,
              pickProperties(this.toJSON(), this.dirtyKeys as never) as object,
              this.previousValues as object,
            );
          runInAction(() => {
            this.dirtyKeys = [];
            this.previousValues = {};
          });
        }

        public async delete(): Promise<void> {
          await storageClient.getController(resolvedEntity).delete(this.id);
        }

        @action
        public hydrate(data: Partial<T>): void {
          this.sync = false;
          (this as unknown as { properties: PropertyKey[] }).properties.forEach((property) => {
            if (property in data) {
              this[property as keyof this] = data[property as never];
            }
          });
          this.sync = true;
        }

        public toJSON(): Snapshot<T> {
          const snapshot = {} as T;
          (this as unknown as { properties: PropertyKey[] }).properties.forEach((property) => {
            if (property in this) {
              snapshot[property as keyof T] = this[property as never];
            }
          });
          return toSnapshot(snapshot);
        }
      };

      storageClient.entityMap[resolvedEntity as never] = Model as never;
      return Model as unknown as MixinConstructor<T & IClientModel<T>>;
    }
    return constructor;
  };
