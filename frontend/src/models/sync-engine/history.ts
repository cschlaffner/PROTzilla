import { observable, runInAction } from "mobx";

import { RollbackUnsupportedError } from "./errors";
import { IStorageHistory, StorageCommand, StorageTransaction } from "./types";
import { MAX_HISTORY_STEPS } from "./utils";

export class StorageHistory<M> implements IStorageHistory<M> {
  @observable protected accessor history: (
    | StorageCommand<keyof M, M>
    | StorageTransaction<keyof M, M>
  )[] = [];
  @observable protected accessor historyOffset = 0;

  constructor(
    protected dispatchHistoryAction: (
      command: StorageCommand<keyof M, M>,
    ) => Promise<void>,
  ) {}

  public get canUndo(): boolean {
    return this.historyOffset < this.history.length;
  }

  public get canRedo(): boolean {
    return Boolean(this.historyOffset);
  }

  public async undo(): Promise<void> {
    if (!this.canUndo) return;

    const currentCommand =
      this.history[this.history.length - 1 - this.historyOffset];
    if (currentCommand.kind === "TRANSACTION") {
      if (currentCommand.commands.find((subCommand) => !subCommand.rollback)) {
        throw new RollbackUnsupportedError();
      }
      for (const subCommand of [...currentCommand.commands].reverse()) {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        await this.dispatchHistoryAction(subCommand.rollback!);
      }
    } else {
      if (!currentCommand.rollback) throw new RollbackUnsupportedError();
      await this.dispatchHistoryAction(currentCommand.rollback);
    }

    runInAction(() => {
      this.historyOffset += 1;
    });
  }

  public async redo(): Promise<void> {
    if (!this.canRedo) return;

    const currentCommand =
      this.history[this.history.length - this.historyOffset];

    if (currentCommand.kind === "TRANSACTION") {
      for (const subCommand of currentCommand.commands) {
        await this.dispatchHistoryAction(subCommand);
      }
    } else {
      await this.dispatchHistoryAction(currentCommand);
    }

    runInAction(() => {
      this.historyOffset -= 1;
    });
  }

  public read(): Promise<undefined> {
    throw new Error("Method not implemented.");
  }
  public readAll(): Promise<never[]> {
    throw new Error("Method not implemented.");
  }

  public dispatch<E extends keyof M>(
    command: StorageCommand<E, M> | StorageTransaction<E, M>,
  ): Promise<void> {
    runInAction(() => {
      if (this.historyOffset) {
        this.history = this.history.splice(0, -this.historyOffset);
      }
      this.historyOffset = 0;
      this.history.push(command);
      this.history = this.history.slice(-MAX_HISTORY_STEPS);
    });
    return Promise.resolve();
  }
}
