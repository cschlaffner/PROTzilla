import { action, observable } from "mobx";

import { ClientModel, IClientModel, Property } from "./sync-engine";

/* eslint-disable @typescript-eslint/no-unsafe-declaration-merging */
@ClientModel("Counter")
export class Counter {
  @Property()
  @observable
  public accessor id!: string;

  @Property()
  @observable
  public accessor count = 0;

  @action
  public increment = () => {
    this.count += 1;
  };
}

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface Counter extends IClientModel<Counter> {}
