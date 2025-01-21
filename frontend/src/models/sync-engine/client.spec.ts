/* eslint-disable @typescript-eslint/no-extraneous-class */
import { observable, runInAction } from "mobx";

import { ClientModel } from "./client-model";
import { defaultStorageClient } from "./main";
import { Property } from "./property";
import { IClientModel } from "./types";

@ClientModel()
// eslint-disable-next-line @typescript-eslint/no-unsafe-declaration-merging
class Project {
  @Property()
  @observable
  public accessor id!: string;

  @Property()
  @observable
  public accessor name!: string;

  @Property({ transform: (value) => new Date(value as string) })
  @observable
  public accessor createdAt!: Date;

  @Property({ observe: true })
  @observable
  public accessor connections: [string, string][] = [];
}
// eslint-disable-next-line @typescript-eslint/no-unsafe-declaration-merging, @typescript-eslint/no-empty-object-type
interface Project extends IClientModel<Project> {}

declare module "./main" {
  export interface DefaultEntityMap {
    Project: Project;
  }
}

describe("Remote Objects", () => {
  it("should undo/redo", async () => {
    const project = await defaultStorageClient
      .getController("Project")
      .create({ name: "test", createdAt: new Date() });

    expect(project.name).toBe("test");
    runInAction(() => {
      project.name = "test1";
      project.name = "test2";
    });
    await project.save();
    expect(project.name).toBe("test2");

    await defaultStorageClient.history.undo();
    expect(project.name).toBe("test");

    await defaultStorageClient.history.redo();
    await defaultStorageClient.history.redo();
    expect(project.name).toBe("test2");

    await defaultStorageClient.history.undo();
    expect(project.name).toBe("test");

    runInAction(() => {
      project.name = "test1";
    });
    await project.save();
    expect(project.name).toBe("test1");

    await defaultStorageClient.history.redo();
    expect(project.name).toBe("test1");

    await defaultStorageClient.history.undo();
    expect(project.name).toBe("test");
  });

  it("should handle observable assignment", async () => {
    const project = await defaultStorageClient
      .getController("Project")
      .create({ name: "test", createdAt: new Date() });

    expect(project.connections).toEqual([]);

    runInAction(() => {
      project.connections = [["a", "b"]];
    });
    await project.save();
    expect(project.connections).toEqual([["a", "b"]]);
  });

  it("should handle observable mutation", async () => {
    const project = await defaultStorageClient
      .getController("Project")
      .create({ name: "test", createdAt: new Date() });

    expect(project.connections).toEqual([]);

    runInAction(() => {
      project.connections.push(["a", "b"]);
    });
    await project.save();
    expect(project.connections).toEqual([["a", "b"]]);
    await defaultStorageClient.history.undo();
    expect(project.connections).toEqual([]);
    await defaultStorageClient.history.redo();
    expect(project.connections).toEqual([["a", "b"]]);
  });
});
