import { motion } from "framer-motion";
import React, { useCallback, useRef, useState } from "react";
import { css, styled } from "styled-components";

import { useEnableDisable, useMultiRef } from "../../hooks";
import { useTranslation } from "../../i18n";
import { FlexColumn, FlexRow, Spacer } from "../box";
import { InvisibleButton } from "../button";
import { EditTag } from "../edit-tag";
import { Icon } from "../icon";
import { InputLabel, Text } from "../text";
import { CollapsibleLabelProps, MultilineTextFieldProps, TextFieldProps } from "./text-field.props";
import {
  color,
  font,
  fontSize,
  fontWeight,
  opacity,
  radius,
  spacing,
  styledDiv,
} from "../../theme";

// TODO: Add translations for built-in texts

const StyledInput = styled.input<Pick<TextFieldProps, "isDisabled" | "hasSuccess" | "hasError">>`
  background: ${(props) => color(props.isDisabled ? "secondaryDisabled" : "backgroundOffset")};
  border: 1px solid
    ${(props) =>
      color(
        props.isDisabled
          ? props.hasError
            ? "redDisabled"
            : props.hasSuccess
              ? "greenDisabled"
              : "primaryDisabled"
          : props.hasError
            ? "red"
            : props.hasSuccess
              ? "green"
              : "gray50",
      )};
  border-radius: ${radius("button")};
  box-sizing: border-box;
  color: ${(props) => (props.isDisabled ? color("divider") : color("text"))};
  font-family: ${font("defaultWithFallbacks")};
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("default")};
  height: 40px;
  padding: ${spacing("buttonPadding")};

  -webkit-appearance: none;
  -moz-appearance: textfield;
  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  ::placeholder {
    color: ${color("textDisabled")};
  }

  ${(props) =>
    props.isDisabled
      ? css`
          cursor: not-allowed;
        `
      : css`
          &:hover {
            border-color: ${color(
              props.hasError ? "redHover" : props.hasSuccess ? "greenHover" : "gray50",
            )};
          }
        `}

  &:focus {
    border-color: ${color("primary")};
    outline: none;
  }
`;

const StyledLabel = styled.label`
  display: flex;
  flex-direction: column;
`;

const InputContainer = styledDiv.div<{ isFocused?: boolean }>`
  display: flex;
  align-items: center;
  position: relative;

  .input {
    width: 100%;
  }

  .show-password {
    display: ${({ isFocused }) => (isFocused ? "inline-flex" : "none")};
  }

  &:hover {
    .show-password {
      display: inline-flex;
    }
  }
`;

const StatusIcon = styled(Icon)`
  height: 10px;
  position: absolute;
  right: 6px;
  top: 6px;
  width: 10px;
`;

const ShowPasswordButton = styled(InvisibleButton)`
  width: 22px;
  height: 22px;
  margin-left: 10px;
  position: absolute;
  right: 10px;
`;

const RequiredLabel = styled(InputLabel)`
  color: ${color("red")};
  ${({ isDisabled }) =>
    isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}
`;

const OptionalLabel = styled(InputLabel)`
  font-size: 8px;
  line-height: 8px;
  color: ${color("text")};
  ${({ isDisabled }) =>
    isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}
`;

const LabelRow = styled(FlexRow)`
  align-items: flex-end;
`;

const SubscriptText = styled(Text)`
  font-size: 10px;
  flex-shrink: 0;
  flex-grow: 0;
  color: ${color("gray50")};
  ${({ isDisabled }) =>
    isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}
`;

const SubscriptsRow = styled(FlexRow)`
  align-self: stretch;
  margin-top: 5px;
  height: 12px;
`;

const SubscriptSpacer = styled(Spacer)<{ hasMinWidth?: boolean }>`
  ${({ hasMinWidth }) =>
    hasMinWidth &&
    css`
      min-width: 10px;
    `}
`;

