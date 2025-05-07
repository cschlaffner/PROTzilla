import { MixinConstructor } from "./types";
import { MaybeArrayElement } from "../../utils";

const transform = <T extends object>(
  newValue: T,
  Model: MixinConstructor<MaybeArrayElement<T> & object>,
): T => {
  // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
  if (newValue instanceof Model || !newValue || typeof newValue !== "object") {
    return newValue;
  }
  if (Array.isArray(newValue)) {
    return newValue.map((value) => transform(value, Model)) as T;
  }
  const value = new Model();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if (typeof (value as any).hydrate === "function") {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (value as any).hydrate(newValue);
  } else {
    Object.keys(value).forEach((key) => {
      if (!(key in (value as object))) return;
      value[key as never] = newValue[key as never];
    });
  }

  return value as T;
};

export const EnsureClass =
  <T extends object>(Model: MixinConstructor<MaybeArrayElement<T> & object>) =>
  (value: { get: () => T; set: (value: T) => void }, { kind }: DecoratorContext) => {
    if (kind === "accessor") {
      const { get, set } = value;

      return {
        get(): T {
          return get.call(this);
        },

        set(newValue: T) {
          set.call(this, transform(newValue, Model));
        },

        init(initialValue: unknown): T {
          return transform(initialValue as Partial<T>, Model) as T;
        },
      };
    }

    return value;
  };
