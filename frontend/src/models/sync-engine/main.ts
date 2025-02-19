import { StorageClient } from "./client";

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface DefaultEntityMap {}

export const defaultStorageClient = new StorageClient<DefaultEntityMap>();
