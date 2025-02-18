import axios, { isAxiosError } from "axios";
import {action, observable, runInAction} from "mobx";

import type { I18nMessage } from "../components";
import { API_ROOT } from "../constants";
import { i18n, SupportedLanguage } from "../i18n";
import { type ColorMode, getTheme, Theme } from "../theme";
import { isPromise } from "../utils";
import { defaultStorageClient } from "./sync-engine";
import { RESTAdapter } from "./sync-engine/rest-adapter";

export class RootStore {
  public axios = axios.create({ baseURL: API_ROOT });

  public client = defaultStorageClient;

  /** The current language. */
  @observable public accessor language: string = i18n.language;

  /** The current theme. */
  @observable public accessor colorMode: ColorMode = "light";

  public shouldPersist = false;

  protected messageTimeouts: Record<string, ReturnType<typeof setTimeout> | undefined> = {};
  @observable protected accessor messages: Record<
    string,
    I18nMessage | undefined
  > = {};

  constructor() {
    this.client.remote = new RESTAdapter(API_ROOT, undefined, this.axios);
    this.client.handleError = (error: Error) => {
      this.processError(error);
    };
  }

  // Theme Management
  public get theme(): Theme {
    return getTheme(this.colorMode);
  }
  @action
  public setColorMode(colorMode: ColorMode): void {
    this.colorMode = colorMode;
    // TODO: Persistence
  }

  // Language Management
  public async setLanguage(language: SupportedLanguage): Promise<void> {
    await i18n.changeLanguage(language);
    runInAction(() => {
      this.language = language;
      // TODO: Persistence
    });
  }

  // Error Handling
  public getMessage(channel = "error"): I18nMessage | undefined {
    return this.messages[channel];
  }

  public get error() {
    return this.getMessage("error");
  }

  @action
  public setMessage(
    channel = "error",
    message?: I18nMessage,
    autoClear = true,
  ): void {
    this.messages[channel] = message;

    if (this.messageTimeouts[channel] !== undefined) {
      clearTimeout(this.messageTimeouts[channel]);
      this.messageTimeouts[channel] = undefined;
    }
    if (message && this.theme.durations.errorDisplayDuration && autoClear) {
      this.messageTimeouts[channel] = setTimeout(() => {
        this.setMessage(channel, undefined);
      }, this.theme.durations.errorDisplayDuration);
    }
  }

  public setError(message?: I18nMessage, autoClear = true) {
    this.setMessage("error", message, autoClear);
  }

  protected processError(
    error: Error,
    mapError?: (error: Error) => Partial<I18nMessage> | undefined,
    autoClear?: boolean,
  ): void {
    const mapped = mapError?.(error);
    if (mapError && !mapped) return;

    this.setError(
      {
        titleTx: "base:error",
        descriptionTx: isAxiosError(error) ? "base:apiError" : error.message, // TODO: Handle status codes
        ...mapped,
      },
      autoClear,
    );
  }

  public handleErrors = <T>(
    executor?: () => T,
    mapError?: (error: unknown) => Partial<I18nMessage> | undefined,
    autoClearError?: boolean,
  ): T extends Promise<infer U>
    ? Promise<{ success: boolean; result?: U }>
    : { success: boolean; result?: T } => {
    if (!executor) {
      this.setError(undefined);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return { success: true } as any;
    }

    try {
      const result = executor();

      if (isPromise(result)) {
        return result
          .then((value) => ({ success: true, result: value }))
          .catch((error: unknown) => {
            this.processError(error as Error, mapError, autoClearError);
            return { success: false };
          })
          .then((returnValue) => {
            if (returnValue.success) this.setError(undefined);
            return returnValue;
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
          }) as any;
      }

      this.setError(undefined);

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return { success: true, result } as any;
    } catch (error) {
      this.processError(error as Error, mapError, autoClearError);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return { success: false } as any;
    }
  };
}