const TagContainer = styledDiv.div<{
  isFocused?: boolean;
  isDisabled?: boolean;
  hasError?: boolean;
  hasSuccess?: boolean;
}>`
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  min-height: 40px;
  max-width: 100%;
  padding: 8px 16px;
  border-radius: 6px;
  gap: 5px;
  box-sizing: border-box;
  position: relative;

  ${(props) =>
    props.isFocused &&
    css`
      border-color: ${color("primary")};
    `}

  border: 1px solid
  ${(props) =>
    color(
      props.isDisabled
        ? props.isFocused
          ? "primaryDisabled"
          : props.hasError
            ? "redDisabled"
            : props.hasSuccess
              ? "greenDisabled"
              : "gray50"
        : props.isFocused
          ? "primary"
          : props.hasError
            ? "red"
            : props.hasSuccess
              ? "green"
              : "gray50",
    )};

  ${(props) =>
    props.isDisabled
      ? css`
          cursor: not-allowed;
        `
      : css`
          &:hover {
            border-color: ${color(
              props.isFocused
                ? "primaryHover"
                : props.hasError
                  ? "redHover"
                  : props.hasSuccess
                    ? "greenHover"
                    : "gray50",
            )};
          }
        `}
`;

const TagInput = styled.input<{
  isDisabled?: boolean;
  hasError?: boolean;
  hasSuccess?: boolean;
}>`
  background: ${(props) => color(props.isDisabled ? "secondaryDisabled" : "backgroundOffset")};
  min-width: 80px;
  flex: 1;
  border: none;
  padding: 0;
  margin: 0;
  height: 20px;
  color: ${(props) => (props.isDisabled ? color("gray50") : color("text"))};
  font-family: ${font("defaultWithFallbacks")};
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("default")};

  -webkit-appearance: none;
  -moz-appearance: textfield;
  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &:focus {
    outline: none;
  }

  ${(props) =>
    props.isDisabled &&
    css`
      cursor: not-allowed;
    `}
`;

const StyledColumn = styled(FlexColumn)`
  align-items: stretch;
`;

export const TextField = React.forwardRef<
  HTMLInputElement,
  TextFieldProps & { as?: "input" | "textarea" }
