import { EnsureClass } from "./ensure-class";

describe("EnsureClass", () => {
  it("should work", () => {
    class Item {
      public name!: string;
    }
    // eslint-disable-next-line @typescript-eslint/no-extraneous-class
    class Project {
      @EnsureClass<Item[]>(Item)
      public accessor items: Item[] = [];
    }

    const project = new Project();
    project.items = [{ name: "A" }, { name: "B" }];
    expect(project.items[0]).toBeInstanceOf(Item);
    expect(project.items[1]).toBeInstanceOf(Item);
  });
});
