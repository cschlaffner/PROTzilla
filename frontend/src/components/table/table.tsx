import { observer } from "mobx-react-lite";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { css, Interpolation, styled } from "styled-components";

import { TableProps, TableRowData, TableRowProps } from "./table.props";
import { useUpdateOnElementResize } from "../../hooks";
import { color, radius, size, spacing } from "../../theme";
import { BoxProps, FlexColumn, FlexRow } from "../box";
import { H6, Text } from "../text";
import {
  TABLE_SCROLL_LOAD_FACTOR,
  TABLE_SCROLL_RENDER_MARGIN,
} from "./constants";
import { InvisibleButton } from "../button";
import { Icon } from "../icon";

const TableWrapper = styled(FlexColumn)`
  gap: ${spacing("small")};
  overflow: hidden;
  width: 100%;
`;

const rowStyle = css<Pick<TableProps<Record<string, unknown>>, "columns">>`
  align-items: center;
  box-sizing: border-box;
  display: grid;
  grid-auto-rows: 1fr;
  grid-template-areas: "${(props) =>
    props.columns.map((column) => column.name).join(" ")}";
  grid-template-columns: ${(props) =>
    props.columns
      .map(
        (column) =>
          `${String((column.width ?? 1 / props.columns.length) * 100)}%`,
      )
      .join(" ")};
  grid-template-rows: 100%;
  gap: 0;
  padding: 0 ${spacing("small")};
  width: 100%;
` as unknown as <
  T extends TableRowData,
  AdditionalKeys extends PropertyKey = never,
>(
  props: Pick<TableProps<T, AdditionalKeys>, "columns">,
) => Interpolation<Pick<TableProps<T, AdditionalKeys>, "columns">>;

const TableHeader = styled(FlexRow)`
  ${rowStyle}

  background: ${color("primary")};
  border-radius: ${radius("smallCard")};
  min-height: ${size("buttonHeight")};
  overflow-y: auto;
  scrollbar-gutter: stable;
` as <T extends TableRowData, AdditionalKeys extends PropertyKey = never>(
  props: React.PropsWithChildren<
    BoxProps & Pick<TableProps<T, AdditionalKeys>, "columns">
  >,
) => React.JSX.Element;

export const TitleCell = styled(InvisibleButton)<{ name: string }>`
  gap: ${spacing("smallButtonGap")};
  grid-area: ${({ name }) => name};
  justify-content: flex-start;
  padding: ${spacing("small")};
`;

const ColumnTitle = styled(H6)`
  color: ${color("onPrimary")};
  overflow: hidden;
  text-align: left;
  text-overflow: ellipsis;
`;

const TableBody = styled.div<
  Pick<TableProps<Record<string, unknown>>, "isOnBackground" | "useBorder">
>`
  display: flex;
  flex: 1;
  flex-direction: column;
  background: ${({ isOnBackground }) =>
    color(isOnBackground ? "secondary" : "background")};
  border-radius: ${radius("smallCard")};
  box-sizing: border-box;
  width: 100%;
  overflow-y: auto;
  scrollbar-gutter: stable;

  ${(props) =>
    props.useBorder &&
    css`
      border: 1px solid ${color("divider")};
    `}
`;

const TableRowContainer = styled.div<
  Pick<TableProps<Record<string, unknown>>, "columns" | "showHoverEffect">
>`
  ${rowStyle}

  ${({ showHoverEffect }) =>
    showHoverEffect &&
    css`
      &:hover {
        background: ${color("secondary")};
      }
    `}
` as <T extends TableRowData, AdditionalKeys extends PropertyKey = never>(
  props: React.PropsWithChildren<
    BoxProps & Pick<TableProps<T, AdditionalKeys>, "columns">
  >,
) => React.JSX.Element;

export const TableCell = styled(FlexRow)<{ name: string }>`
  grid-area: ${({ name }) => name};
  padding: ${spacing("small")};
  overflow: hidden;
`;

const TextCell = styled(Text)<{ name: string }>`
  grid-area: ${({ name }) => name};
  padding: ${spacing("small")};
  overflow: hidden;
  text-overflow: ellipsis;
`;

const NoneFoundText = styled(Text)`
  align-self: center;
  color: ${color("textDisabled")};
  display: block;
  line-height: ${size("buttonHeight")};
  text-align: center;
  width: 100%;
`;

export const TableRow = observer(
  <T extends TableRowData, AdditionalKeys extends PropertyKey = never>({
    columns,
    data,
    children,
    ...rest
  }: React.PropsWithChildren<
    TableRowProps<T, AdditionalKeys> &
      Pick<TableProps<T, AdditionalKeys>, "showHoverEffect">
  >): React.JSX.Element => (
    <TableRowContainer {...rest} columns={columns}>
      {data
        ? columns.map((column) => {
            const value = column.formatCell
              ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
                column.formatCell((data as any)[column.name], data)
              : // eslint-disable-next-line @typescript-eslint/no-explicit-any
                (data as any)[column.name];

            return typeof value === "string" ? (
              <TextCell
                key={String(column.name)}
                name={String(column.name)}
                text={value}
              />
            ) : (
              <TableCell key={String(column.name)} name={String(column.name)}>
                {value as React.ReactElement}
              </TableCell>
            );
          })
        : children}
    </TableRowContainer>
  ),
);

const emptyArray: never[] = [];

