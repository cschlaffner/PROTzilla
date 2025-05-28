export type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;
export type MaybeArrayElement<ArrayType> = ArrayType extends readonly (infer ElementType)[]
  ? ElementType
  : ArrayType;
