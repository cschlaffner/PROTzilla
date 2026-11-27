import { python } from "@codemirror/lang-python";
import { EditorView } from "@codemirror/view";
import { color, fontSize, size, spacing } from "@protzilla/theme";
import CodeMirror from "@uiw/react-codemirror";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { TextInputFieldProps } from "./text-input-field.props";
import { InputContainer } from "../input-container";

const StyledInput = styled.input<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

const StyledTextarea = styled.textarea<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  min-height: ${({ $isSmall }) =>
    $isSmall ? size("inputFieldHeightSmall") : size("inputFieldHeightDefault")};
  width: 100%;
  resize: vertical;
`;

const StyledCodeEditor = styled(CodeMirror)`
  width: 100%;

  .cm-editor {
    background: ${color("transparent")};
  }

  .cm-scroller {
    font-family: monospace;
    font-size: ${fontSize("default")};
  }

  .cm-gutters {
    background: ${color("backgroundOffset")};
    border-right: 1px solid ${color("divider")};
  }
`;

export const TextInputField: React.FC<TextInputFieldProps> = ({
  value: initialValue = "",
  placeholder,
  onChange,
  characterLimit = -1,
  subscript,
  rows = 1,
  isCodeEditor = false,
  ...props
}) => {
  const [value, setValue] = useState(initialValue);

  const wasThereInputAfterHandleBlurRef = useRef(false);
  const isEditingRef = useRef(false);

  const handleChange = useCallback(
    (value: string) => {
      if (characterLimit >= 0 && value.length > characterLimit) {
        return;
      }
      setValue(value);
      if (!wasThereInputAfterHandleBlurRef.current) {
        wasThereInputAfterHandleBlurRef.current = true;
        onChange(value);
      }
    },
    [characterLimit, onChange],
  );

  const handleBlur = useCallback(() => {
    isEditingRef.current = false;
    wasThereInputAfterHandleBlurRef.current = false;
    if (characterLimit >= 0 && value.length > characterLimit) {
      return;
    }
    setValue(value);
    onChange(value);
  }, [characterLimit, onChange, value]);

  useEffect(() => {
    if (!isEditingRef.current) {
      setValue(initialValue);
    }
  }, [initialValue]);

  const codeEditorExtensions = useMemo(
    () => [
      python(),
      EditorView.lineWrapping,
      EditorView.domEventHandlers({
        focus: () => {
          isEditingRef.current = true;
          return false;
        },
        blur: () => {
          handleBlur();
          return false;
        },
      }),
      EditorView.theme({
        "&": {
          minHeight: `${String(Math.max(rows, 6) * 24)}px`,
        },
        ".cm-content": {
          padding: spacing("small"),
        },
        ".cm-focused": {
          outline: "none",
        },
      }),
    ],
    [handleBlur, rows],
  );

  const combinedSubscript =
    characterLimit >= 0
      ? `${subscript ? `${subscript} | ` : ""}Character Limit ${value.length.toString()}/${characterLimit.toString()}`
      : subscript;

  return (
    <InputContainer subscript={combinedSubscript} {...props}>
      {isCodeEditor ? (
        <StyledCodeEditor
          value={value}
          basicSetup={{
            lineNumbers: true,
            foldGutter: false,
          }}
          placeholder={placeholder}
          extensions={codeEditorExtensions}
          onChange={(newValue) => {
            handleChange(newValue);
          }}
        />
      ) : rows > 1 ? (
        <StyledTextarea
          value={value}
          placeholder={placeholder}
          rows={rows}
          onChange={(e) => {
            handleChange(e.target.value);
          }}
          onBlur={handleBlur}
          $isSmall={props.isSmall ?? false}
          {...props}
        />
      ) : (
        <StyledInput
          type="text"
          value={value}
          placeholder={placeholder}
          onChange={(e) => {
            handleChange(e.target.value);
          }}
          onBlur={handleBlur}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleBlur();
              (e.target as HTMLInputElement).blur();
            }
          }}
          $isSmall={props.isSmall ?? false}
          {...props}
        />
      )}
    </InputContainer>
  );
};