export const Table = <
  T extends TableRowData,
  AdditionalKeys extends PropertyKey = never,
>({
  columns,
  rows = [],
  rowHeight,
  hasMore,
  onLoadMore,
  orderBy,
  order = "ASC",
  onOrderBy,
  noItemsText,
  noItemsTx = "base:noItemsToDisplay",
  noItemsComponents,
  noItemsData,
  isOnBackground,
  useBorder,
  showHoverEffect = true,
  children,
  ...rest
}: React.PropsWithChildren<TableProps<T, AdditionalKeys>>) => {
  const rowStyle = useMemo(
    () =>
      rowHeight
        ? {
            height: `${String(rowHeight)}px`,
            maxHeight: `${String(rowHeight)}px`,
            minHeight: `${String(rowHeight)}px`,
          }
        : {},
    [rowHeight],
  );

  const [bodyRef, setBodyRef] = useState<HTMLDivElement | null>(null);

  const [renderRange, setRenderRange] = useState<[number, number]>();
  const [isLoading, setIsLoading] = useState(false);
  const updateRenderRange = useCallback(() => {
    if (!rowHeight || !bodyRef) setRenderRange(undefined);
    if (!bodyRef) return;

    // Conditional Rendering
    if (rowHeight) {
      const start = Math.floor(bodyRef.scrollTop / rowHeight);
      const end = Math.ceil(bodyRef.offsetHeight / rowHeight) + start;
      setRenderRange([
        Math.max(0, start - TABLE_SCROLL_RENDER_MARGIN),
        end + TABLE_SCROLL_RENDER_MARGIN,
      ]);
    }

    // Infinite Scrolling
    if (hasMore && !isLoading) {
      const scrollFactor =
        bodyRef.scrollHeight === bodyRef.offsetHeight
          ? 1
          : bodyRef.scrollTop / (bodyRef.scrollHeight - bodyRef.offsetHeight);
      if (scrollFactor >= TABLE_SCROLL_LOAD_FACTOR) {
        setIsLoading(true);
        void onLoadMore?.().then(() => {
          setIsLoading(false);
        });
      }
    }
  }, [rowHeight, hasMore, onLoadMore, bodyRef, isLoading]);

  const size = useUpdateOnElementResize(bodyRef, Boolean(rowHeight));
  useEffect(updateRenderRange, [updateRenderRange, size]);

  useEffect(() => {
    if (bodyRef) bodyRef.scrollTop = 0;
  }, [orderBy, order, bodyRef]);

  const numRows = rows.length;

  return (
    <TableWrapper {...rest}>
      <TableHeader className="table-header" columns={columns}>
        {columns.map((col, index) => (
          <TitleCell
            name={String(col.name)}
            key={index}
            as={
              onOrderBy &&
              rows[0] &&
              Object.prototype.hasOwnProperty.call(rows[0], col.name)
                ? InvisibleButton
                : FlexRow
            }
            {...(onOrderBy &&
            rows[0] &&
            Object.prototype.hasOwnProperty.call(rows[0], col.name)
              ? {
                  onPress: () => {
                    onOrderBy(
                      col.name as keyof T,
                      orderBy === col.name
                        ? order === "ASC"
                          ? "DESC"
                          : "ASC"
                        : "ASC",
                    );
                  },
                }
              : {})}
          >
            {col.title && typeof col.title !== "string" ? (
              col.title
            ) : (
              <ColumnTitle
                className="title"
                key={index}
                tx={col.titleTx}
                txComponents={col.titleComponents}
                txData={col.titleData}
                text={col.title}
              />
            )}
            {orderBy === col.name && (
              <Icon
                icon={order === "DESC" ? "chevronDown" : "chevronUp"}
                color="onPrimary"
              />
            )}
          </TitleCell>
        ))}
      </TableHeader>

      <TableBody
        className="table-body"
        isOnBackground={isOnBackground}
        useBorder={useBorder}
        onScroll={updateRenderRange}
        ref={setBodyRef}
      >
        {rowHeight && renderRange?.[0] ? (
          <TableRow
            columns={emptyArray}
            style={{
              height: renderRange[0] * rowHeight,
              maxHeight: renderRange[0] * rowHeight,
              minHeight: renderRange[0] * rowHeight,
            }}
          />
        ) : null}
        {numRows
          ? rows
              .slice(
                rowHeight && renderRange ? renderRange[0] : undefined,
                rowHeight && renderRange ? renderRange[1] : undefined,
              )
              .map((row, index) => (
                <TableRow
                  key={
                    (row as { id?: string }).id ??
                    (rowHeight && renderRange ? renderRange[1] + index : index)
                  }
                  columns={columns}
                  data={row}
                  showHoverEffect={showHoverEffect}
                  style={rowStyle}
                />
              ))
          : (children ??
            ((noItemsText ?? noItemsTx) && (
              <NoneFoundText
                text={noItemsText}
                tx={noItemsTx}
                txComponents={noItemsComponents}
                txData={noItemsData}
              />
            )))}
        {rowHeight && renderRange && numRows - renderRange[1] > 0 ? (
          <TableRow
            columns={emptyArray}
            style={{
              height: (numRows - renderRange[1]) * rowHeight,
              maxHeight: (numRows - renderRange[1]) * rowHeight,
              minHeight: (numRows - renderRange[1]) * rowHeight,
            }}
          />
        ) : null}
      </TableBody>
    </TableWrapper>
  );
};
