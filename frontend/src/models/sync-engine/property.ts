import { observable, reaction, toJS } from "mobx";

/* eslint-disable @typescript-eslint/no-explicit-any */

export interface IPropertyConfig<T> {
  transform?: (value: unknown) => T;
  observe?: boolean;
}

export const Property =
  <T>({
    transform = (value) => value as T,
    observe = false,
  }: IPropertyConfig<T> = {}) =>
  (
    value: { get: () => T; set: (value: T) => void },
    // eslint-disable-next-line @typescript-eslint/unbound-method
    { kind, name, addInitializer }: DecoratorContext,
  ) => {
    if (kind === "accessor") {
      const { get, set } = value;

      addInitializer(function () {
        (this as any).properties = (this as any).properties ?? [];
        (this as any).properties.push(name);
      });

      return {
        get(): T {
          return get.call(this);
        },

        set(newValue: T) {
          const previousValue = get.call(this);
          set.call(this, transform(newValue));

          if ((this as any).sync) {
            if ((this as any).dirtyKeys.includes(name)) return;
            (this as any).dirtyKeys.push(name);
            (this as any).previousValues = (this as any).previousValues ?? {};
            (this as any).previousValues[name] = previousValue;
          }
        },

        init(initialValue: unknown) {
          const transformedValue = transform(initialValue);
          if (!observe) return transformedValue;

          const observableValue =
            typeof transformedValue === "object" && transformedValue !== null
              ? observable(transformedValue)
              : transformedValue;

          reaction(
            () => toJS(get.call(this)),
            (_newValue, previousValue) => {
              if ((this as any).sync) {
                if ((this as any).dirtyKeys.includes(name)) return;
                (this as any).dirtyKeys.push(name);
                (this as any).previousValues =
                  (this as any).previousValues ?? {};
                (this as any).previousValues[name] = previousValue;
              }
            },
          );
          return observableValue;
        },
      };
    }

    return value;
  };