>(function TextField(
  {
    as: asProp,
    children,
    className,
    style,
    label,
    labelTx,
    labelComponents,
    labelData,
    placeholder,
    placeholderTx,
    placeholderData,
    type,
    defaultValue,
    value,
    valueTx,
    valueData,
    isDisabled,
    isRequired,
    isOptional,
    hasSuccess,
    hasError,
    subscript,
    subscriptTx,
    subscriptComponents,
    subscriptData,
    maxCharacters,
    maxCharactersTx,
    maxTags,
    maxTagsTx,
    tags = [],
    setTags,
    onFocus,
    onChange,
    onChangeText,
    onBlur,
    onKeyDown,
    onConfirm,
    onCancel,
    onSubmitField,
    tagTransformFunction,
    ...rest
  },
  ref,
) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const setInputRef = useMultiRef(inputRef, ref);

  const [isFocused, setIsFocused] = useState(false);
  const [isEdited, setIsEdited] = useState(false);
  const [internalValue, setInternalValue] = useState("");

  // Store value in a ref to prevent frequent updates of the useCallback hooks
  const valueRef = useRef(value);
  valueRef.current = isEdited ? internalValue : value;

  /**
   * Indicates if an edit confirmation has already been handled to prevent
   * firing twice.
   */
  const hasBeenHandledRef = useRef(false);

  /** Activates the text input. */
  const handleFocus = useCallback(
    (event: React.FocusEvent<HTMLInputElement>) => {
      if (onFocus) onFocus(event);
      setIsFocused(true);

      hasBeenHandledRef.current = false;
      setInternalValue(valueRef.current ?? "");
      setIsEdited(true);
    },
    [onFocus],
  );

  /** Confirms the changed value. */
  const confirmEdit = useCallback(() => {
    if (!isEdited) return;
    if (onConfirm) {
      const newValue = type === "number" ? parseFloat(valueRef.current ?? "") : valueRef.current;
      if (!(type === "number" && Number.isNaN(newValue))) {
        onConfirm(String(newValue ?? ""));
      }
    }

    setIsEdited(false);
    setInternalValue("");
  }, [isEdited, onConfirm, type]);

  /** Discards the changed value. */
  const cancelEdit = useCallback(() => {
    if (!isEdited) return;
    if (onCancel) onCancel(valueRef.current ?? "");

    setIsEdited(false);
    setInternalValue("");
  }, [isEdited, onCancel]);

  // Event Handling

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      if (type === "tag" && maxTags !== undefined && maxTags <= tags.length) {
        return;
      }

      if (onChange) onChange(event);

      const newValue =
        maxCharacters !== undefined
          ? event.target.value.slice(0, maxCharacters)
          : event.target.value;

      if (onChangeText) onChangeText(newValue);
      if (isEdited) setInternalValue(newValue);
    },
    [type, tags, maxTags, onChange, maxCharacters, onChangeText, isEdited],
  );

  const handleBlur = useCallback(
    (event: React.FocusEvent<HTMLInputElement>) => {
      if (onBlur) onBlur(event);
      setIsFocused(false);

      if (!hasBeenHandledRef.current) confirmEdit();
      hasBeenHandledRef.current = false;
    },
    [confirmEdit, onBlur],
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (onKeyDown) onKeyDown(event);

      if (!isEdited) {
        // Still handle submit in case no onConfirm/onCancel handlers are given
        if (event.key === "Enter") onSubmitField?.();
        return;
      }
      if (event.key === "Enter") {
        if (asProp === "textarea" && !(event.metaKey || event.ctrlKey)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();

        confirmEdit();
        hasBeenHandledRef.current = true;
        inputRef.current?.blur();

        onSubmitField?.();
      } else if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();

        cancelEdit();
        hasBeenHandledRef.current = true;
        inputRef.current?.blur();
      }
    },
    [asProp, cancelEdit, confirmEdit, isEdited, onKeyDown, onSubmitField],
  );

  // Hide/Show Password

  const [showPassword, setShowPassword] = useState(false);
  const [enableShowPassword, disableShowPassword] = useEnableDisable(setShowPassword);

  const { t } = useTranslation();

  const removeTag = useCallback(
    (index: number) => {
      setTags?.(tags.filter((_, i) => i !== index));
      inputRef.current?.focus();

      onCancel?.(tags[index]);
    },
    [onCancel, setTags, tags],
  );

  const handleKeyDownTag = useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      onKeyDown?.(event);

      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();

        if (internalValue.length) {
          const newTagValue = tagTransformFunction?.(internalValue) ?? internalValue;
          setTags?.([...tags, newTagValue]);
          onConfirm?.(newTagValue);
          onSubmitField?.();
          setInternalValue("");
        }
      } else if (event.key === "Backspace" && !internalValue.length) {
        const tagsCopy = [...tags];
        const poppedTag = tagsCopy.pop();
        if (poppedTag === undefined) return;
        event.preventDefault();
        setTags?.(tagsCopy);
        setInternalValue(poppedTag);
      }
    },
    [onKeyDown, internalValue, tagTransformFunction, setTags, tags, onConfirm, onSubmitField],
  );

  const input = (
    <StyledInput
      {...rest}
      as={asProp as undefined}
      className="input"
      placeholder={placeholderTx ? t(placeholderTx, placeholderData) : placeholder}
      type={showPassword ? "text" : type}
      defaultValue={defaultValue}
      value={isEdited ? internalValue : valueTx ? t(valueTx, valueData) || "" : value}
      disabled={isDisabled}
      isDisabled={isDisabled}
      hasSuccess={hasSuccess}
      hasError={hasError}
      ref={setInputRef}
      onFocus={handleFocus}
      onChange={handleChange}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
    />
  );

  const statusIcons = (
    <>
      {hasSuccess && !hasError && (
        <StatusIcon
          className="status-icon"
          icon="checkmark"
          color="green"
          isDisabled={isDisabled}
        />
      )}
      {hasError && (
        <StatusIcon className="status-icon" icon="close" color="red" isDisabled={isDisabled} />
      )}
    </>
  );

  const subscripts =
    maxCharacters !== undefined ||
    (type === "tag" && maxTags !== undefined) ||
    subscript ||
    subscriptTx ? (
      <SubscriptsRow>
        {type === "tag" && maxTags !== undefined ? (
          <SubscriptText
            tx={maxTagsTx ?? "base:maxTags"}
            txData={{
              currentLength: tags.length || 0,
              maxLength: maxTags,
            }}
            isDisabled={isDisabled}
          />
        ) : (
          (subscript ?? subscriptTx) && (
            <SubscriptText
              text={subscript}
              tx={subscriptTx}
              txComponents={subscriptComponents}
              txData={subscriptData}
              isDisabled={isDisabled}
            />
          )
        )}

        <SubscriptSpacer
          hasMinWidth={Boolean(
            maxCharacters &&
              (subscript ?? subscriptTx ?? (type === "tag" && maxTags !== undefined)),
          )}
        />

        {maxCharacters !== undefined && (
          <SubscriptText
            tx={maxCharactersTx ?? "base:inputLength"}
            txData={{
              currentLength: (isEdited ? internalValue : value)?.length ?? 0,
              maxLength: maxCharacters,
            }}
            isDisabled={isDisabled}
          />
        )}
      </SubscriptsRow>
    ) : null;

  const inputContainer =
    type === "tag" ? (
      <TagContainer
        isFocused={isFocused}
        isDisabled={isDisabled}
        hasError={hasError}
        hasSuccess={hasSuccess}
      >
        {tags.map((tag, index) => (
          <EditTag
            key={index}
            text={tag}
            onButtonPress={() => {
              removeTag(index);
            }}
            isDisabled={isDisabled}
          />
        ))}

        <TagInput
          onKeyDown={handleKeyDownTag}
          placeholder={placeholderTx ? t(placeholderTx, placeholderData) : placeholder}
          onFocus={handleFocus}
          onBlur={handleBlur}
          value={internalValue}
          onChange={handleChange}
          disabled={
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            isDisabled ?? (Boolean(maxTags) && tags.length >= maxTags!)
          }
          isDisabled={
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            isDisabled ?? (Boolean(maxTags) && tags.length >= maxTags!)
          }
          ref={setInputRef}
        />

        {statusIcons}

        {children}
      </TagContainer>
    ) : (
      <InputContainer isFocused={isFocused}>
        {input}

        {statusIcons}

        {children}

        {type === "password" && (
          <ShowPasswordButton
            className="show-password"
            icon="eye"
            tabIndex={-1}
            isDisabled={isDisabled}
            onPointerDown={enableShowPassword}
            onPointerUp={disableShowPassword}
          />
        )}
      </InputContainer>
    );

  return label || labelTx ? (
    <StyledLabel className={className} style={style}>
      <LabelRow>
        <InputLabel
          className="label"
          text={label}
          tx={labelTx}
          txComponents={labelComponents}
          txData={labelData}
          isDisabled={isDisabled}
        />
        {isRequired && <RequiredLabel text="*" isDisabled={isDisabled} />}
        {isOptional && !isRequired && (
          <>
            <Spacer />
            <OptionalLabel tx="base:optional" isDisabled={isDisabled} />
          </>
        )}
      </LabelRow>

      {inputContainer}
      {subscripts}
    </StyledLabel>
  ) : (
    <StyledColumn className={className} style={style}>
      {inputContainer}
      {subscripts}
    </StyledColumn>
  );
});

