import axios, { AxiosInstance } from "axios";

import {
  ID,
  IStorageAdapter,
  Snapshot,
  StorageCommand,
  StorageCommandKind,
  StorageTransaction,
} from "./types";
import { defaultMapEntityToRoute, handleTransaction } from "./utils";

export class RESTAdapter<M> implements IStorageAdapter<M> {
  constructor(
    public baseUrl: string,
    public mapEntityToRoute: (
      entity: keyof M,
    ) => string = defaultMapEntityToRoute,
    protected axiosInstance: AxiosInstance = axios,
  ) {}

  public async create<E extends keyof M>(
    entity: E,
    value: Snapshot<M[E]>,
  ): Promise<void> {
    await this.axiosInstance.post(
      `${this.baseUrl}/${this.mapEntityToRoute(entity)}`,
      value,
    );
  }

  public async read<E extends keyof M>(
    entity: E,
    id: ID,
  ): Promise<Snapshot<M[E]> | undefined> {
    const response = await this.axiosInstance.get<Snapshot<M[E]>>(
      `${this.baseUrl}/${this.mapEntityToRoute(entity)}/${String(id)}`,
    );
    return response.data;
  }

  public async readAll<E extends keyof M>(
    entity: E,
    query?: unknown,
  ): Promise<Snapshot<M[E]>[]> {
    const response = await this.axiosInstance.get<Snapshot<M[E]>[]>(
      `${this.baseUrl}/${this.mapEntityToRoute(entity)}`,
      {
        params: query,
      },
    );
    return response.data;
  }

  public async update<E extends keyof M>(
    entity: E,
    id: ID,
    newValue: Snapshot<Partial<M[E]>>,
  ): Promise<void> {
    await this.axiosInstance.patch(
      `${this.baseUrl}/${this.mapEntityToRoute(entity)}/${String(id)}`,
      newValue,
    );
  }

  public async delete<E extends keyof M>(entity: E, id: ID): Promise<void> {
    await this.axiosInstance.delete(
      `${this.baseUrl}/${this.mapEntityToRoute(entity)}/${String(id)}`,
    );
  }

  public dispatch<E extends keyof M>(
    transaction: StorageCommand<E, M> | StorageTransaction<E, M>,
  ): Promise<void> {
    return handleTransaction(transaction, async (command) => {
      switch (command.kind) {
        case StorageCommandKind.CREATE:
          await this.create(command.entity, command.data as Snapshot<M[E]>);
          break;

        case StorageCommandKind.UPDATE:
          await this.update(
            command.entity,
            command.id,
            command.data as Snapshot<Partial<M[E]>>,
          );
          break;

        case StorageCommandKind.DELETE:
          await this.delete(command.entity, command.id);
          break;
      }
      return Promise.resolve();
    });
  }
}
