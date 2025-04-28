import { Section } from "../components/sidebar/types.ts";

export type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

export type MaybeArrayElement<ArrayType> = ArrayType extends readonly (infer ElementType)[]
  ? ElementType
  : ArrayType;

export interface Run {
  run_name: string;
  creation_date: string;
  modification_date: string;
  memory_mode: string;
  run_steps: string[];
  favourite_status: boolean;
  run_tags: string[];
}

export interface RunData {
  current_section: string;
  current_step_index: number;
  displayed_steps: Section[];
  memory_usage: string;
}