export const SmallTextField = styled(TextField)`
  .input {
    height: 30px;
  }
`;

export const MultilineTextField = styled(
  React.forwardRef<HTMLInputElement, MultilineTextFieldProps>(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    function MultilineTextField({ height, width, ...rest }, ref) {
      return <TextField as="textarea" ref={ref} {...rest} />;
    },
  ),
)`
  .input {
    ${({ height }) =>
      height &&
      css`
        max-height: ${height};
        resize: none;
      `}

    height: ${({ height }) => height ?? "100px"};
    min-height: ${({ height }) => height ?? "100px"};

    ${({ width }) =>
      width &&
      css`
        width: ${width};
        max-width: ${width};
        min-width: ${width};
      `}

    padding: 12px 16px;
  }
`;

const CollapsibleContainer = styled(motion.div)`
  overflow: hidden;
  white-space: nowrap;
  padding-bottom: 1px;
`;

export const CollapsibleLabel: React.FC<CollapsibleLabelProps> = ({
  width,
  collapsedWidth = 0,
  isCollapsed,
  children,
}: CollapsibleLabelProps) => {
  return (
    <CollapsibleContainer
      initial={{ width: isCollapsed ? collapsedWidth : width }}
      animate={{ width: isCollapsed ? collapsedWidth : width }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      {children}
    </CollapsibleContainer>
  );
};
