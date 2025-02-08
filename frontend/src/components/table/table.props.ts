import React from "react";

import { OrderKind } from "../../utils";
import { I18nComponents, I18nData, I18nTitleProps } from "../types";

// Define TableRowData where keys can be both string or number
export type TableRowData = object;

// Define TableColumnProps with flexible key type (string | number)
export interface TableColumnProps<T extends TableRowData, K extends PropertyKey>
  extends I18nTitleProps {
  /** The column values' key in the row data objects. */
  name: K;

  /** The fraction of the table's total width this column should occupy. */
  width?: number;

  /** An optional custom formatter for all values in the column. */
  formatCell?: (
    value: K extends keyof T ? T[K] : undefined,
    rowData: T,
  ) => React.ReactNode;
}

// TableRowProps, where columns and data follow the same logic
export interface TableRowProps<
  T extends TableRowData,
  AdditionalKeys extends PropertyKey = never,
> extends React.HTMLAttributes<HTMLDivElement> {
  columns: TableColumnProps<T, keyof T | AdditionalKeys>[]; // The columns this row belongs to.
  /** The data displayed in this row, keyed by column names. */
  data?: T;
}

// Define NavbarProps, where columns and rows are based on the above flexible types
export interface TableProps<
  T extends TableRowData,
  AdditionalKeys extends PropertyKey = never,
> extends React.HTMLAttributes<HTMLDivElement> {
  /** The column definitions of the table. */
  columns: TableColumnProps<T, keyof T | AdditionalKeys>[];

  /** The row data of the table. */
  rows?: T[];

  /**
   * If given, applies a fixed width to all table rows, enabling conditional
   * rendering based on the scroll position.
   *
   * `60` is a reasonable default if you want to enable conditional rendering.
   */
  rowHeight?: number;

  /** If set to true, enables loading using infinite scrolling. */
  hasMore?: boolean;

  /** Triggers when more content should be loaded, only fires if `hasMore` is set. */
  onLoadMore?: () => Promise<unknown>;

  /** The column to sort by. */
  orderBy?: keyof T;

  /** The order to sort by. Defaults to `"ASC"`. */
  order?: OrderKind;

  /** Fires when the user selects a new sorting. */
  onOrderBy?: (orderBy?: keyof T, order?: OrderKind) => void;

  /** The raw text shown when the table is empty. */
  noItemsText?: React.ReactNode;

  /** The key for i18n translation of the no items text. */
  noItemsTx?: string;

  /** Optional components to style the translated no items text. */
  noItemsComponents?: I18nComponents;

  /** Additional data passed to the no items text translation function. */
  noItemsData?: I18nData;

  /** If set to `true`, displays an offset background. */
  isOnBackground?: boolean;

  /** If set to `true`, displays a border around the table body.   */
  useBorder?: boolean;

  /**
   * If set to `false`, hides the hover effect.
   *
   * Defaults to `true`.
   */
  showHoverEffect?: boolean;
}
